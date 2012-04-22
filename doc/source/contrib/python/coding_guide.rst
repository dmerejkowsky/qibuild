Python coding guide
===================

.. highlight:: python

General
-------

* The code should follow the Python coding style expressed in
  http://www.python.org/dev/peps/pep-0008/ PEP8 with the following
  reminders/exceptions

* Keep the length of the line below *80* characters when possible,
  and when it does not hurt readability, and below *100* characters
  at any case.

* Indentation is made of *four spaces*

* No trailing whitespace are allowed.

* Every text file must be pushed using *UNIX line endings*. (On windows, you
  are advised to set ``core.autocrlf`` to true).

* Variables, functions and modules are named ``like_this``
  *lower case, underscore*

* Classes are named ``LikeThis`` *camel case*

* Constants and globals are named ``LIKE_THIS`` *upper case, underscore*

* Please use a spell checker when you write comments. Typos in
  comments are annoying and distractive, typos in doc strings are
  bad because we may generate public documentation from those
  doc strings one day.

Doc strings
------------

Right now the state of the docstrings inside qiBuild are quite a mess.
But you should try to write docstrings as if all of then were going
to be use with `sphinx autodoc extension <http://sphinx.pocoo.org/ext/autodoc.html>`_.

So the canonical docstring should look like:

.. code-block:: python

    def foo(bar, baz):
        """ Does this and that
        :param bar: ...
        :param baz: ...

        :raise: MyError if ...
        :return: True if ...

        """

For easy code re-use
--------------------


* *Every file* that ends with a .py *must* support to be imported, without
  doing anything or printing anything to the screen.

* ``import foo`` must never fails, unless there's a necessary module that could
  not be found. But do not catch the ImportError unless it is necessary, for
  example to deal with optional dependencies, for instance::

    import required_module

    HAS_NICE_FEATURE = True
    try:
      import nicefeature
    except ImportError:
      HAS_NICE_FEATURE = False

    ...

    if HAS_NICE_FEATURE:
      ....



* Even if you are sure you code is standalone, and is only supposed to be used
  as a script, please follow the following skeleton::

    """The foo script adds spam to the eggs """

    def add_eggs(spam, eggs):
      """Add some spam to the eggs """

      ...


    def main():
      """Parse command line """

      ...

      add_eggs(spam, eggs)

    if __name__ == "__main__":
      main()

Note that the ``main()`` function does nothing but parsing command line, the real
work being done by a nicely named ``add_eggs`` function.

Unless you have a good reason too, please do not call ``sys.exit()`` outside the
``main()`` function.

You will be glad to have written your ``foo.py`` script this way if you want to
add some spam to the eggs somewhere else :)


* Please avoid doing lots and lots of import at the beginning of
  the file::

    # BAD:
    import foo
    from foo.spam import Spam
    from foo.eggs import Eggs

    ...

    spam = Spam()
    eggs = Eggs()


    # OK:
    import foo

    ...

    spam = foo.spam.Spam()

    eggs = foo.eggs.Eggs()


For this to work, you will have to put something like this in
``foo/__init__.py`` ::

  from foo import spam
  from foo import eggs


File Paths
----------

* **Never** use strings to manipulate file paths. Use ``os.path.join``
  which will handle all the nasty stuff for you::

    # BAD : you are doomed if you ever want to
    # generate a .bat file with bar_path
    bar_path = spam_path + "/" + "bar"

    # OK:
    bar_path = os.path.join(spam_path, "bar")

* When using ``os.path.join``, use one argument per file part::

    # BAD: you can end up with an ugly path like c:\path\to/foo/bar
    my_path = os.path.join(base_dir, "foo/bar")

    # OK:
    my_path = os.path.join(base_dir, "foo", "bar")


* **Always** convert files coming from the user to native, absolute path::

    user_input = ...
    my_path = qibuild.sh.to_native_path(user_input)

