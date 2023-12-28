import os
from flask import Flask, render_template, request, redirect, url_for, flash,jsonify,session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
from config import config
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect
import pandas as pd
from datetime import datetime

#Modelos
from models.ModelUser import ModelUser
from models.entities.User import User


from routers.cliente import actualizar, insertar



app = Flask(__name__, static_folder='static', template_folder='templates')


csrf= CSRFProtect(app)
app.secret_key = config
db= MySQL(app)
login_manager_app= LoginManager(app)


@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db,id)

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    #consulta = db.query("INSERT INTO operaciones tipo=% ", "login")
    if request.method== 'POST':
        #print(request.form['username'])
        #print(request.form['password'])
        user = User(0, request.form['username'], request.form['contraseña'])
        logeado = ModelUser.login(db, user)
        if logeado != None:
            if logeado.contraseña:
                login_user(logeado)
                #consulta = ("UPDATE operaciones set res= %, datosIngresados=% ", "acceso exitoso", user)
                return redirect(url_for('home'))
            else:
                flash("Contraseña invalida...")
                return render_template('auth/login.html')

        else:
            flash("Usuario no encontrado...")
            return render_template('auth/login.html')

    else:
        return render_template('auth/login.html')
 
    
    

        


def status_401(error):
    return redirect(url_for('login')), 401

def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404

# Pagina principal
@app.route('/home')
@login_required
def home():
    mycursor = db.connection.cursor()
    sql = "SELECT * FROM clientes"
    mycursor.execute(sql)
    data = mycursor.fetchall()
    mycursor.close()


    return render_template('home.html', data=data )

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return response
    
# @app.errorhandler(401)  
# def unauthorized(error):
#     return redirect(url_for('login'))    

@app.errorhandler(401)  
def unauthorized(e):
    return redirect(url_for('login'), code=307)

    
# Insertar borrar y actualizar clientes
@app.route('/nuevocliente', methods=['GET', 'POST'])
@login_required
def nuevocliente():   
    if request.method == 'POST': #para que inserte en la base de datos cuando trae informacion
        insertar()
        flash("Guardado con exito...")
        return redirect(url_for('home'))   


@app.route("/editarcliente",methods= ['POST', 'GET'])# tiene que llamarse igual la funcion y la url/
@login_required
def editarcliente():
    if request.method == 'POST':
        actualizar()
        flash("Actualizado con exito...")
        return redirect(url_for('home'))

@app.route("/borrarcliente/<string:ruc>", methods=['GET'])
@login_required
def borrarcliente(ruc):
    flash("Cliente eliminado")
    mycursor = db.connection.cursor() #para asegurar la coneccion y el cierre se usa .connection
    mycursor.execute( "DELETE FROM clientes WHERE ruc= %s",(ruc,))
    db.connection.commit()
    mycursor.close()
    return redirect(url_for('home'))
    
# ---------Carga de los asientos---------------

@app.route("/cargar/")
@login_required
def fact():
    idcliente = request.args.get('idcliente')
    
    
    session['idcliente'] = idcliente
    mycursor = db.connection.cursor()
    sql = "SELECT idplancuenta, descripcion FROM plancuentas WHERE imputable=1"
    mycursor.execute(sql)
    data = mycursor.fetchall()
    mycursor.close()
    # Consulta para obtener los años únicos asociados al cliente
    mycursor = db.connection.cursor()
    sql_years = "SELECT DISTINCT YEAR(fecha) AS year FROM asientoregistro WHERE clientefk = %s"
    mycursor.execute(sql_years, (idcliente,))
    years_data = mycursor.fetchall()
    
    # Obtén la lista de años desde los resultados
    list = [year[0] for year in years_data]

    
    
    mycursor.close()
    
    
    
    
    return render_template('cargar_diario.html', idcliente=idcliente, data=data,list=list)

    
# @app.route("/cargar_diario/",methods= ['POST', 'GET'])
# @login_required
# def cargar_diario():
#     try:
#         mycursor = db.connection.cursor()
#         sql = "SELECT idplancuenta, descripcion FROM plancuentas WHERE imputable=1"
#         mycursor.execute(sql)
#         data = mycursor.fetchall()
#         mycursor.close()
     

#         if request.method == 'POST':
#             fecha = request.form.get("fecha")
#             descripcion = request.form.get("descripcion")
#             importe = request.form.get("importe")
#             tipo = request.form.get("tipo")
#             cuentas = request.form.get("cuentas")
            
#             idcliente = session.get('idcliente')
#             mycursor = db.connection.cursor()
#             query = "SELECT idregistro, fecha, numeroasiento, descripcion FROM asientoregistro WHERE clientefk = %s ORDER BY numeroasiento DESC LIMIT 1"
#             mycursor.execute(query, (idcliente,))z

#             resultado = mycursor.fetchone()

#             if resultado :
#                 idasiento= resultado[0]
#                 date = resultado[1]
#                 numeroasiento_bd = resultado[2]
#                 definicion = resultado[3]
                
