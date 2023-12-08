from weasyprint import HTML
import os
import base64
import sqlite3
from datetime import datetime

def recuperar_datos_bd():
    conexion = sqlite3.connect("./database/db.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT Codigo,Descripcion,Unidad_de_medida,Cantidad,Fecha_de_entrada,Llimite_de_reorden,Notas FROM consumibles")
    datos_base = cursor.fetchall()
    cursor.close()
    return datos_base
    
def crearPdf(ruta_salida):
    fecha_actual = datetime.now()
    fecha_formateada = fecha_actual.strftime("%Y-%m-%d")
    if fecha_formateada:
       
        datos_base = recuperar_datos_bd()
        html =f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
          </head>
            <body>
            <style>
            
            table{{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td{{
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }}
            th{{
                 background-color: #f2f2f2;
            }}
            h2{{
                text-align:center;
            
            }}
            </style>
            <h2>Inventario</h2>
            <table>
                    <thead>
                        <tr>
                            <th>Codigo</th>
                            <th>Descripción</th>
                            <th>Unidad de Medida</th>
                            <th>Cantidad</th>
                            <th>Fecha de Entrada</th>
                            <th>Límite de Reorden</th>
                            <th>Notas</th>
                        </tr>
                    </thead>
                    <tbody>
                       
                       """
        for dato in datos_base:
            html += "<tr>"
            for valor in dato:
                html += f"<td>{valor}</td>"
            html += "</tr>"

            # Cerrar la estructura HTML
        html += """
                       
                    </tbody>
                </table>
            
            
             </body>
             
    </html>
        
        """
    HTML(string=html).write_pdf(ruta_salida)
    
if __name__ =="__main__":
    ruta_salida = './hola.pdf'
    crearPdf(ruta_salida=ruta_salida)
    
    