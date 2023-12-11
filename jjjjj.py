import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QMdiSubWindow, QTextEdit, QAction

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)

        self.create_actions()
        self.create_menus()

    def create_actions(self):
        self.new_action = QAction('New', self)
        self.new_action.triggered.connect(self.new_document)

    def create_menus(self):
        self.file_menu = self.menuBar().addMenu('File')
        self.file_menu.addAction(self.new_action)

    def new_document(self):
        sub_window = QMdiSubWindow()
        text_edit = QTextEdit()
        sub_window.setWidget(text_edit)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec_())