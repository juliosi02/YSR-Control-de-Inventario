import sys
import shutil 
import time
from os import remove
from shutil import copyfile
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QBrush, QColor
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QLabel, QDialog,QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QProgressDialog
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

import os
os.environ["QT_LOGGING_RULES"] = "qt.gui.icc=false"


# Clase Login 
class IngresoUsuario(QtWidgets.QMainWindow):
    def __init__(self):
        super(IngresoUsuario, self).__init__()
        uic.loadUi("./ui/login.ui", self)
        self.btn_acceder.clicked.connect(self.ingreso)
        self.showMaximized()
        self.setWindowTitle("Manejo de inventario YSR Soluciones, C.A")

    def menuPrincipal_access(self, admin, user_name):
        menuview = MenuPrincipal(admin, user_name )
        widget.addWidget(menuview)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def ingreso(self):
        usuario = self.txt_user.text()
        password = self.txt_password.text()
        if not usuario or not password:
            QMessageBox.warning(self, "Error", "Por favor ingrese usuario y contraseña.")
            return

        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE User = ?", (usuario,))
        user = cursor.fetchone()

        if user:
            passwordDb = user[1]
            user_name = user[4]

            if password == passwordDb:
                print("contraseña correcta")
                admin = user[3]
                self.menuPrincipal_access(admin, user_name)
            else:
                QMessageBox.warning(self, "Error", "Contraseña incorrecta")
        else:
            QMessageBox.information(self, "Error", "Usuario no encontrado en la base de datos")
        conexion.close()

