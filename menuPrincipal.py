# APLICACION PARA MANEJO DE INVENTARIO #

# importaciones

#importaciones del sistema
import os
from os import remove
import sys
import time
import datetime
import shutil
from shutil import copyfile
os.environ["QT_LOGGING_RULES"]= "qt.gui.icc= false"
#importar sqlite para manejjo de la bdd
import sqlite3
#importaciones de pyqt5
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox,QTableWidgetItem, QLabel, QDialog, QVBoxLayout, QLineEdit, QPushButton, QProgressDialog, QWidget
from PyQt5.QtCore import Qt, Qdate, pyqtSignal
from PyQt5.QtGui import QBrush, QColor
#importaciones de reportlab y panda para los reportes impresos
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, paragraph, Spacer, Image
#importar clases 

# clase de la ventana de inicio de sesion para acceder al sistema

#clase menu principal
class MenuPrincipalc(QtWidgets.QMainWindow):
    def __init__(self, admin, nameUsDB, usuarioDB, passwordDB ):
        super(MenuPrincipalc, self).__init__()
        uic.loadUi("./ui/menu_principal.ui", self)
        self.admin = admin
        self.usuarioDB = usuarioDB
        self.passwordDB = passwordDB
        self.nameUsDB = nameUsDB
        if self.admin == "true":
           self.Label_nameUser.setText(f"Bienvenido Administrador, {nameUsDB}")
        else : 
            self.Label_nameUser.setText(f"Bievenido, {nameUsDB} ")