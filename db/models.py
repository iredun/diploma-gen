from PyQt5 import QtSql, QtCore
from .db import init_db


class Models:
    def __init__(self, parent):
        self.db = init_db()

        self.template_model = QtSql.QSqlTableModel(parent)
        self.template_model.setTable("templates")
        self.template_model.select()
        self.template_model.setHeaderData(0, QtCore.Qt.Horizontal, 'ID')
        self.template_model.setHeaderData(1, QtCore.Qt.Horizontal, 'Название')