#clase menu principal
class MenuPrincipal(QtWidgets.QMainWindow):
    def __init__(self, admin, user_name ):
        super(MenuPrincipal, self).__init__()
        uic.loadUi("./ui/menu_principal.ui", self)
        self.admin = admin
        self.user_name = user_name
        if self.admin == "true":
           self.Label_nameUser.setText(f"Bienvenido Administrador, {user_name}")
        else : 
            self.Label_nameUser.setText(f"Bievenido, {user_name} ")
        self.setWindowTitle("Manejo de Inventario")
        self.bt_salir.clicked.connect(self.backLogin)
        # dirigir a la pagina de  gestion de usuarios
        self.bt_config_usser.clicked.connect(self.verifyAdmin)
        self.bt_BDD.clicked.connect(self.bddView)
        # pagina de gestion de ver inventario en el menu principal
        self.pushButton_aggalInventario.clicked.connect(self.geestInventView)
        self.btn_pagePrincipal.clicked.connect( lambda:self.stackedWidget.setCurrentWidget(self.page_principal) )
        self.btn_page_em.clicked.connect( lambda:self.stackedWidget.setCurrentWidget(self.page_EquiposMaquinarias) )
        self.bt_page_hm.clicked.connect( lambda:self.stackedWidget.setCurrentWidget(self.page_herramientas_manuales) )
        self.btn_pageC.clicked.connect( lambda:self.stackedWidget.setCurrentWidget(self.page_Consumibles) )
        # metodos relacionados a equipos y maquinarias
        self.bt_reload.clicked.connect(self.reloaddataEM)
        self.reloaddataEM()
        
        
        #cargar nombre proyecot
        self.cargarnombreProyecto()
        
        # metodos relacionados a herramientas manuales
        self.reloaddataHM()
        self.bt_reload_2.clicked.connect(self.reloaddataHM)
        # metodos relacionados a consumibles
        self.bt_reload_3.clicked.connect(self.reloaddataC)
        self.reloaddataC()
        # metodos de Pedidos:
        self.btn_generarPedidos.clicked.connect( lambda:self.stackedWidget_pedidos.setCurrentWidget(self.page_generarPedidos) )
        self.btn_visualizarPedidos.clicked.connect(lambda:self.stackedWidget_pedidos.setCurrentWidget(self.page_VisualizaPedidos))
        self.btn_guardar_pedid.clicked.connect(self.agregar_pedido)
        self.btn_aggtblPedidos.clicked.connect(self.agregarprod_pedido)
        self.btn_buscarPedido.clicked.connect(self.buscar_pedido)
        self.btn_limpiarCampos_pedid.clicked.connect(self.limpiar_pedido)
        self.btn_editarPedido.clicked.connect(self.editar_pedido)
        self.btn_elimiarPedido_1.clicked.connect(self.eliminarPedido)
        self.tablapedidocrear.cellClicked.connect(self.llenar_lineeditsPDidos)
        # ver pedidos
        self.btn_bscrPedidos.clicked.connect(self.vertabla_pedido)
        # metodos de Salidas:
        self.btn_generarSalidas.clicked.connect( lambda:self.stackedWidget_salidas.setCurrentWidget(self.page_GenerarSalidas) )
        self.btn_visualizarSalidas.clicked.connect(lambda:self.stackedWidget_salidas.setCurrentWidget(self.page_Visualizar_salidas))
        self.bt_buscarsalida.clicked.connect(self.buscar_salida)
        self.btn_guardar_salida.clicked.connect(self.guardarResponsable_salida)
        self.btn_limpiarsalida.clicked.connect(self.limpiar_salida)
        self.btn_editarSalida.clicked.connect(self.editar_salida)
        self.btn_buscar_consumibles_salidas.clicked.connect(self.busquedacons_salida)
        self.btn_buscar_herr_salidas.clicked.connect(self.busquedaHM_salidas)
        #metodos de agregar y quitar salidas de equipos y maquinarias
        self.btn_buscar_equi_salidas.clicked.connect(self.busquedaEM_salidas)
        self.btn_eliminarEM_salida.clicked.connect(self.borrarSalida_EM)
        self.btn_guardarEMsalidas.clicked.connect(self.guardarSalida_EM)
        self.tableWidget_EM_salidas.cellClicked.connect(self.llenar_lineeditsEM_salidas)
        
        #busqueda principal
        self.btn_buscar.clicked.connect(self.busquedaprincipal)
        #filtrar Contenido Segun el estado
        self.btn_filtrarEstado.clicked.connect(self.filtrarporestado)
        #filtrar por cantidad baja cantidad en inventario
        self.btn_actualizarTablabajaExist.clicked.connect(self.filtrar_bajaCantidad)
    
    # Cargar configuracion global
    def cargarnombreProyecto(self):
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre_proyecto FROM configuracion_global")
            resultado = cursor.fetchone()

            if resultado is not None and resultado[0]:
                self.label_nombreProyecto.setText(resultado[0])
            else:
                self.label_nombreProyecto.setText("Registre el nombre del proyecto en los ajustes del programa")

        except sqlite3.Error as e:
            self.mostrar_error(f"Error en la conexión a la base de datos: {str(e)}")
        except Exception as e:
            self.mostrar_error(f"Error inesperado: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion:
                conexion.close()

    def mostrar_error(self, mensaje):
        QMessageBox.critical(self, "Error", mensaje)

    # abrir menu de gestion de usuarios 
    def verifyAdmin(self):
        if self.admin == "true":
            self.userView()
        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return
    def userView(self):
        Usuario = Users(admin=self.admin, widget=widget, user_name=self.user_name)
        widget.addWidget(Usuario)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    # abrir ventana de agregar al inventario    
    def geestInventView(self):
        GestionarInvent = gestionInventario(admin=self.admin, widget=widget, user_name=self.user_name)
        widget.addWidget(GestionarInvent)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
    # abrir ventana de respaldar base de datos 
    def bddView(self):
        if self.admin == "true":
            bddVentana = bddMenu(admin=self.admin, widget=widget, user_name=self.user_name)
            widget.addWidget(bddVentana)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return
        
    #abrir ventana de ajustes de inventario
    def ajustesView(self):
        if self.admin == "true":
            historial_cambio_inventario = ajustesInventario(admin=self.admin, widget=widget, user_name=self.user_name)
            widget.addWidget(historial_cambio_inventario)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return
              
        
    ### BUSQUEDA PRINCIPAL EN LA PAGINa GENERAL ###
    
    #buscar y mostrar resultados de la busqueda en una tabla en la seccion "General"
    def busquedaprincipal(self):
        busqueda = self.lineEdit_busqueda.text()
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            # Consultas a la base de datos
            cursor.execute("SELECT Codigo, Descripcion, Unidad_de_medida, Cantidad, Fecha_de_entrada, Llimite_de_reorden, Notas FROM consumibles WHERE Descripcion LIKE ?", ('%' + busqueda + '%',))
            data_consumibles = cursor.fetchall()

            cursor.execute("SELECT * FROM HerramientasManuales WHERE Descripcion LIKE ?", ('%' + busqueda + '%',))
            data_herramientas = cursor.fetchall()

            cursor.execute("SELECT * FROM EquiposyMaquinarias WHERE Descripcion LIKE ?", ('%' + busqueda + '%',))
            data_equipos = cursor.fetchall()

            # Combinar los resultados en una lista
            data_total = data_consumibles + data_herramientas + data_equipos

            # Configurar la tabla con los datos obtenidos
            self.tabla_resultados.setRowCount(len(data_total))

            for row, row_data in enumerate(data_total):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tabla_resultados.setItem(row, col, item)

            conexion.close()
        except Exception as e:
            # Mostrar un mensaje de error en caso de excepción
            QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}")
            
    #filtrar equipos y maquinarias & herramientas manuales en la tabla de la vista general
    def filtrarporestado(self):
        
        filtro = self.comboBox_filtroEstado.currentText()
        
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            
            # Consultas SQL parametrizadas para evitar inyección de SQL
            #print("Query Equipos:", query_equipos)
            query_equipos = "SELECT * FROM EquiposyMaquinarias WHERE Estado LIKE ? || '%'"
            cursor.execute(query_equipos, (filtro,))
            data_equipos = cursor.fetchall()

            query_herramientas = "SELECT * FROM HerramientasManuales WHERE Estado LIKE ? || '%'"
            cursor.execute(query_herramientas, (filtro,))
            data_herramientas = cursor.fetchall()
            
            # Establecer el número de filas y columnas en la tabla
            self.tableWidget_Estado_HM.setRowCount(len(data_herramientas))
            self.tableWidget_Estado_EM.setRowCount(len(data_equipos))
            
            # Llenar las tablas con los datos recuperados
            for row, row_data in enumerate(data_equipos):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_Estado_EM.setItem(row, col, item)
            for row, row_data in enumerate(data_herramientas):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_Estado_HM.setItem(row, col, item)
            conexion.close()
        except Exception as e:
            # Mostrar un mensaje de error en caso de excepción
            QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}")
    
    # filtrar consumibles con baja cantidad en almacen
    def filtrar_bajaCantidad(self):
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()

        query = """
        SELECT Codigo, Descripcion, Cantidad, Llimite_de_reorden, Fecha_de_entrada, Notas
        FROM consumibles
        WHERE Cantidad <= Llimite_de_reorden OR (Cantidad > Llimite_de_reorden - 5 AND Cantidad <= Llimite_de_reorden + 5);
        """

        cursor.execute(query)
        data_resultado = cursor.fetchall()
        conexion.close()

        # Actualizar la tabla con los resultados de la consulta
        self.tableWidget_bajacantidadStock.setRowCount(len(data_resultado))
        self.tableWidget_bajacantidadStock.setColumnCount(len(data_resultado[0]) if data_resultado else 0)

        for row, row_data in enumerate(data_resultado):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.tableWidget_bajacantidadStock.setItem(row, col, item)

                # Resaltar las celdas cuando la cantidad sea igual o menor al límite de reorden
                if col == 2:  # Columna de "Cantidad"
                    limite_reorden = row_data[3]  # Índice 3 es la columna de "Limite_de_reorden"
                    if value <= limite_reorden:
                        item.setBackground(QBrush(QColor(255, 0, 0)))  # Fondo rojo

  
    ### EQUIPOS Y MAQUINARIAS ###  
    #mostrar datos en la tabla de reportes de Equipos y maquinarias
    def reloaddataEM(self):
            try:
                conexion = sqlite3.connect("./database/db.db")
                cursor = conexion.cursor()
                cursor.execute("SELECT Codigo,Serial,Descripcion,Estado,Fecha_de_ingreso,Fecha_de_UltimoMantenimiento,Notas FROM EquiposyMaquinarias")
                data = cursor.fetchall()

                self.tablaEquiposyMaquinarias.setRowCount(len(data))  

                for row, row_data in enumerate(data):
                    for col, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value))
                        self.tablaEquiposyMaquinarias.setItem(row, col, item)

                conexion.close()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}")
    
    ### HERRAMIENTAS MANUALES ###   
    #mostrar datos en la tabla de herramientass manuales    
    def reloaddataHM(self):
            try:
                conexion = sqlite3.connect("./database/db.db")
                cursor = conexion.cursor()
                cursor.execute("SELECT * FROM HerramientasManuales")
                data = cursor.fetchall()

                self.tablaHerramientas.setRowCount(len(data))  

                for row, row_data in enumerate(data):
                    for col, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value))
                        self.tablaHerramientas.setItem(row, col, item)

                conexion.close()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}")
                
    ### CONSUMIBLES ###   
    # mostrar datos en la tabla de reportes de consumibles
    def reloaddataC(self):
            try:
                conexion = sqlite3.connect("./database/db.db")
                cursor = conexion.cursor()
                cursor.execute("SELECT Codigo,Descripcion,Unidad_de_medida,Cantidad,Fecha_de_entrada,Llimite_de_reorden,Notas FROM consumibles")
                data = cursor.fetchall()

                self.tablaConsumibles.setRowCount(len(data))  

                for row, row_data in enumerate(data):
                    for col, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value))
                        self.tablaConsumibles.setItem(row, col, item)
                        
                conexion.close()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}")
    
    ### PEDIDOS ###
   
    def eliminarPedido(self):
        nombrePedido = self.lineEdit_nombreP.text()
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM contenido_pedido WHERE nombre_producto=?",(nombrePedido,))
            conexion.commit()
            conexion.close()
            QMessageBox.information(self,"Eliminado","Ha sido elimindo correctamente")
            self.lineEdit_nombreP.clear()
            self.lineEdit_espsTecP.clear()
            self.lineEdit_espsTecP.clear()
            self.lineEdit_undmedP.clear()
            self.lineEdit_cantP.clear()
            self.lineEdit_necesP.clear()
            
        except:
            print ("Error al conectarse a SQLite")
    def llenar_lineeditsPDidos(self, row, col):
        # Obtener datos de la fila seleccionada
        Nombre = self.tablapedidocrear.item(row, 0).text()
        especificaciones = self.tablapedidocrear.item(row, 1).text()
        cantidad = self.tablapedidocrear.item(row, 2).text()
        UMedida = self.tablapedidocrear.item(row, 3).text()
      
        Necesidad= self.tablapedidocrear.item(row, 5).text()
        
        fech_entrada = self.tablapedidocrear.item(row, 4).text()
        fecha = QDate.fromString(fech_entrada, 'yyyy-MM-dd')
        self.calendarWidget.setSelectedDate(fecha)
        self.lineEdit_nombreP.setText(Nombre)
        self.lineEdit_espsTecP.setText(especificaciones)
        self.lineEdit_undmedP.setText(UMedida)
        self.lineEdit_cantP.setText(cantidad)
        self.lineEdit_necesP.setText(Necesidad)
    def editar_pedido(self):
        numeroPedido = self.lineEdit_numeroPedido.text()
        if not numeroPedido:
            QMessageBox.warning(self,'Error','No ha ingresado un número de pedido')
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            nombreProyecto = self.txtbx_nameproyectoPed.text()
            responsableProyecto = self.lineEdit_ResponsablePed.text()
          
          
          
            telefono = self.txtbx_telefonoresponsablePed.text()
            cursor.execute("UPDATE pedidos SET Nombre_Proyecto=?,Responsable_pedido=?,telefon_responsable=? WHERE numero_pedido=?",(nombreProyecto,responsableProyecto,telefono,numeroPedido))
            if cursor.execute:
                QMessageBox.information(self,"Datos actualizados","Los datos se actualizaron correctamente")
                
            conexion.commit()
            conexion.close()
    def limpiar_pedido(self):
        self.txtbx_nameproyectoPed.clear()
        self.lineEdit_ResponsablePed.clear()
        self.txtbx_telefonoresponsablePed.clear()
        self.lineEdit_numeroPedido.clear()
        self.btn_guardar_pedid.setEnabled(True)
        self.lineEdit_numeroPedido.setReadOnly(False)
    def buscar_pedido(self):
        NumeroPedido = self.lineEdit_busqueda_pedido.text()
        if not NumeroPedido:
            QMessageBox.information(self,"Error","Ingresa un numero de pedido")
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT numero_pedido,Nombre_Proyecto,Responsable_pedido,telefon_responsable FROM pedidos WHERE numero_pedido=?",(NumeroPedido,))
            resultado = cursor.fetchone()
            if resultado:
                self.txtbx_nameproyectoPed.setText(resultado[1])
                self.lineEdit_ResponsablePed.setText(resultado[2])
                self.txtbx_telefonoresponsablePed.setText(str(resultado[3]))
                self.lineEdit_numeroPedido.setText(str(resultado[0]))
                self.lineEdit_numeroPedido.setReadOnly(True)
                self.btn_guardar_pedid.setEnabled(False)
                self.cargar_pedido()
            if not resultado:
                QMessageBox.information(self,"Error","No hay pedido actual con ese numero ")
    def cargar_pedido(self):
        NumeroPedido = self.lineEdit_busqueda_pedido.text()
        if not NumeroPedido:
            QMessageBox.information(self,"Error","Ingresa un numero de pedido")
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre_producto,especificaciones_tecnicas,cantidad,unidad_de_medida,fecha_tope,necesidadPedido FROM contenido_pedido WHERE numero_pedido=? ",(NumeroPedido,))
            resultado = cursor.fetchall()
            print (resultado)
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
    def agregar_pedido(self):
        
        numerodepedido = self.lineEdit_numeroPedido.text()
        # Realizar una verificación para evitar registros duplicados
        if self.verificar_existencia_numeroPedido(numerodepedido):
            QMessageBox.warning(self, "Error", "Ya existe un registro con este código.")
            return

        # Resto del código para insertar el nuevo registro
        nombreproyecto = self.txt_descrip_HM.text()
        responsableretiro = self.txtbx_telefonoresponsablePed.text()
        telefonresponsable = self.comboBox_agg_HM.currentText()

        if (not numerodepedido
            or not nombreproyecto
            or not responsableretiro
            or not telefonresponsable
            ):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            query = "INSERT INTO pedidos (numero_pedido, Nombre_Proyecto, Responsable_pedido, telefon_responsable) VALUES (?, ?, ?, ?)"

            cursor.execute(query, (numerodepedido, nombreproyecto, responsableretiro, telefonresponsable))

            conexion.commit()
            QMessageBox.information(self, "Exito", "Los datos se almacenaron correctamente")           
    def verificar_existencia_numeroPedido(self, numerodepedido):
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            query = "SELECT COUNT(*) FROM pedidos WHERE numero_pedido = ?"
            cursor.execute(query, (numerodepedido,))
            count = cursor.fetchone()[0]
            conexion.close()
            return count > 0    
    def agregarprod_pedido(self):
        
        numerodepedido = self.lineEdit_numeroPedido.text()
        nonmbreProd = self.lineEdit_nombreP.text()
        espTecnicas= self.lineEdit_espsTecP.text()
        cantidad = self.lineEdit_cantP.text()
        unidadMEdida = self.lineEdit_undmedP.text()
        
        fecha_ingreso = self.calendarWidget.selectedDate()
        fecha_formato_cadena = fecha_ingreso.toString("yyyy-MM-dd")
        necesidadProducto = self.lineEdit_necesP.text()
        if (not numerodepedido or not nonmbreProd or not espTecnicas or not cantidad or not unidadMEdida or not fecha_formato_cadena or not necesidadProducto):
            QMessageBox .warning(self, "Error", "Todos los campos osn obligatorios")
            return
        else: 
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            query = "INSERT INTO contenido_pedido ( nombre_producto, especificaciones_tecnicas, cantidad, unidad_de_medida, fecha_tope, necesidadPedido,numero_pedido) VALUES (?,?,?,?,?,?,?)"
            
            cursor.execute(query, (nonmbreProd, espTecnicas, cantidad, unidadMEdida, fecha_formato_cadena, necesidadProducto, numerodepedido))
            conexion.commit()
            QMessageBox.information(self, "Exito", "Los datos se almacenaron correctamente")
      
      
    ##ver pedidos##
    def vertabla_pedido(self):
        NumeroPedido = self.lineEdit_busqueda_pedido_ver.text()
        if not NumeroPedido:
            QMessageBox.information(self, "Error", "Ingresa un número de pedido")
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()

        # Obtener datos del pedido
            cursor.execute("SELECT nombre_producto, especificaciones_tecnicas, cantidad, unidad_de_medida, fecha_tope, necesidadPedido FROM contenido_pedido WHERE numero_pedido=? ", (NumeroPedido,))
            resultado_contenido = cursor.fetchall()

            if resultado_contenido:
            # Configurar la tabla con los datos obtenidos
                self.tablapedidocrear.setRowCount(len(resultado_contenido))
                self.tablapedidocrear.setColumnCount(len(resultado_contenido[0]))
                headers_contenido = ["Nombre Producto", "Especificaciones Técnicas", "Cantidad", "Unidad de Medida", "Fecha Tope", "Necesidad de Pedido"]
                self.tablapedidocrear.setHorizontalHeaderLabels(headers_contenido)

                for row, row_data in enumerate(resultado_contenido):
                    for col, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value))
                        self.tablapedidocrear.setItem(row, col, item)

            # Obtener datos del pedidp
                cursor.execute("SELECT Nombre_Proyecto, Responsable_pedido, telefon_responsable FROM pedidos WHERE numero_pedido=?", (NumeroPedido,))
                resultado_pedido = cursor.fetchone()

                if resultado_pedido:
                    self.txtbx_nameproyecto_ver_pedido.setText(resultado_pedido[0])
                    self.lineEdit_Responsable_verPedido.setText(resultado_pedido[1])
                    self.txtbx_telefonoresponsable_VerPedido.setText(str(resultado_pedido[2]))
                    


            else:
                QMessageBox.information(self, "Error", "No hay contenido asociado a ese número de pedido")

            conexion.close()          
      
    ### SALIDAS ###
    
    #editar los datos del "encabezado" de las ssalidas, informacion de responsable de retiro
    def editar_salida(self):
        numeroSalida = self.txt_salidanumero.text()
        if not numeroSalida:
            QMessageBox.warning(self, "Error", "Ingrese el número de la salida")
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            nombreProyecto = self.txtbx_nameproyecto_3.text()
            responsableRetiro = self.lineEdit_Responsable_3.text()
            cedula = self.txtbx_cedula_Responsable.text()
            
            telefono = self.txtbx_telefonoresponsable_3.text()
            numeroRetiro = self.txt_salidanumero.text()
            cursor.execute("UPDATE SalidaResponsable SET Nombre_Responsable=?,Nombre_Proyecto=?,Telefono=?, Cedula=? WHERE Nro_retiro=?",(responsableRetiro,nombreProyecto,telefono,cedula,numeroRetiro))
            if cursor.execute:
                QMessageBox.information(self,"Datos actualizados","Los datos se actualizaron correctamente")
                
            conexion.commit()
            conexion.close()
    # metodo para limpiar los campos y tablas una vez terminados los registros
    def limpiar_salida(self):
        self.txtbx_nameproyecto_3.clear()
        self.lineEdit_Responsable_3.clear()
        self.txtbx_cedula_Responsable.clear()
        self.txt_salidanumero.clear()
        self.txtbx_telefonoresponsable_3.clear()
        self.btn_guardar_salida.setEnabled(True)
    # metodo para guardar informacion de los responsables del retiro de la salida y numero de salida
    def guardarResponsable_salida(self):
        nombreProyecto = self.txtbx_nameproyecto_3.text()
        responsableProyecto= self.lineEdit_Responsable_3.text()
        cedulaResponsable = self.txtbx_cedula_Responsable.text()
        telefonoResponsable = self.txtbx_telefonoresponsable_3.text()
        if not (nombreProyecto or 
                responsableProyecto or 
                cedulaResponsable or telefonoResponsable):
            QMessageBox.information(self, "Error", "Es necesario ingresar los datos")
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
           
            cursor.execute("INSERT INTO SalidaResponsable (Nombre_Responsable,Telefono,Cedula,Nombre_Proyecto) VALUES (?,?,?,?)",(responsableProyecto,telefonoResponsable,cedulaResponsable,nombreProyecto))
            #last_inserted_id = cursor.lastrowid
            conexion.commit()
            QMessageBox.information(self,"Almacenado correctamente","Los datos fueron guardados correctamente")
    # metodo para realizar la busqueda de una salida de acuerdo al numero de salida insertado ### por editar ###
    def buscar_salida(self):
        numeroSalida = self.lineEdit_busqueda_salida.text()
        if not numeroSalida:
            QMessageBox.information(self,"Error","Ingresa un numero de salida")
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT Nombre_Responsable,Telefono,Cedula,Nro_retiro,Nombre_Proyecto FROM SalidaResponsable WHERE Nro_retiro=?",(numeroSalida,))
            resultado = cursor.fetchone()
            if resultado:
                self.txtbx_nameproyecto_3.setText(resultado[4])
                self.lineEdit_Responsable_3.setText(resultado[0])
                self.txtbx_cedula_Responsable.setText(str(resultado[2]))
                self.txtbx_telefonoresponsable_3.setText(str(resultado[1]))
                self.txt_salidanumero.setText(str(resultado[3]))
               
                self.btn_guardar_salida.setEnabled(False)
            if not resultado:
                QMessageBox.information(self,"Error","No hay salida actual con ese numero ")
    # metodo para mostrar los datos en la tabla de herramientas en la seccion de salidas o retiros
    def busquedaHM_salidas(self):
        busqueda = self.txt_busqueda_herr_salidas.text()
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            # Consultas a la base de datos
            
            cursor.execute("SELECT * FROM HerramientasManuales WHERE Descripcion LIKE ?", ('%' + busqueda + '%',))
            data_herramientass = cursor.fetchall()

            # Combinar los resultados en una lista
            data_total = data_herramientass

            # Configurar la tabla con los datos obtenidos
            self.tableWidget_herr_salidas.setRowCount(len(data_total))
            
            for row, row_data in enumerate(data_total):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_herr_salidas.setItem(row, col, item)

            conexion.close()
        except Exception as e:
            # Mostrar un mensaje de error en caso de excepción
            QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}") 
    #metodo para mostrar los datos en la tabla de consumibles en la seccion de salidas o retiros
    def busquedacons_salida(self):
        busqueda = self.txt_busqueda_cons_salida.text()
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            # Consultas a la base de datos
            
            cursor.execute("SELECT * FROM consumibles WHERE Descripcion LIKE ?", ('%' + busqueda + '%',))
            data_consumibless = cursor.fetchall()

            # Combinar los resultados en una lista
            data_total = data_consumibless

            # Configurar la tabla con los datos obtenidos
            self.tableWidget_consumibles_salidas.setRowCount(len(data_total))

            for row, row_data in enumerate(data_total):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_consumibles_salidas.setItem(row, col, item)

            conexion.close()
        except Exception as e:
            # Mostrar un mensaje de error en caso de excepción
            QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}")
    # metodo para mostraar los datos en la tabla de equipos y maquinarias en la seccion de salidas
    def busquedaEM_salidas(self):
        busqueda = self.txt_busqueda_equiM_salidas.text()
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            # Consultas a la base de datos
            
            cursor.execute("SELECT * FROM EquiposyMaquinarias WHERE Descripcion LIKE ?", ('%' + busqueda + '%',))
            data_equipos = cursor.fetchall()

            # Combinar los resultados en una lista
            data_total = data_equipos

            # Configurar la tabla con los datos obtenidos
            self.tableWidget_EM_salidas.setRowCount(len(data_total))

            for row, row_data in enumerate(data_total):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_EM_salidas.setItem(row, col, item)

            conexion.close()
        except Exception as e:
            # Mostrar un mensaje de error en caso de excepción
            QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}"
                                )
    # metodo de llenar los lineedits con los datos de la celda de la tabla clickeada
    def llenar_lineeditsEM_salidas(self, row, col):
        # Obtener datos de la fila seleccionada
        codigo = self.tableWidget_EM_salidas.item(row, 0).text()
        placa = self.tableWidget_EM_salidas.item(row, 1).text()
        serial = self.tableWidget_EM_salidas.item(row, 2).text()
        descripcion = self.tableWidget_EM_salidas.item(row, 3).text()
        estado = self.tableWidget_EM_salidas.item(row, 4).text()
        # Llenar LineEdits con los datos
        self.txt_codigo_EM_salidas.setText(codigo)
        self.txt_placa_EM_salidas.setText(placa)
        self.txt_descrip_EM_salidas.setText(descripcion)
        self.txt_serial_EM_salidas.setText(serial)
        # Configurar el estado
        index = self.comboBox_aggEM_salidas.findText(estado)
        if index >= 0:
            self.comboBox_aggEM_salidas.setCurrentIndex(index)
            
        #self.btn_guardarEMsalidas.setEnabled(False)
        self.txt_codigo_EM_salidas.setReadOnly(True)
        self.txt_placa_EM_salidas.setReadOnly(True)
        self.txt_serial_EM_salidas.setReadOnly(True)
        self.txt_descrip_EM_salidas.setReadOnly(True)
    
    def guardarSalida_EM(self):
        codigo = self.txt_codigo_EM_salidas.text()

        # Resto del código para insertar el nuevo registro
        placa = self.txt_placa_EM_salidas.text()
        serial = self.txt_serial_EM_salidas.text()
        descripcion = self.txt_descrip_EM_salidas.toPlainText()
        estado = self.comboBox_aggEM_salidas.currentText()
        motivo = self.txt_motivo_salidasEM.text()
        nro_salida = self.txt_salidanumero.text()

        if (not nro_salida): QMessageBox.warning(self, "Error", "Debe registrar el responsable del retiro antes de continuar")
        
        if (not codigo
            or not placa
            or not serial
            or not descripcion
            or not estado 
            or not motivo
            ):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            
            cursor = conexion.cursor()
            
            query = "INSERT INTO salidas_maq (codigo, placa, serial, descripcion, estado, Motivo_s, Nrosalida) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (codigo, placa, serial, descripcion, estado, motivo, nro_salida ))
            conexion.commit()
            
            query_actualizar_disponibilidad = "UPDATE HerramientasManuales SET disponibilidad = 'En uso' WHERE codigo = ?"
            cursor.execute(query_actualizar_disponibilidad, (codigo,))
            conexion.commit()

            
            QMessageBox.information(self, "Exito", "Los datos se almacenaron correctamente")
            
            try:
                conexion = sqlite3.connect("./database/db.db")
                cursor = conexion.cursor()
                cursor.execute("SELECT codigo, placa, serial, descripcion, descripcion, estado, Motivo_s, Nrosalida FROM salidas_maq")
                data = cursor.fetchall()

                self.tableWidget_salidas_equipos_maq.setRowCount(len(data))  

                for row, row_data in enumerate(data):
                    for col, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value))
                        self.tableWidget_salidas_equipos_maq.setItem(row, col, item)

                conexion.close()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}")                 
        
    def borrarSalida_EM(self):
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
# otros métodos de la clase MenuPrincipal
    
    #volver al inicio
    def backLogin(self):
        ingreso_usuario.show()
        ingreso_usuario.txt_user.clear()
        ingreso_usuario.txt_password.clear()
        self.hide()

