# -*- encoding: utf-8 -*-

# Author: Savenko Mike
from datetime import datetime
from logging import error
from sys import argv, exc_info
from traceback import format_exception

from PyQt5.Qt import QMainWindow, QMessageBox, QObject, QApplication, \
    QGridLayout, QTableWidget, QScrollArea, QLabel, QLineEdit, QWidget, \
    QPushButton, QHBoxLayout, pyqtSlot, QSizePolicy, QDateEdit, QDate, \
    QGroupBox, QStackedWidget, QComboBox, QVBoxLayout, QMetaObject, \
    QCoreApplication, QMenuBar, QMenu, QStatusBar, QAction, QDialog, QFileDialog

from about import Ui_Dialog

tr = QObject().tr


class Ui(QApplication):
    def __init__(self):
        super().__init__(argv)
        self.w = QMainWindow()
        self.w.setMinimumWidth(300)
        self.w.setMinimumHeight(300)
        # self.w.setWindowTitle(tr("Отправка запросов на ВС АУГО"))
        self.cw = QScrollArea()
        # self.__create_ui()
        self.__showed = False
        self.__wgts = {}
        self.cb = QComboBox()
        self.individuals = []
        self.entities = []
        self.documents = []
        self.doc_files = []
        self.__setupUi(self.w)
        self.w.showMaximized()

    def report_error(self, msg=None):
        if not msg:
            etype, value, tb = exc_info()
            trace = ''.join(format_exception(etype, value, tb))
            delim_len = 40
            msg = ("*" * delim_len + "\n%s\n" + "*" * delim_len) % trace
            error(msg)
        mb = QMessageBox(QMessageBox.Critical, tr('Ошибка'), str(exc_info()[1]))
        mb.setDetailedText(msg)
        mb.exec()

    def __create_ui(self):
        self.l = QGridLayout()
        self.t = QTableWidget(0, 3)
        self.t.setHorizontalHeaderLabels(
            ('№ дела (обращения)', 'Дата приёма', 'Дата отправки в СМЭВ'))
        self.t.resizeColumnsToContents()
        self.l.addWidget(self.t, 0, 0, 1, 2)
        w = QWidget()
        hl = QHBoxLayout(w)
        hl.setDirection(QHBoxLayout.LeftToRight)
        hl.addWidget(QWidget())
        ok_b = QPushButton(tr('Добавить запрос'))
        ok_b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        ok_b.clicked.connect(self.__show_form)
        hl.addWidget(ok_b)
        w.setLayout(hl)
        self.l.addWidget(w, 1, 0, 1, 2)
        w = QWidget()
        w.setLayout(self.l)
        self.cw.setWidget(w)
        # self.cw.setLayout(self.l)
        # self.w.setCentralWidget(self.cw)
        w = QWidget()
        l = QVBoxLayout()
        l.addWidget(self.cw)
        w.setLayout(l)
        self.w.setCentralWidget(w)

    def __setupUi(self, mainWindow):
        mainWindow.setObjectName("MainWindow")
        self.centralwidget = QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.__show_form()
        # self.pushButton = QPushButton(self.scrollAreaWidgetContents)
        # self.pushButton.clicked.connect(self.__show_form)
        # self.pushButton.setObjectName("pushButton")
        # self.gridLayout.addWidget(self.pushButton, 2, 1, 1, 1)
        # spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding,
        #                          QSizePolicy.Minimum)
        # self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        # self.tableWidget = QTableWidget(self.scrollAreaWidgetContents)
        # self.tableWidget.setColumnCount(3)
        # self.tableWidget.setObjectName("tableWidget")
        # self.tableWidget.setHorizontalHeaderLabels(
        #     ('№ дела (обращения)', 'Дата приёма', 'Дата отправки в СМЭВ'))
        # self.tableWidget.resizeColumnsToContents()
        # self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(mainWindow)
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 600, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName("menu")
        # self.menu_2 = QMenu(self.menubar)
        # self.menu_2.setObjectName("menu_2")
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(mainWindow)
        self.statusbar.setObjectName("statusbar")
        mainWindow.setStatusBar(self.statusbar)
        self.action_1 = QAction(mainWindow)
        self.action_1.setObjectName("action")
        self.action_1.triggered.connect(self.send)
        self.action = QAction(mainWindow)
        self.action.setObjectName("action")
        self.action.triggered.connect(self.on_action_triggered)
        self.action_2 = QAction(mainWindow)
        self.action_2.setObjectName("action_2")
        self.menu.addAction(self.action)
        # self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.action_1)
        self.menubar.addAction(self.action_2)
        self.menubar.addAction(self.menu.menuAction())

        self.__retranslateUi(mainWindow)
        QMetaObject.connectSlotsByName(mainWindow)

    @pyqtSlot(bool)
    def send(self):
        try:
            from dmsic import Integration
            i = Integration(self)
            declar = {}
            for k, v in self.__wgts.items():
                if k in (
                        'object_address', 'AppliedDocument', 'legal_entity',
                        'person'):
                    a = {}
                    for key, val in v.items():
                        if val.metaObject().className() == 'QDateEdit':
                            a[key] = datetime.strptime(val.text(), '%d.%m.%Y')
                        else:
                            a[key] = val.text()
                    declar[k] = a
                else:
                    if v.metaObject().className() == 'QDateEdit':
                        declar[k] = datetime.strptime(v.text(), '%d.%m.%Y')
                    else:
                        declar[k] = v.text()
            a = declar['AppliedDocument'] if 'AppliedDocument' in declar else []
            for v in self.documents:
                d = {}
                for key, val in v.items():
                    if val.metaObject().className() == 'QDateEdit':
                        d[key] = datetime.strptime(val.text(), '%d.%m.%Y')
                    else:
                        d[key] = val.text()
                if not self.doc_files:
                    raise Exception('Добавте файл документа')
                d['file_name'] = self.doc_files[self.documents.index(v)]
                a.append(d)
            declar['AppliedDocument'] = a
            a = declar['person'] if 'person' in declar else []
            for v in self.individuals:
                ind = {}
                for key, val in v.items():
                    if key in ('address', 'fact_address'):
                        adr = {}
                        for k, vl in val.items():
                            adr[k] = vl.text()
                        ind[key] = adr
                    else:
                        if val.metaObject().className() == 'QDateEdit':
                            ind[key] = datetime.strptime(val.text(), '%d.%m.%Y')
                        else:
                            ind[key] = val.text()
                a.append(ind)
            declar['person'] = a
            a = declar['legal_entity'] if 'legal_entity' in declar else []
            for v in self.entities:
                ent = {}
                for key, val in v.items():
                    if key == 'address':
                        adr = {}
                        for k, vl in val.items():
                            adr[k] = vl.text()
                        ent[key] = adr
                    else:
                        if val.metaObject().className() == 'QDateEdit':
                            ent[key] = datetime.strptime(val.text(), '%d.%m.%Y')
                        else:
                            ent[key] = val.text()
                a.append(ent)
            declar['legal_entity'] = a
            i.send(declar)
            mb = QMessageBox(self.w)
            mb.information(self.w, tr('Готово'), tr('Запрос отправлен'))
        except:
            self.report_error()

    @pyqtSlot(bool)
    def on_action_triggered(self):
        a = Ui_Dialog()
        d = QDialog()
        a.setupUi(d)
        d.exec()

    def __retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(
            _translate("MainWindow", "Отправка запросов на ВС АУГО"))
        # self.pushButton.setText(_translate("MainWindow", "Добавить"))
        self.menu.setTitle(_translate("MainWindow", "Справка"))
        self.action_1.setText(_translate("MainWindow", "Отправить"))
        self.action_2.setText(_translate("MainWindow", "Настройка"))
        self.action.setText(_translate("MainWindow", "О программе"))

    @pyqtSlot(bool)
    def __show_form(self):
        if self.__showed:
            return

        self.gridLayout.addWidget(
            QLabel(tr('№ дела (обращения) <em style="color: red">*</em>')))
        w = QLineEdit()
        self.gridLayout.addWidget(w)
        w.setFocus()
        self.__wgts['declar_number'] = w
        self.gridLayout.addWidget(
            QLabel(tr('Код (номер) услуги <em style="color: red">*</em>')))
        w = QLineEdit()
        self.gridLayout.addWidget(w)
        self.__wgts['service'] = w
        self.gridLayout.addWidget(QLabel(
            tr('Дата регистрации запроса <em style="color: red">*</em>')))
        de = QDateEdit(QDate().currentDate())
        de.setCalendarPopup(True)
        self.gridLayout.addWidget(de)
        self.__wgts['register_date'] = de
        self.gridLayout.addWidget(QLabel(tr(
            'Плановый срок предоставления услуги <em style="color: red">*</em>')
        ))
        de = QDateEdit()
        self.__wgts['register_date'].dateChanged.connect(de.setMinimumDate)
        de.setCalendarPopup(True)
        de.setMinimumDate(self.__wgts['register_date'].date())
        self.gridLayout.addWidget(de)
        self.__wgts['end_date'] = de

        gb = QGroupBox(tr('Место нахождения объекта услуги'))
        gb_l = QGridLayout()
        self.__wgts['object_address'] = self.__add_address(gb_l)
        gb.setLayout(gb_l)
        self.gridLayout.addWidget(gb, self.gridLayout.rowCount() + 1, 0, 1, 2)

        doc = {}
        gb = QGroupBox(tr('Приложенный документ *'))
        gb_l = QGridLayout()
        gb_l.addWidget(
            QLabel(tr('Наименование документа <em style="color: red">*</em>')))
        w = QLineEdit()
        w.setMaxLength(1024)
        gb_l.addWidget(w, 0, 1, 1, 1)
        doc['title'] = w
        gb_l.addWidget(
            QLabel(tr('Номер документа <em style="color: red">*</em>')))
        w = QLineEdit()
        w.setMaxLength(50)
        gb_l.addWidget(w)
        doc['number'] = w
        gb_l.addWidget(
            QLabel(tr('Дата документа <em style="color: red">*</em>')))
        w = QDateEdit()
        w.setCalendarPopup(True)
        gb_l.addWidget(w)
        doc['date'] = w
        gb_l.addWidget(
            QLabel(tr('Прямая ссылка на файл. Поддерживаются только пртоколы '
                      'HTTP, FTP <em style="color: red">*</em>')))
        w = QLineEdit()
        gb_l.addWidget(w)
        doc['url'] = w
        gb.setLayout(gb_l)
        self.gridLayout.addWidget(gb, self.gridLayout.rowCount() + 1, 0, 1, 2)
        self.documents.append(doc)

        gb = QGroupBox(tr('Заявители *'))
        self.dec_layout = QGridLayout()
        self.cb = QComboBox()
        self.cb.addItems(('Физическое лицо',
                          'Юридическое лицо/Индивидуальный предприниматель'))
        self.dec_layout.addWidget(self.cb)
        b = QPushButton(tr('Добавить'))
        b.clicked.connect(self.add_declarant)
        self.dec_layout.addWidget(b, 0, 1, 1, 1)
        gb.setLayout(self.dec_layout)
        self.gridLayout.addWidget(gb, self.gridLayout.rowCount() + 1, 0, 1, 2)

        b = QPushButton(tr('Добавить файл документа'))
        b.clicked.connect(self.__add_doc_file)
        self.gridLayout.addWidget(b)
        self.file_label = QLabel()
        self.gridLayout.addWidget(self.file_label)
        self.warn_label = QLabel(tr("Не удаляйте файл до отправки запроса"))
        self.warn_label.setStyleSheet('color: red')
        self.warn_label.setVisible(False)
        self.gridLayout.addWidget(
            self.warn_label, self.gridLayout.rowCount() + 1, 0, 1, 2)

        self.__showed = True

    @pyqtSlot(bool)
    def __add_doc_file(self):
        file_name = QFileDialog.getOpenFileName(
            caption=tr('Выбурите файл'),
            filter=tr('Файлы pdf (*.pdf);;Все файлы (*.*)'))[0]
        self.file_label.setText(file_name)
        if self.doc_files:
            self.doc_files = []
        self.doc_files.append(file_name)
        self.warn_label.setVisible(True)

    def __add_address(self, gb_l):
        wgts = {}
        gb_l.addWidget(QLabel(tr('Почтовый индекс')))
        w = QLineEdit()
        gb_l.addWidget(w, 0, 1, 1, 1)
        wgts['Postal_Code'] = w
        gb_l.addWidget(QLabel(tr('Регион')))
        w = QLineEdit()
        gb_l.addWidget(w)
        wgts['Region'] = w
        gb_l.addWidget(QLabel(tr('Район')))
        w = QLineEdit()
        gb_l.addWidget(w)
        wgts['District'] = w
        gb_l.addWidget(QLabel(tr('Муниципальное образование')))
        w = QLineEdit()
        gb_l.addWidget(w)
        wgts['City'] = w
        gb_l.addWidget(QLabel(tr('Городской район')))
        w = QLineEdit()
        gb_l.addWidget(w)
        wgts['Urban_District'] = w
        gb_l.addWidget(QLabel(tr('Сельсовет')))
        w = QLineEdit()
        gb_l.addWidget(w)
        wgts['Soviet_Village'] = w
        gb_l.addWidget(
            QLabel(tr('Населенный пункт <em style="color: red">*</em>')))
        w = QLineEdit()
        gb_l.addWidget(w)
        wgts['Locality'] = w
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
        wgts["Street"] = w
        l.addWidget(QLabel(tr('Дом <em style="color: red">*</em>')))
        w = QLineEdit()
        l.addWidget(w)
        wgts["House"] = w
        p1.setLayout(l)
        st.addWidget(p1)
        p2 = QWidget()
        l = QGridLayout()
        l.setSpacing(3)
        l.addWidget(QLabel(tr('Ориентир')))
        w = QLineEdit()
        l.addWidget(w, 0, 1, 1, 1)
        wgts["Reference_point"] = w
        p2.setLayout(l)
        st.addWidget(p2)
        gb_l.addWidget(st, 9, 0, 1, 2)
        cb.activated.connect(st.setCurrentIndex)
        gb_l.addWidget(QLabel(tr('Корпус')))
        w = QLineEdit()
        gb_l.addWidget(w)
        wgts['Housing'] = w
        gb_l.addWidget(QLabel(tr('Строение')))
        w = QLineEdit()
        gb_l.addWidget(w)
        wgts['Building'] = w
        gb_l.addWidget(QLabel(tr('Квартира')))
        w = QLineEdit()
        gb_l.addWidget(w)
        wgts['Apartment'] = w
        return wgts

    @pyqtSlot(bool)
    def add_declarant(self, var=True, gl=None):
        if not gl:
            gl = self.dec_layout
        dc = {}
        gb_l = QGridLayout()
        if self.cb.currentIndex() == 0 or gl != self.dec_layout:
            # Add Individual
            gb = QGroupBox(tr('Физическое лицо *'))
            gb_l.addWidget(QLabel(tr('Фамилия <em style="color: red">*</em>')))
            w = QLineEdit()
            gb_l.addWidget(w, 0, 1, 1, 1)
            dc['surname'] = w
            gb_l.addWidget(QLabel(tr('Имя <em style="color: red">*</em>')))
            w = QLineEdit()
            gb_l.addWidget(w)
            dc['first_name'] = w
            gb_l.addWidget(QLabel(tr('Отчество')))
            w = QLineEdit()
            gb_l.addWidget(w)
            dc['patronymic'] = w

            adr = QGroupBox(tr('Адрес регистрации *'))
            adr_l = QGridLayout()
            dc['address'] = self.__add_address(adr_l)
            adr.setLayout(adr_l)
            gb_l.addWidget(adr, gb_l.rowCount() + 1, 0, 1, 2)

            gb.setLayout(gb_l)
            gl.addWidget(gb, gl.rowCount() + 1, 0, 1, 2)
            self.individuals.append(dc)
        else:
            # Add LegalEntity
            gb = QGroupBox(
                tr('Юридическое лицо/Индивидуальный предприниматель *'))
            gb_l.addWidget(QLabel(
                tr('Краткое наименование ЮЛ <em style="color: red">*</em>')))
            w = QLineEdit()
            gb_l.addWidget(w, 0, 1, 1, 1)
            dc['name'] = w

            adr = QGroupBox(tr('Юридический адрес *'))
            adr_l = QGridLayout()
            dc['address'] = self.__add_address(adr_l)
            adr.setLayout(adr_l)
            gb_l.addWidget(adr, gb_l.rowCount() + 1, 0, 1, 2)

            gb.setLayout(gb_l)
            gl.addWidget(gb, gl.rowCount() + 1, 0, 1, 2)
            self.entities.append(dc)
