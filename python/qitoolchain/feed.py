## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Toolchain feeds

"""


import os
import sys
import logging
import hashlib
import urlparse
from StringIO import StringIO
from xml.etree import ElementTree as etree

import qibuild
import qitoolchain

LOGGER = logging.getLogger(__name__)


def raise_parse_error(package_tree, feed, message):
    """ Raise a nice pasing error about the given
    package_tree element.

    """
    as_str = etree.tostring(package_tree)
    mess  = "Error when parsing feed: '%s'\n" % feed
    mess += "Could not parse:\t%s\n" % as_str
    mess += message
    raise Exception(mess)


def tree_from_feed(feed_location):
    """ Returns an ElementTree object from an
    feed location

    """
    fp = None
    tree = None
    try:
        if os.path.exists(feed_location):
            fp = open(feed_location, "r")
        else:
            fp = qitoolchain.remote.open_remote_location(feed_location)
        tree = etree.ElementTree()
        tree.parse(fp)
    except Exception, e:
        mess  = "Could not parse %s\n" % feed_location
        LOGGER.error(mess)
        raise
    finally:
        if fp:
            fp.close()
    return tree


def handle_package(package, package_tree, toolchain):
    """ Handle a package.

    It is has an url, download and extract it.

    Update the package given as first parameter
    """
    # feed attribue of package_tree is set during parsing
    feed = package_tree.get("feed")
    name = package_tree.get("name")
    if not name:
        raise_parse_error(package_tree, feed, "Missing 'name' attribute")

    package.name = name
    # set package.feed so that toolchain will know where the package
    # came from
    package.feed = feed
    package.version = package_tree.get("version")
    if package_tree.get("url"):
        handle_remote_package(feed, package, package_tree, toolchain)
    if package_tree.get("directory"):
        handle_local_package(package, package_tree)
    if package_tree.get("toolchain_file"):
        handle_toochain_file(package, package_tree)

def handle_remote_package(feed, package, package_tree, toolchain):
    """ Set package.path of the given package,
    downloading it and extracting it if necessary.

    """
    package_url = package_tree.get("url")
    package_name = package_tree.get("name")

    if "://"  in feed:
        # package_url may be relative to the feed url:
        package_url = urlparse.urljoin(feed, package_url)

    # We use a sha1 for the url to be sure to not downlad the
    # same package twice
    # pylint: disable-msg=E1101
    archive_name = hashlib.sha1(package_url).hexdigest()
    top = archive_name[:2]
    rest = archive_name[2:]
    if package_url.endswith(".tar.gz"):
        rest += ".tar.gz"
    if package_url.endswith(".zip"):
        rest += ".zip"
    output = toolchain.cache
    output = os.path.join(output, top)
    message = "Getting package %s from %s" % (package_name, package_url)
    package_archive = qitoolchain.remote.download(package_url,
        output,
        output_name=rest,
        clobber=False,
        message=message)

    LOGGER.info("Toolchain %s: adding package %s", toolchain.name, package.name)
    packages_path = qitoolchain.toolchain.get_default_packages_path(toolchain.name)
    should_skip = False
    dest = os.path.join(packages_path, package_name)
    if not os.path.exists(dest):
        should_skip = False
    else:
        dest_mtime = os.stat(dest).st_mtime
        src_mtime  = os.stat(package_archive).st_mtime
        if src_mtime < dest_mtime:
            should_skip = True
    if not should_skip:
        if os.path.exists(dest):
            qibuild.sh.rm(dest)
        try:
            extracted = qibuild.archive.extract(package_archive, packages_path, topdir=package_name)
        except qibuild.archive.InvalidArchive, err:
            mess = str(err)
            mess += "\nPlease fix the archive and try again"
            raise Exception(mess)
    package.path = dest


def handle_local_package(package, package_tree):
    """ Set package.path using package.feed

    """
    # feed attribue of package_tree is set during parsing
    feed = package_tree.get("feed")
    directory = package_tree.get("directory")
    feed_root = os.path.dirname(feed)
    package_path = os.path.join(feed_root, directory)
    package_path = qibuild.sh.to_native_path(package_path)
    package.path = package_path


def handle_toochain_file(package, package_tree):
    """ Make sure package.toolchain_file is
    relative to package.path

    """
    toolchain_file = package_tree.get("toolchain_file")
    package_path = package.path
    # toolchain_file can be an url too
    if not "://" in toolchain_file:
        package.toolchain_file = os.path.join(package_path, toolchain_file)
    else:
        tc_file = qitoolchain.remote.download(toolchain_file, package_path)
        package.toolchain_file = tc_file

class ToolchainFeedParser:
    """ A class to handle feed parsing

    """
    def __init__(self):
        self.packages = list()
        # A dict name -> version used to only keep the latest
        # version
        self._versions = dict()

    def append_package(self, package_tree):
        """ Add a package to self.packages.
        If an older version of the package exists,
        replace by the new version

        """
        version = package_tree.get("version")
        name = package_tree.get("name")

        names = self._versions.keys()
        if name not in names:
            self._versions[name] = version
            self.packages.append(package_tree)
        else:
            if version is None:
                # if version not defined, don't keep it
                return
            prev_version = self._versions[name]
            if qitoolchain.version.compare(prev_version, version) > 0:
                return
            else:
                self.packages = [x for x in self.packages if x.get("name") != name]
                self.packages.append(package_tree)
                self._versions[name] = version

    def parse(self, feed):
        """ Recursively parse the feed, filling the self.packages

        """
        tree = tree_from_feed(feed)
        package_trees = tree.findall("package")
        for package_tree in package_trees:
            package_tree.set("feed", feed)
            self.append_package(package_tree)
        feeds = tree.findall("feed")
        for feed_tree in feeds:
            feed_url = feed_tree.get("url")
            if feed_url:
                # feed_url can be relative to feed:
                if not "://" in feed_url:
                    feed_url = urlparse.urljoin(feed, feed_url)
                self.parse(feed_url)


def parse_feed(toolchain, feed, dry_run=False):
    """ Helper for toolchain.parse_feed

    """
    # Remove every package that came from a feed
    # (thus keeping the packages added directly)
    for package in toolchain.packages:
        if package.feed:
            toolchain.remove_package(package.name)
    parser = ToolchainFeedParser()
    parser.parse(feed)
    package_trees = parser.packages
    errors = list()
    for package_tree in package_trees:
        package = qitoolchain.Package(None, None)
        if dry_run:
            package_name = package_tree.get("name")
            package_url  = package_tree.get("url")
            # Check that url can be opened
            fp = None
            try:
                fp = qitoolchain.remote.open_remote_location(package_url)
            except Exception, e:
                error = "Could not add %s from %s\n" % (package_name, package_url)
                error += "Error was: %s" % e
                errors.append(error)
                continue
            finally:
                if fp:
                    fp.close()
            if package_url:
                print "Would add ", package_name, "from", package_url
            continue
        else:
            handle_package(package, package_tree, toolchain)
        if package.path is None:
            mess  = "could guess package path from this configuration:\n"
            mess += etree.tostring(package_tree)
            mess += "Please make sure you have at least an url or a directory\n"
            LOGGER.warning(mess)
            continue
        if not dry_run:
            toolchain.add_package(package)

    if dry_run and errors:
        print "Errors when parsing %s\n" % feed
        for error in errors:
            print error
        sys.exit(2)

def add_package_to_feed(feed_xml, name, url, version=None):
    """ Add a package to a xml feed
    :param feed_xml: string contents of the feed
    :param name: the name of the package
    :param url: the url of the package
    :param version:  (optional) the version of the package
    :returns: the new xml contents as string

    """
    tree = etree.ElementTree()
    tree.parse(feed_xml)
    package_elem = etree.Element("package")
    package_elem.set("name", name)
    package_elem.set("url", url)
    if version:
        package_elem.set("version", version)
    root = tree.getroot()
    root.append(package_elem)
    out = StringIO()
    tree.write(feed_xml)