#### CLASE DE GESTION DE INVENTARIO ###
class gestionInventario(QtWidgets.QMainWindow):
    def __init__(self, admin, widget, user_name):
        super(gestionInventario, self).__init__()
        uic.loadUi("./ui/agginventario.ui", self)
        self.admin = admin
        self.user_name = user_name
        self.widget = widget
        self.setWindowTitle("Gestionar Inventario")
        self.btn_VolverMenu.clicked.connect(self.backMenu)
        self.bt_salir_2.clicked.connect(self.backLogin)
        # Cambio de paginas del stacked widget 
        self.btn_EM.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.page_equipos))
        self.btn_Herr.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.page_herramientas))
        self.btn_cons.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.page_consumibles))
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
    
    # volver al menu principal
    def backMenu(self):
        menuprincipal = MenuPrincipal(admin=self.admin, user_name=self.user_name)
        widget.addWidget(menuprincipal)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    #volver al inicio
    def backLogin(self):
        ingreso_usuario.show()
        ingreso_usuario.txt_user.clear()
        ingreso_usuario.txt_password.clear()
        self.hide()
    
    ### CONSUMIBLES ###
    
    # busca consumibles en la pagina de agregar consumibles
    def busquedacons(self):
        busqueda = self.lineEdit_busqueda_C.text()
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
            query = "INSERT INTO EquiposyMaquinarias (Codigo, Placa, Serial, Descripcion, Estado, Fecha_de_ingreso, Fecha_de_UltimoMantenimiento, Notas, Lapso_entre_mantenimiento, Disponibilidad) VALUES (?, ?, ?, ?, ?, ?, ?)"

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
        # (similar a tu función agregarEM pero utilizando una sentencia DELETE)
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()

        query = """
            DELETE FROM EquiposyMaquinarias
            WHERE Codigo = ?;
        """

        cursor.execute(query, (codigo,))

        conexion.commit()
        QMessageBox.information(self, "Exito", "Los datos se eliminaron correctamente")


