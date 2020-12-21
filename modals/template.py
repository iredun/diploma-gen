import json
import shutil
import uuid

from common import const

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QPixmap, QCloseEvent
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog, QGraphicsPixmapItem, QMainWindow, QMessageBox

from common.graphics import GraphicsView


class AddTemplateDialog(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        uic.loadUi('designs/add_template.ui', self)  # Загружаем дизайн

        self.parent = parent
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

        self.not_saved = False

    def add_bg(self):
        self.scene.clear()
        self.bg = QFileDialog.getOpenFileName(self, 'Открыть файл', filter="Изображения (*.png *.jpg)")[0]
        if self.bg:
            self.not_saved = True
            self.groupBoxMainInfo.setEnabled(True)
            img = QPixmap(self.bg)
            self.bg_item = QGraphicsPixmapItem(img)
            self.scene.addItem(self.bg_item)
            self.scene.update()
            self.graphicsView.setFocus()
            self.is_edit_mode()
        else:
            self.groupBoxMainInfo.setEnabled(False)

    def save(self):
        template_name = self.editName.text()
        if template_name:
            bg = f'./templates/{uuid.uuid4()}.template'
            shutil.copy2(self.bg, bg)
            data = {
                'items': [],
                'bg': bg,
            }
            for item in self.scene.items():
                if item.toolTip():
                    pos_from = self.graphicsView.mapFromScene(item.sceneBoundingRect())
                    pos = self.graphicsView.mapToScene(pos_from)
                    rect = pos.boundingRect()
                    x, y = rect.x(), rect.y()
                    data['items'].append({
                        'name': item.toolTip(),
                        'x': x,
                        'y': y,
                        'w': rect.width(),
                        'h': rect.height(),
                        'params': {
                            const.ITEM_DATA_KEY_FONT: item.data(const.ITEM_DATA_KEY_FONT),
                            const.ITEM_DATA_KEY_FONT_SIZE: item.data(const.ITEM_DATA_KEY_FONT_SIZE),
                            const.ITEM_DATA_KEY_FONT_COLOR: item.data(const.ITEM_DATA_KEY_FONT_COLOR),
                            const.ITEM_DATA_KEY_FONT_ALIGN: item.data(const.ITEM_DATA_KEY_FONT_ALIGN),
                        }
                    })
            rec = self.parent.models.template_model.record()
            rec.setValue('name', QVariant(template_name))
            rec.setValue('settings', QVariant(json.dumps(data)))
            if self.parent.models.template_model.insertRecord(-1, rec):
                self.not_saved = False
                self.close()
            else:
                msg = QMessageBox(QMessageBox.Critical, "Ошибка сохранения", 'Что-то пошло не так')
                msg.exec_()

        else:
            msg = QMessageBox(QMessageBox.Critical, "Ошибка сохранения", 'Введите название шаблона')
            msg.exec_()

    def is_edit_mode(self):
        result = self.edit_mode and self.bg
        if result:
            self.statusbar.showMessage('Режим работы: Добавление')
        else:
            self.statusbar.showMessage('Режим работы: Редактирование')
        return result

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.not_saved:
            ret = QMessageBox.question(self, 'Закрыть',
                                       "У Вас есть несохраненные изменения. Вы действительно хотите закрыть редактор?",
                                       QMessageBox.Ok | QMessageBox.Cancel)

            if ret == QMessageBox.Ok:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
        self.parent.reload_templates()
