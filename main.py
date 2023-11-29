import sys
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QBrush, QColor
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
import sqlite3


# Clase Login 
class IngresoUsuario(QtWidgets.QMainWindow):
    def __init__(self):
        super(IngresoUsuario, self).__init__()
        uic.loadUi("./ui/login.ui", self)
        self.btn_acceder.clicked.connect(self.ingreso)
        self.showMaximized()
        

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
        uic.loadUi("./ui/menuprincipal.ui", self)
        self.admin = admin
        self.user_name = user_name
        self.bt_salir.clicked.connect(self.backLogin)
        self.bt_config_usser.clicked.connect(self.verifyAdmin)
        
        #metodos relacionados a equipos y maquinarias
        self.bt_reload.clicked.connect(self.reloaddataEM)
        self.reloaddataEM()
        self.btn_edit_EM.clicked.connect(self.editar_em)
        self.btn_delete_EM.clicked.connect(self.eliminar_em)
        self.btn_agg_EM.clicked.connect(self.agregarEM)
        self.btn_buscarEMagg.clicked.connect(self.busquedaEM)
        self.tableWidget_aggEM.cellClicked.connect(self.llenar_lineeditsEM)
        self.btn_limpiarEMagg.clicked.connect(self.limpiarEM)
        
        #metodos relacionados a herramientas manuales
        self.btn_buscarHM.clicked.connect(self.busquedaHM)
        self.btn_aggHM.clicked.connect(self.agregagrHM)
        self.bt_reload_2.clicked.connect(self.reloaddataHM)
        self.tableWidget_aggHM.cellClicked.connect(self.llenar_lineeditsHM)
        self.btn_editHM.clicked.connect(self.editar_hm)
        self.btn_limpiarHM.clicked.connect(self.limpiarHM)
        self.btn_deleteHM.clicked.connect(self.deleteHM)
        self.reloaddataHM()
        
        #metodos relacionados a consumibles
        self.bt_reload_3.clicked.connect(self.reloaddataC)
        self.reloaddataC()
        self.btn_buscar_ConsAgg.clicked.connect(self.busquedacons)
        self.btn_agg_ConsAgg.clicked.connect(self.agregagrCons)
        self.btn_edit_ConsAgg.clicked.connect(self.editarCons)
        self.btn_delete_ConsAgg.clicked.connect(self.deleteCons)
        self.btn_limpiar_ConsAgg.clicked.connect(self.limpiarCons)
        self.tableWidget_AggCons.cellClicked.connect(self.llenar_lineeditsCons)
        
        #metodos de Pedidos:
        self.btn_guardar_pedid.clicked.connect(self.agregar_pedido)
        self.btn_aggtblPedidos.clicked.connect(self.agregarprod_pedido)
        
        #busqueda principal
        self.btn_buscar.clicked.connect(self.busquedaprincipal)
        #filtrar Contenido Segun el estado
        self.btn_filtrarEstado.clicked.connect(self.filtrarporestado)
        self.filtrarporestado()
        #filtrar por cantidad baja cantidad en inventario
        self.btn_actualizarTablabajaExist.clicked.connect(self.filtrar_bajaCantidad)
       
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
            self.tabla_resultados.setColumnCount(7)

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
            
            data_total = data_herramientas + data_equipos
            
            # Establecer el número de filas y columnas en la tabla
            self.tableWidget_Estado_EM_HM.setRowCount(len(data_total))
            self.tableWidget_Estado_EM_HM.setColumnCount(7)
            
            # Llenar la tabla con los datos recuperados
            for row, row_data in enumerate(data_total):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_Estado_EM_HM.setItem(row, col, item)
            print("Data Equipos:", data_equipos)
            print("Data Herramientas:", data_herramientas)
            print("Data Total:", data_total)
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
            self.tableWidget_aggEM.setColumnCount(7)

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
        # Realizar una verificación para evitar registros duplicados
        if self.verificar_existencia_codigo(codigo):
            QMessageBox.warning(self, "Error", "Ya existe un registro con este código.")
            return

        # Resto del código para insertar el nuevo registro
        serial = self.txt_serial_EM_2.text()
        descripcion = self.txt_descrip_EM_2.text()
        notas = self.txt_notas_EM_2.text()
        fech_ult_mant = self.dateEdit_aggEM.date().toString(Qt.ISODate)
        fech_entr = self.dateEdit_aggEMultMant.date().toString(Qt.ISODate)
        estado = self.comboBox_aggEM.currentText()

        if (not codigo
            or not serial
            or not descripcion
            or not notas
            or not fech_ult_mant
            or not fech_entr
            or not estado
            ):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            query = "INSERT INTO EquiposyMaquinarias (Codigo, Serial, Descripcion, Estado, Fecha_de_ingreso, Fecha_de_UltimoMantenimiento, Notas) VALUES (?, ?, ?, ?, ?, ?, ?)"

            cursor.execute(query, (codigo, serial, descripcion, estado, fech_entr, fech_ult_mant, notas))

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
        serial = self.tableWidget_aggEM.item(row, 1).text()
        descripcion = self.tableWidget_aggEM.item(row, 2).text()
        estado = self.tableWidget_aggEM.item(row, 3).text()
        fech_entr = self.tableWidget_aggEM.item(row, 4).text()
        fech_ult_mant = self.tableWidget_aggEM.item(row, 5).text()
        notas = self.tableWidget_aggEM.item(row, 6).text()

        # Llenar LineEdits con los datos
        self.txt_codigo_EM_2.setText(codigo)
        self.txt_serial_EM_2.setText(serial)
        self.txt_descrip_EM_2.setText(descripcion)
        self.txt_notas_EM_2.setText(notas)

        # Configurar las fechas y el estado
        self.dateEdit_aggEM.setDate(QDate.fromString(fech_ult_mant, Qt.ISODate))
        self.dateEdit_aggEMultMant.setDate(QDate.fromString(fech_entr, Qt.ISODate))
        index = self.comboBox_aggEM.findText(estado)
        if index >= 0:
            self.comboBox_aggEM.setCurrentIndex(index)
        self.btn_agg_EM.setEnabled(False)
        self.txt_codigo_EM_2.setReadOnly(True)
            
    #limpiar los lineedits y entradas de datos
    def limpiarEM(self):
        self.txt_codigo_EM_2.clear()
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
        serial = self.txt_serial_EM_2.text()
        descripcion = self.txt_descrip_EM_2.text()
        notas = self.txt_notas_EM_2.text()
        fech_ult_mant = self.dateEdit_aggEM.date().toString(Qt.ISODate)
        fech_entr = self.dateEdit_aggEMultMant.date().toString(Qt.ISODate)
        estado = self.comboBox_aggEM.currentText()

    # Realizar la actualización en la base de datos usando los valores obtenidos
        conexion = sqlite3.connect("./database/db.db")
        cursor = conexion.cursor()
        query = """
        UPDATE EquiposyMaquinarias
        SET
            Codigo = ?,
            Serial = ?,
            Descripcion = ?,
            Estado = ?,
            Fecha_de_ingreso = ?,
            Fecha_de_UltimoMantenimiento = ?,
            Notas = ?
        WHERE Codigo = ?;
        """

        cursor.execute(query, (codigo, serial, descripcion, estado, fech_entr, fech_ult_mant, notas, codigo_original))

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
        codigo = self.txt_codigo_HM.text()
    # Realizar una verificación para evitar registros duplicados
        if self.verificar_existencia_codigo_hm(codigo):
            QMessageBox.warning(self, "Error", "Ya existe un registro con este código.")
            return

    # Resto del código para insertar el nuevo registro
        descripcion = self.txt_descrip_HM.text()
        cantidad = self.txt_cant_HM.text()
        estado = self.comboBox_agg_HM.currentText()
        notas = self.txt_Notas_aggHM.text()

        if (not codigo
            or not descripcion
            or not cantidad
            or not estado
            or not notas
            ):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        else:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            query = "INSERT INTO HerramientasManuales (Codigo, Descripcion, Cantidad, Estado, Notas) VALUES (?, ?, ?, ?, ?)"

            cursor.execute(query, (codigo, descripcion, cantidad, estado, notas))

            conexion.commit()
            QMessageBox.information(self, "Exito", "Los datos se almacenaron correctamente")

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
        notas = self.tableWidget_aggHM.item(row, 4).text()
        # Llenar LineEdits con los datos
        self.txt_codigo_HM.setText(codigo)
        self.txt_cant_HM.setText(cantidad)
        self.txt_descrip_HM.setText(descripcion)
        self.txt_Notas_aggHM.setText(notas)
        # Configurar las fechas y el estado
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
        notas = self.txt_Notas_aggHM.text()
    
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
            Notas = ?
        WHERE Codigo = ?;
        """

        cursor.execute(query, (codigo, descripcion, cantidad, estado, notas, codigo))

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
            self.tableWidget_AggCons.setColumnCount(7)

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
        # Realizar una verificación para evitar registros duplicados
        if self.verificar_existencia_codigo_consumibles(codigo):
            QMessageBox.warning(self, "Error", "Ya existe un registro con este código.")
            return

        # Resto del código para insertar el nuevo registro
        descripcion = self.txt_descrip_consAgg.text()
        uni_medida = self.txt_uni_medConsagg.text()
        cantidad = self.txt_cant_ConsAgg.text()
        fech_entrada = self.dateEdit_fechEConsAGG.date().toString(Qt.ISODate)
        limite_reorden = self.txt_limite_reorden_AGgCons.text()
        notas = self.txtbox_notasAggCons.text()

        if (not codigo
            or not descripcion
            or not uni_medida
            or not cantidad
            or not fech_entrada
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

            cursor.execute(query, (codigo, descripcion, uni_medida, cantidad, fech_entrada, limite_reorden, notas))

            conexion.commit()
            QMessageBox.information(self, "Exito", "Los datos se almacenaron correctamente")
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
        fech_entrada= self.tableWidget_AggCons.item(row, 4).text()
        limite_reorden = self.tableWidget_AggCons.item(row, 5).text()
        notas = self.tableWidget_AggCons.item(row, 6).text()

        # Llenar LineEdits con los datos
        self.txt_codigo_consAgg.setText(codigo)
        self.txt_descrip_consAgg.setText(descripcion)
        self.txt_uni_medConsagg.setText(uni_medida)
        self.txt_cant_ConsAgg.setText(cantidad)
        self.txt_limite_reorden_AGgCons.setText(limite_reorden)
        self.txtbox_notasAggCons.setText(notas)
        self.dateEdit_fechEConsAGG.setDate(QDate.fromString(fech_entrada, Qt.ISODate))
        self.btn_agg_ConsAgg.setEnabled(False)
        self.txt_codigo_consAgg.setReadOnly(True)
    
    
    #editar y eliminar consumibles
    def editarCons(self):
        # Obtener los valores de los LineEdits
        codigo = self.txt_codigo_consAgg.text()
        descripcion = self.txt_descrip_consAgg.text()
        uni_medida = self.txt_uni_medConsagg.text()
        cantidad = self.txt_cant_ConsAgg.text()
        fech_entrada = self.dateEdit_fechEConsAGG.date().toString(Qt.ISODate)
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

        cursor.execute(query, (codigo, descripcion, uni_medida, cantidad, fech_entrada, limite_reorden, notas, codigo))

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
        self.btn_agg_ConsAgg.setEnabled(True)
        self.txt_codigo_consAgg.setReadOnly(False)
    
    ### PEDIDOS ###
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
        numerodepedido = self.lineEdit_nombreP.text()
        nonmbreProd = self.lineEdit_nombreP.text()
        espTecnicas= self.lineEdit_espsTecP.text()
        cantidad = self.lineEdit_cantP.text()
        unidadMEdida = self.lineEdit_undmedP.text()
        fechaTope= self.lineEdit_fechtP.text()
        necesidadProducto = self.lineEdit_necesP.text()
        if (not numerodepedido or not nonmbreProd or not espTecnicas or not cantidad or not unidadMEdida or not fechaTope or not necesidadProducto):
            QMessageBox .warning(self, "Error", "Todos los campos osn obligatorios")
            return
        else: 
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            query = "INSERT INTO contenido_pedido ( nombre_producto, especificaciones_tecnicas, cantidad, unidad_de_medida, fecha_tope, necesidad_del_pedido, numero_pedido) VALUES (?,?,?,?,?,?,?)"
            
            cursor.execute(query, (nonmbreProd, espTecnicas, cantidad, unidadMEdida, fechaTope, necesidadProducto, numerodepedido))
            conexion.commit()
            QMessageBox.information(self, "Exito", "Los datos se almacenaron correctamente")
        
    #METODOS DE LA CLASE DE MENU PRINCIPAL
    
    #volver al inicio
    def backLogin(self):
        ingreso_usuario = IngresoUsuario()  # Crear una instancia de IngresoUsuario
        ingreso_usuario.showMaximized()
        ingreso_usuario.txt_user.clear()
        ingreso_usuario.txt_password.clear()
        self.widget.setCurrentIndex(0)
        self.hide()
    # otros métodos de la clase MenuPrincipal
    
# clase Configuracionn de usuarios
class Users(QtWidgets.QMainWindow):
    def __init__(self, admin, widget ,user_name):
        super(Users, self).__init__()
        uic.loadUi("./ui/usuarios.ui", self)
        self.admin = admin
        
        self.user_name = user_name
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
        ingreso_usuario = IngresoUsuario()  # Crear una instancia de IngresoUsuario
        ingreso_usuario.showMaximized()
        ingreso_usuario.txt_user.clear()
        ingreso_usuario.txt_password.clear()
        self.widget.setCurrentIndex(0)
        self.hide()

        
   
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    
    ingreso_usuario = IngresoUsuario()
    widget.addWidget(ingreso_usuario)
    widget.show()

    sys.exit(app.exec_())
   
      