#### CLASE DE GESTION DE USUARIOS ####
class Users(QtWidgets.QMainWindow):
    def __init__(self, admin, widget ,user_name):
        super(Users, self).__init__()
        uic.loadUi("./ui/usuarios.ui", self)
        self.admin = admin
        self.user_name = user_name
        self.widget = widget
        self.setWindowTitle("Gestion de Usuarios")
        self.btn_backmenu.clicked.connect(self.backMenu)
        self.btn_cerrarSesion_1.clicked.connect(self.backLogin)
        self.bt_buscarUsser.clicked.connect(self.busquedauser)
        self.btn_aggusser.clicked.connect(self.AggUser)
        self.btn_clear_inputs.clicked.connect(self.clearinputs1)
        self.btn_clear_inputs2.clicked.connect(self.clearinputs)
        self.bt_reload_user.clicked.connect(self.reloadUser)
        self.btn_deleteusser.clicked.connect(self.deleteuser)
        self.btn_editusser.clicked.connect(self.edituser)
        self.reloadUser()
        # otros métodos de la clase Users

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
    
    # funcion de limpiar los textbox
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
    # metodo de volver al menu principal    
    def backMenu(self):
        menuprincipal = MenuPrincipal(admin=self.admin, user_name=self.user_name)
        widget.addWidget(menuprincipal)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    # metodo de volver al login
    def backLogin(self):
        ingreso_usuario = IngresoUsuario()  
        ingreso_usuario.showMaximized()
        ingreso_usuario.txt_user.clear()
        ingreso_usuario.txt_password.clear()
        self.widget.setCurrentIndex(0)
        self.hide()


