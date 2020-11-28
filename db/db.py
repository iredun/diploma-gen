from PyQt5 import QtSql, QtWidgets


def init_db():
    db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("db.db")
    if not db.open():
        QtWidgets.QMessageBox.critical(None, "Ошибка открытия БД",
                                       "Проверьте, все ли на месте :)",
                                       QtWidgets.QMessageBox.Cancel)
        return False

    return db
