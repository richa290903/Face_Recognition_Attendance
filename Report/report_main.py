import sys
import subprocess
from PyQt5 import QtWidgets, QtCore
from PyQt5.uic import loadUi
from connect1 import get_db_connection  # Assuming get_db_connection is defined to get a database connection
from Report.student_info_dialog import StudentInfoDialog
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

class ReportWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(ReportWindow, self).__init__(parent)
        loadUi('Report/att_report.ui', self)
        self.home_window = parent

        # Connect button clicks to functions
        self.pushButton.clicked.connect(self.cancel_action)
        self.pushButton_2.clicked.connect(self.ok_action)

        # Initialize custom date section
        self.date_edit = QtWidgets.QDateEdit(self.groupBox)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.date_edit.setVisible(False)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")

        # Connect combo box index change
        self.comboBox.currentIndexChanged.connect(self.handle_combo_box_change)
        self.comboBox_2.currentIndexChanged.connect(self.handle_report_type_change)

        # Add date edit widget immediately below the combo boxes in the layout
        self.verticalLayout_3.insertWidget(self.verticalLayout_3.indexOf(self.horizontalLayout) + 1, self.date_edit)

    def cancel_action(self):
        # Close the report window and show the home window
        self.close()
        if self.home_window:
            self.home_window.show()

    def ok_action(self):
        # Get the values from the form elements
        standard = self.lineEdit.text()
        class_name = self.lineEdit_2.text()
        report_type = self.comboBox_2.currentText()
        time_period = self.comboBox.currentText()

        if not standard or not class_name:
            QtWidgets.QMessageBox.warning(self, 'Missing Information', 'Please enter Standard and Class.')
            return

        if report_type == "Student Wise":
            # Open student info dialog for entering student details
            self.open_student_info_dialog(standard, class_name)
        else:
            if time_period == "Custom Date":
                selected_date = self.date_edit.date().toString("yyyy-MM-dd")  # Ensure the date format is correct
                self.fetch_attendance_data(standard, class_name, selected_date=selected_date)
            else:
                self.fetch_attendance_data(standard, class_name, time_period=time_period)

    def handle_combo_box_change(self, index):
        # Toggle visibility of date edit based on combo box selection
        if self.comboBox.itemText(index) == "Custom Date":
            self.date_edit.setVisible(True)
        else:
            self.date_edit.setVisible(False)

    def handle_report_type_change(self, index):
        # Handle when the report type (comboBox_2) changes
        report_type = self.comboBox_2.itemText(index)
        if report_type == "Student Wise":
            # Immediately show the student information dialog
            standard = self.lineEdit.text()
            class_name = self.lineEdit_2.text()
            self.open_student_info_dialog(standard, class_name)

    def open_student_info_dialog(self, standard, class_name):
        dialog = StudentInfoDialog(self, standard, class_name)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            student_name, roll_no = dialog.get_info()
            if not student_name or not roll_no:
                QtWidgets.QMessageBox.warning(self, 'Missing Information', 'Please enter Student Name and Roll Number.')
                return
            # Fetch and display attendance data for the student
            self.fetch_attendance_data(standard, class_name, student_name=student_name, roll_no=roll_no)
   
    def fetch_attendance_data(self, standard, class_name, student_name=None, roll_no=None, selected_date=None, time_period=None):
        time_period = self.comboBox.currentText()
        selected_date = self.date_edit.date().toString("yyyy-MM-dd")
        connection = get_db_connection()
        if connection is None:
            QtWidgets.QMessageBox.warning(self, 'Database Connection Error', 'Unable to connect to the database.')
            return

        try:
            query = """
            SELECT s.name, s.roll_no, s.standard, s.class, a.date, a.time
            FROM stud_info1 s
            LEFT JOIN attendance1 a ON s.name = a.name
            """
            params = []

            conditions = ["s.standard = %s", "s.class = %s"]
            params.extend([standard, class_name])

            if student_name and roll_no:
                conditions.append("s.name = %s AND s.roll_no = %s")
                params.extend([student_name, roll_no])

            if time_period and time_period != "Custom Date":
                current_date = datetime.now().date()
                if time_period == "Weekly":
                    start_date = current_date - timedelta(days=7)
                elif time_period == "Monthly":
                    start_date = current_date - timedelta(days=30)
                elif time_period == "Yearly":
                    start_date = current_date - timedelta(days=365)
                conditions.append("a.date BETWEEN %s AND %s")
                params.extend([start_date.strftime('%Y-%m-%d'), current_date.strftime('%Y-%m-%d')])
            elif selected_date:
                conditions.append("a.date = %s")
                params.append(selected_date)

            query += " WHERE " + " AND ".join(conditions)

            cursor = connection.cursor()
            cursor.execute(query, tuple(params))
            records = cursor.fetchall()
            print(params)
            if records:
                self.generate_pdf(records)
            else:
                QtWidgets.QMessageBox.information(self, 'No Records', 'No attendance records found for the given criteria.')

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Database Error', f'Error: {e}')

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()



    def generate_pdf(self, records):
        file_name = "attendance_report.pdf"
        document = SimpleDocTemplate(file_name, pagesize=letter)
        styles = getSampleStyleSheet()

        data = [["Name", "Roll No", "Standard", "Class", "Date", "Time"]]
        for record in records:
            data.append([record[0], record[1], record[2], record[3], record[4], record[5]])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements = [Paragraph("Attendance Report", styles['Title']), table]
        document.build(elements)

        QtWidgets.QMessageBox.information(self, 'Report Generated', f'Report saved as {file_name}')
        self.open_pdf(file_name)

    def open_pdf(self, pdf_file):
        try:
            subprocess.Popen([pdf_file], shell=True)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Error Opening PDF', f'Error: {str(e)}')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = ReportWindow()
    mainWindow.show()
    sys.exit(app.exec_())