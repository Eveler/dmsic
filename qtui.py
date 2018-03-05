# -*- encoding: utf-8 -*-

from PyQt5.Qt import QMainWindow, QMessageBox, QObject, Qt, QApplication

from dmsic import Integration

tr = QObject().tr


class Ui(QApplication):
    def __init__(self):
        from sys import argv
        super().__init__(argv)
        self.w = QMainWindow(flags=Qt.Window)
        # w.setMinimumWidth(640)
        # w.setMinimumHeight(480)
        self.w.setWindowTitle(tr("Отправка запросов на ВС АУГО"))
        self.w.showMaximized()
        self.i = Integration(self)

    def report_error(self, msg):
        mb = QMessageBox(QMessageBox.Critical, tr('Ошибка'), msg,
                         parent=self.ui)
        mb.exec()
