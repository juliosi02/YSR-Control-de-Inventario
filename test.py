import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from plyer import notification

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Notificaciones en PyQt5')

        btn_notify = QPushButton('Mostrar Notificación', self)
        btn_notify.clicked.connect(self.show_notification)
        btn_notify.setGeometry(150, 150, 200, 50)

    def show_notification(self):
        title = 'Notificación'
        message = 'Este es un mensaje de notificación.'
        # Puedes personalizar los parámetros según tus necesidades
        notification.notify(
            title=title,
            message=message,
            app_name='Tu Aplicación',
            timeout=10  # Duración en segundos que la notificación estará visible
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
