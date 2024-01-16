# APLICACION PARA MANEJO DE INVENTARIO #

# importaciones

#importaciones del sistema
import os
from os import remove
import sys
import time
import datetime
import shutil
import csv
from shutil import copyfile
os.environ["QT_LOGGING_RULES"]= "qt.gui.icc= false"
#importar sqlite para manejjo de la bdd
import sqlite3
#importaciones de pyqt5
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox,QTableWidgetItem, QLabel, QDialog, QVBoxLayout, QLineEdit, QPushButton, QProgressDialog, QWidget
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QBrush, QColor
#importaciones de reportlab y panda para los reportes impresos
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, paragraph, Spacer, Image
#importar clases 

#####################################################################################################################################################

# clase de la ventana de inicio de sesion para acceder al sistema
class login(QtWidgets.QMainWindow):
    def __init__(self):
        super(login, self).__init__()
        uic.loadUi("./ui/login.ui", self)
        self.btn_acceder.clicked.connect(self.validacion)
        self.setWindowTitle("|Manejo de Inventario|")
    
    def validacion(self):
        usuario = self.txt_user.text()
        contras = self.txt_password.text()
        
        if not usuario or not contras:
            QMessageBox.warning(self, "Error de autenticación", "Por favor ingrese su usuario y contraseña ")         
            return

        with sqlite3.connect("./database/db.db") as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE User = ?", (usuario,))
            user = cursor.fetchone()

            if user: 
                usuarioDB = user[0]
                passwordDB = user[1]
                nameUsDB = user[4]
                admin = user[3]

                if contras == passwordDB:
                    self.registrarOperacion(usuarioDB, "Inicio de Sesión", datetime.datetime.now())
                    self.menu_principal = MenuPrincipalc(admin, nameUsDB, usuarioDB, passwordDB)
                    self.menu_principal.show()
                    self.hide()  # Oculta la ventana actual
                else:
                    QMessageBox.warning(self, "Error al autenticar", "Contraseña incorrecta")
            else:
                QMessageBox.warning(self, "Error al autenticar", "Usuario no encontrado en la base de datos")

    def registrarOperacion(self, responsable, operacion, fecha_operacion):
        try:
            with sqlite3.connect("./database/db.db") as conexion:
            # Convertir la fecha a un formato compatible con SQLite
                fecha_sqlite = fecha_operacion.strftime('%Y-%m-%d %H:%M:%S')

            # Insertar la operación en la tabla de operaciones
                cursor = conexion.cursor()
                cursor.execute("""
                    INSERT INTO operaciones (responsable, operacion, fecha_operacion)
                    VALUES (?, ?, ?)
                """, (responsable, operacion, fecha_sqlite))

                conexion.commit()

        except sqlite3.Error as e:
            print(f"Error al registrar operación: {str(e)}")
            raise  
# clase de login lista y completamente funcional sin errores :) (###LISTO###)   
    
#####################################################################################################################################################
    
