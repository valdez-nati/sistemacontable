from flask import Flask, request
from flask_mysqldb import MySQL

db= MySQL()


def insertar():
    nombre = request.form['nombre']
    apellido= request.form['apellido']
    ruc = request.form['ruc']
    razon = request.form['razon']
    mycursor = db.connection.cursor() #para asegurar la coneccion y el cierre se usa .connection
    sql = "INSERT INTO clientes (nombre, apellido, razonsocial, ruc) VALUES (%s, %s, %s, %s)"
    val = (nombre,apellido,razon, ruc)
    mycursor.execute(sql, val,)
    db.connection.commit()
    mycursor.close()

def actualizar():
    nombre = request.form['nombre']
    apellido= request.form['apellido']
    ruc = request.form['ruc']
    razon = request.form['razon']

    mycursor = db.connection.cursor() #para asegurar la coneccion y el cierre se usa .connection
    sql = "UPDATE clientes SET nombre=%s, apellido=%s, razonsocial=%s, ruc=%s WHERE ruc=%s"
    val = (nombre,apellido, razon, ruc)
    mycursor.execute(sql, val,)
    db.connection.commit()
    mycursor.close()

def borrar():
    ruc = request.form['ruc']
    mycursor = db.connection.cursor() #para asegurar la coneccion y el cierre se usa .connection
    sql = "DELETE clientes WHERE ruc = %s"
    val = (ruc)
    mycursor.execute(sql, val,)
    db.connection.commit()
    mycursor.close()