* Always store and manipulate native paths (using ``os.path``), and if needed
  convert to POSIX or Windows format at the last moment.
  Native paths are also *always* stored as ``str`` objects, not ``unicode``
  (See :ref:`qibuild-coding-guide-string-unicode`)

.. note:: If you need to build POSIX paths, don't use string operations
   either, use `posixpath.join`  (This works really well to build URL, for
   instance)

* Pro-tip: hard-coding paths on Windows:

Use `r"` rather than ugly `\\\\` ::

  # UGLY:
  WIN_PATH = "c:\\windows\\spam\\eggs"

  # NICE:
  WIN_PATH = r"c:\windows\spam\eggs"


Environment Variables
---------------------

Please make sure to **never** modify ``os.environ``

Remember that ``os.environ`` is in fact a huge global variable, and we all know
it's a bad idea to use global variables ...

Instead, use a copy of ``os.environ``, for instance::

  import qibuild

  # Note the .copy() !
  # If you forget it, build_env is a *reference* to
  # os.environ, so os.environ will be modified ...
  cmd_env = os.environ.copy()
  cmd_env["SPAM"] = "eggs"
  # Assuming foobar need SPAM environment variable set to 'eggs'
  cmd = ["foobar"]
  qibuild.command.call(foobar, env=cmd_env)


In more complex cases, especially when handling the
%PATH% environment variable, you can use ``qibuild.envsetter.EnvSetter``.

A small example::

  import qibuild

  envsetter = qibuild.envsetter.EnvSetter()
  envsetter.prepend_to_path(r"c:\Program Files\Foobar\bin")
  build_env = envsetter.get_build_env()
  cmd = ["foobar", "/spam:eggs"]
  qibuild.command.call(cmd, env=build_env)


.. _qibuild-coding-guide-string-unicode:

Strings and Unicode
--------------------

What will be a Python coding guide not mentionning this subject ?

Principle
+++++++++

 - Assume every file is UTF-8 encoded (FIXME : check what CMake does with toolchain files ...)
 - Store every configuration strings as ``unicode`` types
 - Store file paths as ``str`` types. (Because they will directly be used by the OS)
 - Convert input from user from ``str`` to ``unicode`` as soon as possible
 - Convert output from qibuild to OS from ``unicode`` to ``str`` at the last moment

Convention (for local variables only)
+++++++++++++++++++++++++++++++++++++

  - Unicode types are prefixed with `u_`
  - String types are prefixed with `b_`

Small examples:

.. code-block:: python

    # A file path: we know it's a ``str`` and a absolute, native path:
    b_project_dir = project.directory
    # So this should work:
    cmake = os.path.join(b_project_dir, project.directory)

    # Read from configuration: we know it's a ``unicode``
    u_build_type = toc.build_type
    # Will be sent to the OS: so we need to convert to ``str``:
    b_build_type = u_build_type.encode("UTF-8")
    cmake_args = ["-DCMAKE_BUILD_TYPE=%s" % b_build_type]


    # Read from the comman line: it's a ``str``
    b_project_name = args.name
    # Using internal strings variables, we need to convert to ``unicode``:
    u_project_name = b_project_name.decode("UTF-8")
    project = toc.get_project(u_project_name)


Rationale
+++++++++

* If you are creating a local variable and don't know if it's a ``str`` or a
  ``unicode``, we know we have a bug waiting to happen ...

* Such a convention will make it much easier to port qibuild to Python3 in the
  future  (the ``b_`` prefix obviously means ``bytes``)

* It also creates two easy to remember patterns:

.. code-block:: python

  b_<foo>  = u_<foo>.encode("UTF-8")
  u_<foo>  = b_<foo>.decode("UTF-8")


* We really want qibuild to be usbable everywhere, and not force people to
  have a specific locale.



Logging
-------

* Usage of the logging module is advised. It enables you to display nice,
  colorful messages to the user, helps to debug with the ``-v`` option, has a
  nice syntax...
  Please do not use print unless you have a very good reason to.

* Get a logger with::

    import logging

    LOGGER = logging.getLogger(__name__)

