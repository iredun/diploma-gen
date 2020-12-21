import os
import sys

from db import Models
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from modals.template import AddTemplateDialog
from modals.export import ExportDialog

# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('designs/main.ui', self)  # Загружаем дизайн

        self.models = Models(self)

        self.tableTemplates.setModel(self.models.template_model)
        self.tableTemplates.hideColumn(2)

        self.addTemplate.clicked.connect(self.add_template)
        self.useTemplate.clicked.connect(self.export_template)

        self.selected_template_settings = None

        self.add_template_window = None
        self.export_template_window = None

        self.tableTemplates.selectionModel().selectionChanged.connect(self.change_item_selected)

    @QtCore.pyqtSlot()
    def add_template(self):
        self.add_template_window = AddTemplateDialog(self)
        self.add_template_window.show()

    @QtCore.pyqtSlot()
    def export_template(self):
        self.export_template_window = ExportDialog(self, self.selected_template_settings)
        self.export_template_window.show()

    def reload_templates(self):
        self.models.template_model.select()

    def change_item_selected(self, selected, deselected):
        rows = self.tableTemplates.selectionModel().selectedRows()
        if rows:
            for index in rows:
                if index.row() >= 0:
                    self.useTemplate.setEnabled(True)
                    self.selected_template_settings = index.model().record(index.row()).value('settings')
                else:
                    self.useTemplate.setEnabled(False)
        else:
            self.useTemplate.setEnabled(False)


def except_hook(cls, exception, traceback):
    print(cls, exception, traceback)
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
