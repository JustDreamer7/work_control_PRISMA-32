from PyQt6.QtWidgets import QMessageBox


class DateError(Exception):
    def __init__(self, start_date, end_date, message='The start date of data processing is greater than the end date'):
        self.start_date = start_date
        self.end_date = end_date
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.start_date} > {self.end_date} -> {self.message}'

    def ui_output_error(self):
        msg = QMessageBox()
        msg.setText("Date-time Error")
        msg.setInformativeText(self.__str__())
        msg.setWindowTitle("Error")
        msg.exec()
