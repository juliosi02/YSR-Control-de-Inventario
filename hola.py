import json

# Función para guardar los datos de acceso en un archivo
def guardar_datos_acceso(usuario, contrasena):
    datos_acceso = {"usuario": usuario, "contrasena": contrasena}
    with open("datos_acceso.json", "w") as archivo:
        json.dump(datos_acceso, archivo)

# Función para cargar los datos de acceso desde un archivo
def cargar_datos_acceso():
    try:
        with open("datos_acceso.json", "r") as archivo:
            datos_acceso = json.load(archivo)
            return datos_acceso["usuario"], datos_acceso["contrasena"]
    except FileNotFoundError:
        return None, None

# Ejemplo de uso
def main():
    usuario, contrasena = cargar_datos_acceso()

    if usuario and contrasena:
        print(f"¡Hola {usuario}! Has iniciado sesión automáticamente.")
    else:
        print("No se encontraron datos de acceso almacenados.")

    # Simular un inicio de sesión
    nuevo_usuario = input("Ingrese su nombre de usuario: ")
    nueva_contrasena = input("Ingrese su contraseña: ")

    # Guardar los datos de acceso
    guardar_datos_acceso(nuevo_usuario, nueva_contrasena)
    print("Datos de acceso guardados exitosamente.")

if __name__ == "__main__":
    main()
