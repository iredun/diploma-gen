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
        self.template = None

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

    def load_bg(self):
        if self.bg:
            self.scene.clear()
            self.groupBoxMainInfo.setEnabled(True)
            img = QPixmap(self.bg)
            self.bg_item = QGraphicsPixmapItem(img)
            self.scene.addItem(self.bg_item)
            self.scene.update()
            self.graphicsView.setFocus()
            self.is_edit_mode()
        else:
            self.groupBoxMainInfo.setEnabled(False)

    def add_bg(self):
        self.bg = QFileDialog.getOpenFileName(self, 'Открыть файл', filter="Изображения (*.png *.jpg)")[0]
        if self.bg:
            self.not_saved = True
            self.load_bg()

    def load_template(self, template: dict):
        template['settings'] = json.loads(template['settings'])
        self.bg = template['settings']['bg']
        self.editName.setText(template['name'])
        self.load_bg()
        for item in template['settings']['items']:
            self.graphicsView.add_custom_item(
                (item['x'], item['y']),
                (item['w'], item['h']),
                item
            )
        self.template = template

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
                    data['items'].append({
                        'name': item.toolTip(),
                        'x': rect.x() + 2,
                        'y': rect.y() + 2,
                        'w': rect.width() - 5,
                        'h': rect.height() - 5,
                        'params': {
                            const.ITEM_DATA_KEY_FONT: item.data(int(const.ITEM_DATA_KEY_FONT)),
                            const.ITEM_DATA_KEY_FONT_SIZE: item.data(int(const.ITEM_DATA_KEY_FONT_SIZE)),
                            const.ITEM_DATA_KEY_FONT_COLOR: item.data(int(const.ITEM_DATA_KEY_FONT_COLOR)),
                            const.ITEM_DATA_KEY_FONT_ALIGN: item.data(int(const.ITEM_DATA_KEY_FONT_ALIGN)),
                        }
                    })

            rec_name = QVariant(template_name)
            rec_settings = QVariant(json.dumps(data))

            if self.template:
                rec = self.parent.models.template_model.record(self.template['index'])
            else:
                rec = self.parent.models.template_model.record()

            rec.setValue('name', rec_name)
            rec.setValue('settings', rec_settings)

            if self.template:
                self.parent.models.template_model.updateRowInTable(self.template['index'], rec)
                self.not_saved = False
                self.close()
            else:
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
        self.parent.useTemplate.setEnabled(False)
        self.parent.editTemplate.setEnabled(False)
