import random
from . import const
from modals.item_config import ItemConfigDialog
from PyQt5 import QtCore  # Импортируем uic
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QColor, QMouseEvent, QKeyEvent, QFont
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsView, QGraphicsSceneMouseEvent


class GraphicsRectItem(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.font = QFont()

        self.main_view: QGraphicsView = QGraphicsView()

        self.setCursor(Qt.PointingHandCursor)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        self.item_config_window = ItemConfigDialog()

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        self.item_config()
        super(GraphicsRectItem, self).mouseDoubleClickEvent(event)

    @QtCore.pyqtSlot()
    def item_config(self):
        self.item_config_window.item = self
        self.item_config_window.main_view = self.main_view
        self.item_config_window.show()


class GraphicsView(QGraphicsView):
    def __init__(self, parent):
        super().__init__()
        self.start_coords = tuple()
        self.end_coords = tuple()

        self.pen = QPen()
        self.pen.setWidth(5)

        self.parent = parent

        self.current_item = None

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            for item in self.items():
                if item.isSelected():
                    self.scene().removeItem(item)
        if event.key() == Qt.Key_Control:
            self.parent.edit_mode = True

        self.parent.is_edit_mode()
        super(GraphicsView, self).keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Control:
            self.parent.edit_mode = False
        self.parent.is_edit_mode()
        super(GraphicsView, self).keyReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.start_coords and self.parent.is_edit_mode() and event.buttons() & Qt.LeftButton:
            pos = self.mapToScene(event.pos())
            self.end_coords = (pos.x(), pos.y())
            w, h = int(self.end_coords[0] - self.start_coords[0]), int(
                self.end_coords[1] - self.start_coords[1])
            self.current_item.setRect(
                QRectF(int(self.start_coords[0]), int(self.start_coords[1]), w, h))
        else:
            super(GraphicsView, self).mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if not self.start_coords and self.parent.is_edit_mode() and event.buttons() & Qt.LeftButton:
            pos = self.mapToScene(event.pos())
            self.start_coords = (pos.x(), pos.y())
            rect_item = GraphicsRectItem(
                QRectF(int(self.start_coords[0]), int(self.start_coords[1]), 1, 1))

            color = QColor(random.randint(0, 180), random.randint(100, 255),
                           random.randint(50, 200))
            self.pen.setColor(color)
            rect_item.setPen(self.pen)
            rect_item.main_view = self

            rect_item.setData(int(const.ITEM_DATA_KEY_FONT), 'Arial')
            rect_item.setData(int(const.ITEM_DATA_KEY_FONT_SIZE), 12)
            rect_item.setData(int(const.ITEM_DATA_KEY_FONT_ALIGN), 'center')
            rect_item.setData(int(const.ITEM_DATA_KEY_FONT_COLOR), (0, 0, 0))

            self.scene().addItem(rect_item)
            rect_item.setToolTip(f'Поле_{len(self.scene().items()) - 1}')
            self.current_item = rect_item

            self.scene().update()

        super(GraphicsView, self).mousePressEvent(event)

    def add_custom_item(self, start_coords: tuple, rect: tuple, init_params: dict = dict):
        rect_item = GraphicsRectItem(QRectF(int(start_coords[0]), int(start_coords[1]), rect[0], rect[1]))
        color = QColor(random.randint(0, 180), random.randint(100, 255), random.randint(50, 200))

        self.pen.setColor(color)
        rect_item.setPen(self.pen)
        rect_item.main_view = self

        keys = [const.ITEM_DATA_KEY_FONT, const.ITEM_DATA_KEY_FONT_SIZE, const.ITEM_DATA_KEY_FONT_ALIGN,
                const.ITEM_DATA_KEY_FONT_COLOR]

        for key in keys:
            rect_item.setData(int(key), init_params['params'][key])

        self.scene().addItem(rect_item)
        rect_item.setToolTip(init_params['name'])
        self.scene().update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.parent.is_edit_mode():
            w, h = self.current_item.rect().width(), self.current_item.rect().height()
            if w + h < 50:
                self.scene().removeItem(self.current_item)
            self.start_coords = tuple()
            self.end_coords = tuple()
            self.current_item = None
            self.parent.not_saved = True

        super(GraphicsView, self).mouseReleaseEvent(event)
