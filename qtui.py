# -*- encoding: utf-8 -*-

from PyQt5.Qt import QMainWindow, QMessageBox, QObject, Qt, QApplication, \
    QGridLayout, QTableWidget, QScrollArea, QLabel, QLineEdit, QWidget, \
    QPushButton, QHBoxLayout, pyqtSlot, QSizePolicy, QDateEdit, QDate, QGroupBox
from PyQt5.QtWidgets import QRadioButton, QStackedWidget, QComboBox

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
        self.__showed = False
        self.__wgts = {}

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
        hl.setDirection(QHBoxLayout.LeftToRight)
        hl.addWidget(QWidget())
        ok_b = QPushButton(tr('Добавить запрос'))
        ok_b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        ok_b.clicked.connect(self.show_form)
        hl.addWidget(ok_b)
        w.setLayout(hl)
        self.l.addWidget(w, 1, 0, 1, 2)
        self.cw.setLayout(self.l)

    @pyqtSlot(bool)
    def show_form(self):
        if self.__showed:
            return

        self.l.addWidget(
            QLabel(tr('№ дела (обращения) <em style="color: red">*</em>')))
        self.l.addWidget(QLineEdit())
        self.l.addWidget(
            QLabel(tr('Код (номер) услуги <em style="color: red">*</em>')))
        self.l.addWidget(QLineEdit())
        self.l.addWidget(QLabel(
            tr('Дата регистрации запроса <em style="color: red">*</em>')))
        de = QDateEdit(QDate().currentDate())
        de.setCalendarPopup(True)
        self.l.addWidget(de)
        self.l.addWidget(QLabel(tr(
            'Плановый срок предоставления услуги <em style="color: red">*</em>')
        ))
        de.setCalendarPopup(True)
        self.l.addWidget(de)

        gb = QGroupBox(tr('Место нахождения объекта услуги'))
        gb_l = QGridLayout()
        gb_l.addWidget(QLabel(tr('Почтовый индекс')))
        w = QLineEdit()
        gb_l.addWidget(w, 0, 1, 1, 1)
        self.__wgts['Postal_Code'] = w
        gb_l.addWidget(QLabel(tr('Регион')))
        w = QLineEdit()
        gb_l.addWidget(w)
        self.__wgts['Region'] = w
        gb_l.addWidget(QLabel(tr('Район')))
        w = QLineEdit()
        gb_l.addWidget(w)
        self.__wgts['District'] = w
        gb_l.addWidget(QLabel(tr('Муниципальное образование')))
        w = QLineEdit()
        gb_l.addWidget(w)
        self.__wgts['City'] = w
        gb_l.addWidget(QLabel(tr('Городской район')))
        w = QLineEdit()
        gb_l.addWidget(w)
        self.__wgts['Urban_District'] = w
        gb_l.addWidget(QLabel(tr('Сельсовет')))
        w = QLineEdit()
        gb_l.addWidget(w)
        self.__wgts['Soviet_Village'] = w
        gb_l.addWidget(
            QLabel(tr('Населенный пункт <em style="color: red">*</em>')))
        w = QLineEdit()
        gb_l.addWidget(w)
        self.__wgts['Locality'] = w
        cb = QComboBox()
        cb.addItems(('Вариант 1', 'Вариант 2'))
        gb_l.addWidget(cb)
        st = QStackedWidget()
        p1 = QWidget()
        l = QGridLayout()
        l.setSpacing(3)
        l.addWidget(QLabel(tr('Улица <em style="color: red">*</em>')))
        w = QLineEdit()
        l.addWidget(w, 0, 1, 1, 1)
        self.__wgts["Street"] = w
        l.addWidget(QLabel(tr('Дом <em style="color: red">*</em>')))
        w = QLineEdit()
        l.addWidget(w)
        self.__wgts["House"] = w
        p1.setLayout(l)
        st.addWidget(p1)
        p2 = QWidget()
        l = QGridLayout()
        l.setSpacing(3)
        l.addWidget(QLabel(tr('Ориентир')))
        w = QLineEdit()
        l.addWidget(w, 0, 1, 1, 1)
        self.__wgts["Reference_point"] = w
        p2.setLayout(l)
        st.addWidget(p2)
        gb_l.addWidget(st, 9, 0, 1, 2)
        cb.activated.connect(st.setCurrentIndex)
        gb_l.addWidget(QLabel(tr('Корпус')))
        w = QLineEdit()
        gb_l.addWidget(w)
        self.__wgts['Housing'] = w
        gb_l.addWidget(QLabel(tr('Строение')))
        w = QLineEdit()
        gb_l.addWidget(w)
        self.__wgts['Building'] = w
        gb_l.addWidget(QLabel(tr('Квартира')))
        w = QLineEdit()
        gb_l.addWidget(w)
        self.__wgts['Apartment'] = w
        gb.setLayout(gb_l)
        self.l.addWidget(gb, 6, 0, 1, 2)

        self.__showed = True
