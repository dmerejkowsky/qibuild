#ifndef IDE_LIST_MODEL_H
#define IDE_LIST_MODEL_H

#include <QAbstractListModel>
#include <qibuild/config.hpp>

class IdeListModel : public QAbstractTableModel
{
  Q_OBJECT

  public:
    explicit IdeListModel(QObject *parent);
    virtual ~IdeListModel();
    virtual int rowCount(const QModelIndex &parent) const;
    virtual int columnCount(const QModelIndex &parent) const;
    virtual QVariant data(const QModelIndex &index, int role) const;
    virtual bool setData(const QModelIndex &index, const QVariant &value, int role);
    virtual QVariant headerData(int section, Qt::Orientation orientation, int role) const;
    virtual bool insertRows(int row, int count, const QModelIndex &parent);
    virtual bool removeRows(int row, int count, const QModelIndex &parent);
    virtual Qt::ItemFlags flags(const QModelIndex &index) const;

    // Called during initialization:
    void addIde(const qibuild::config::Ide &ide);
    // Called when edition is over:
    QList<qibuild::config::Ide> ides();

    void readConfig(qibuild::config::QiBuildConfig *cfg);
    void updateConfig(qibuild::config::QiBuildConfig *cfg);

  private:
    QList<qibuild::config::Ide> m_ides;

};

#endif // IDE_LIST_MODEL_H
