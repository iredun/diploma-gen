import json
import os
import sys

from db import Models
from PyQt5.QtWidgets import QApplication, QMainWindow
from designs.main import Ui_MainWindow
from modals.template import AddTemplateDialog
from modals.export import ExportDialog
from designs.res import res


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.models = Models(self)

        self.tableTemplates.setModel(self.models.template_model)
        self.tableTemplates.hideColumn(2)

        self.addTemplate.clicked.connect(self.add_template)
        self.useTemplate.clicked.connect(self.export_template)
        self.editTemplate.clicked.connect(self.edit_template)
        self.deleteTemplate.clicked.connect(self.delete_template)

        self.selected_template_settings = None

        self.add_template_window = None
        self.export_template_window = None

        self.tableTemplates.selectionModel().selectionChanged.connect(self.change_item_selected)

    def add_template(self):
        self.add_template_window = AddTemplateDialog(self)
        self.add_template_window.show()

    def delete_template(self):
        if self.models.template_model.deleteRowFromTable(self.selected_template_settings['index']):
            settings = json.loads(self.selected_template_settings['settings'])
            os.remove(settings['bg'])
            self.reload_templates()
            self.useTemplate.setEnabled(False)
            self.editTemplate.setEnabled(False)
            self.deleteTemplate.setEnabled(False)

    def edit_template(self):
        self.add_template_window = AddTemplateDialog(self)
        self.add_template_window.load_template(self.selected_template_settings)
        self.add_template_window.show()

    def export_template(self):
        self.export_template_window = ExportDialog(self, self.selected_template_settings['settings'])
        self.export_template_window.show()

    def reload_templates(self):
        self.models.template_model.select()

    def change_item_selected(self):
        rows = self.tableTemplates.selectionModel().selectedRows()
        if rows:
            for index in rows:
                if index.row() >= 0:
                    self.useTemplate.setEnabled(True)
                    self.editTemplate.setEnabled(True)
                    self.deleteTemplate.setEnabled(True)
                    self.selected_template_settings = {
                        'index': index.row(),
                        'name': index.model().record(index.row()).value('name'),
                        'settings': index.model().record(index.row()).value('settings')
                    }
                else:
                    self.useTemplate.setEnabled(False)
                    self.editTemplate.setEnabled(False)
                    self.deleteTemplate.setEnabled(False)
        else:
            self.useTemplate.setEnabled(False)
            self.editTemplate.setEnabled(False)
            self.deleteTemplate.setEnabled(False)


def except_hook(cls, exception, traceback):
    print(cls, exception, traceback)
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
