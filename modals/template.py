import random

from .item_config import ItemConfigDialog

from PyQt5 import uic, QtCore  # Импортируем uic
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPen, QColor, QMouseEvent, QKeyEvent, QFont
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog, QGraphicsPixmapItem, QGraphicsRectItem, \
    QGraphicsItem, QGraphicsView, QGraphicsSceneMouseEvent, QMainWindow


class GraphicsRectItem(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.font = QFont()

        print(self.toolTip())

        self.setCursor(Qt.PointingHandCursor)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        self.item_config_window = ItemConfigDialog()
        self.item_config_window.closeEvent = self.get_config

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        self.item_config()
        super(GraphicsRectItem, self).mouseDoubleClickEvent(event)

    @QtCore.pyqtSlot()
    def item_config(self):
        self.item_config_window.item = self
        self.item_config_window.show()

    def get_config(self, event):
        print("close", event)


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

            self.scene().addItem(rect_item)
            rect_item.setToolTip(f'Поле_{len(self.scene().items()) - 1}')
            self.current_item = rect_item

            self.scene().update()

        super(GraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.parent.is_edit_mode():
            w, h = self.current_item.rect().width(), self.current_item.rect().height()
            if w + h < 50:
                self.scene().removeItem(self.current_item)
            self.start_coords = tuple()
            self.end_coords = tuple()
            self.current_item = None

        super(GraphicsView, self).mouseReleaseEvent(event)


class AddTemplateDialog(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('designs/add_template.ui', self)  # Загружаем дизайн

        self.bg_item = None
        self.bg = None

        self.buttonAddBg.clicked.connect(self.add_bg)

        self.scene = QGraphicsScene()

        self.graphicsView = GraphicsView(self)
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setFocus()
        self.horizontalLayout.insertWidget(0, self.graphicsView, 2)

        self.graphicsView.setScene(self.scene)

        self.buttonSave.clicked.connect(self.save)

        self.statusbar.showMessage('Для начала добавьте изображени фона')

        self.edit_mode = False

    def add_bg(self):
        self.scene.clear()
        self.bg = \
        QFileDialog.getOpenFileName(self, 'Открыть файл', filter="Изображения (*.png *.jpg)")[0]
        if self.bg:
            self.groupBoxMainInfo.setEnabled(True)
            img = QPixmap(self.bg)
            w, h = img.width(), img.height()
            self.bg_item = QGraphicsPixmapItem(img)
            self.scene.addItem(self.bg_item)
            self.graphicsView.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
            self.scene.update()
            self.graphicsView.setFocus()
            self.is_edit_mode()
        else:
            self.groupBoxMainInfo.setEnabled(False)

    def save(self):
        for item in self.scene.items():
            pos = item.mapFromItem(item)
            x, y = pos.x(), pos.y()
            print(item.toolTip(), x, y)

    def is_edit_mode(self):
        result = self.edit_mode and self.bg
        if result:
            self.statusbar.showMessage('Режим работы: Добавление')
        else:
            self.statusbar.showMessage('Режим работы: Редактирование')
        return result