# clase de la ventana de menu principal
class MenuPrincipalc(QtWidgets.QMainWindow):
    def __init__(self, admin, nameUsDB, usuarioDB, passwordDB):
        super(MenuPrincipalc, self).__init__()
        uic.loadUi("./ui/menu_principal.ui", self)
        # cargar datos del usuario(nombre, contraseña, usuario) para uso posterior
        self.admin = admin
        self.usuarioDB = usuarioDB
        self.passwordDB = passwordDB
        self.nameUsDB = nameUsDB
        # mostrar los datos del usuario en un label en la ventana.
        if self.admin == "true":
            self.Label_nameUser.setText(f"Bienvenido Administrador, {nameUsDB}, su usuario es: {usuarioDB}, su contraseña:{passwordDB}")
        else:
            self.Label_nameUser.setText(f"Bienvenido, {nameUsDB}, su usuario es: {usuarioDB}, su contraseña:{passwordDB}")
        
        ### abrir otras ventanas desde la ventana de menu principal
        # abrir ventana de ajustes del sistema
        self.bt_ajustes.clicked.connect(self.abrirAjustes)
        # abrir ventana de menu de la base de datos (opciones avanzadas)
        self.bt_BDD.clicked.connect(self.abrirBddMenu)
        # abrir ventana de gestion de usuarios
        self.bt_config_usser.clicked.connect(self.abrirUsuarios)
        # abrir ventana de agregar al inventario
        self.pushButton_aggalInventario.clicked.connect(self.abrirInventario)
        # cerrar sesion
        self.bt_salir.clicked.connect(self.cerrarSesion)
        
        ## Metodos de pedidos (ver, crear, editar, eliminar) ##
        # cambio de paginas en la seccion de pedidos 
        self.btn_generarPedidos.clicked.connect( lambda:self.stackedWidget_pedidos.setCurrentWidget(self.page_generarPedidos) ) #pagina de generar pedidos
        self.btn_visualizarPedidos.clicked.connect(lambda:self.stackedWidget_pedidos.setCurrentWidget(self.page_VisualizaPedidos)) # pagina de visualizar pedidos
        # conexion al metodo para guardar los pedidos
        self.btn_guardar_pedid.clicked.connect(self.agregar_pedido)
        # conexion al metodo para agregar el contenido los pedidos
        self.btn_aggtblPedidos.clicked.connect(self.agregarprod_pedido)
        # conexion al metodo para buscar  los pedidos
        self.btn_buscarPedido.clicked.connect(self.buscar_pedido)
        # conexion al metodo para limpiar los campos en el area de generar los pedidos
        self.btn_limpiarCampos_pedid.clicked.connect(self.limpiar_pedido)
        # conexion al metodo para editar los pedidos
        self.btn_editarPedido.clicked.connect(self.editar_pedido)
        # conexion al metodo para eliminar los pedidos
        self.btn_elimiarPedido_1.clicked.connect(self.eliminarPedido)
        # conexion al metodo para llenar los campos 
        # con la informacion de la tabla con el contenido de los pedidos
        self.tablapedidocrear.cellClicked.connect(self.llenar_lineeditsPedidos)
        # conexion al metodo para buscar y ver pedidos en la pagina de visualizar los pedidos
        self.btn_bscrPedidos.clicked.connect(self.vertabla_pedido)
        # conexion al metodo para limpiar los campos de productos  del pedido
        self.btn_limpiarProdPedido.clicked.connect(self.limpiarCamposPedido)

    # metodo para el registro de operaciones
    def registrarOperacion(self, operacion):
        try:
            with sqlite3.connect("./database/db.db") as conexion:
                fecha_operacion = datetime.datetime.now()
                fecha_sqlite = fecha_operacion.strftime('%Y-%m-%d %H:%M:%S')

                cursor = conexion.cursor()
                cursor.execute("""
                    INSERT INTO operaciones (responsable, operacion, fecha_operacion)
                    VALUES (?, ?, ?)
                """, (self.usuarioDB, operacion, fecha_sqlite))

                conexion.commit()

        except sqlite3.Error as e:
            print(f"Error al registrar operación: {str(e)}")
            raise
    
    # abrir ventana de menu de la base de datos
    def abrirBddMenu(self):
        if self.admin == "true":
            self.registrarOperacion("Abrir Ventana de Menu de Base de Datos")
            self.bddmenu = baseDeDatos(admin=self.admin, nameUsDB=self.nameUsDB, usuarioDB=self.usuarioDB, passwordDB=self.passwordDB)
            self.bddmenu.show()
            self.hide()  # Oculta la ventana actual
        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return

    # abrir ventana de ajustes del sistema
    def abrirAjustes(self):
        if self.admin == "true":
            self.registrarOperacion("Abrir Ventana de Ajustes")
            self.ajustes = Ajustes(admin=self.admin, nameUsDB=self.nameUsDB, usuarioDB=self.usuarioDB, passwordDB=self.passwordDB)
            self.ajustes.show()
            self.hide()  # Oculta la ventana actual
        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return

    # abrir ventana de gestion de usuarios
    def abrirUsuarios(self):
        if self.admin == "true":
            self.registrarOperacion("Abrir Ventana de Gestión de Usuarios")
            self.usuarios = Usuarios(admin=self.admin, nameUsDB=self.nameUsDB, usuarioDB=self.usuarioDB, passwordDB=self.passwordDB)
            self.usuarios.show()
            self.hide()  # Oculta la ventana actual
        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return

    # abrir ventana de agg/editar equipos herramientas o prod del inventario
    def abrirInventario(self):
        if self.admin == "true":
            self.registrarOperacion("Abrir Ventana de Inventario")
            self.inventario = Inventario(admin=self.admin, nameUsDB=self.nameUsDB, usuarioDB=self.usuarioDB, passwordDB=self.passwordDB)
            self.inventario.show()
            self.hide()  # Oculta la ventana actual
        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return

    # metodo de Cerrar sesion
    def cerrarSesion(self):
        self.registrarOperacion("Cerrar Sesión")
        ingreso_usuario.show()
        ingreso_usuario.txt_user.clear()
        ingreso_usuario.txt_password.clear()
        self.hide()

    ### Metodos para realizar editar eliminar y visualizar pedidos ###
    
    ## Ver pedidos en la página de visualizar ##
    # visualizar los pedidos que ya han sido generados
    def vertabla_pedido(self):
        NumeroPedido = self.lineEdit_busqueda_pedido_ver.text()

        if not NumeroPedido:
            QMessageBox.information(self, "Error", "Ingresa un número de pedido")
            return

        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()

            # Obtener datos del pedido
            cursor.execute("SELECT nombre_producto, especificaciones_tecnicas, cantidad, unidad_de_medida, fecha_tope, necesidadPedido FROM contenido_pedido WHERE numero_pedido=? ", (NumeroPedido,))
            resultado_contenido = cursor.fetchall()

            if resultado_contenido:
                # Configurar la tabla con los datos obtenidos
                self.tablapedido_ver.setRowCount(len(resultado_contenido))
                self.tablapedido_ver.setColumnCount(len(resultado_contenido[0]))
                headers_contenido = ["Nombre Producto", "Especificaciones Técnicas", "Cantidad", "Unidad de Medida", "Fecha Tope", "Necesidad de Pedido"]
                self.tablapedido_ver.setHorizontalHeaderLabels(headers_contenido)

                for row, row_data in enumerate(resultado_contenido):
                    for col, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value))
                        self.tablapedidocrear.setItem(row, col, item)

                # Obtener datos del pedido
                cursor.execute("SELECT Nombre_Proyecto, Responsable_pedido, telefon_responsable FROM pedidos WHERE numero_pedido=?", (NumeroPedido,))
                resultado_pedido = cursor.fetchone()

                if resultado_pedido:
                    self.txtbx_nameproyecto_ver_pedido.setText(resultado_pedido[0])
                    self.lineEdit_Responsable_verPedido.setText(resultado_pedido[1])
                    self.txtbx_telefonoresponsable_VerPedido.setText(str(resultado_pedido[2]))

            else:
                QMessageBox.information(self, "Error", "No hay contenido asociado a ese número de pedido")

            conexion.close()

        except sqlite3.Error as e:
            print("Error al conectarse a SQLite:", e)
            
    # Función auxiliar para limpiar campos de pedido
    def limpiarCamposPedido(self):
        self.lineEdit_nombreP.clear()
        self.lineEdit_espsTecP.clear()
        self.lineEdit_undmedP.clear()
        self.lineEdit_cantP.clear()
        self.lineEdit_necesP.clear()
        
    ##  pedidos en la página de generar ##
    # Buscar pedido (información y también contenido del pedido(tabla))
    def buscar_pedido(self):
        NumeroPedido = self.lineEdit_busqueda_pedido.text()
        # Registrar operación
        self.registrarOperacion(f"Busqueda del pedido: {NumeroPedido}")

        if not NumeroPedido:
            QMessageBox.information(self, "Error", "Ingresa un numero de pedido")
            return

        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT numero_pedido,Nombre_Proyecto,Responsable_pedido,telefon_responsable FROM pedidos WHERE numero_pedido=?", (NumeroPedido,))
            resultado = cursor.fetchone()

            if resultado:
                self.txtbx_nameproyectoPed.setText(resultado[1])
                self.lineEdit_ResponsablePed.setText(resultado[2])
                self.txtbx_telefonoresponsablePed.setText(str(resultado[3]))
                self.lineEdit_numeroPedido.setText(str(resultado[0]))
                self.lineEdit_numeroPedido.setReadOnly(True)
                self.btn_guardar_pedid.setEnabled(False)
                self.cargar_pedido()

            else:
                QMessageBox.information(self, "Error", "No hay pedido actual con ese numero ")

        except sqlite3.Error as e:
            print("Error al conectarse a SQLite:", e)

    def cargar_pedido(self):
        NumeroPedido = self.lineEdit_busqueda_pedido.text()

        if not NumeroPedido:
            QMessageBox.information(self, "Error", "Ingresa un numero de pedido")
            return

        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre_producto,especificaciones_tecnicas,cantidad,unidad_de_medida,fecha_tope,necesidadPedido FROM contenido_pedido WHERE numero_pedido=? ", (NumeroPedido,))
            resultado = cursor.fetchall()

            if resultado:
                # Configurar la tabla con los datos obtenidos
                self.tablapedidocrear.setRowCount(len(resultado))
                self.tablapedidocrear.setColumnCount(len(resultado[0]))
                headers = ["Nombre Producto", "Especificaciones Técnicas", "Cantidad", "Unidad de Medida", "Fecha Tope", "Necesidad de Pedido"]
                self.tablapedidocrear.setHorizontalHeaderLabels(headers)

                for row, row_data in enumerate(resultado):
                    for col, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value))
                        self.tablapedidocrear.setItem(row, col, item)

        except sqlite3.Error as e:
            print("Error al conectarse a SQLite:", e)

    # Agregar información de pedido de mercancia(responsable, telefono, numero pedido)
    def agregar_pedido(self):
        numerodepedido = self.lineEdit_numeroPedido.text()
        # Registrar operación
        self.registrarOperacion(f"Agregar PEDIDO: {numerodepedido}")

        # Realizar una verificación para evitar registros duplicados
        if self.verificar_existencia_numeroPedido(numerodepedido):
            QMessageBox.warning(self, "Error", "Ya existe un registro con este código.")
            return

        # Resto del código para insertar el nuevo registro
        nombreproyecto = self.txt_descrip_HM.text()
        responsableretiro = self.txtbx_telefonoresponsablePed.text()
        telefonresponsable = self.comboBox_agg_HM.currentText()

        if not (numerodepedido and nombreproyecto and responsableretiro and telefonresponsable):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return

        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            query = "INSERT INTO pedidos (numero_pedido, Nombre_Proyecto, Responsable_pedido, telefon_responsable) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (numerodepedido, nombreproyecto, responsableretiro, telefonresponsable))
            conexion.commit()
            QMessageBox.information(self, "Exito", "Los datos se almacenaron correctamente")

        except sqlite3.Error as e:
            print("Error al conectarse a SQLite:", e)

    def verificar_existencia_numeroPedido(self, numerodepedido):
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            query = "SELECT COUNT(*) FROM pedidos WHERE numero_pedido = ?"
            cursor.execute(query, (numerodepedido,))
            count = cursor.fetchone()[0]
            conexion.close()
            return count > 0

        except sqlite3.Error as e:
            print("Error al conectarse a SQLite:", e)

    # Llenar campos con la información de la tabla para editar o eliminar los pedidos
    def llenar_lineeditsPedidos(self, row, col):
        # Obtener datos de la fila seleccionada
        Nombre = self.tablapedidocrear.item(row, 0).text()
        especificaciones = self.tablapedidocrear.item(row, 1).text()
        cantidad = self.tablapedidocrear.item(row, 2).text()
        UMedida = self.tablapedidocrear.item(row, 3).text()
        Necesidad = self.tablapedidocrear.item(row, 5).text()
        fech_entrada = self.tablapedidocrear.item(row, 4).text()
        fecha = QDate.fromString(fech_entrada, 'yyyy-MM-dd')
        
        self.calendarWidget.setSelectedDate(fecha)
        self.lineEdit_nombreP.setText(Nombre)
        self.lineEdit_espsTecP.setText(especificaciones)
        self.lineEdit_undmedP.setText(UMedida)
        self.lineEdit_cantP.setText(cantidad)
        self.lineEdit_necesP.setText(Necesidad)

    # Editar la información del pedido (responsable, nombre proyecto, etc)
    def editar_pedido(self):
        numeroPedido = self.lineEdit_numeroPedido.text()
        # Registrar operación
        self.registrarOperacion(f"Editar informacion del pedido: {numeroPedido}")

        if not numeroPedido:
            QMessageBox.warning(self, 'Error', 'No ha ingresado un número de pedido')
            return

        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            nombreProyecto = self.txtbx_nameproyectoPed.text()
            responsableProyecto = self.lineEdit_ResponsablePed.text()
            telefono = self.txtbx_telefonoresponsablePed.text()
            
            cursor.execute("UPDATE pedidos SET Nombre_Proyecto=?,Responsable_pedido=?,telefon_responsable=? WHERE numero_pedido=?",
                           (nombreProyecto, responsableProyecto, telefono, numeroPedido))
            
            if cursor.rowcount > 0:
                QMessageBox.information(self, "Datos actualizados", "Los datos se actualizaron correctamente")
            
            conexion.commit()
            conexion.close()

        except sqlite3.Error as e:
            print("Error al conectarse a SQLite:", e)

    # Limpiar formulario y tablas
    def limpiar_pedido(self):
        self.txtbx_nameproyectoPed.clear()
        self.lineEdit_ResponsablePed.clear()
        self.txtbx_telefonoresponsablePed.clear()
        self.lineEdit_numeroPedido.clear()
        self.limpiarCamposPedido()
        self.btn_guardar_pedid.setEnabled(True)
        self.lineEdit_numeroPedido.setReadOnly(False)
        self.tablapedidocrear.clear()
    
    # Agregar contenido del pedido
    def agregarprod_pedido(self):
        numerodepedido = self.lineEdit_numeroPedido.text()
        nonmbreProd = self.lineEdit_nombreP.text()
        espTecnicas = self.lineEdit_espsTecP.text()
        cantidad = self.lineEdit_cantP.text()
        unidadMEdida = self.lineEdit_undmedP.text()
        fecha_ingreso = self.calendarWidget.selectedDate()
        fecha_formato_cadena = fecha_ingreso.toString("yyyy-MM-dd")
        necesidadProducto = self.lineEdit_necesP.text()

        if not (numerodepedido and nonmbreProd and espTecnicas and cantidad and unidadMEdida and fecha_formato_cadena and necesidadProducto):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return

        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            query = "INSERT INTO contenido_pedido ( nombre_producto, especificaciones_tecnicas, cantidad, unidad_de_medida, fecha_tope, necesidadPedido,numero_pedido) VALUES (?,?,?,?,?,?,?)"
            cursor.execute(query, (nonmbreProd, espTecnicas, cantidad, unidadMEdida, fecha_formato_cadena, necesidadProducto, numerodepedido))
            conexion.commit()
            QMessageBox.information(self, "Exito", "Los datos se almacenaron correctamente")
            # Registrar operación
            self.registrarOperacion(f"Agregar producto: {nonmbreProd} en el contenido del pedido: {numerodepedido}")

        except sqlite3.Error as e:
            print("Error al conectarse a SQLite:", e)
    
    # Eliminar producto del pedido
    def eliminarPedido(self):
        nombrePedido = self.lineEdit_nombreP.text()
        numerodepedido = self.lineEdit_numeroPedido.text()
        # Registrar operación
        self.registrarOperacion(f"Eliminar producto :  {nombrePedido} del contenido del pedido: {numerodepedido}")

        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM contenido_pedido WHERE nombre_producto=?", (nombrePedido,))
            conexion.commit()
            conexion.close()
            QMessageBox.information(self, "Eliminado", "Ha sido eliminado correctamente")
            self.limpiarCamposPedido()
            
        except sqlite3.Error as e:
            print("Error al conectarse a SQLite:", e)