### CLASE DE MENU DE BASSE DE DATOS ###
class bddMenu(QtWidgets.QMainWindow):
    def __init__(self, admin, widget, user_name):
        super(bddMenu, self).__init__()
        uic.loadUi("./ui/bdd.ui", self)
        self.admin = admin
        self.user_name = user_name
        self.widget = widget
        self.btn_VolverMenu.clicked.connect(self.volver_menu)
        self.btn_gest_usuario.clicked.connect(self.verifyAdmin_user)
        self.bt_salir_2.clicked.connect(self.cerrarSesion)
        self.btn_limpiarbdd.clicked.connect(self.LimpiarBDD)
        self.btn_importar.clicked.connect(self.importar_base_datos)
        self.btn_respaldar.clicked.connect(self.exportarBDD)
        self.btn_ajustesInvent.clicked.connect(self.HistorialView)

    ### Exportar basse de datos ###
    def exportarBDD(self):
        try:
            # El usuario selecciona la carpeta de destino
            carpeta_destino = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Destino")

            if not carpeta_destino:
                return

            db_backup_path = f"{carpeta_destino}/db.db"

            conexion = sqlite3.connect("./database/db.db")

            # Cambiar la sección de copia de la base de datos
            shutil.copy2("./database/db.db", db_backup_path)

            consulta_tablas_sql = "SELECT name FROM sqlite_master WHERE type='table';"
            tablas = pd.read_sql_query(consulta_tablas_sql, conexion)["name"].tolist()

            estilo_pdf = TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (0, 0), 1, colors.black),
                ]
            )

            # Cambiar la orientación de las páginas a horizontal
            pdf_filename = f"{carpeta_destino}/exportacion_inventario.pdf"
            pdf = SimpleDocTemplate(pdf_filename, pagesize=(letter[1], letter[0]))

            story = []

            for tabla in tablas:
                consulta_sql = f"SELECT * FROM {tabla}"
                df = pd.read_sql_query(consulta_sql, conexion)

                # Convertir todos los datos a Unicode antes de pasarlos a la tabla PDF
                data = [
                    [str(cell) for cell in row]
                    for row in [df.columns.tolist()] + df.values.tolist()
                ]

                tabla_pdf = Table(data)
                tabla_pdf.setStyle(estilo_pdf)
                story.append(tabla_pdf)

            pdf.build(story)

            self.mostrar_mensaje(
                f"Base de datos y tablas exportadas a:\n{db_backup_path} y {pdf_filename}"
            )

        except sqlite3.Error as e:
            self.mostrar_error(f"Error en la conexión a la base de datos: {str(e)}")
        except pd.errors.EmptyDataError:
            self.mostrar_error("Error: La base de datos está vacía.")
        except Exception as e:
            self.mostrar_error(f"Error inesperado: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion:
                conexion.close()
    def mostrar_mensaje(self, mensaje):
        QMessageBox.information(self, "Éxito", mensaje)
    def mostrar_error(self, mensaje):
        QMessageBox.critical(self, "Error", mensaje)
        
    ### Importar datos de la base de datos copia (respaldo) ###
    def importar_base_datos(self):
        # Abrir el cuadro de diálogo para seleccionar la base de datos a importar
        ruta_importar, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Base de Datos",
            "",
            "SQLite Database Files (*.db *.sqlite *.db3)",
        )

        if not ruta_importar:
            # Si el usuario cierra el cuadro de diálogo, salir de la función
            return

        # Ruta de destino de la base de datos
        ruta_destino = "db.db"

        try:
            # Cerrar conexiones a la base de datos si es necesario
            # (Asegúrate de adaptar esto según cómo manejes las conexiones en tu código)

            # Esperar un breve período antes de intentar eliminar o reemplazar
            time.sleep(2)  # Ajusta el tiempo según sea necesario

            # Crear una copia temporal de la base de datos
            ruta_temporal = "db_temp.db"
            copyfile(ruta_importar, ruta_temporal)

            # Reemplazar la base de datos existente con la copia temporal
            os.replace(ruta_temporal, ruta_destino)

            # Mostrar un mensaje de éxito
            self.mostrar_mensaje(f"Base de datos importada desde:\n{ruta_importar}")
        except Exception as e:
            # Mostrar un mensaje de error si ocurre un problema
            self.mostrar_mensaje(f"Error al importar la base de datos:\n{str(e)}")

    def mostrar_mensaje(self, mensaje):
        # Mostrar un cuadro de mensaje con la información proporcionada
        QMessageBox.information(self, "Éxito", mensaje)
        
    # limpiar las tablas en la base de datos.
    def LimpiarBDD(self):
        # Mostrar el diálogo de confirmación de contraseña
        dialogo_contraseña = DialogoContraseña(parent=self)
        if dialogo_contraseña.exec_() == QDialog.Accepted:
            # Contraseña correcta, proceder con la limpieza de la base de datos
            if self.admin == "true":
                try:
                    conexion = sqlite3.connect("./database/db.db")
                    cursor = conexion.cursor()
                    # Aquí realizas las consultas para borrar la información de las tablas
                    cursor.execute("DELETE FROM EquiposyMaquinarias;")
                    cursor.execute("DELETE FROM HerramientasManuales;")
                    cursor.execute("DELETE FROM consumibles;")
                    cursor.execute("DELETE FROM configuracion_global;")
                    cursor.execute("DELETE FROM pedidos;")
                    cursor.execute("DELETE FROM contenido_pedido;")
                    conexion.commit()
                    conexion.close()
                    QMessageBox.information(self, "Limpieza Exitosa", "Base de datos limpia exitosamente.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error al limpiar la base de datos:\n{str(e)}")
            else:
                QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
        else:
            # Contraseña incorrecta o diálogo cerrado
            QMessageBox.warning(self, "Operación Cancelada", "La limpieza de la base de datos fue cancelada.")

    # cerrar sesion
    def cerrarSesion(self):
        ingreso_usuario.show()
        ingreso_usuario.txt_user.clear()
        ingreso_usuario.txt_password.clear()
        self.hide()
        
    # abrir ventana de gestion de usuarios    
    def verifyAdmin_user(self):
        if self.admin == "true":
            Usuario = Users(admin=self.admin, widget=widget, user_name=self.user_name)
            widget.addWidget(Usuario)
            widget.setCurrentIndex(widget.currentIndex() + 1)
         
        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return
        
    # volver al menu principal
    def volver_menu(self):
        menuprincipal = MenuPrincipal(admin=self.admin, user_name=self.user_name)
        widget.addWidget(menuprincipal)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    # abrir ventana de ajustes de inventario si es admin
    def HistorialView(self):
        if self.admin == "true":
            historial_cambio_inventario = ajustesInventario(admin=self.admin, widget=widget, user_name=self.user_name)
            widget.addWidget(historial_cambio_inventario)
            widget.setCurrentIndex(widget.currentIndex() + 1)
         
        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return
    
    
        
