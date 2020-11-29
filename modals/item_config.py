from PyQt5 import uic  # Импортируем uic
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter, QImage, QPixmap, QColor, QFont
from PyQt5.QtWidgets import QMainWindow, QGraphicsRectItem, QGraphicsScene, QGraphicsPixmapItem, QGraphicsView, \
    QGraphicsTextItem, QColorDialog

from common import const


class ItemConfigDialog(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('designs/item_config.ui', self)  # Загружаем дизайн

        self.text_aligns = [
            ('center', 'По центру'),
            ('left', 'По левому краю'),
            ('right', 'По правому краю'),
        ]
        self.text_align = 'center'

        for align, align_text in self.text_aligns:
            self.textPosH.addItem(align_text)

        self.item: QGraphicsRectItem = QGraphicsRectItem()
        self.main_view: QGraphicsView = QGraphicsView()

        self.fontSelect.currentFontChanged.connect(self.render_text)
        self.fontSize.valueChanged.connect(self.render_text)
        self.textPosH.currentTextChanged.connect(self.render_text)
        self.exText.textChanged.connect(self.render_text)

        self.font_color = QColor('black')

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.text = QGraphicsTextItem()

        self.buttonBox.accepted.connect(self.accepted)

        self.colorPicker.clicked.connect(self.select_color)

    def show(self):
        super(ItemConfigDialog, self).show()
        self.text = QGraphicsTextItem()
        self.name.setText(self.item.toolTip())
        font = QFont()
        font_name = self.item.data(const.ITEM_DATA_KEY_FONT)
        if font_name:
            font.fromString(font_name)
            font_size = self.item.data(const.ITEM_DATA_KEY_FONT_SIZE)
            if font_size:
                font.setPointSize(font_size)
            else:
                font.setPointSize(font_size)
            font_color = self.item.data(const.ITEM_DATA_KEY_FONT_COLOR)
            if font_color:
                self.font_color.setRgb(*font_color)
            self.text.setFont(font)
        self.text_align = self.item.data(const.ITEM_DATA_KEY_FONT_ALIGN)

        self.render_text()
        self.render_item()

    def select_color(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.font_color = color
            self.render_text()

    def render_text(self, event=None):
        font = self.fontSelect.currentFont()
        font.setPointSize(self.fontSize.value())
        self.text.setFont(font)
        self.text.setTextWidth(self.item.rect().width())
        self.text.setDefaultTextColor(self.font_color)
        for align, align_text in self.text_aligns:
            if align_text == self.textPosH.currentText():
                self.text_align = align

        self.text.setHtml(f"<div align='{self.text_align}'>{self.exText.text()}</div>")

    def render_item(self):
        self.scene.clear()
        pos_from = self.main_view.mapFromScene(self.item.sceneBoundingRect())
        pos = self.main_view.mapToScene(pos_from)
        point = pos.boundingRect()
        width, height = point.width(), point.height()

        img = QImage(width, height, QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(img)
        painter.setRenderHint(QPainter.Antialiasing)
        self.item.scene().render(painter, source=QRectF(point.x(), point.y(), width, height))
        painter.end()

        self.scene.addItem(QGraphicsPixmapItem(QPixmap(img)))
        self.scene.addItem(self.text)
        self.graphicsView.fitInView(QRectF(0, 0, width, height), Qt.KeepAspectRatio)

        self.scene.update()

    def accepted(self):
        self.item.setData(const.ITEM_DATA_KEY_FONT, self.text.font().toString().split(',')[0])
        self.item.setData(const.ITEM_DATA_KEY_FONT_SIZE, self.text.font().pointSize())
        self.item.setData(const.ITEM_DATA_KEY_FONT_ALIGN, self.text_align)
        self.item.setData(const.ITEM_DATA_KEY_FONT_COLOR, self.font_color.getRgb())
        self.item.setToolTip(self.name.text())
        self.item.scene().update()
        self.close()
