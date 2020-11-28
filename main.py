import sys
from db import Models
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from modals import AddTemplateDialog


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('designs/main.ui', self)  # Загружаем дизайн

        self.models = Models(self)

        self.tableTemplates.setModel(self.models.template_model)
        self.tableTemplates.hideColumn(2)

        self.addTemplate.clicked.connect(self.add_template)

        self.add_template_window = AddTemplateDialog(self)
        # self.add_template_window.finished.connect(self.reload_templates)
        self.add_template_window.closeEvent = self.reload_templates

    @QtCore.pyqtSlot()
    def add_template(self):
        self.add_template_window.show()

    def reload_templates(self, event):
        self.models.template_model.select()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