#                 año = date.year
#                 print("Fecha de base de datos:",año)    
#                 if año != fecha:
#                     numeroasiento = 1
#                 else:
                 
#                     if descripcion != definicion:
#                         numeroasiento = numeroasiento_bd + 1
#                     else:
#                         numeroasiento = numeroasiento_bd
            
#             else:
#                 numeroasiento = resultado[2]
#                 descripcion = resultado[3]
            
            
#             print("Fecha",fecha)
#             print("Numero de asiento:",numeroasiento)
#             print("Descripcion:",descripcion)
#             print("Importe:",importe)
#             print("Tipo:",tipo)
#             print("Cuenta:",cuentas)
            
#             print("CLIENTE:",idcliente)
#             if tipo == "debe":
#                     debe = importe
#                     haber = 0
#             else:
#                 if tipo == "haber":
#                     debe = 0
#                     haber = importe
                    
#             print("Debe:",debe,"","Haber:",haber)
            
#             if descripcion != definicion:   
                
#                 sql = "INSERT INTO asientoregistro (fecha,numeroasiento,descripcion,clientefk) VALUES (%s, %s, %s, %s)"
#                 val = (fecha,numeroasiento,descripcion,idcliente)
#                 mycursor.execute(sql, val,)
#                 db.connection.commit()
                
#                 idasiento = mycursor.lastrowid
            
#             mycursor = db.connection.cursor()
#             sql2=  "INSERT INTO asientodetalle (debe,haber,plancuentasfk,asientoregistrofk) VALUES (%s, %s, %s, %s)"
#             val2 = (debe,haber,cuentas,idasiento)
#             mycursor.execute(sql2, val2,)
#             db.connection.commit()
#             mycursor.close()
#         else:
            
#             print("Error: Request method is not POST")
#             return render_template('cargar_diario.html', idcliente=session['idcliente'], data=data)
            
            

#         return render_template('cargar_diario.html',idcliente=session['idcliente'],data=data,descripcion=descripcion, numeroasiento=numeroasiento)



#     except Exception as e:
#         # En caso de error, puedes imprimir o manejar el error de alguna manera
#         print(f"Error: {str(e)}")
#         return jsonify({'success': False, 'error': str(e)})



