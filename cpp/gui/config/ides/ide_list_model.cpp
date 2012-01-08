#include "ide_list_model.h"

using namespace qibuild::config;

IdeListModel::IdeListModel(QObject *parent):
  QAbstractTableModel(parent)
{
}

IdeListModel::~IdeListModel()
{
}

void IdeListModel::addIde(const Ide &ide)
{
  m_ides.append(ide);
}


QList<Ide> IdeListModel::ides()
{
  return m_ides;
}

int IdeListModel::rowCount(const QModelIndex &parent) const
{
  Q_UNUSED(parent);
  return m_ides.size();
}

int IdeListModel::columnCount(const QModelIndex &parent) const
{
  Q_UNUSED(parent);
  // name, path
  return 2;
}

QVariant IdeListModel::data(const QModelIndex &index, int role) const
{
  if (!index.isValid()) {
    return QVariant();
  }
  if (role != Qt::DisplayRole) {
    return QVariant();
  }

  Ide ide = m_ides.at(index.row());
  int column = index.column();
  switch (column) {
    case 0:
      return ide.name;
    case 1:
      return ide.path;
  }
}

bool IdeListModel::setData(const QModelIndex &index, const QVariant &value, int role)
{
  if (!index.isValid()) {
    return false;
  }

  Ide& ide = m_ides[index.row()];
  int column = index.column();
  switch (column) {
    case 0:
      ide.name = value.toString();
      break;
    case 1:
      ide.path = value.toString();
      break;
  }
  emit(dataChanged(index, index));
  return true;
}

QVariant IdeListModel::headerData(int section, Qt::Orientation orientation, int role) const
{
  if (role != Qt::DisplayRole) {
    return QVariant();
  }

  if (orientation != Qt::Horizontal) {
    return QVariant();
  }

  switch(section) {
    case 0:
      return tr("name");
    case 1:
      return tr("path");
  }
}

bool IdeListModel::insertRows(int row, int count, const QModelIndex &parent)
{
  beginInsertRows(parent, row, row + count);
  for (int i=0; i < count ; i++) {
    Ide ide;
    m_ides.append(ide);
  }
  endInsertRows();
  return true;
}

bool IdeListModel::removeRows(int row, int count, const QModelIndex &parent)
{
  beginRemoveRows(parent, row, row+count);
  for (int i=0; i < count ; i++) {
    m_ides.removeAt(row);
  }
  endRemoveRows();
  return true;
}

Qt::ItemFlags IdeListModel::flags(const QModelIndex &index) const
{
  if (!index.isValid()) {
    return Qt::ItemIsEnabled;
  }

  return QAbstractTableModel::flags(index) | Qt::ItemIsEditable;
}

void IdeListModel::readConfig(QiBuildConfig *cfg)
{
  m_ides = cfg->ides().values();
}

void IdeListModel::updateConfig(QiBuildConfig *cfg)
{
  cfg->clearIdes();
  foreach(Ide ide, m_ides) {
    cfg->addIde(ide);
  }
}
