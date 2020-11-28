from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QMainWindow, QGraphicsRectItem, QGraphicsScene


class ItemConfigDialog(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('designs/item_config.ui', self)  # Загружаем дизайн
        self.item: QGraphicsRectItem

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.buttonBox.accepted.connect(self.accepted)

    def show(self):
        super(ItemConfigDialog, self).show()
        self.name.setText(self.item.toolTip())
        self.render_item()
        print(self.item.rect().topLeft(), self.item.rect().size())

    def render_item(self):
        self.scene.clear()
        # painter = QPainter()
        self.item.scene().render(self.scene, target=self.item.rect())
        # self.scene.addItem(painter)

    def accepted(self):
        self.close()
