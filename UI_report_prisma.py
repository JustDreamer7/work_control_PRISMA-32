import datetime
import os

from PyQt6 import QtCore, QtWidgets
from interfaces.clientui import Ui_MainWindow
from interfaces.drctryChoice import Ui_drctryChoice
from interfaces.takeFiles import Ui_takeFiles
from make_report_prisma import make_report_prisma, preparing_data
from exceptions import DateError
from file_reader.db_file_reader import DbFileReader


class UIReportPrisma32(QtWidgets.QMainWindow, Ui_MainWindow):
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
        self.dateEdit.setDate(QtCore.QDate(int(str(datetime.datetime.today()).split(' ')[0].split('-')[0]), 1, 1))
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
        start_date = self.dateEdit.date().toPyDate()
        end_date = self.dateEdit_2.date().toPyDate()
        try:
            if start_date > end_date:
                raise DateError(start_date, end_date)
            with open('path_prisma_report.txt', 'r') as f:
                report_path = f.read()
            picture_path = report_path + '/Pics' + f'/{start_date.year}'
            with open('path_prisma_1cl_files.txt', 'r') as f:
                path_to_files_1 = f.read()
            with open('path_prisma_2cl_files.txt', 'r') as f:
                path_to_files_2 = f.read()
            if ~os.path.exists(picture_path):
                try:
                    os.mkdir(picture_path)
                except OSError:
                    print(f"Создать директорию {picture_path} не удалось")
                else:
                    print(f"Успешно создана директория {picture_path}")
            # concat_n_df_1, concat_n_df_2 = DbFileReader.db_preparing_data(start_date=start_date,
            #                                                               end_date=end_date,
            #                                                               path_to_db="mongodb://localhost:27017/")
            concat_n_df_1, concat_n_df_2 = preparing_data(start_date=start_date,
                                                          end_date=end_date,
                                                          path_to_files_1=path_to_files_1,
                                                          path_to_files_2=path_to_files_2)
            make_report_prisma(start_date=start_date, end_date=end_date, report_path=report_path,
                               picture_path=picture_path, concat_n_df_1=concat_n_df_1, concat_n_df_2=concat_n_df_2)
        except PermissionError:
            print("Закройте предыдущую версию файла!")
        except DateError:
            DateError(start_date, end_date).ui_output_error()


# запуск основного окна
app = QtWidgets.QApplication([])
window = UIReportPrisma32()
window.show()
app.exec()
