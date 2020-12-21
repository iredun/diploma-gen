import csv
import json
import os

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QCursor, QPixmap, QFont, QColor, QImage, QPainter
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem, QGraphicsScene, QGraphicsPixmapItem, \
    QGraphicsView, QGraphicsTextItem, QCommandLinkButton, QFormLayout, QHBoxLayout

from common import const


class ExportDialog(QMainWindow):
    def __init__(self, parent, settings: str):
        super().__init__()
        uic.loadUi('designs/export.ui', self)  # Загружаем дизайн
        self.parent = parent
        self.image_format = 4
        self.file = ''
        self.export_dir_template = os.path.sep
        self.export_file_template = ""

        self.bg_item = None

        self.settings = json.loads(settings)
        self.csv_headers = []

        self.links = dict()
        self.test_row = dict()

        self.openFileBtn.clicked.connect(self.open_file)

        self.nextPushButton.clicked.connect(self.next_slide)
        self.prevPushButton.clicked.connect(self.prev_slide)
        self.toolButtonChangeDir.clicked.connect(self.open_dir)
        self.startGen.clicked.connect(self.export)

        self.stackedWidget.currentChanged.connect(self.slide_change)

        self.scene = QGraphicsScene()
        self.graphicsView = QGraphicsView()
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setFocus()
        self.linkSettinghorizontalLayout.insertWidget(0, self.graphicsView, 0)

        self.graphicsView.setScene(self.scene)

        self.spinBoxRow.valueChanged.connect(self.reload_row)

        self.encodingComboBox.currentTextChanged.connect(self.render_table)
        self.haveHeaderCheckBox.stateChanged.connect(self.render_table)
        self.delimiterLineEdit.editingFinished.connect(self.render_table)
        self.lineEditDir.editingFinished.connect(self.edit_path)
        self.lineEditFileMask.editingFinished.connect(self.edit_file)
        self.strDelimiterLineEdit.editingFinished.connect(self.render_table)

        self.textBrowserDirs.anchorClicked.connect(self.dir_link_click)
        self.textBrowserFileName.anchorClicked.connect(self.file_link_click)

    def reload_row(self, i):
        self.test_row = self.get_csv_row(i)
        self.render_items()

    def get_csv_row(self, row=1):
        data = dict()
        for i, name in enumerate(self.csv_headers):
            itm = self.csvTable.item(row, i)
            if itm:
                data[name] = itm.text()
            else:
                data[name] = ''
        return data

    def get_links_dict(self):
        data = dict()
        for row in range(self.tableLinkSettings.rowCount()):
            itm_name = self.tableLinkSettings.item(row, 0)
            itm_data = self.tableLinkSettings.cellWidget(row, 1)
            if itm_name and itm_data:
                name = itm_name.text()
                data[name] = self.tableLinkSettings.cellWidget(row, 1).currentText()
        return data

    def render_preview(self):
        if self.settings['bg']:
            if self.bg_item:
                for item in self.scene.items():
                    if item != self.bg_item:
                        self.scene.removeItem(item)
            else:
                self.scene.clear()
                img = QPixmap(self.settings['bg'])
                self.image_format = img.toImage().format()
                self.bg_item = QGraphicsPixmapItem(img)
                self.scene.addItem(self.bg_item)
            self.scene.update()

    def render_items(self, event=None):
        self.links = self.get_links_dict()
        self.render_preview()
        for item in self.settings['items']:
            text = QGraphicsTextItem()
            font_color = QColor('black')

            text.setPos(QPointF(item['x'], item['y']))

            font = QFont()
            font_name = item['params'].get(const.ITEM_DATA_KEY_FONT)
            if font_name:
                font.fromString(font_name)
                font_size = item['params'].get(const.ITEM_DATA_KEY_FONT_SIZE)
                if font_size:
                    font.setPointSize(font_size)
                else:
                    font.setPointSize(12)
                font_color_list = item['params'].get(const.ITEM_DATA_KEY_FONT_COLOR)
                if font_color_list:
                    font_color.setRgb(*font_color_list)
                text.setFont(font)
            text_align = item['params'].get(const.ITEM_DATA_KEY_FONT_ALIGN)

            text.setFont(font)
            text.setTextWidth(item['w'])
            text.setDefaultTextColor(font_color)

            text.setHtml(f"<div align='{text_align}'>{self.test_row[self.links[item['name']]]}</div>")

            self.scene.addItem(text)

    def edit_path(self, *args):
        self.export_dir_template = self.lineEditDir.text()
        self.build_path(self.test_row)

    def edit_file(self, *args):
        self.export_file_template = self.lineEditFileMask.text()
        self.build_path(self.test_row)

    def build_path(self, row: dict, preview=True):
        path = self.export_dir_template
        selected_path = self.lineEditSaveDir.text()
        if selected_path:
            path = selected_path + path

        for k, v in row.items():
            path = path.replace(f'#{k}#', v)

        path = os.path.abspath(os.path.normpath(path))

        if self.export_file_template:
            path = path + os.path.sep + self.export_file_template + '.png'

        for k, v in row.items():
            path = path.replace(f'#{k}#', v)

        if preview:
            self.dirPreview.setText(path)
        else:
            return path

    def dir_link_click(self, url):
        sep = ''
        if self.export_dir_template:
            if self.export_dir_template[-1] != os.path.sep:
                sep = os.path.sep
        else:
            sep = os.path.sep

        self.export_dir_template = self.export_dir_template + sep + url.toString() + '#'
        self.lineEditDir.setText(self.export_dir_template)
        self.build_path(self.test_row)

    def file_link_click(self, url):
        self.export_file_template = self.export_file_template + url.toString() + '#'
        self.lineEditFileMask.setText(self.export_file_template)
        self.build_path(self.test_row)

    def update_buttons(self):
        html = ['<ul>']
        for h in self.csv_headers:
            li = f"<li><a href='#{h}'>#{h}#</a></li>"
            html.append(li)
        html.append('</ul>')
        self.textBrowserDirs.setHtml(const.DIRS_HTML + "\n".join(html))
        self.textBrowserFileName.setHtml(const.FILE_MASK_HTML + "\n".join(html))

    def update_settings_table(self):
        self.tableLinkSettings.setRowCount(0)

        fields = [itm['name'] for itm in self.settings['items']]
        fields.sort()

        self.update_buttons()

        for i, field in enumerate(fields):
            field_item = QtWidgets.QTableWidgetItem(field)
            field_item.setFlags(field_item.flags() ^ Qt.ItemIsEditable)

            self.tableLinkSettings.setRowCount(self.tableLinkSettings.rowCount() + 1)
            self.tableLinkSettings.setItem(i, 0, field_item)

            combo_box = QtWidgets.QComboBox(self)
            combo_box.addItems(self.csv_headers)
            combo_box.currentTextChanged.connect(self.render_items)

            self.tableLinkSettings.setCellWidget(i, 1, combo_box)

        self.test_row = self.get_csv_row()
        self.render_items()

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
        self.lineEditSaveDir.setText(os.path.dirname(os.path.abspath(self.file)))
        self.selectedFile.setText("Файл: " + self.file)
        self.render_table()
        self.nextPushButton.setEnabled(True)

    def open_dir(self):
        dir = QFileDialog.getExistingDirectory(self, 'Выбор директории')
        if dir:
            self.lineEditSaveDir.setText(dir)
            self.build_path(self.test_row)

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
                self.csv_headers = title
                self.csvTable.setColumnCount(len(title))
                self.csvTable.setHorizontalHeaderLabels(title)
            else:
                title_len = len(next(reader))
                self.csvTable.setColumnCount(title_len)
                self.csv_headers = list(map(lambda x: str(x + 1), range(title_len)))
                csv_file.seek(0)

            self.csvTable.setRowCount(0)
            for i, row in enumerate(reader):
                self.csvTable.setRowCount(
                    self.csvTable.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.csvTable.setItem(i, j, QTableWidgetItem(elem))
            self.spinBoxRow.setMaximum(i)
            self.progressBar.setMaximum(i)
            self.csvTable.resizeColumnsToContents()

        self.csv.setCursor(QCursor(Qt.ArrowCursor))
        self.update_settings_table()

    def export(self):
        for i in range(self.csvTable.rowCount()):
            self.progressBar.setValue(i)
            self.reload_row(i)

            file_name = self.build_path(self.test_row, preview=False)
            path = os.path.dirname(file_name)
            if not os.path.exists(path):
                os.makedirs(path)

            img = QImage(self.scene.sceneRect().size().toSize(), self.image_format)
            img.fill(Qt.transparent)

            painter = QPainter(img)
            painter.setRenderHint(QPainter.Antialiasing)
            self.scene.render(painter)

            if not img.save(file_name, quality=100):
                print('fail', file_name)
            else:
                del painter  # нужно дропать обязательно, иначе в памяти остается связь и оно ложится
                del img  # что бы это понять я потратил 3 часа