####################################################################################################################################################
       
# clase de la ventana de ajustes del inventario
class Ajustes(QtWidgets.QMainWindow):
    def __init__(self, admin, nameUsDB, usuarioDB, passwordDB ):
        super(Ajustes, self).__init__()
        uic.loadUi("./ui/Historial_cambios.ui", self)
        # cargar datos del usuario(nombre, contraseña, usuario) para uso posterior
        self.admin = admin
        self.usuarioDB = usuarioDB
        self.passwordDB = passwordDB
        self.nameUsDB = nameUsDB
        
###################################################################################################################################################    

# clase de la ventana de menu de opciones aavanzadas (opciones de la base de datos) 
class baseDeDatos(QtWidgets.QMainWindow):
    def __init__(self, admin, nameUsDB, usuarioDB, passwordDB ):
        super(baseDeDatos, self).__init__()
        uic.loadUi("./ui/bdd.ui", self)
        # cargar datos del usuario(nombre, contraseña, usuario) para uso posterior
        self.admin = admin
        self.usuarioDB = usuarioDB
        self.passwordDB = passwordDB
        self.nameUsDB = nameUsDB
        # inicializacion de variables.
        self.conexion = None
        self.tablas = None
        
        # metodos de exportacion e importacion de base de datos en un archivo csv
        self.btn_importar.clicked.connect(self.importarCSV)
        self.btn_respaldar.clicked.connect(self.exportarBDD_CSV)
        # metodo para limpiar la base de datos
        self.btn_limpiarbdd.clicked.connect(self.limpiarBaseDeDatos)
        # abrir otras ventanas desde esta ventana
        self.btn_VolverMenu.clicked.connect(self.volverMenu)# volver al menu principal
        self.bt_salir_2.clicked.connect(self.cerrarSesion)# cerrar sesion
        self.btn_gest_usuario.clicked.connect(self.abrirUsuarios)# abrir ventana de gestion de usuarios
        self.btn_ajustesInvent.clicked.connect(self.abrirAjustes)
    
    # metodo para el registro de operaciones    
    def registrar_operacion(self, descripcion):
        try:
            # Establecer conexión a la base de datos de operaciones
            conn = sqlite3.connect("./database/db.db")
            cursor = conn.cursor()

            # Obtener la fecha y hora actual
            fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insertar datos de la operación en la tabla operaciones
            cursor.execute("INSERT INTO operaciones (usuario, fecha, descripcion) VALUES (?, ?, ?)",
                           (self.nameUsDB, fecha_hora_actual, descripcion))

            # Confirmar la transacción y cerrar la conexión
            conn.commit()
            conn.close()

            # Mostrar mensaje de éxito
            QMessageBox.information(self, "Operación Registrada", "La operación se ha registrado correctamente.")

        except Exception as e:
            # En caso de error, mostrar mensaje de error
            QMessageBox.critical(self, "Error", f"Error al registrar la operación: {str(e)}")

    def cerrarSesion(self):
        ingreso_usuario.show()
        ingreso_usuario.txt_user.clear()
        ingreso_usuario.txt_password.clear()
        # Luego de realizar la operación, registrarla
        self.registrar_operacion("Cierre de Sesión")
        self.hide()

    def volverMenu(self):
        self.menuprinc = MenuPrincipalc(admin=self.admin, nameUsDB=self.nameUsDB, usuarioDB=self.usuarioDB, passwordDB=self.passwordDB)
        self.menuprinc.show()
        # Luego de realizar la operación, registrarla
        self.registrar_operacion("Volver al Menú Principal")
        self.hide()

    def abrirUsuarios(self):
        if self.admin == "true":
            self.usuarios = Usuarios(admin=self.admin, nameUsDB=self.nameUsDB, usuarioDB=self.usuarioDB, passwordDB=self.passwordDB)
            self.usuarios.show()
            # Luego de realizar la operación, registrarla
            self.registrar_operacion("Apertura de Gestión de Usuarios")
            self.hide()  # Oculta la ventana actual

        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return

    def abrirAjustes(self):
        if self.admin == "true":
            self.ajustes = Ajustes(admin=self.admin, nameUsDB=self.nameUsDB, usuarioDB=self.usuarioDB, passwordDB=self.passwordDB)
            self.ajustes.show()
            # Luego de realizar la operación, registrarla
            self.registrar_operacion("Apertura de Ajustes del Sistema")
            self.hide()  # Oculta la ventana actual

        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return

    def exportarBDD_CSV(self):
        try:
            # El usuario selecciona la carpeta de destino
            carpeta_destino = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Destino")

            if not carpeta_destino:
                return

            # Conectar a la base de datos
            self.conexion = sqlite3.connect("./database/db.db")

            # Obtener la lista de tablas
            consulta_tablas_sql = "SELECT name FROM sqlite_master WHERE type='table';"
            self.tablas = pd.read_sql_query(consulta_tablas_sql, self.conexion)["name"].tolist()

            # Iterar sobre las tablas y exportar a CSV
            for tabla in self.tablas:
                consulta_sql = f"SELECT * FROM {tabla}"
                df = pd.read_sql_query(consulta_sql, self.conexion)

                # Crear el nombre del archivo CSV
                csv_filename = f"{carpeta_destino}/{tabla}.csv"

                # Exportar la tabla a CSV
                df.to_csv(csv_filename, index=False)

            # Luego de realizar la operación, registrarla
            self.registrar_operacion("Exportación de Base de Datos a CSV")
            self.mostrar_mensaje(f"Datos exportados a archivos CSV en: {carpeta_destino}")

        except sqlite3.Error as e:
            self.mostrar_error(f"Error en la conexión a la base de datos: {str(e)}")
        except pd.errors.EmptyDataError:
            self.mostrar_error("Error: La base de datos está vacía.")
        except Exception as e:
            self.mostrar_error(f"Error inesperado: {str(e)}")
        finally:
            if self.conexion:
                self.conexion.close()

    def importarCSV(self):
        try:
            # El usuario selecciona el archivo CSV
            csv_filename, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo CSV", "", "Archivos CSV (*.csv)")

            if not csv_filename:
                return

            if not self.conexion or not self.tablas:
                # Mostrar un error si la conexión o las tablas no están definidas
                self.mostrar_error("Error: La conexión o las tablas no están definidas.")
                return

            # Luego de realizar la operación, registrarla
            self.registrar_operacion(f"Importación de Datos desde CSV: {csv_filename}")

            # Leer el archivo CSV
            with open(csv_filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Obtener el nombre de la tabla desde el nombre del archivo CSV
                tabla = os.path.splitext(os.path.basename(csv_filename))[0]

                # Eliminar datos existentes en la tabla antes de la importación
                cursor = self.conexion.cursor()
                cursor.execute(f"DELETE FROM {tabla}")
                self.conexion.commit()

                # Insertar los datos en la tabla
                for row in reader:
                    cursor.execute(f"INSERT INTO {tabla} VALUES ({','.join(['?']*len(row))})", row)
                self.conexion.commit()

                self.mostrar_mensaje(f"Datos importados desde: {csv_filename} a la tabla {tabla}")

        except sqlite3.Error as e:
            self.mostrar_error(f"Error en la conexión a la base de datos: {str(e)}")
        except pd.errors.EmptyDataError:
            self.mostrar_error("Error: El archivo CSV está vacío.")
        except Exception as e:
            self.mostrar_error(f"Error inesperado: {str(e)}")
    
    # metodo de limpiar la base de datos (eliminar datos de las tablas excepto "usuarios" y "operaciones")        
    def limpiarBaseDeDatos(self):
        # Mostrar un cuadro de diálogo para ingresar la contraseña
        dialog = QDialog(self)
        dialog.setWindowTitle("Confirmar Contraseña")
        layout = QVBoxLayout()
        label = QLabel("Introduce la contraseña del administrador:")
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(label)
        layout.addWidget(password_input)
        dialog.setStyleSheet("QPushButton{\n"
"    color: rgb(255, 255, 255);\n"
"    background-color: rgb(0, 0, 127);\n"
"    font: 75 11pt \"Arial\";\n"
"}\n"
"QLineEdit{\n"
"    color: rgb(0, 0, 0);\n"
"    border:0;\n"
"    background-color: rgba(106, 106, 106, 0.5);\n"
"    font: 75 11pt \"Arial\";\n"
"}\n"
"QMainWindow{\n"
"    background-color: rgb(255, 255, 255);\n"
"}\n"
"QMainWindow::item:selected {\n"
"    background-color: #555;\n"
"\n"
"}\n"
"\n"
"QTabWidget{\n"
"    border:0; \n"
"\n"
"}\n"
"QLabel{\n"
"    \n"
"    font: 75 14pt \"Arial\";\n"
"}\n"
"QGroupBox{\n"
"    \n"
"    font: italic 11pt \"Arial\";\n"
"}\n"
"QComboBox{\n"
"    \n"
"    background-color: rgba(102, 102, 102, 0.5);\n"
"    font: 75 11pt \"Arial\";\n"
"}\n"
"QTableWidget{\n"
"    \n"
"    font: 16pt \"Arial\";\n"
"}")


        def aceptar():
            # Verificar si la contraseña es correcta
            if password_input.text() == self.passwordDB:
                # Eliminar datos de todas las tablas excepto 'usuarios' y 'operaciones'
                cursor = self.conexion.cursor()
                for tabla in self.tablas:
                    if tabla not in ('usuarios', 'operaciones'):
                        cursor.execute(f"DELETE FROM {tabla}")
                self.conexion.commit()
                self.mostrar_mensaje("Base de datos limpiada exitosamente.")
                self.registrar_operacion("Limpieza de Base de Datos")
                dialog.accept()
            else:
                QMessageBox.warning(self, "Contraseña Incorrecta", "La contraseña del administrador es incorrecta.")
    
        button_aceptar = QPushButton("Aceptar")
        button_aceptar.clicked.connect(aceptar)
        layout.addWidget(button_aceptar)
    
        dialog.setLayout(layout)
        dialog.exec_()
# LISTO# funciona totalmente

###################################################################################################################################################

# clase de la ventana de agregar y editar equipos herramientas y productos del inventario 
class Inventario(QtWidgets.QMainWindow):
    def __init__(self, admin, nameUsDB, usuarioDB, passwordDB ):
        super(Inventario, self).__init__()
        uic.loadUi("./ui/agginventario.ui", self)
        # cargar datos del usuario(nombre, contraseña, usuario) para uso posterior
        self.admin = admin
        self.usuarioDB = usuarioDB
        self.passwordDB = passwordDB
        self.nameUsDB = nameUsDB
        # Cambio de paginas del stacked widget 
        self.btn_EM.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.page_equipos))
        self.btn_Herr.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.page_herramientas))
        self.btn_cons.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.page_consumibles))
        #abrir ventanas
        # volver al menu principal
        self.btn_VolverMenu.clicked.connect(self.volverMenu) 
         # abrir la ventana de usuarios
        self.btn_gest_usuario.clicked.connect(self.abrirUsuarios)
        # abrir la ventana de ajustes del sistema
        self.btn_ajustesInvent.clicked.connect(self.abrirAjustes)
        # abrir ventana de opciones avanzadas ( opciones de la base de datos) 
        self.btn_bdd.clicked.connect(self.abrirBddMenu) 
        # cerrar sesion
        self.bt_salir_2.clicked.connect(self.cerrarSesion)
        # METODOS DE CONSUMIBLES 
        self.btn_buscar_ConsAgg.clicked.connect(self.busquedacons)
        self.btn_agg_ConsAgg.clicked.connect(self.agregagrCons)
        self.btn_edit_ConsAgg.clicked.connect(self.editarCons)
        self.btn_delete_ConsAgg.clicked.connect(self.deleteCons)
        self.btn_limpiar_ConsAgg.clicked.connect(self.limpiarCons)
        self.tableWidget_AggCons.cellClicked.connect(self.llenar_lineeditsCons)
        # METODOS DE HERRAMIENTAS
        self.btn_buscarHM.clicked.connect(self.busquedaHM)
        self.btn_aggHM.clicked.connect(self.agregagrHM)
        self.tableWidget_aggHM.cellClicked.connect(self.llenar_lineeditsHM)
        self.btn_editHM.clicked.connect(self.editar_hm)
        self.btn_limpiarHM.clicked.connect(self.limpiarHM)
        self.btn_deleteHM.clicked.connect(self.deleteHM)
        # METODOS DE EQUIPOS Y MAQUINARIAS
        self.btn_edit_EM.clicked.connect(self.editar_em)
        self.btn_delete_EM.clicked.connect(self.eliminar_em)
        self.btn_agg_EM.clicked.connect(self.agregarEM)
        self.btn_buscarEMagg.clicked.connect(self.busquedaEM)
        self.tableWidget_aggEM.cellClicked.connect(self.llenar_lineeditsEM)
        self.btn_limpiarEMagg.clicked.connect(self.limpiarEM)
    
         
    # metodo para el registro de operaciones
    def registrarOperacion(self, operacion):
        try:
            with sqlite3.connect("./database/db.db") as conexion:
                fecha_operacion = datetime.datetime.now()
                fecha_sqlite = fecha_operacion.strftime('%Y-%m-%d %H:%M:%S')

                cursor = conexion.cursor()
                cursor.execute("""
                    INSERT INTO operaciones (responsable, operacion, fecha_operacion)
                    VALUES (?, ?, ?)
                """, (self.usuarioDB, operacion, fecha_sqlite))

                conexion.commit()

        except sqlite3.Error as e:
            print(f"Error al registrar operación: {str(e)}")
            raise
           
    # cerrar sesion 
    def cerrarSesion(self):
        self.registrarOperacion("Cierre de Sesión")
        ingreso_usuario.show()
        ingreso_usuario.txt_user.clear()
        ingreso_usuario.txt_password.clear()
        self.hide()
    
    #volver al menu principal
    def volverMenu(self):
        self.registrarOperacion("Abrir menu principal")
        self.menuprinc = MenuPrincipalc(admin=self.admin, nameUsDB=self.nameUsDB, usuarioDB=self.usuarioDB, passwordDB=self.passwordDB)
        self.menuprinc.show()
        self.hide()
    
    # abrir ventana de gestion de usuarios
    def abrirUsuarios(self):
        if self.admin == "true":
            self.registrarOperacion("Ingreso al menu de gestión de usuarios")
            self.usuarios = Usuarios(admin=self.admin, nameUsDB=self.nameUsDB, usuarioDB=self.usuarioDB, passwordDB=self.passwordDB)
            self.asuarios.show()
            self.hide()  # Oculta la ventana actual

        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return
    
    # abrir ventana de ajustes del sistema
    def abrirAjustes(self):
        if self.admin == "true":
            self.registrarOperacion("Ingreso al menu de ajustes del sistema")
            self.ajustes = Ajustes(admin=self.admin, nameUsDB=self.nameUsDB, usuarioDB=self.usuarioDB, passwordDB=self.passwordDB)
            self.ajustes.show()
            self.hide()  # Oculta la ventana actual

        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return
    
    # abrir ventana de opciones avanzadas ( opciones de la base de datos)
    def abrirBddMenu(self):
        if self.admin == "true":
            self.registrarOperacion("Ingreso al menu de opciones avanzadas y Base de datos")
            self.bddmenu = baseDeDatos(admin=self.admin, nameUsDB=self.nameUsDB, usuarioDB=self.usuarioDB, passwordDB=self.passwordDB)
            self.bddmenu.show()
            self.hide()  # Oculta la ventana actual
        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return

    ### CONSUMIBLES ###
    
    # busca consumibles en la pagina de agregar consumibles
    def busquedacons(self):
        busqueda = self.lineEdit_busqueda_C.text()
        self.registrarOperacion(f"Búsqueda en Base de Datos: {busqueda}")
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            # Consultas a la base de datos
            
            cursor.execute("SELECT * FROM consumibles WHERE Descripcion LIKE ?", ('%' + busqueda + '%',))
            data_consumibless = cursor.fetchall()

            # Combinar los resultados en una lista
            data_total = data_consumibless

            # Configurar la tabla con los datos obtenidos
            self.tableWidget_AggCons.setRowCount(len(data_total))
            #self.tableWidget_AggCons.setColumnCount(7)

            for row, row_data in enumerate(data_total):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_AggCons.setItem(row, col, item)

            conexion.close()
        except Exception as e:
            # Mostrar un mensaje de error en caso de excepción
            QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}") 
    # agregar consumibles
    def agregagrCons(self):
        codigo = self.txt_codigo_consAgg.text()
        self.registrarOperacion("Agregado de consumibles: ")
       #reaizar verificacion para que no se pueda insertar letras en el campo de cantidad
        try:
            #cantidad = int(cantidad)
            cantidad = int(self.txt_cant_ConsAgg.text())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "La cantidad debe ser un número entero positivo.")
            return
         # Realizar una verificación para evitar registros duplicados
        if self.verificar_existencia_codigo_consumibles(codigo):
            QMessageBox.warning(self, "Error", "Ya existe un registro con este código.")
            return

        # Resto del código para insertar el nuevo registro
        descripcion = self.txt_descrip_consAgg.text()
        uni_medida = self.txt_uni_medConsagg.text()
        cantidad = self.txt_cant_ConsAgg.text()
        fecha_ingreso = self.calendar_ingresodecons.selectedDate()
        fecha_formato_cadena = fecha_ingreso.toString("yyyy-MM-dd")
        limite_reorden = self.txt_limite_reorden_AGgCons.text()
        notas = self.txtbox_notasAggCons.text()

        codigo = f"{self.agregar_prefijo_ysr(codigo)}"
        if (not codigo
            or not descripcion
            or not uni_medida
            or not cantidad
            or not fecha_formato_cadena
            or not limite_reorden
            or not notas
            ):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            query = """
            INSERT INTO consumibles (Codigo, Descripcion, Unidad_de_medida, Cantidad, Fecha_de_entrada, Llimite_de_reorden, Notas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (codigo, descripcion, uni_medida, cantidad, fecha_formato_cadena, limite_reorden, notas))

            conexion.commit()
            QMessageBox.information(self, "Exito", "Los datos se almacenaron correctamente")
    # agregar el prefijo de "ysr-" al codigo en caso de que no lo tenga
    def agregar_prefijo_ysr(self, codigo):
        if codigo and not codigo.startswith("ysr-"):
            return f"ysr-{codigo}"
        return codigo
    # Verificar exixtencia de consumibles para evitar resgistrar dos consumibles con el mismo codigo
    def verificar_existencia_codigo_consumibles(self, codigo):
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()
        query = "SELECT COUNT(*) FROM consumibles WHERE Codigo = ?"
        cursor.execute(query, (codigo,))
        count = cursor.fetchone()[0]
        conexion.close()
        return count > 0
    # llenar los lineedits con los valores de la celdda seleccionada    
    def llenar_lineeditsCons(self, row, col):
        # Obtener datos de la fila seleccionada
        codigo = self.tableWidget_AggCons.item(row, 0).text()
        descripcion = self.tableWidget_AggCons.item(row, 1).text()
        uni_medida = self.tableWidget_AggCons.item(row, 2).text()
        cantidad = self.tableWidget_AggCons.item(row, 3).text()
        limite_reorden = self.tableWidget_AggCons.item(row, 5).text()
        notas = self.tableWidget_AggCons.item(row, 6).text()

        fech_entrada = self.tableWidget_AggCons.item(row, 4).text()
        fecha = QDate.fromString(fech_entrada, 'yyyy-MM-dd')
        
        self.calendar_ingresodecons.setSelectedDate(fecha)
        
        # Llenar LineEdits con los datos
        self.txt_codigo_consAgg.setText(codigo)
        self.txt_descrip_consAgg.setText(descripcion)
        self.txt_uni_medConsagg.setText(uni_medida)
        self.txt_stock_ConsAgg.setText(cantidad)
        self.txt_limite_reorden_AGgCons.setText(limite_reorden)
        self.txtbox_notasAggCons.setText(notas)
        self.btn_agg_ConsAgg.setEnabled(False)
        self.txt_codigo_consAgg.setReadOnly(True)
        self.txt_stock_ConsAgg.setReadOnly(True)      
    #editar y eliminar consumibles
    def editarCons(self):
        # Obtener los valores de los LineEdits
        codigo = self.txt_codigo_consAgg.text()
        descripcion = self.txt_descrip_consAgg.text()
        uni_medida = self.txt_uni_medConsagg.text()
        cantidad = self.txt_cant_ConsAgg.text()
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "La cantidad debe ser un número entero positivo.")
            return
        fechaingreso = self.calendar_ingresoHM_fechaIngreso.selectedDate()
        fecha_formato_cadena = fechaingreso.toString("yyyy-MM-dd")
        limite_reorden = self.txt_limite_reorden_AGgCons.text()
        notas = self.txtbox_notasAggCons.text()
        
        # Realizar la actualización en la base de datos usando los valores obtenidos
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()
        query = """
        UPDATE consumibles
        SET
            Codigo = ?,
            Descripcion = ?,
            Unidad_de_medida = ?,
            Cantidad = ?,
            Fecha_de_entrada = ?,
            Llimite_de_reorden = ?,
            Notas = ?
        WHERE Codigo = ?;
        """

        cursor.execute(query, (codigo, descripcion, uni_medida, cantidad, fecha_formato_cadena, limite_reorden, notas, codigo))

        conexion.commit()
        QMessageBox.information(self,"Exito","Los datos se actualizaron correctamente")
    def deleteCons(self):  
        # Obtener el código del producto a eliminar
        codigo = self.txt_codigo_consAgg.text()
        # Realizar la eliminación en la base de datos usando el código obtenido
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()

        query = """
            DELETE FROM consumibles
            WHERE Codigo = ?;
        """

        cursor.execute(query, (codigo,))

        conexion.commit()
        QMessageBox.information(self, "Exito", "Los datos se eliminaron correctamente")
    #limpiar campos para habilitar el boton de agregar   
    def limpiarCons(self):
        self.txt_codigo_consAgg.clear()
        self.txt_descrip_consAgg.clear()
        self.txt_uni_medConsagg.clear()
        self.txt_cant_ConsAgg.clear()
        self.txt_limite_reorden_AGgCons.clear()
        self.txtbox_notasAggCons.clear()
        self.txt_stock_ConsAgg.clear()
        self.btn_agg_ConsAgg.setEnabled(True)
        self.txt_codigo_consAgg.setReadOnly(False)
        
    ### HERRAMIENTAS ###
    
    #busqueda de heramientas manuales en la pagina deingresos
    def busquedaHM(self):
        busqueda = self.lineEdit_busqueda_HM.text()
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            # Consultas a la base de datos
            
            cursor.execute("SELECT * FROM HerramientasManuales WHERE Descripcion LIKE ?", ('%' + busqueda + '%',))
            data_herramientass = cursor.fetchall()

            # Combinar los resultados en una lista
            data_total = data_herramientass

            # Configurar la tabla con los datos obtenidos
            self.tableWidget_aggHM.setRowCount(len(data_total))
            self.tableWidget_aggHM.setColumnCount(7)

            for row, row_data in enumerate(data_total):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_aggHM.setItem(row, col, item)

            conexion.close()
        except Exception as e:
            # Mostrar un mensaje de error en caso de excepción
            QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}") 
    #metodo de agregar herramientas en la pagiande ingresos
    def agregagrHM(self):
        codigo_base = self.txt_codigo_HM.text()
        cantidad = self.txt_cant_HM.text()

        # Validaciones para la cantidad
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "La cantidad debe ser un número entero positivo.")
            return

        for i in range(1, cantidad + 1):
            codigo = f"{self.agregar_prefijo_ysr(codigo_base)}{i}"

            # Realizar una verificación para evitar registros duplicados
            if self.verificar_existencia_codigo_hm(codigo):
                QMessageBox.warning(self, "Error", f"Ya existe un registro con el código {codigo}.")
                return

            # Resto del código para insertar el nuevo registro
            descripcion = self.txt_descrip_HM.text()
            estado = self.comboBox_agg_HM.currentText()
            disponibilidad = self.comboBox_aggdisponibilidadHerr.currentText()
            notas = self.txt_Notas_aggHM.text()
            fecha_ingreso = self.calendar_ingresoHM_fechaIngreso.selectedDate()
            fecha_formato_cadena = fecha_ingreso.toString("yyyy-MM-dd")

            if (not codigo or not descripcion or not estado or not fecha_ingreso or not notas):
                QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
                return

            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            query = "INSERT INTO HerramientasManuales (Codigo, Descripcion, Cantidad, Estado, FechaIngreso, Notas, Disponibilidad) VALUES (?, ?, 1, ?, ?, ?, ?)"

            cursor.execute(query, (codigo, descripcion, estado, fecha_formato_cadena, notas, disponibilidad))

            conexion.commit()

        QMessageBox.information(self, "Éxito", "Los datos se almacenaron correctamente")
    def agregar_prefijo_ysr(self, codigo):
        if codigo and not codigo.startswith("ysr-"):
            return f"ysr-{codigo}"
        return codigo
    def verificar_existencia_codigo_hm(self, codigo):
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()
        query = "SELECT COUNT(*) FROM HerramientasManuales WHERE Codigo = ?"
        cursor.execute(query, (codigo,))
        count = cursor.fetchone()[0]
        conexion.close()
        return count > 0        
    #llenar los lineedits con los datos de la celda clickeada
    def llenar_lineeditsHM(self, row, col):
        # Obtener datos de la fila seleccionada
        codigo = self.tableWidget_aggHM.item(row, 0).text()
        descripcion = self.tableWidget_aggHM.item(row, 1).text()
        cantidad = self.tableWidget_aggHM.item(row, 2).text()
        estado = self.tableWidget_aggHM.item(row, 3).text()
        notas = self.tableWidget_aggHM.item(row, 5).text()
        # Llenar LineEdits con los datos
        self.txt_codigo_HM.setText(codigo)
        self.txt_cant_HM.setText(cantidad)
        self.txt_descrip_HM.setText(descripcion)
        self.txt_Notas_aggHM.setText(notas)
        
        # Configurar las fechas y el estado
        
        # Configurar la fecha y el estado
        # AJUSTE DE FORMATO DE FECHA
        fecha_str = self.tableWidget_aggHM.item(row, 4).text()
        fecha = QDate.fromString(fecha_str, 'yyyy-MM-dd')
        self.calendar_ingresoHM_fechaIngreso.setSelectedDate(fecha)
        
        index = self.comboBox_agg_HM.findText(estado)
        if index >= 0:
            self.comboBox_agg_HM.setCurrentIndex(index)
            
        self.btn_aggHM.setEnabled(False)
        self.txt_codigo_HM.setReadOnly(True)
    #editar y eliminar herramientass manuales
    def editar_hm(self):
    # Obtener los valores de los LineEdits
        codigo = self.txt_codigo_HM.text()
        descripcion = self.txt_descrip_HM.text()
        cantidad = self.txt_cant_HM.text()
        estado = self.comboBox_agg_HM.currentText()
        disponibilidad = self.comboBox_aggdisponibilidadHerr.currentText()
        notas = self.txt_Notas_aggHM.text()
        fechaingreso = self.calendar_ingresoHM_fechaIngreso.selectedDate()
        fecha_formato_cadena = fechaingreso.toString("yyyy-MM-dd")
        
        # Realizar la actualización en la base de datos usando los valores obtenidos
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()
        query = """
        UPDATE HerramientasManuales
        SET
            Codigo = ?,
            Descripcion = ?,
            Cantidad = ?,
            Estado = ?,
            FechaIngreso = ?,
            Notas = ?,
            Disponibilidad = ?
        WHERE Codigo = ?;
        """

        cursor.execute(query, (codigo, descripcion, cantidad, estado, fecha_formato_cadena, notas, disponibilidad, codigo))

        conexion.commit()
        QMessageBox.information(self, "Exito", "Los datos se actualizaron correctamente")        
    def deleteHM(self):  
        # Obtener el código del producto a eliminar
        codigo = self.txt_codigo_HM.text()
        # Realizar la eliminación en la base de datos usando el código obtenido
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()

        query = """
            DELETE FROM HerramientasManuales
            WHERE Codigo = ?;
        """

        cursor.execute(query, (codigo,))

        conexion.commit()
        QMessageBox.information(self, "Exito", "Los datos se eliminaron correctamente")
    #limpiar campos para habilitar el boton de agregar   
    def limpiarHM(self):
        self.txt_codigo_HM.clear()
        self.txt_descrip_HM.clear()
        self.txt_cant_HM.clear()
        self.txt_Notas_aggHM.clear()
        self.btn_aggHM.setEnabled(True)
        self.txt_codigo_HM.setReadOnly(False)
        
        
    ### EQUIPOS Y MAQUINARIAS ###
    
    #buscar equipos y maquinarias en la pagina de ingresos
    def busquedaEM(self):
        busqueda = self.lineEdit_busqueda_EM.text()
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            # Consultas a la base de datos
            
            cursor.execute("SELECT * FROM EquiposyMaquinarias WHERE Descripcion LIKE ?", ('%' + busqueda + '%',))
            data_equipos = cursor.fetchall()

            # Combinar los resultados en una lista
            data_total = data_equipos

            # Configurar la tabla con los datos obtenidos
            self.tableWidget_aggEM.setRowCount(len(data_total))
            #self.tableWidget_aggEM.setColumnCount(7)

            for row, row_data in enumerate(data_total):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_aggEM.setItem(row, col, item)

            conexion.close()
        except Exception as e:
            # Mostrar un mensaje de error en caso de excepción
            QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}")          
    #agregar equipos y maquinarias en la tabla de ingresos                  
    def agregarEM(self):
       
        codigo = self.txt_codigo_EM_2.text()
        
        if not codigo.startswith("ysr-"):
            codigo = "ysr-" + codigo
        # Realizar una verificación para evitar registros duplicados
        if self.verificar_existencia_codigo(codigo):
            QMessageBox.warning(self, "Error", "Ya existe un registro con este código.")
            return
        # Resto del código para insertar el nuevo registro
        placa = self.txt_placa_EM.text()
        serial = self.txt_serial_EM_2.text()
        descripcion = self.txt_descrip_EM_2.text()
        notas = self.txt_notas_EM_2.text()
        fecha_ingreso = self.calendarWidget_aggEM_ingreso.selectedDate()
        fecha_formato_cadena_ing = fecha_ingreso.toString("yyyy-MM-dd")
        fecha_ult_mant = self.calendarWidget_agg_fechultMant_em.selectedDate()
        fecha_formato_cadena_um = fecha_ult_mant.toString("yyyy-MM-dd")
        estado = self.comboBox_aggEM.currentText()
        disponibilidad = self.comboBox_aggDisponibilidadEM.currentText()
        frecuencia_mant = self.comboBox_aggFrecuenciadeMAntEM_2.currentText()
        if (not codigo
            or not placa
            or not serial
            or not descripcion
            or not notas
            or not fecha_ult_mant
            or not fecha_ingreso
            or not estado
            or not disponibilidad
            or not frecuencia_mant
            ):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            query = "INSERT INTO EquiposyMaquinarias (Codigo, Placa, Serial, Descripcion, Estado, Fecha_de_ingreso, Fecha_de_UltimoMantenimiento, Notas, Lapso_entre_mantenimiento, Disponibilidad) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

            cursor.execute(query, (codigo, placa, serial, descripcion, estado, fecha_formato_cadena_ing, fecha_formato_cadena_um, notas, frecuencia_mant, disponibilidad))

            conexion.commit()
            QMessageBox.information(self, "Exito", "Los datos se almacenaron correctamente")
            
    def verificar_existencia_codigo(self, codigo):
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()
        query = "SELECT COUNT(*) FROM EquiposyMaquinarias WHERE Codigo = ?"
        cursor.execute(query, (codigo,))
        count = cursor.fetchone()[0]
        conexion.close()
        return count > 0   
    #llenar los lineedits de acuerdo a los datos seleccionados en la tabla
    def llenar_lineeditsEM(self, row, col):
        # Obtener datos de la fila seleccionada
        codigo = self.tableWidget_aggEM.item(row, 0).text()
        placa= self.tableWidget_aggEM.item(row,1).text()
        serial = self.tableWidget_aggEM.item(row, 2).text()
        descripcion = self.tableWidget_aggEM.item(row, 3).text()
        estado = self.tableWidget_aggEM.item(row, 4).text()
        #fech_entr = self.tableWidget_aggEM.item(row, 4).text()
        #fech_ult_mant = self.tableWidget_aggEM.item(row, 5).text()
        notas = self.tableWidget_aggEM.item(row, 7).text()
        fech_entr = self.tableWidget_aggEM.item(row, 5).text()
        fech_ult_mant = self.tableWidget_aggEM.item(row, 6).text()
        # Llenar LineEdits con los datos
        self.txt_codigo_EM_2.setText(codigo)
        self.txt_placa_EM.setText(placa)
        self.txt_serial_EM_2.setText(serial)
        self.txt_descrip_EM_2.setText(descripcion)
        self.txt_notas_EM_2.setText(notas)
        fecha_ing = QDate.fromString(fech_entr, 'yyyy-MM-dd')
        self.calendarWidget_aggEM_ingreso.setSelectedDate(fecha_ing)

        fecha_ult_mant = QDate.fromString(fech_ult_mant, 'yyyy-MM-dd')
        self.calendarWidget_agg_fechultMant_em.setSelectedDate(fecha_ult_mant)

        # Configurar las fechas y el estado
        #self.dateEdit_aggEM.setDate(QDate.fromString(fech_ult_mant, Qt.ISODate))
        #self.dateEdit_aggEMultMant.setDate(QDate.fromString(fech_entr, Qt.ISODate))
        
        #fecha_ing = self.tableWidget_aggEM.item(row, 5).text()
        #fecha = QDate.fromString(fecha_ing, 'yyyy-MM-dd')
        #self.calendarWidget_aggEM_ingreso.setSelectedDate(fecha)
        
        #fecha_ult_mant= self.tableWidget_aggEM.item(row, 6).text()
        #fecha = QDate.fromString(fecha_ult_mant, 'yyyy-MM-dd')
        #self.calendarWidget_agg_fechultMant_em.setSelectedDate(fecha)
        
        index = self.comboBox_aggEM.findText(estado)
        if index >= 0:
            self.comboBox_aggEM.setCurrentIndex(index)
        self.btn_agg_EM.setEnabled(False)
        self.txt_codigo_EM_2.setReadOnly(True)         
    #limpiar los lineedits y entradas de datos
    def limpiarEM(self):
        self.txt_codigo_EM_2.clear()
        self.txt_placa_EM.clear()
        self.txt_serial_EM_2.clear()
        self.txt_descrip_EM_2.clear()
        self.txt_notas_EM_2.clear()
        self.btn_agg_EM.setEnabled(True)
        self.txt_codigo_EM_2.setReadOnly(False)   
    #editar los equipos y maquinarias
    def editar_em(self):
        # Obtener el código original antes de la edición
        codigo_original = self.txt_codigo_EM_2.text()

        # Obtener los valores de los LineEdits
        codigo = self.txt_codigo_EM_2.text()
        placa= self.txt_placa_EM.text()
        serial = self.txt_serial_EM_2.text()
        descripcion = self.txt_descrip_EM_2.text()
        notas = self.txt_notas_EM_2.text()
        
        fecha_ingreso = self.calendarWidget_aggEM_ingreso.selectedDate()
        fecha_formato_cadena_ing = fecha_ingreso.toString("yyyy-MM-dd")
        fecha_ult_mant = self.calendarWidget_agg_fechultMant_em.selectedDate()
        fecha_formato_cadena_um = fecha_ult_mant.toString("yyyy-MM-dd")
        
        #fech_ult_mant = self.dateEdit_aggEM.date().toString(Qt.ISODate)
        #fech_entr = self.dateEdit_aggEMultMant.date().toString(Qt.ISODate)
        estado = self.comboBox_aggEM.currentText()

        # Realizar la actualización en la base de datos usando los valores obtenidos
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()
        query = """
        UPDATE EquiposyMaquinarias
        SET
            Codigo = ?,
            Placa = ?,
            Serial = ?,
            Descripcion = ?,
            Estado = ?,
            Fecha_de_ingreso = ?,
            Fecha_de_UltimoMantenimiento = ?,
            Notas = ?
        WHERE Codigo = ?;
        """

        cursor.execute(query, (codigo, placa, serial, descripcion, estado, fecha_formato_cadena_ing, fecha_formato_cadena_um, notas, codigo_original))

        conexion.commit()
        QMessageBox.information(self, "Exito", "Los datos se actualizaron correctamente")       
    #eliminar los equipos y maquinarias    
    def eliminar_em(self):
        # Obtener el código del producto a eliminar
        codigo = self.txt_codigo_EM_2.text()

        # Realizar la eliminación en la base de datos usando el código obtenido
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()

        query = """
            DELETE FROM EquiposyMaquinarias
            WHERE Codigo = ?;
        """

        cursor.execute(query, (codigo,))

        conexion.commit()
        QMessageBox.information(self, "Exito", "Los datos se eliminaron correctamente")

################################################################################################################################################   

# clase la ventana  de gestion de usuarios 
class Usuarios(QtWidgets.QMainWindow):
    def __init__(self, admin, nameUsDB, usuarioDB, passwordDB ):
        super(Usuarios, self).__init__()
        uic.loadUi("./ui/usuarios.ui", self)
        # cargar datos del usuario(nombre, contraseña, usuario) para uso posterior
        self.admin = admin
        self.usuarioDB = usuarioDB
        self.passwordDB = passwordDB
        self.nameUsDB = nameUsDB
        #cerrar sesion 
        self.btn_cerrarSesion_1.clicked.connect(self.cerrarSesion)
        #abrir ventana de volver al menu principal
        self.btn_backmenu.clicked.connect(self.volverMenu)
        #metodo de buscar ususario
        self.bt_buscarUsser.clicked.connect(self.busquedauser)
        #metodo de agregar usuario en la base de datos
        self.btn_aggusser.clicked.connect(self.AggUser)
        # metoddo de limpiar todos los campos de los forms
        self.btn_clear_inputs.clicked.connect(self.clearinputs1)
        self.btn_clear_inputs2.clicked.connect(self.clearinputs)
        # metodo de actualizar la tabla de usuarios
        self.bt_reload_user.clicked.connect(self.reloadUser)
        #metodos de editar y eliminar usuarios de la bdd
        self.btn_deleteusser.clicked.connect(self.deleteuser)
        self.btn_editusser.clicked.connect(self.edituser)
        # metodo de cargar los datos de la base de datos en la tabla de usuarios
        self.reloadUser()
    
    # metodo de volver al menu principal
    def volverMenu(self):
        self.menuprinc = MenuPrincipalc(admin=self.admin, nameUsDB=self.nameUsDB, usuarioDB=self.usuarioDB, passwordDB=self.passwordDB)
        self.menuprinc.show()
        self.hide()
    
    # Metodo de cerrar sesion 
    def cerrarSesion(self):
        ingreso_usuario.show()
        ingreso_usuario.txt_user.clear()
        ingreso_usuario.txt_password.clear()
        self.hide()
    
    # busqueda de usuario en la pagina de editar y eliminar usuarios
    def busquedauser(self):
        busqueda = self.lineEdit_buscarUsser.text()
        if not busqueda :
            QMessageBox.information(self,"Falta el usuario","Introduzca el usuario para proceder a la busqueda")
            return
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE User=?", (busqueda,))
            usuario = cursor.fetchone()
            if usuario:
                self.lineEdit_usser.setText(usuario[0])
                self.lineEdit_password.setText(usuario[1])
                self.lineEdit_id.setText(usuario[2])
                if usuario[3] =="true":
                    self.radioButton_true.setChecked(True)
                if usuario[3] =="false":
                    self.radioButton_false.setChecked(True)
                self.lineEdit_nameusser.setText(usuario[4])
                self.lineEdit_cedulausser.setText(usuario[5])
                self.lineEdit_cargo.setText(usuario[6])

            else:
                QMessageBox.information(self,"Error","El usuario no existe")
                self.lineEdit_buscarUsser.clear()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}")
    
    # editar y eliminar usuarios
    def deleteuser(self):
        busqueda = self.lineEdit_buscarUsser.text()
        if not busqueda:
            QMessageBox.information(self,"Error","Se necesita buscar el usuario")
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM usuarios WHERE User=?",(busqueda,))
            conexion.commit()
            QMessageBox.information(self,"Exito","Se elimino el usuario")
            self.clearinputs()
            self.clearinputs1()
    def edituser(self):
        busqueda = self.lineEdit_buscarUsser.text()
        if not busqueda:
            QMessageBox.information(self,"Error","Se necesita buscar el usuario")
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            telefono = self.lineEdit_id.text()
            cargo = self.lineEdit_cargo.text()
            admin = None
            if self.radioButton_true.isChecked():
                admin = "true"
            if self.radioButton_false.isChecked():
                admin = "false"
            cedula = self.lineEdit_cedulausser.text()
            usuario = self.lineEdit_usser.text()
            contrase = self.lineEdit_password.text()
            nombre = self.lineEdit_nameusser.text()
            
            cursor.execute("UPDATE usuarios SET User=?,Password=?,ID=?,Admin=?,Nombre=?,Cedula=?,Cargo=? WHERE User=?",(usuario,
                                                                                                  contrase,telefono,admin,nombre,cedula,cargo,busqueda))    
            conexion.commit()
            QMessageBox.information(self,"Exito","Se actualizo el usuario")
            self.clearinputs()
            self.clearinputs1()
    
    # agregar usuarios     
    def AggUser(self):
        usuario = self.txtbx_aggusser.text()
        password = self.txtbx_password.text()
        nombres = self.txtbx_nameAGGusser.text()
        cedula = self.lineEdit_cedulaAgguser.text()
        cargo= self.lineEdit_cargoAGGuser.text()
        iD = self.lineEdit_idAgguser.text()
        
        adminPermisos = None
        if self.rd_bt_true.isChecked() :
            adminPermisos ="true"
        if self.rd_btn_false.isChecked():
            adminPermisos = "false"
        if not  usuario or not password or not adminPermisos:
            QMessageBox.warning(self, "Error", "Por favor ingrese usuario y contraseña.")
            return
        if not nombres or not cedula or not cargo:
            QMessageBox.warning(self, "Error", "Por favor ingrese nombre completo, cédula y cargo del usuario")
            return
        if len(password) <=8 :
            QMessageBox.information(self,"Error","Por favor introduzca más de 8 digitos en su contraseña")
            return
        if len(usuario) <=6:
            QMessageBox.information(self,"Error","Por favor introduzca más de 6 digitos en su usuario")
            return
        
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT User FROM usuarios WHERE User=?", (usuario,))
        existing_user = cursor.fetchone()

        if existing_user:
            QMessageBox.warning(self, "Advertencia", "Ya existe un usuario registrado con el mismo usuario.")
            self.txtbx_aggusser.clear()
            self.txtbx_password.clear()
            self.txtbx_nameAGGusser.clear()
            self.lineEdit_cedulaAgguser.clear()
            self.lineEdit_cargoAGGuser.clear()
            self.lineEdit_idAgguser.clear()
            return
        else:
            cursor.execute("INSERT INTO usuarios (User, Password,ID, Admin, Nombre, Cedula, Cargo)  VALUES (?, ?, ?, ?, ?, ?, ?)", (usuario, password, iD, adminPermisos, nombres, cedula, cargo))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Los datos se almacenaron correctamente")
            self.txtbx_aggusser.clear()
            self.txtbx_password.clear()
            self.txtbx_nameAGGusser.clear()
            self.lineEdit_cedulaAgguser.clear()
            self.lineEdit_cargoAGGuser.clear()
            self.lineEdit_idAgguser.clear()
            self.rd_bt_true.setChecked(False)
            self.rd_btn_false.setChecked(False)
        conexion.close()
    
    # funcion de limpiar los textbox de los formularios de insercion y edicion de datos
    def clearinputs(self):
        self.txtbx_aggusser.clear()
        self.txtbx_password.clear()
        self.txtbx_nameAGGusser.clear()
        self.lineEdit_cedulaAgguser.clear()
        self.lineEdit_idAgguser.clear()
        self.lineEdit_cargoAGGuser.clear()
        self.rd_bt_true.setChecked(False)
        self.rd_btn_false.setChecked(False)  
    def clearinputs1(self):
        self.lineEdit_usser.clear()
        self.lineEdit_password.clear()
        self.lineEdit_nameusser.clear()
        self.lineEdit_id.clear()
        self.lineEdit_cedulausser.clear()
        self.lineEdit_cargo.clear()
        self.radioButton_true.setChecked(False)
        self.radioButton_false.setChecked(False)
        
    # metodo de mostrar y refrescar la tabla de ver usuarios
    def reloadUser(self):
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM Usuarios")
            data = cursor.fetchall()

            self.tableWidget_usuarios.setRowCount(len(data))  

            for row, row_data in enumerate(data):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_usuarios.setItem(row, col, item)
                        
            conexion.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}")
#( completamente lista y funcional ###LISTO###)



if __name__ == '__main__':
    app = QApplication([])
    ingreso_usuario = login()
    ingreso_usuario.show()
    app.exec_()