This makes sure the names of the loggers are always consistent with the source code.

Debugging
---------

When something goes wrong, you will just have the last error message printed,
with no other information. (Which is nice for the end user!)

If it's an *unexpected* error message, here is what you can do:

* run qibuild with ``-v`` flag to display debug messages

* run qibuild with ``--backtrace`` to print the full backtrace

* run qibuild with ``--pdb`` to drop to a pdb session when an uncaught exception is raised.

.. _qibuild-coding-guide-error-messages:

Error messages
--------------

Please do not overlook those. Often, when writing code you do something like::

  try:
     something_really_complicated()
  except SomeStrangeError, e:
     log.error("Error occured: %s", e)


Because you are in an hurry, and just are thinking "Great, I've handled the
exception, now I can go back to write some code ..."

The problem is: the end user does not care you are glad you have handled the
exception, he needs to **understand** what just happens.

So you need to take a step back, think a little. "What path would lead to
this exception? What was the end user probably doing? How can I help him
understand what went wrong, and how he can fix this?"

So here is a short list of do's and don'ts when you are writing your error
message.

* Wording should look like::

    Could not < descritiion for what went wrong >
    <Detailed explanation>
    Please < suggestion of a solution >

  For instance::

    Could not open configuration file
    'path/to/inexistant.cfg' does not exist
    Please check your configuration.


* Put filenames between quotes. For instance, if you are using a path given
  via a GUI, or via a prompt, it's possible that you forgot to strip it before
  using it, thus trying to create ``'/path/to/foo '`` or ``'path/to/foo\n'``.
  Unless you are putting the filename between quotes, this kind of error is hard
  to find.


* Put commands to use like this::

    Please try running: `qibuild configure -c linux32 foo'


* Give information

  Code like this makes little kitten cry::

    try:
      with open(config_file, "w") as fp:
        config = fp.read()
    except IOError, err:
      raise Exception("Could not open config file for writing")


  It's not helpful at all!
  It does not answer those basic questions:

    * What was the config file?
    * What was the problem with opening the config file?
    * ...

  So the end user has **no clue** what to do...

  And the fix is so simple! Just add a few lines::

    try:
      with open(config_file, "w") as fp:
        config = fp.read()
    except IOError, err:
      mess   = "Could not open config '%s' file for writing\n" % config_file
      mess += "Error was: %s" % err
      raise Exception(mess)

  So the error message would then be ::

    Could not open '/etc/foo/bar.cfg' for writing
    Error was: [Errno 13] Permission denied

  Which is much more helpful.



* Suggest a solution

  This is the harder part, but it is nice if the user can figure out what to do
  next.

  Here are a few examples::

    $ qibuild configure -c foo

    Error: Invalid configuration foo
     * No toolchain named foo. Known toolchains are:
        ['linux32', 'linux64']
     * No custom cmake file for config foo found.
       (looked in /home/dmerejkowsky/work/tmp/qi/.qi/foo.cmake)


    $ qibuild install foo (when build dir does not exists)

    Error: Could not find build directory:
      /home/dmerejkowsky/work/tmp/qi/foo/build-linux64-release
    If you were trying to install the project, make sure that you have configured
    and built it first


    $ qibuild configure # when not in a worktree

    Error: Could not find a work tree. please try from a valid work tree,
    specify an existing work tree with '--work-tree {path}', or create a new
    work tree with 'qibuild init'


    $ qibuild configure # at the root for the worktree

    Error: Could not guess project name from the working tree. Please try
    from a subdirectory of a project or specify the name of the project.


Interacting with the user
--------------------------

Make sure you only ask user when you have absolutely no way
to do something smart by default

(See for instance how ``qibuild open`` ask when it has absolutely
no choice but to ask)

And when you ask, make sure the default action (pressing enter) will
do the smart thing by default.

Most people will not pay attention to the questions, (and they do not
have to), so make the default obvious.

(See for instance how ``qibuild config --wizard`` does it)
