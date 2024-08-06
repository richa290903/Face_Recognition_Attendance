from PyQt5 import QtWidgets, QtGui, QtCore
from connect1 import get_db_connection

class StudentInfoDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, standard=None, class_name=None):
        super(StudentInfoDialog, self).__init__(parent)
        self.setWindowTitle("Student Information")
        
        # Set fixed size
        self.setFixedSize(400, 300)  # Width: 400, Height: 300

        self.standard = standard
        self.class_name = class_name

        # Layout
        layout = QtWidgets.QVBoxLayout()

        # Student name
        self.name_label = QtWidgets.QLabel("Student Name")
        self.name_combo = QtWidgets.QComboBox()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_combo)

        # Roll number
        self.roll_label = QtWidgets.QLabel("Roll Number")
        self.roll_combo = QtWidgets.QComboBox()
        layout.addWidget(self.roll_label)
        layout.addWidget(self.roll_combo)

        # Fetch button
        self.fetch_button = QtWidgets.QPushButton("Fetch")
        self.fetch_button.clicked.connect(self.fetch_student_info)
        layout.addWidget(self.fetch_button)

        # Buttons
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        self.populate_student_info()

    def populate_student_info(self):
        connection = get_db_connection()
        if connection is None:
            QtWidgets.QMessageBox.warning(self, 'Database Connection Error', 'Unable to connect to the database.')
            return

        try:
            query = "SELECT name, roll_no FROM stud_info1 WHERE standard = %s AND class = %s"
            cursor = connection.cursor()
            cursor.execute(query, (self.standard, self.class_name))
            students = cursor.fetchall()

            if students:
                for student in students:
                    self.name_combo.addItem(student[0])
                    self.roll_combo.addItem(str(student[1]))
            else:
                print("No students found for the given standard and class.")

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Database Error', f"Error fetching data: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def fetch_student_info(self):
        # This method can be used to validate or further process selected student info
        pass

    def get_info(self):
        return self.name_combo.currentText(), self.roll_combo.currentText()
