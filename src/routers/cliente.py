from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from config import DevelopmentConfig
from flask_mysqldb import MySQL

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')


@clientes_bp.route('/nuevocliente', methods=['GET', 'POST'])
@login_required
def nuevocliente():   
    if request.method == 'POST': #para que inserte en la base de datos cuando trae informacion
        nombre = request.form['nombre']
        apellido= request.form['apellido']
        ruc = request.form['ruc']
        razon = request.form['razon']
        db = MySQL(current_app)
  
        mycursor = db.connection.cursor() #para asegurar la coneccion y el cierre se usa .connection
        sql = "INSERT INTO clientes (nombres, apellidos, razonsocial, ruc) VALUES (%s, %s, %s, %s)"
        val = (nombre,apellido,razon, ruc)
        mycursor.execute(sql, val,)
        db.connection.commit()
        mycursor.close()        
        flash("Guardado con exito...")
    return redirect(url_for('home')) 
    
    
    
    
    
       
@clientes_bp.route("/editarcliente", methods= ['POST', 'GET'])# tiene que lamarse igual la funcion y la url/
@login_required
def editarcliente():
    if request.method == 'POST':
       
       
        idcliente = request.form['idcliente']
        nombre = request.form['nombre']
        apellido= request.form['apellido']
        ruc = request.form['ruc']
        razon = request.form['razon']
        
        db = MySQL(current_app)
        mycursor = db.connection.cursor() #para asegurar la coneccion y el cierre se usa .connection
        sql = "UPDATE clientes SET nombres=%s, apellidos=%s, razonsocial=%s, ruc=%s WHERE idcliente=%s"
        val = (nombre,apellido, razon, ruc, idcliente)
        mycursor.execute(sql, val)
        db.connection.commit()
        mycursor.close()
        flash("Actualizado con exito...")
        return redirect(url_for('home'))
    
@clientes_bp.route("/borrarcliente/<string:ruc>", methods=['GET'])
@login_required
def borrarcliente(ruc):
    flash("Cliente eliminado")
    mycursor = db.connection.cursor() #para asegurar la coneccion y el cierre se usa .connection
    mycursor.execute( "DELETE FROM clientes WHERE ruc= %s",(ruc,))
    db = MySQL(current_app)
    db.connection.commit()
    #mycursor.close()
    return redirect(url_for('home'))


