# -*- encoding: utf-8 -*-

from PyQt5.Qt import QMainWindow, QMessageBox, QObject, Qt, QApplication, \
    QGridLayout, QTableWidget, QScrollArea, QLabel, QLineEdit, QWidget, \
    QPushButton, QHBoxLayout, pyqtSlot

from dmsic import Integration

tr = QObject().tr


class Ui(QApplication):
    def __init__(self):
        from sys import argv
        super().__init__(argv)
        self.w = QMainWindow(flags=Qt.Window)
        self.w.setMinimumWidth(300)
        self.w.setMinimumHeight(300)
        self.w.setWindowTitle(tr("Отправка запросов на ВС АУГО"))
        self.cw = QScrollArea()
        self.w.setCentralWidget(self.cw)
        self.__create_ui()
        self.w.showMaximized()
        self.i = Integration(self)

    def report_error(self, msg):
        mb = QMessageBox(QMessageBox.Critical, tr('Ошибка'), msg)
        mb.exec()

    def __create_ui(self):
        self.l = QGridLayout()
        self.t = QTableWidget(0, 3)
        self.t.setHorizontalHeaderLabels(
            ('№ дела (обращения)', 'Дата приёма', 'Дата отправки в СМЭВ'))
        self.t.resizeColumnsToContents()
        self.l.addWidget(self.t, 0, 0, 1, 2)
        w = QWidget(self.cw)
        hl = QHBoxLayout(w)
        hl.setDirection(QHBoxLayout.RightToLeft)
        ok_b = QPushButton(tr('Добавить запрос'))
        ok_b.clicked.connect(self.add_query)
        hl.addWidget(ok_b)
        w.setLayout(hl)
        self.l.addWidget(w, 1, 0, 1, 2)
        self.cw.setLayout(self.l)

    @pyqtSlot(bool)
    def add_query(self):
        self.report_error(tr('Проба'))

    def show_form(self):
        self.l.addWidget(QLabel(tr('№ дела (обращения)')))
        self.l.addWidget(QLineEdit())