# Implementa un diálogo para la fuuncion de limpiar tablas de la bdd en la clase de base de datos en la ventana de opciones avanzada
class DialogoContraseña(QDialog):
    def __init__(self, parent=None):
        super(DialogoContraseña, self).__init__(parent)
        self.setWindowTitle("Confirmar Contraseña")
        layout = QVBoxLayout()
        self.label_contraseña = QLabel("Si desea eliminar la informacion del inventario \n Ingrese su contraseña:")
        self.txt_contraseña = QLineEdit(self)
        self.txt_contraseña.setEchoMode(QLineEdit.Password)
        self.btn_aceptar = QPushButton("Aceptar", self)
        self.btn_aceptar.clicked.connect(self.accept)
        self.btn_cancelar = QPushButton("Cancelar", self)
        self.btn_cancelar.clicked.connect(self.reject)
        layout.addWidget(self.label_contraseña)
        layout.addWidget(self.txt_contraseña)
        layout.addWidget(self.btn_aceptar)
        layout.addWidget(self.btn_cancelar)
        self.setLayout(layout)
 
 
###    CLASE DE AJUSTES DEL PROGRAMA Y HISTORIAL DE CAMBIOS
class ajustesInventario(QtWidgets.QMainWindow):
    def __init__(self, admin, widget, user_name):
        super(ajustesInventario, self).__init__()
        uic.loadUi("./ui/Historial_cambios.ui", self)
        self.admin = admin
        self.user_name = user_name
        self.widget = widget
        #volver al menu
        self.btn_VolverMenu.clicked.connect(self.volvermenup)
        self.btn_gest_usuario.clicked.connect(self.abrirMenu_gestUsuario)
        self.btn_bddRespaldo.clicked.connect(self.abrirmenu_BDD)
        self.btn_guardar.clicked.connect(self.guardarProyecto)
        #self.btn_guardar.clicked.connect(self.guardar_config)
        # self.btn_recargardataConfig.clicked.connect(self.reloadDataConfig)
    
    # metodo de guardar configuración
    #def guardar_config(self):
        
    # metodo de recargar los datos dde configuracion
    #def reloadDataConfig(self):
           
    # metodo de volver al menu principal
    def guardarProyecto(self):
        nombre =self.lineEdit_nameproyecto.text()
        gerente = self.lineEdit_nameGerente.text()
        ingenieroREsidente = self.lineEdit_IngenieroResidente.text()
        if not (nombre or gerente or ingenieroREsidente):
            QMessageBox.information(self,"Error","Los datos son obligatorios")
            return
        
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO configuracion_global (nombre_proyecto,Encargado_proyecto,Ingeniero_Residente) VALUES (?,?,?)",(nombre,gerente, ingenieroREsidente))
        conexion.commit()
        QMessageBox.information(self,"Guardado","El proyecto fue almacenado correctamente")
        if cursor.execute:
            cursor.execute("SELECT nombre_proyecto,Encargado_proyecto,Ingeniero_Residente FROM configuracion_global WHERE nombre_proyecto=?",(nombre,))
            resultado = cursor.fetchone()
            self.label_Name_proyecto.setText(resultado[0])
            self.label_Gerente.setText(resultado[1])
            self.label_IngenieroResidente.setText(resultado[2])
    
    # volver al menu principal    
    def volvermenup(self):
        menuprincipal = MenuPrincipal(admin=self.admin, user_name=self.user_name)
        widget.addWidget(menuprincipal)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
    # abrir ventana de ajustes de inventario si es admin
    def abrirMenu_gestUsuario(self):
        if self.admin == "true":
            Menu_gestionUsers = Users(admin=self.admin, widget=widget, user_name=self.user_name)
            widget.addWidget(Menu_gestionUsers)
            widget.setCurrentIndex(widget.currentIndex() + 1)
         
        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return
        
    # abrir ventana de opciones avanzadas( base de datos)
    def abrirmenu_BDD(self):
        if self.admin == "true":
            Menu_BDD = bddMenu(admin=self.admin, widget=widget, user_name=self.user_name)
            widget.addWidget(Menu_BDD)
            widget.setCurrentIndex(widget.currentIndex() + 1)
         
        else:
            QMessageBox.information(self, "Permiso Denegado", "No tienes permisos de administrador")
            return
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    app.setApplicationName("Manejo de Inventario") 
    ingreso_usuario = IngresoUsuario()
    widget.addWidget(ingreso_usuario)
    widget.show()

    sys.exit(app.exec_())