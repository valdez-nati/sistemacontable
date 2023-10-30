from flask import Flask, request, redirect, url_for, flash, Blueprint
from flask_mysqldb import MySQL
from app import db

c = Blueprint('c', __name__, static_folder='static', template_folder='templates')

@c.route('/nuevocliente', methods=['GET', 'POST'])
def nuevocliente():   
    if request.method == 'POST': #para que inserte en la base de datos cuando trae informacion
        nombre = request.form['nombre']
        apellido= request.form['apellido']
        ruc = request.form['ruc']
        razon = request.form['razon']
  
        mycursor = db.connection.cursor() #para asegurar la coneccion y el cierre se usa .connection
        sql = "INSERT INTO clientes (nombres, apellidos, razonsocial, ruc) VALUES (%s, %s, %s, %s)"
        val = (nombre,apellido,razon, ruc)
        mycursor.execute(sql, val,)
        db.connection.commit()
        mycursor.close()        
        flash("Guardado con exito...")
    return redirect(url_for('home')) 
    
    
    
    
    
       
@c.route("/editarcliente", methods= ['POST', 'GET'])# tiene que lamarse igual la funcion y la url/
def editarcliente():
    if request.method == 'POST':
       
       
        idcliente = request.form['idcliente']
        nombre = request.form['nombre']
        apellido= request.form['apellido']
        ruc = request.form['ruc']
        razon = request.form['razon']
        
        
        mycursor = db.connection.cursor() #para asegurar la coneccion y el cierre se usa .connection
        sql = "UPDATE clientes SET nombres=%s, apellidos=%s, razonsocial=%s, ruc=%s WHERE idcliente=%s"
        val = (nombre,apellido, razon, ruc, idcliente)
        mycursor.execute(sql, val)
        db.connection.commit()
        mycursor.close()
        flash("Actualizado con exito...")
        return redirect(url_for('home'))
    
@c.route("/borrarcliente/<string:ruc>", methods=['GET'])
def borrarcliente(ruc):
    flash("Cliente eliminado")
    mycursor = db.connection.cursor() #para asegurar la coneccion y el cierre se usa .connection
    mycursor.execute( "DELETE FROM clientes WHERE ruc= %s",(ruc,))
    db.connection.commit()
    #mycursor.close()
    return redirect(url_for('home'))


