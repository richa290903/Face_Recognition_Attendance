from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from home import Ui_MainWindow  # Assuming 'home' is the name of your UI file
from Student_Info.main import StudentInfoWindow
from attendance import mark_attendance_with_face_recognition
from Report.report_main import ReportWindow
import threading

class HomeWindow(QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect buttons to their respective functions 
        self.ui.pushButton_3.clicked.connect(self.open_student_info)
        self.ui.pushButton.clicked.connect(self.take_attendance)
        self.ui.pushButton_2.clicked.connect(self.open_attendance_report)
        self.ui.exitButton.clicked.connect(self.exit_application)

    def open_student_info(self):
        self.student_info_window = StudentInfoWindow(self)
        self.student_info_window.show()
        self.hide()

    def take_attendance(self):
        self.hide()
        attendance_thread = threading.Thread(target=self.run_attendance)
        attendance_thread.start()

    def run_attendance(self):
        try:
            mark_attendance_with_face_recognition()
        except Exception as e:
            self.show_error_message(f"Error taking attendance: {e}")
        finally:
            self.show()

    def open_attendance_report(self):
        self.hide()
        self.report_window = ReportWindow(self)
        self.report_window.show()

    def exit_application(self):
        QApplication.quit()

    def show_error_message(self, message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = HomeWindow()
    mainWindow.show()
    sys.exit(app.exec_())
