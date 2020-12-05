import csv

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem


class ExportDialog(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        uic.loadUi('designs/export.ui', self)  # Загружаем дизайн
        self.parent = parent
        self.file = ''

        self.openFileBtn.clicked.connect(self.open_file)

        self.nextPushButton.clicked.connect(self.next_slide)
        self.prevPushButton.clicked.connect(self.prev_slide)

        self.stackedWidget.currentChanged.connect(self.slide_change)

        self.encodingComboBox.currentTextChanged.connect(self.render_table)
        self.haveHeaderCheckBox.stateChanged.connect(self.render_table)
        self.delimiterLineEdit.editingFinished.connect(self.render_table)
        self.strDelimiterLineEdit.editingFinished.connect(self.render_table)

    def slide_change(self, index):
        cnt = self.stackedWidget.count() - 1

        if index == 0:
            self.prevPushButton.setEnabled(False)
        else:
            self.prevPushButton.setEnabled(True)

        if index == cnt:
            self.nextPushButton.setEnabled(False)
        else:
            self.nextPushButton.setEnabled(True)

    def next_slide(self):
        cnt = self.stackedWidget.count() - 1
        current = self.stackedWidget.currentIndex()
        if current + 1 <= cnt:
            self.stackedWidget.setCurrentIndex(current + 1)

    def prev_slide(self):
        current = self.stackedWidget.currentIndex()
        if current - 1 >= 0:
            self.stackedWidget.setCurrentIndex(current - 1)

    def open_file(self):
        self.file = QFileDialog.getOpenFileName(self, 'Открыть файл', filter="CSV (*.csv)")[0]
        self.selectedFile.setText("Файл: " + self.file)
        self.render_table()

    def render_table(self):
        if not self.file:
            return
        self.csvTable.clear()

        self.csv.setCursor(QCursor(Qt.WaitCursor))
        have_head = self.haveHeaderCheckBox.checkState() != 0
        with open(self.file, encoding=self.encodingComboBox.currentText()) as csv_file:
            reader = csv.reader(csv_file, delimiter=self.delimiterLineEdit.text(),
                                quotechar=self.strDelimiterLineEdit.text())
            if have_head:
                title = next(reader)
                self.csvTable.setColumnCount(len(title))
                self.csvTable.setHorizontalHeaderLabels(title)
            else:
                self.csvTable.setColumnCount(len(next(reader)))
                csv_file.seek(0)

            self.csvTable.setRowCount(0)
            for i, row in enumerate(reader):
                self.csvTable.setRowCount(
                    self.csvTable.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.csvTable.setItem(i, j, QTableWidgetItem(elem))
            self.csvTable.resizeColumnsToContents()

        self.csv.setCursor(QCursor(Qt.ArrowCursor))
