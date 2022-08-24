import os
import datetime
from PyQt6 import QtCore, QtWidgets


from interfaces.clientui import Ui_MainWindow
from interfaces.drctryChoice import Ui_drctryChoice
from interfaces.takeFiles import Ui_takeFiles


class ReportPrisma32(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.widget = QtWidgets.QWidget()
        """Описание работы UI приложения, связь кнопок с методами, выставление даты."""
        self.setupUi(self)
        self.runPassport.pressed.connect(self.report_on_click)
        self.openDirectory.pressed.connect(self.open_report_directory)
        self.openFileDirectory.pressed.connect(self.open_file_directory)
        self.dateEdit_2.setDate(QtCore.QDate(int(str(datetime.datetime.today()).split(' ')[0].split('-')[0]),
                                             int(str(datetime.datetime.today()).split(' ')[0].split('-')[1]),
                                             int(str(datetime.datetime.today()).split(' ')[0].split('-')[2])))
        self.dateEdit_2.setDisplayFormat("dd.MM.yyyy")
        self.dateEdit.setDate(QtCore.QDate(2020, 1, 1))
        self.dateEdit.setDisplayFormat("dd.MM.yyyy")

    def open_file_directory(self):
        """Описание работы всплывающей формы проводника с выбором папки с файлами ПРИЗМА.
         Производится запись в 2 файла -> 2 кластера, чтобы данные о папке сохранялись в отрыве от работы программы"""
        ui_file_drctry = Ui_takeFiles()
        ui_file_drctry.setupUi(self.widget)
        """Чтение пути папки с файлами ПРИЗМА"""
        try:
            with open('path_prisma_1cl_files.txt', 'r') as f:
                ui_file_drctry.lineEdit.setText(f.read())
        except FileNotFoundError:
            ui_file_drctry.lineEdit.setText("")
        try:
            with open('path_prisma_2cl_files.txt', 'r') as f2:
                ui_file_drctry.lineEdit_2.setText(f2.read())
        except FileNotFoundError:
            ui_file_drctry.lineEdit_2.setText("")
        """Запись в файл пути папки с файлами ПРИЗМА"""
        ui_file_drctry.pushButton.clicked.connect(
            lambda: Ui_takeFiles.get_file_directory(ui_file_drctry, 'path_prisma_1cl_files'))
        ui_file_drctry.pushButton_2.clicked.connect(
            lambda: Ui_takeFiles.get_file_directory(ui_file_drctry, 'path_prisma_2cl_files'))
        self.widget.show()

    def open_report_directory(self):
        """Описание работы всплывающей формы проводника с выбором папки сохранения справки о работе установки,
         картинок, файлов и т.д."""
        ui_report_drctry = Ui_drctryChoice()
        ui_report_drctry.setupUi(self.widget)
        ui_report_drctry.pushButton.clicked.connect(lambda: Ui_drctryChoice.get_report_directory(ui_report_drctry))
        try:
            with open('path_prisma_report.txt', 'r') as f:
                ui_report_drctry.lineEdit.setText(f.read())
        except FileNotFoundError:
            ui_report_drctry.lineEdit.setText("")
        self.widget.show()

    def report_on_click(self):
        """Метод, описывающий получение паспорта с помощью данных UI"""
        start_date = self.dateEdit.dateTime()
        end_date = self.dateEdit_2.dateTime()
        print(f'start_date - {start_date}, \n end_date - {end_date}')
        with open('path_prisma_report.txt', 'r') as f:
            report_path = f.read()
        picture_path = report_path + '/Pics'
        with open('path_prisma_1cl_files.txt', 'r') as f:
            file1cl = f.read()
        with open('path_prisma_2cl_files.txt', 'r') as f:
            file2cl = f.read()
        if ~os.path.exists(picture_path):
            try:
                os.mkdir(picture_path)
            except OSError:
                print(f"Создать директорию {picture_path} не удалось")
            else:
                print(f"Успешно создана директория {picture_path}")

        # проверяем нормальные даты или нет, если да, то графики и word файл строятся
        try:
            pass
        except ZeroDivisionError:
            pass


# запуск основного окна
app = QtWidgets.QApplication([])
window = ReportPrisma32()
window.show()
app.exec()
