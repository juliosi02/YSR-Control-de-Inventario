import sys
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QDate
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
import sqlite3

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
        self.btn_edit_2.clicked.connect(self.editar_em)
        self.btn_delete_2.clicked.connect(self.eliminar_em)
        self.btn_agg_2.clicked.connect(self.agregarEM)
        self.btn_buscar_2.clicked.connect(self.busquedaEM)
        self.tableWidget_3.cellClicked.connect(self.llenar_lineeditsEM)
        self.btn_limpiar4.clicked.connect(self.limpiarEM)
        #metodos relacionados a herramientas manuales
        self.bt_reload_2.clicked.connect(self.reloaddataHM)
        self.reloaddataHM()
        
        #metodos relacionados a consumibles
        self.bt_reload_3.clicked.connect(self.reloaddataC)
        self.reloaddataC()
        
        #busqueda principal
        self.btn_buscar.clicked.connect(self.busquedaprincipal)
        x
       
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
        
    ### BUSQUEDA PRINCIPAL EN LA PAGIAN GENERAL ###
    
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
            self.tableWidget_3.setRowCount(len(data_total))
            self.tableWidget_3.setColumnCount(7)

            for row, row_data in enumerate(data_total):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_3.setItem(row, col, item)

            conexion.close()
        except Exception as e:
            # Mostrar un mensaje de error en caso de excepción
            QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}") 
            
    #agregar equipos y maquinarias en la tabla de ingresos                  
    def agregarEM(self):
        
        codigo = self.txt_codigo_EM_2.text()
        serial = self.txt_serial_EM_2.text()
        descripcion = self.txt_descrip_EM_2.text()
        notas = self.txt_notas_EM_2.text()
        # Captura las fechas de los QDateEdit
        fech_ult_mant = self.dateEdit_2.date().toString(Qt.ISODate)
        fech_entr = self.dateEdit_3.date().toString(Qt.ISODate)
        # Captura el estado de la QComboBox
        estado = self.comboBox_3.currentText()
        
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
            QMessageBox.information(self,"Exito","Los datos se almacenaron correctamente")
    
    #llenar los lineedits de acuerdo a los datos seleccionados en la tabla
    def llenar_lineeditsEM(self, row, col):
        # Obtener datos de la fila seleccionada
        codigo = self.tableWidget_3.item(row, 0).text()
        serial = self.tableWidget_3.item(row, 1).text()
        descripcion = self.tableWidget_3.item(row, 2).text()
        estado = self.tableWidget_3.item(row, 3).text()
        fech_entr = self.tableWidget_3.item(row, 4).text()
        fech_ult_mant = self.tableWidget_3.item(row, 5).text()
        notas = self.tableWidget_3.item(row, 6).text()

        # Llenar LineEdits con los datos
        self.txt_codigo_EM_2.setText(codigo)
        self.txt_serial_EM_2.setText(serial)
        self.txt_descrip_EM_2.setText(descripcion)
        self.txt_notas_EM_2.setText(notas)

        # Configurar las fechas y el estado
        self.dateEdit_2.setDate(QDate.fromString(fech_ult_mant, Qt.ISODate))
        self.dateEdit_3.setDate(QDate.fromString(fech_entr, Qt.ISODate))
        index = self.comboBox_3.findText(estado)
        if index >= 0:
            self.comboBox_3.setCurrentIndex(index)
            self.btn_agg_2.setEnabled(False)
            self.txt_codigo_EM_2.setReadOnly(True)
            
    #limpiar los lineedits y entradas de datos
    def limpiarEM(self):
        self.txt_codigo_EM_2.clear()
        self.txt_serial_EM_2.clear()
        self.txt_descrip_EM_2.clear()
        self.txt_notas_EM_2.clear()
        self.btn_agg_2.setEnabled(True)
        self.txt_codigo_EM_2.setReadOnly(False)
    
    #editar los equipos y maquinarias
    def editar_em(self):
        # Obtener los valores de los LineEdits
        codigo = self.txt_codigo_EM_2.text()
        
        serial = self.txt_serial_EM_2.text()
        descripcion = self.txt_descrip_EM_2.text()
        notas = self.txt_notas_EM_2.text()
        fech_ult_mant = self.dateEdit_2.date().toString(Qt.ISODate)
        fech_entr = self.dateEdit_3.date().toString(Qt.ISODate)
        estado = self.comboBox_3.currentText()
        
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

        cursor.execute(query, (codigo, serial, descripcion, estado, fech_entr, fech_ult_mant, notas, codigo))

        conexion.commit()
        QMessageBox.information(self,"Exito","Los datos se actualizaron correctamente")
    
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
    
    def busquedaHM(self):
        busqueda = self.lineEdit_busqueda_HM.text()
        try:
            conexion = sqlite3.connect("./database/db.db")
            cursor = conexion.cursor()
            # Consultas a la base de datos
            
            cursor.execute("SELECT * FROM  WHERE Descripcion LIKE ?", ('%' + busqueda + '%',))
            data_equipos = cursor.fetchall()

            # Combinar los resultados en una lista
            data_total = data_equipos

            # Configurar la tabla con los datos obtenidos
            self.tableWidget_3.setRowCount(len(data_total))
            self.tableWidget_3.setColumnCount(7)

            for row, row_data in enumerate(data_total):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_3.setItem(row, col, item)

            conexion.close()
        except Exception as e:
            # Mostrar un mensaje de error en caso de excepción
            QMessageBox.warning(self, "Error", f"Error al recuperar datos: {str(e)}") 
            

    ### cONSUMIBLES ###
    
    #mostrar datos en la tabla de reportes de consumibles
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
    
    #volver al inicio
    def backLogin(self):
        ingreso_usuario = self.widget.widget(0)
        ingreso_usuario.txt_user.clear()
        ingreso_usuario.txt_password.clear()
        ingreso_usuario.showMaximized()
        self.widget.setCurrentIndex(0)
        self.hide()
    # otros métodos de la clase MenuPrincipal
    
# clase Configuracionn de usuarios
class Users(QtWidgets.QMainWindow):
    def __init__(self, admin, widget,user_name):
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
        ingreso_usuario = self.widget.widget(0)
        ingreso_usuario.txt_user.clear()
        ingreso_usuario.txt_password.clear()
        ingreso_usuario.showMaximized()
        self.widget.setCurrentIndex(0)
        self.hide()
        
   
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    
    ingreso_usuario = IngresoUsuario()
    widget.addWidget(ingreso_usuario)
    widget.show()

    sys.exit(app.exec_())
   
      