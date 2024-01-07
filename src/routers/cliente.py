from flask import Flask, request
from flask_mysqldb import MySQL
import json
db= MySQL()


def insertar(user):
    nombre = request.form['nombre']
    apellido= request.form['apellido']
    ruc = request.form['ruc']
    correo = request.form['correo']
    razon = request.form['razon']
    mycursor = db.connection.cursor() #para asegurar la coneccion y el cierre se usa .connection
    sql = "INSERT INTO clientes (nombres, apellidos, razonsocial, correo, ruc) VALUES (%s, %s, %s, %s, %s)"
    val = (nombre,apellido,razon,correo, ruc)
    mycursor.execute(sql, val,)
    db.connection.commit()
    
    
    audit_log = {
    'table_name': 'clientes',
  
    'action': 'INSERT',
    'user': user,
     'changed_data': json.dumps({
        'nombre': nombre,
        'apellido': apellido  
    }) 
    }
  
    insert_query = """INSERT INTO audit_log (table_name,  action, user, changed_data)
                 VALUES (%(table_name)s,  %(action)s, %(user)s, %(changed_data)s);"""

    mycursor.execute(insert_query, audit_log)
    db.connection.commit()
    
    mycursor.close()

def actualizar(user):
    idcliente = request.form['idcliente']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    ruc = request.form['ruc']
    correo = request.form['correo']
    razon = request.form['razon']

    mycursor = db.connection.cursor()
    sql = "UPDATE clientes SET nombres=%s, apellidos=%s, razonsocial=%s, correo=%s, ruc=%s WHERE idcliente=%s"
    val = (nombre, apellido, razon, correo, ruc, idcliente)
    mycursor.execute(sql, val)
    db.connection.commit()
    
    audit_log = {
    'table_name': 'clientes',
  
    'action': 'UPDATE',
    'user': user,
    'changed_data': json.dumps({
        'nombre': nombre,
        'apellido': apellido  
    }) 
    }
    
  
    insert_query = """INSERT INTO audit_log (table_name,  action, user, changed_data)
                 VALUES (%(table_name)s, %(action)s, %(user)s, %(changed_data)s);"""

    mycursor.execute(insert_query, audit_log)
    db.connection.commit()
    mycursor.close()