@app.route("/cargar_diario/",methods= ['POST', 'GET'])
@login_required
def cargar_diario():
    try:
        mycursor = db.connection.cursor()
        sql = "SELECT idplancuenta, descripcion FROM plancuentas WHERE imputable=1"
        mycursor.execute(sql)
        data = mycursor.fetchall()
        mycursor.close()
     
        
        if request.method == 'POST':
            fecha = request.form.get("fecha")
            descripcion = request.form.get("descripcion")
            importe = request.form.get("importe")
            tipo = request.form.get("tipo")
            cuentas = request.form.get("cuentas")
            #para poder sacar el año de la fecha            
            fechaform= datetime.strptime(fecha, "%Y-%m-%d")
            print("Convertio:", fechaform.year)
            añoform= fechaform.year
            idcliente = session.get('idcliente')
            mycursor = db.connection.cursor()
            definicion = None
            query = "SELECT idregistro, fecha, numeroasiento, descripcion FROM asientoregistro WHERE clientefk = %s AND YEAR (fecha)=%s ORDER BY numeroasiento DESC LIMIT 1"
            try:
                mycursor.execute(query, (idcliente,añoform, ))
                
                resultado = mycursor.fetchone()
                print("Consulta ultimo registro",resultado)
            except Exception as e:
                        print("Error executing query:", e)
            finally:
                    mycursor.close()
            if resultado:
                idasiento = resultado[0]
                date = resultado[1]
                numeroasiento_bd = resultado[2]
                definicion = resultado[3]
                print("Definicion",definicion)
                año = date.year
                print("Fecha de base de datos:",año)    
                print("Numero de base de datos:",numeroasiento_bd)
                if año != añoform :
                    print("Se quedo aca....")
            
                    mycursor = db.connection.cursor()
                    query = """
                            SELECT
                                ad.plancuentasfk,
                                ar.clientefk,
                                SUM(ad.debe) AS totaldebe,
                                SUM(ad.haber) AS totalhaber
                            FROM 
                                asientodetalle ad
                            JOIN
                                asientoregistro ar ON ad.asientoregistrofk = ar.idregistro
                            WHERE
                                ar.clientefk = %s AND YEAR(ar.fecha)  = %s 
                            GROUP BY
                                ad.plancuentasfk, ar.clientefk;
                            """

                    try:
                        mycursor.execute(query, (idcliente, año,))
                        resultados = mycursor.fetchall()
                        print("Consulta de totales", resultados)
                    except Exception as e:
                        print("Error executing query:", e)
                    finally:
                        mycursor.close()
                    try:
                        for row in resultados:
                            plancuentasfk, clientefk, totaldebe, totalhaber = row
                            print("Para insertar:",row) 
                            mycursor = db.connection.cursor()
                            query1= "INSERT INTO mayor (plancuentasfk, clientefk, totaldebe, totalhaber, periodo) VALUES (%s, %s, %s, %s,%s)"
                            res = (plancuentasfk, clientefk, totaldebe, totalhaber,año)
                            mycursor.execute(query1, res,)
                            db.connection.commit()
                
                        print("resutaldos:",resultados[0], resultados[1])
                    except Exception as e:
                        # Handle any exceptions
                        print("Error during insertion:", e)

                    finally:
                        # Close the cursor
                        mycursor.close()
                    numeroasiento = 1
                else:
                    if descripcion != definicion:
                        print("Entro para sumar")
                        numeroasiento = numeroasiento_bd + 1
                    else:
                        print("numero de asiento igual")
                        numeroasiento = numeroasiento_bd

                        
                        
                        
                        
                        
            else:
                idasiento = 1
                numeroasiento = 1
                

            print("Fecha",fecha)
            print("Numero de asiento:",numeroasiento)
            print("Descripcion:",descripcion)
            print("Importe:",importe)
            print("Tipo:",tipo)
            print("Cuenta:",cuentas)
            
            print("CLIENTE:",idcliente)
            if tipo == "debe":
                debe = importe
                haber = 0
            else:
                if tipo == "haber":
                    debe = 0
                    haber = importe
                            
            print("Debe:",debe,"","Haber:",haber)
            
            if (descripcion != definicion) or  (idasiento ==1 and definicion is None):   
                mycursor = db.connection.cursor()
                sql = "INSERT INTO asientoregistro (fecha,numeroasiento,descripcion,clientefk) VALUES (%s, %s, %s, %s)"
                val = (fecha,numeroasiento,descripcion,idcliente)
                mycursor.execute(sql, val,)
                db.connection.commit()
                
                idasiento = mycursor.lastrowid
            
            mycursor = db.connection.cursor()
            sql2=  "INSERT INTO asientodetalle (debe,haber,plancuentasfk,asientoregistrofk) VALUES (%s, %s, %s, %s)"
            val2 = (debe,haber,cuentas,idasiento)
            mycursor.execute(sql2, val2,)
            db.connection.commit()
            mycursor.close()

            return render_template('cargar_diario.html',idcliente=session['idcliente'],data=data,descripcion=descripcion, numeroasiento=numeroasiento)



        #return render_template('cargar_diario.html')
    except Exception as e:
        # En caso de error, puedes imprimir o manejar el error de alguna manera
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/exportar_diario')
@login_required
def exportar_excel():
    try:
        idcliente = session.get('idcliente')
        mycursor = db.connection.cursor()
        sql = "SELECT  descripcion FROM asientoregistro WHERE clientefk = %s"
        mycursor.execute(sql, (idcliente,))
        data = mycursor.fetchall()
        df = pd.DataFrame(data)
        carpeta_destino = 'C:/Users/Naty/OneDrive/Documentos'

        ruta_archivo = os.path.join(carpeta_destino, 'descripcion.xlsx')

        df.to_excel(ruta_archivo, index=False)
        print("Directorio de trabajo actual:", os.getcwd())

        flash("Excel generado con éxito...")
        return redirect(url_for('home'))
    except Exception as e:
        # En caso de error, puedes imprimir o manejar el error de alguna manera
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

            
@app.route("/obtener_compra/",methods= ['POST', 'GET'])# tiene que llamarse igual la funcion y la url/
@login_required
def obtener_compra():
    try:

        #trae el json del javascript
        data = request.get_json()
        # el json por separado
        idcliente = data.get('idcliente')
        total10 = data.get('total10')
        total5 = data.get('total5')
        totalIVA = data.get('totalIVA')
        montoExento= data.get('montoExento')
        montoGravado10 = data.get('montoGravado10')
        montoGravado5 = data.get('montoGravado5')
        totalComprobante= data.get('totalComprobante')
      
        # print("ID Cliente:", idcliente)
        # print("Tototal10:", total10)
        # print("Total5:", total5)
        # print("Gravado5:", montoGravado5)
        # print("Gravado10:", montoGravado10)
        # print("Exento:", montoExento)

        # print("Total IVA:",totalIVA)
        # print("TOTAL:", totalComprobante)
        
        
        session['datos_compra'] = {
            'idcliente': idcliente,
            'total10': total10,
            'total5': total5,
            'totalIVA': totalIVA,
            'montoExento': montoExento,
            'montoGravado10': montoGravado10,
            'montoGravado5': montoGravado5,
            'totalComprobante': totalComprobante
        }
        return redirect(url_for('cargar_compra'))


   
       # return jsonify({'success': True})

    except Exception as e:
        # En caso de error, puedes imprimir o manejar el error de alguna manera
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

            
            
            
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    

    app.run()