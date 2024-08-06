from PyQt5 import QtWidgets, QtGui, QtCore
from Student_Info.student_details import Ui_Window  # Update to match your directory structure
from connect import connection, mycursor, mysql

class StudentInfoWindow(QtWidgets.QWidget):
    def __init__(self, home_window):
        super().__init__()
        self.ui = Ui_Window()
        self.ui.setupUi(self)
        self.home_window = home_window  # Store the reference to the home window

        # Connect buttons to their respective functions
        self.ui.upload_button.clicked.connect(self.upload_photo)
        self.ui.submit_button.clicked.connect(self.submit_data)
        self.ui.submit_button_2.clicked.connect(self.cancel)

    def upload_photo(self):
        try:
            file_dialog = QtWidgets.QFileDialog(self)
            file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
            if file_dialog.exec_():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    pixmap = QtGui.QPixmap(selected_files[0])
                    pixmap_resized = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio)
                    self.ui.photo_label.setPixmap(pixmap_resized)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Error', f"Failed to upload photo: {e}")

    def submit_data(self):
        name = self.ui.name_input.text().strip()
        roll_number = self.ui.roll_number_input.text().strip()
        class_ = self.ui.standard_input.text().strip()
        standard = self.ui.class_input.text().strip()
        pixmap = self.ui.photo_label.pixmap()

        # Validate inputs
        if not name or not roll_number:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Name and Roll Number are required fields!')
            return

        if pixmap is None:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Photo is required!')
            return

        # Convert the pixmap to binary data
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QIODevice.WriteOnly)
        pixmap.save(buffer, "PNG")
        photo_data = buffer.data().data()

        # Debug: Print photo_data to ensure it's correct
        print(f"Photo data: {photo_data[:100]}...")  # Print only the first 100 bytes for brevity

        # Prepare the insert query
        insert_query = "INSERT INTO stud_info1 (name, `roll_no`, standard, class, photo) VALUES (%s, %s, %s, %s, %s)"
        values = (name, roll_number, standard, class_, photo_data)

        try:
            # Execute the query
            mycursor.execute(insert_query, values)
            connection.commit()  # Commit the transaction
            QtWidgets.QMessageBox.information(self, 'Success', 'Student information submitted successfully!')
            self.clear_fields()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            QtWidgets.QMessageBox.critical(self, 'Error', f"Failed to insert data: {err}")

    def cancel(self):
        self.clear_fields()
        self.home_window.show()  # Show the home window
        self.close()  # Close the student info window

    def clear_fields(self):
        self.ui.name_input.clear()
        self.ui.roll_number_input.clear()
        self.ui.standard_input.clear()
        self.ui.class_input.clear()
        self.ui.photo_label.clear()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    student_info_window = StudentInfoWindow(None)  # Pass None as we don't have the home window reference in this context
    student_info_window.show()
    sys.exit(app.exec_())
