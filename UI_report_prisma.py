import datetime
import os

from PyQt6 import QtCore, QtWidgets
from interfaces.clientui import Ui_MainWindow
from interfaces.drctryChoice import Ui_drctryChoice
from interfaces.takeFiles import Ui_takeFiles
from make_report_prisma import make_report_prisma
from exceptions import DateError
from file_reader.db_file_reader import DbFileReader
from file_reader.file_reader import FileReader
from dotenv import load_dotenv
import pathlib
load_dotenv()


class UIReportPrisma32(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.widget = QtWidgets.QWidget()
        """Описание работы UI приложения, связь кнопок с методами, выставление даты."""
        self.setupUi(self)
        self.runPassport.pressed.connect(self.report_on_click)
        self.openDirectory.pressed.connect(self.open_report_directory)
        self.openFileDirectory.pressed.connect(self.open_file_directory)
        self.radioButton.setChecked(True)
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
        ui_file_drctry.lineEdit.setText(os.environ.get("PATH_PRISMA_1CL"))
        ui_file_drctry.lineEdit_2.setText(os.environ.get("PATH_PRISMA_2CL"))
        """Запись в файл пути папки с файлами ПРИЗМА"""
        ui_file_drctry.pushButton.clicked.connect(
            lambda: Ui_takeFiles.get_file_directory(ui_file_drctry, 'PATH_PRISMA_1CL'))
        ui_file_drctry.pushButton_2.clicked.connect(
            lambda: Ui_takeFiles.get_file_directory(ui_file_drctry, 'PATH_PRISMA_2CL'))
        self.widget.show()

    def open_report_directory(self):
        """Описание работы всплывающей формы проводника с выбором папки сохранения справки о работе установки,
         картинок, файлов и т.д."""
        ui_report_drctry = Ui_drctryChoice()
        ui_report_drctry.setupUi(self.widget)
        ui_report_drctry.lineEdit.setText(os.environ.get("PATH_PRISMA_REPORT"))
        ui_report_drctry.pushButton.clicked.connect(lambda: Ui_drctryChoice.get_report_directory(ui_report_drctry))
        self.widget.show()

    def report_on_click(self):
        """Метод, описывающий получение паспорта с помощью данных UI"""
        load_dotenv()
        start_date = self.dateEdit.date().toPyDate()
        end_date = self.dateEdit_2.date().toPyDate()
        try:
            if start_date > end_date:
                raise DateError(start_date, end_date)
            report_path = os.environ.get('PATH_PRISMA_REPORT')
            path_to_files_1 = os.environ.get('PATH_PRISMA_1CL')
            path_to_files_2 = os.environ.get('PATH_PRISMA_2CL')
            picture_path = pathlib.PurePath(report_path, 'Pics')
            try:
                os.mkdir(picture_path)
            except OSError:
                print(f"Создать директорию {picture_path} не удалось")
            else:
                print(f"Успешно создана директория {picture_path}")
            if self.radioButton.isChecked():
                concat_n_df_1 = FileReader.preparing_data(start_date=start_date,
                                                          end_date=end_date,
                                                          cluster=1,
                                                          path_to_files=path_to_files_1)
                concat_n_df_2 = FileReader.preparing_data(start_date=start_date,
                                                          end_date=end_date,
                                                          cluster=2,
                                                          path_to_files=path_to_files_2)
            else:
                concat_n_df_1 = DbFileReader.db_preparing_data(start_date=start_date,
                                                               end_date=end_date,
                                                               path_to_db=os.environ.get('DB_URL'),
                                                               cluster=1)
                concat_n_df_2 = DbFileReader.db_preparing_data(start_date=start_date,
                                                               end_date=end_date,
                                                               path_to_db=os.environ.get('DB_URL'),
                                                               cluster=2)
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
