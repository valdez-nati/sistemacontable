
from flask import Flask, render_template, request, redirect, url_for, flash,jsonify,session,make_response, send_file,request
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
from config import config
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect
import pandas as pd
from openpyxl.styles import Alignment

from datetime import datetime
import json
import os
import openpyxl
from xlsxwriter import Workbook
from io import BytesIO  
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
        user = User(0, request.form['username'], request.form['contraseña'], idrol=0)
        logeado = ModelUser.login(db, user)
        if logeado != None:
            user.idrol = logeado.idrol 
            insert_audit_log(request.form['username'], 'ÉXITO')
            session['user'] = request.form['username']
            if logeado.contraseña:
                login_user(logeado)
                session['idrol'] = user.idrol 
        
                #consulta = ("UPDATE operaciones set res= %, datosIngresados=% ", "acceso exitoso", user)
                return redirect(url_for('home'))
            else:
                flash("Contraseña invalida...")
                return render_template('auth/login.html')

        else:
            insert_audit_log(request.form['username'], 'FALLIDO')
            flash("Usuario no encontrado...")
            return render_template('auth/login.html')

    else:
        return render_template('auth/login.html')
 
    

def insert_audit_log(username, status):
    mycursor = db.connection.cursor()
    query = "INSERT INTO login_audit_log (user, status) VALUES (%s, %s)"
    values = (username, status)
    
    mycursor.execute(query, values)
    db.connection.commit()
    mycursor.close()    


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
    idrol = session.get('idrol')
    id=idrol
    return render_template('home.html', data=data, id=id )

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
        
        idrol = session.get('user')
        user=idrol
        insertar(user)
        flash("Guardado con exito...")
        return redirect(url_for('home'))   


@app.route("/editarcliente",methods= ['POST', 'GET'])# tiene que llamarse igual la funcion y la url/
@login_required
def editarcliente():
    if request.method == 'POST':
        
        idrol = session.get('user')
        user=idrol
        actualizar(user)
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

@app.route('/guardar-idcliente', methods=['GET'])
@login_required
def guardar_idcliente():
    try:
        idcliente = request.args.get('idcliente')
        print("trae el id", idcliente) 

        session['idcliente'] = idcliente

        return 'ok'
    except Exception as e:
        print(f"Error: {e}")
        return 'Error en el servidor', 500  




@app.route("/cargar_diario",methods= ['POST', 'GET'])
@login_required
def cargar_diario():
    try:
        fecha = request.form.get('fecha')
        descripcion = request.form.get('descripcion')
        
        idcliente = session.get('idcliente')
        print("cliente", idcliente)
        mycursor = db.connection.cursor()
        último_año = "SELECT MAX(YEAR(fecha)) FROM asientoregistro WHERE clientefk=%s"
        mycursor.execute(último_año, (idcliente,))
        año_permitido = mycursor.fetchone()[0]
        mycursor.close()
        if request.method == 'POST':
            fecha = request.form.get("fecha")
            session['fecha'] = fecha
            descripcion = request.form.get("descripcion")
            session['descripcion'] = descripcion
            print("desctripcion",descripcion)
            importe = request.form.get("importe")
            descripcion_ultima = ""
            tipo = request.form.get("tipo")
            cuentas = request.form.get("cuentas")
            #para poder sacar el año de la fecha            
            fechaform= datetime.strptime(fecha, "%Y-%m-%d")
            print("Convertio:", fechaform.year)
            añoform= fechaform.year
            print("tipo",tipo)
            asiento = 0  
            print("año formu")
            idrol = session.get('idrol')
            id=idrol
            print("rol",id)
            try:
                mycursor = db.connection.cursor()
                último_asiento = "SELECT numeroasiento, descripcion FROM asientoregistro WHERE clientefk=%s AND YEAR(fecha)=%s ORDER BY idregistro DESC LIMIT 1"
                mycursor.execute(último_asiento, (idcliente, añoform))
                último = mycursor.fetchone()
                
               
            
            except Exception as e:
                print("Error executing the query:", e)
            print("ultimo:",último)
            print("descripcion ultima:",descripcion_ultima)
            print("año permitido",año_permitido)
            if año_permitido is not None  :
                print("entro en el if de año permitido")
                if último is not None: 
                    print("entro en el if de ultimo ")
                    if añoform == año_permitido or id==1 : 
                       
                            descripcion_ultima = último[1]

                            if descripcion != descripcion_ultima:
                                # Incrementar número
                                print("Entro para sumar")
                                mycursor = db.connection.cursor()
                                siguiente_asiento = "SELECT MAX(numeroasiento) + 1 FROM asientoregistro WHERE clientefk=%s AND YEAR(fecha)=%s;" 
                                
                            else: 
                                # Mantener mismo número
                                print("numero de asiento igual")
                                mycursor = db.connection.cursor()
                                siguiente_asiento = "SELECT MAX(numeroasiento) FROM asientoregistro WHERE clientefk=%s AND YEAR(fecha)=%s;"
                                
                            # Ejecutar consulta para obtener número siguiente
                            mycursor.execute(siguiente_asiento, (idcliente, añoform))
                            numeroasiento = mycursor.fetchone()[0]
                         
                    else:
                        # Mensaje de error 
                        flash("No puede insertar para ese año")
                        return redirect(url_for('cargar_diario'))         
                else:
                    print("inserta en periodo")
                    sql = "INSERT INTO periodos (periodo,clientefk) VALUES (%s, %s)"
                    val = (añoform,idcliente)
                    mycursor.execute(sql, val,)
                    db.connection.commit()
                        
                    
                    numeroasiento = 1
            
            else:
                print("si entro en el sino")
              
                
                idasiento = 1
                numeroasiento = 1
            
            if tipo == "debe":
                print("entro en el debe")
                debe = importe
                haber = 0
            else:
                if tipo == "haber":
                    print("entro en el haber")

                    debe = 0
                    haber = importe

            print("Fecha",fecha,"Numero de asiento:",numeroasiento)
            print("Descripcion:",descripcion,"Importe:",importe)
            print("Tipo:",tipo,"Cuenta:",cuentas)
            print("CLIENTE:",idcliente)
          
                            
            print("Debe:",debe,"","Haber:",haber)
            if ( descripcion_ultima is None or descripcion != descripcion_ultima): 
            #antes de insertar obtener el ultimo asientoregistro y insertar en el mayor
                print("entro en el if de descripcion")
                
                sql = "INSERT INTO asientoregistro (fecha,numeroasiento,descripcion,clientefk,periodofk) VALUES (%s,%s, %s, %s, %s)"
                val = (fecha,numeroasiento,descripcion,idcliente,añoform)
                mycursor.execute(sql, val,)
                db.connection.commit()
                
                print("numeroasiento inserttado:",numeroasiento)
                session['numeroasiento'] = numeroasiento
                
                idasiento = mycursor.lastrowid
                print("asiento2:",idasiento)
                session['idasiento'] = idasiento
                
                query = """
                        SELECT idregistro
                        FROM asientoregistro 
                        WHERE clientefk =  %s AND YEAR(fecha)= %s
                        ORDER BY numeroasiento DESC LIMIT 1
                        """
                mycursor.execute(query, (idcliente, añoform, ))
            try:
                mycursor = db.connection.cursor()
                sql_id= "SELECT idregistro FROM asientoregistro WHERE clientefk = %s AND YEAR(fecha) = %s ORDER BY idregistro DESC LIMIT 1;"
                mycursor.execute(sql_id, (idcliente, añoform))
                idregistro= mycursor.fetchone()
            
            except Exception as e:
                print("Error executing the query:", e)
            
            print("Idregistro:",idregistro)
                
                
            if asiento==1  :
                idasiento = session.get('idasiento')
            else:
                if idregistro is not None:
                    idasiento=idregistro[0]
                else  :
                    idasiento=1
            print ("insertado asiento:",idasiento)
            mycursor = db.connection.cursor()
            sql2=  "INSERT INTO asientodetalle (debe,haber,plancuentasfk,asientoregistrofk) VALUES (%s, %s, %s, %s)"
            val2 = (debe,haber,cuentas,idasiento)
            mycursor.execute(sql2, val2,)
            db.connection.commit()
            mycursor.close()
        mycursor = db.connection.cursor()
        sql = "SELECT idplancuenta, codigo, descripcion FROM plancuentas WHERE imputable=1"
        mycursor.execute(sql)
        data = mycursor.fetchall()
        session['data'] = data
                                
        return redirect(url_for('fact',data=data, fecha=fecha, descripcion=descripcion,numeroasiento=numeroasiento))# rediret lleva el nombre de la funcion

     
    except Exception as e:
        # En caso de error, para imprimir o manejar el error de alguna manera
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})




@app.route("/cargar")
@login_required
def fact():

    
    idcliente = session.get("idcliente")
    id = session.get('idrol')
    list = session.get('list')
    data = session.get('data')
    descripcion = session.get('descripcion')
    fecha = session.get('fecha')
    numeroasiento = session.get('numeroasiento')
    print("CLIENTE DE FACT",idcliente)

    mycursor = db.connection.cursor()
 


    sql = "SELECT idplancuenta, codigo, descripcion FROM plancuentas WHERE imputable=1"
    mycursor.execute(sql)
    data = mycursor.fetchall()
    #print("Data from the database:", data) 
    
    mycursor.close()
    
  
    
 
   
   
    return render_template('cargar_diario.html',data=data, idcliente=idcliente, id=id,fecha=fecha,descripcion=descripcion,numeroasiento=numeroasiento)


#REGISTRO DIARIO

@app.route('/mostrar_registro',methods= ['POST', 'GET'])
@login_required
def mostrar_registro():
    if request.method == 'POST':
        idcliente = session.get('idcliente')
        año = int(request.form.get('year'))   
        print("cliente",idcliente,"año",año)
        session['año'] = año 
        mycursor = db.connection.cursor()
        query = """
            SELECT 
                    ar.idregistro AS idregistro,
                    ar.fecha AS fecha,
                    ar.numeroasiento AS numeroasiento,
                    pc.descripcion AS descripcion,
                    ad.debe AS debe,
                    ad.haber AS haber,
                    ad.idetalle AS idetalle,
                    pc.idplancuenta AS idplancuenta
                FROM 
                    asientodetalle ad
                JOIN 
                    asientoregistro ar ON ad.asientoregistrofk = ar.idregistro
                JOIN 
                    plancuentas pc ON ad.plancuentasfk = pc.idplancuenta
                WHERE 
                    ar.clientefk = %s
                    AND YEAR(ar.fecha) = %s;

                    
                """
        mycursor.execute(query, (idcliente, año,))
        registros = mycursor.fetchall()
        
        print("Consulta de totales", registros)
        session['registros'] = registros
           
        # Consulta para obtener los años únicos asociados al cliente
        mycursor = db.connection.cursor()
        sql_years = "SELECT DISTINCT YEAR(fecha) AS year FROM asientoregistro WHERE clientefk = %s"
        mycursor.execute(sql_years, (idcliente,))
        years_data = mycursor.fetchall()
        
        # Obtén la lista de años desde los resultados
        lis =  [year[0] for year in years_data]
        
        
    
        print("resultado de la vista",registros)
        mycursor.close()

        mycursor = db.connection.cursor()
        sql_month = "SELECT DISTINCT fecha FROM asientoregistro WHERE clientefk = %s"
        mycursor.execute(sql_month, (idcliente,))
        month_data = mycursor.fetchall()

        mycursor.close()
        unico = set(me[0].strftime('%Y-%m') for me in month_data)
        lista = list(unico)
        idrol = session.get('idrol')
        id=idrol

   


    #return redirect(url_for('registros', registros=registros))
    return render_template('listar_registro.html', registros=registros, lis=lis,id=id,lista=lista)



@app.route('/registros')
@login_required
def registros():
    
    #idcliente = session.get('idcliente')
    idcliente = session.get('idcliente')
    
    
    # Consulta para obtener los años únicos asociados al cliente
    mycursor = db.connection.cursor()
    sql_years = "SELECT DISTINCT YEAR(fecha) AS year FROM asientoregistro WHERE clientefk = %s"
    mycursor.execute(sql_years, (idcliente,))
    years_data = mycursor.fetchall()
    
    # Obtén la lista de años desde los resultados
    lis =  [year[0] for year in years_data]
    
    
   
    print("resultado de la vista",registros)
    mycursor.close()

    mycursor = db.connection.cursor()
    sql_month = "SELECT DISTINCT fecha FROM asientoregistro WHERE clientefk = %s"
    mycursor.execute(sql_month, (idcliente,))
    month_data = mycursor.fetchall()

    mycursor.close()
    unico = set(me[0].strftime('%Y-%m') for me in month_data)
    lista = list(unico)
    idrol = session.get('idrol')
    id=idrol

    return render_template('listar_registro.html', lis=lis, lista=lista, id=id)

@app.route('/mes_registro',methods= ['POST', 'GET'])
@login_required
def mes_registro():
    if request.method == 'POST':
        idcliente = session.get('idcliente')
        mes = request.form.get('month') 
        session['mes'] = mes 
        print("mes:",mes)
        mycursor = db.connection.cursor()
        fecha = datetime.strptime(mes, "%Y-%m")
        m = str(fecha.strftime("%m"))
        y= fecha.year
        print("m:",m,"y:",y)
        query = """
            SELECT 
                ar.idregistro AS idregistro,
                ar.fecha AS fecha,
                ar.numeroasiento AS numeroasiento,
                pc.descripcion AS descripcion,
                ad.debe AS debe,
                ad.haber AS haber,
                ad.idetalle AS idetalle,
                pc.idplancuenta AS idplancuenta
            FROM 
                asientodetalle ad
            JOIN 
                asientoregistro ar ON ad.asientoregistrofk = ar.idregistro
            JOIN 
                plancuentas pc ON ad.plancuentasfk = pc.idplancuenta
            WHERE 
                ar.clientefk = %s
                AND MONTH(ar.fecha)=%s
                AND YEAR(ar.fecha) = %s;
            """

        
        mycursor.execute(query, (idcliente,m, y,))
        registros = mycursor.fetchall()
        if session.get('registros') is None:
            session['registros'] = []

        print("Consulta de totales", registros)
    
        # Consulta para obtener los años únicos asociados al cliente
        mycursor = db.connection.cursor()
        sql_years = "SELECT DISTINCT YEAR(fecha) AS year FROM asientoregistro WHERE clientefk = %s"
        mycursor.execute(sql_years, (idcliente,))
        years_data = mycursor.fetchall()
        
        # Obtén la lista de años desde los resultados
        lis =  [year[0] for year in years_data]
        
        
    
        print("resultado de la vista",registros)
        mycursor.close()

        mycursor = db.connection.cursor()
        sql_month = "SELECT DISTINCT fecha FROM asientoregistro WHERE clientefk = %s"
        mycursor.execute(sql_month, (idcliente,))
        month_data = mycursor.fetchall()

        mycursor.close()
        unico = set(me[0].strftime('%Y-%m') for me in month_data)
        lista = list(unico)
        idrol = session.get('idrol')
        id=idrol

   


    #return redirect(url_for('registros', registros=registros))
    return render_template('listar_registro.html', registros=registros, lis=lis,id=id,lista=lista)



@app.route("/editar_registro",methods= ['POST', 'GET'])# tiene que llamarse igual la funcion y la url/
@login_required
def editar_registro():
    if request.method == 'POST':
        idcliente = session.get('idcliente')
        fecha = request.form.get("fecha")
        descripcion = request.form.get("descripcion")
        debe = request.form.get("debe")
        haber = request.form.get("haber")
        numeroasiento= request.form.get("idregistro")
        registrofk= request.form.get("idregistrofk")
        detalle= request.form.get("idetalle")
        año =  session.get('año')#para que la edicion sea dentro del año seleccionado
        print("registro",registrofk)
        print("detalle",detalle)
        print("AÑO DEL COMBO:",año)
        
        if datetime.strptime(fecha, '%Y-%m-%d').year != año:
          flash("No puedes editar registros en un año diferente al seleccionado", "error")
          return redirect(url_for('registros'))
        else: 
            mycursor = db.connection.cursor()
            sql1 = "UPDATE asientoregistro SET fecha=%s WHERE clientefk=%s AND numeroasiento=%s "
            val1 = (fecha,  idcliente,numeroasiento)
            mycursor.execute(sql1, val1)
            db.connection.commit()
            mycursor.close()
            
            
            mycursor = db.connection.cursor()
            sql2 = "UPDATE asientodetalle SET debe=%s, haber=%s, plancuentasfk=%s WHERE  idetalle=%s AND asientoregistrofk=%s  "
                
            val2 = (debe,  haber,descripcion,detalle,registrofk)
            mycursor.execute(sql2, val2)
            db.connection.commit()
            mycursor.close()
      
       

            return redirect(url_for('registros'))



@app.route("/borrar_asiento/<int:idregistro>", methods=['GET'])
@login_required
def borrar_asiento(idregistro):
    
    # flash("Cliente eliminado")
    mycursor = db.connection.cursor()
    sql_id = """SELECT ad.debe,ad.haber,ad.plancuentasfk,ar.periodofk, ar.clientefk
                FROM asientodetalle ad
                JOIN asientoregistro ar ON ad.asientoregistrofk = ar.idregistro
                WHERE ar.idregistro = %s;
                """
    mycursor.execute(sql_id, (idregistro,))
    resultados = mycursor.fetchall()
    for row in resultados:
        debe = row[0]
        haber = row[1]
        plan = row[2]
        periodo = row[3]
        cliente = row[4]
        print("debe:",debe,"haber",haber,"plan:",plan,"año:",periodo,"cliente",cliente)
       
        

    mycursor.execute( "DELETE FROM asientoregistro WHERE idregistro = %s",(idregistro,))
    db.connection.commit()
    mycursor.close()

    idcliente = session.get('idcliente')
    
    mycursor = db.connection.cursor()
    sql_years = "SELECT DISTINCT YEAR(fecha) AS year FROM asientoregistro WHERE clientefk = %s"
    mycursor.execute(sql_years, (idcliente,))
    years_data = mycursor.fetchall()
    
    # Obtén la lista de años desde los resultados
    lis =  [year[0] for year in years_data]
    
    
    
    mycursor.close()

    mycursor = db.connection.cursor()
    sql_month = "SELECT DISTINCT fecha FROM asientoregistro WHERE clientefk = %s"
    mycursor.execute(sql_month, (idcliente,))
    month_data = mycursor.fetchall()

    mycursor.close()
    unico = set(me[0].strftime('%Y-%m') for me in month_data)
    lista = list(unico)
    
    idrol = session.get('idrol')
    id=idrol
    return redirect(url_for('registros', lis=lis, lista=lista, id=id))

@app.route('/exportar_excel', methods=['POST'])
def exportar_excel():
    idcliente = session.get('idcliente')
    año = session.get('año') 
    mes = session.get('mes')  
    fecha = datetime.strptime(mes, "%Y-%m")
    m = str(fecha.strftime("%m"))
    y= fecha.year
    mycursor_cliente = db.connection.cursor()
    sql_cliente = "SELECT nombres, apellidos, razonsocial FROM clientes WHERE idcliente = %s"
    mycursor_cliente.execute(sql_cliente, (idcliente,))
    resultado_cliente = mycursor_cliente.fetchone()
    if resultado_cliente:
        # Verificar si nombres y apellidos están vacíos y usar razonsocial en su lugar
        nombres = resultado_cliente[0] if resultado_cliente[0] else ""
        apellidos = resultado_cliente[1] if resultado_cliente[1] else ""
        razonsocial = resultado_cliente[2] if resultado_cliente[2] else ""

        # Unir nombres y apellidos (si están presentes) o usar razonsocial
        nombre_cliente = f"{nombres} {apellidos}" if nombres or apellidos else razonsocial
    else:
        # Manejar el caso en el que no se encuentre el cliente
        nombre_cliente = "Cliente Desconocido"

    mycursor = db.connection.cursor()
    query = """
        SELECT 
            ar.fecha AS Fecha,
            ar.numeroasiento AS Asiento,
            pc.descripcion AS Descripcion,
            ad.debe AS Debe,
            ad.haber AS Haber
        FROM 
            asientodetalle ad
        JOIN 
            asientoregistro ar ON ad.asientoregistrofk = ar.idregistro
        JOIN 
            plancuentas pc ON ad.plancuentasfk = pc.idplancuenta
        WHERE 
            ar.clientefk = %s
            AND YEAR(ar.fecha) = %s
            AND MONTH(ar.fecha) = %s;
    """

    mycursor.execute(query, (idcliente, y, m))
    registros = mycursor.fetchall()
    print("registeos:",registros)
    carpeta_destino = 'C:/Users/Naty/OneDrive/Documentos'
    df = pd.DataFrame(registros, columns=['Fecha', 'Asiento', 'Descripcion', 'Debe', 'Haber'])

    # Crear archivo Excel en memoria 
    output = BytesIO()

    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)

    # Cerrar archivo
    writer.close()
    
    # Reiniciar puntero de memoria
    output.seek(0)

    # Obtener los datos
    data = output.read()

    # Definir ruta y nombre archivo
    nombre_archivo = f'reporte_cliente_{nombre_cliente}_mes_{mes}.xlsx'
    ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)

    # Guardar archivo
    with open(ruta_archivo, 'wb') as f:
        f.write(data)

    # Enviar archivo
    return send_file(ruta_archivo, as_attachment=True)
            


@app.route('/diario_año', methods=['POST'])
def diario_excel():
    idcliente = session.get('idcliente')
    año = session.get('año')  

    mycursor_cliente = db.connection.cursor()
    sql_cliente = "SELECT nombres, apellidos, razonsocial FROM clientes WHERE idcliente = %s"
    mycursor_cliente.execute(sql_cliente, (idcliente,))
    resultado_cliente = mycursor_cliente.fetchone()
    if resultado_cliente:
        # Verificar si nombres y apellidos están vacíos y usar razonsocial en su lugar
        nombres = resultado_cliente[0] if resultado_cliente[0] else ""
        apellidos = resultado_cliente[1] if resultado_cliente[1] else ""
        razonsocial = resultado_cliente[2] if resultado_cliente[2] else ""

        # Unir nombres y apellidos (si están presentes) o usar razonsocial
        nombre_cliente = f"{nombres} {apellidos}" if nombres or apellidos else razonsocial
    else:
        # Manejar el caso en el que no se encuentre el cliente
        nombre_cliente = "Cliente Desconocido"

    mycursor = db.connection.cursor()
    query = """
       SELECT 

                ar.fecha AS fecha,
                ar.numeroasiento AS numeroasiento,
                pc.descripcion AS descripcion,
                ad.debe AS debe,
                ad.haber AS haber
                
            FROM 
                asientodetalle ad
            JOIN 
                asientoregistro ar ON ad.asientoregistrofk = ar.idregistro
            JOIN 
                plancuentas pc ON ad.plancuentasfk = pc.idplancuenta
            WHERE 
                ar.clientefk = %s
                AND YEAR(ar.fecha) = %s;
                

    """

    mycursor.execute(query, (idcliente, año))
    registros = mycursor.fetchall()
    print("registeos:",registros)
    carpeta_destino = 'C:/Users/Naty/OneDrive/Documentos'
    df = pd.DataFrame(registros, columns=['Fecha', 'Asiento', 'Descripcion', 'Debe', 'Haber'])

    # Crear archivo Excel en memoria 
    output = BytesIO()

    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)

    # Cerrar archivo
    writer.close()
    
    # Reiniciar puntero de memoria
    output.seek(0)

    # Obtener los datos
    data = output.read()

    # Definir ruta y nombre archivo
    nombre_archivo = f'diario_cliente_{nombre_cliente}_anio_{año}.xlsx'
    ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)

    # Guardar archivo
    with open(ruta_archivo, 'wb') as f:
        f.write(data)

    # Enviar archivo
    return send_file(ruta_archivo, as_attachment=True)
            

#MAYOR

@app.route('/mayor')
def mayor():
    idcliente = session.get('idcliente')
    
    # Consulta para obtener los años únicos asociados al cliente
    mycursor = db.connection.cursor()
    sql_years = "SELECT DISTINCT YEAR(fecha) AS year FROM asientoregistro WHERE clientefk = %s"
    mycursor.execute(sql_years, (idcliente,))
    years_data = mycursor.fetchall()
    
    # Obtén la lista de años desde los resultados
    lis =  [year[0] for year in years_data]
    
    mycursor = db.connection.cursor()
    sql = "SELECT idplancuenta, codigo, descripcion FROM plancuentas WHERE imputable=1"
    mycursor.execute(sql)
    data = mycursor.fetchall()
       
    
    mycursor.close()

    
    idrol = session.get('idrol')
    id=idrol

    return render_template('mayor.html', lis=lis, data=data, id=id)




@app.route('/mes_mayor',methods= ['POST', 'GET'])
def mes_mayor():
    if request.method == 'POST':
        idcliente = session.get('idcliente')
        cuentas = request.form.get("cuentas")
        año = request.form.get("year")
        año = session.get('año')
        mycursor = db.connection.cursor()
        
        query = """
            SELECT ar.fecha AS fecha, 
                pc.descripcion AS cuentas,
                ar.numeroasiento AS numeroasiento, 
                ar.descripcion AS descripcion,
                ad.debe AS debe, ad.haber AS haber, 
                CASE WHEN ad.debe - ad.haber < 0 THEN 0 ELSE ad.debe - ad.haber END AS saldo 
            FROM asientodetalle ad 
            JOIN asientoregistro ar ON ad.asientoregistrofk = ar.idregistro 
            JOIN plancuentas pc ON ad.plancuentasfk = pc.idplancuenta 
            WHERE ar.clientefk = %s AND pc.idplancuenta =%s  AND YEAR(ar.fecha) =%s
            ORDER BY  pc.idplancuenta;
            """

        
        mycursor.execute(query, (idcliente,cuentas, año,))
        libros = mycursor.fetchall()
        print("Consulta de totales", libros)
        

        # Consulta para obtener los años únicos asociados al cliente
        mycursor = db.connection.cursor()
        sql_years = "SELECT DISTINCT YEAR(fecha) AS year FROM asientoregistro WHERE clientefk = %s"
        mycursor.execute(sql_years, (idcliente,))
        years_data = mycursor.fetchall()
        
        # Obtén la lista de años desde los resultados
        lis =  [year[0] for year in years_data]
        
        
        
        mycursor.close()


        
        
        idrol = session.get('idrol')
        id=idrol
        
        mycursor = db.connection.cursor()
        sql = "SELECT idplancuenta, codigo, descripcion FROM plancuentas WHERE imputable=1"
        mycursor.execute(sql)
        data = mycursor.fetchall()
        
        
        mycursor.close()
        response = make_response(render_template('mayor.html', lis=lis, data=data, id=id))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return render_template('mayor.html',libros=libros,  lis=lis, id=id,data=data)



@app.route('/mayor_excel', methods=['POST'])
def mayor_excel():
    idcliente = session.get('idcliente')
    cuentas = request.form.get("cuentas")
    año = request.form.get("year")
    mycursor_cliente = db.connection.cursor()
    sql_cliente = "SELECT nombres, apellidos, razonsocial FROM clientes WHERE idcliente = %s"
    mycursor_cliente.execute(sql_cliente, (idcliente,))
    resultado_cliente = mycursor_cliente.fetchone()
    if resultado_cliente:
        # Verificar si nombres y apellidos están vacíos y usar razonsocial en su lugar
        nombres = resultado_cliente[0] if resultado_cliente[0] else ""
        apellidos = resultado_cliente[1] if resultado_cliente[1] else ""
        razonsocial = resultado_cliente[2] if resultado_cliente[2] else ""

        # Unir nombres y apellidos (si están presentes) o usar razonsocial
        nombre_cliente = f"{nombres} {apellidos}" if nombres or apellidos else razonsocial
    else:
        # Manejar el caso en el que no se encuentre el cliente
        nombre_cliente = "Cliente Desconocido"

    mycursor = db.connection.cursor()
    query = """
      SELECT ar.fecha AS Fecha, 
 	pc.descripcion AS Cuentas,
    ar.numeroasiento AS Asiento, 
    ar.descripcion AS Descripcion,
    ad.debe AS Debe, 
    ad.haber AS Haber, 
    CASE WHEN ad.debe - ad.haber < 0 THEN 0 ELSE ad.debe - ad.haber END AS Saldo 
    FROM asientodetalle ad JOIN asientoregistro ar ON ad.asientoregistrofk = ar.idregistro JOIN plancuentas pc ON ad.plancuentasfk = 				pc.idplancuenta 
    WHERE ar.clientefk = %s AND pc.idplancuenta =%s  AND YEAR(ar.fecha) =%s
    ORDER BY  pc.idplancuenta;
    """

    mycursor.execute(query, (idcliente,cuentas, año))
    registros = mycursor.fetchall()
    print("registeos:",registros)
    carpeta_destino = 'C:/Users/Naty/OneDrive/Documentos'
    df = pd.DataFrame(registros, columns=['Fecha', 'Cuentas',  'Asiento', 'Descripcion', 'Debe', 'Haber', 'Saldo'])

    
    
    additional_info = {
        'Cliente': [nombre_cliente],
        'Año': [año],
        'Fecha de Expedición': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    }
    df_info = pd.DataFrame(additional_info)

    # Concatenate the additional information DataFrame with the main DataFrame
    df = pd.concat([df_info, df], axis=1)

    # Crear archivo Excel en memoria 
    output = BytesIO()

    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)

    # Cerrar archivo
    writer.close()
    
    # Reiniciar puntero de memoria
    output.seek(0)

    # Obtener los datos
    data = output.read()

    # Definir ruta y nombre archivo
    nombre_archivo = f'mayor_cliente_{nombre_cliente}_anio_{año}.xlsx'
    ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)

    # Guardar archivo
    with open(ruta_archivo, 'wb') as f:
        f.write(data)

    # Enviar archivo
    return send_file(ruta_archivo, as_attachment=True)



@app.route('/balance')
def balance():
    
    idcliente = session.get('idcliente')
    
    # Consulta para obtener los años únicos asociados al cliente
    mycursor = db.connection.cursor()
    sql_years = "SELECT DISTINCT YEAR(fecha) AS year FROM asientoregistro WHERE clientefk = %s"
    mycursor.execute(sql_years, (idcliente,))
    years_data = mycursor.fetchall()
    
    # Obtén la lista de años desde los resultados
    lis =  [year[0] for year in years_data]
    print("balance año:",lis)
    mycursor.close()

    mycursor = db.connection.cursor()
    sql_month = "SELECT DISTINCT fecha FROM asientoregistro WHERE clientefk = %s"
    mycursor.execute(sql_month, (idcliente,))
    month_data = mycursor.fetchall()

    mycursor.close()
    unico = set(me[0].strftime('%Y-%m') for me in month_data)
    lista = list(unico)

    print("balance mes:",lista)
    return render_template('listar_balance.html', lis=lis, lista=lista)



@app.route('/balance_año', methods=['POST', 'GET'])
def balance_año():
    if request.method == 'POST':
        idcliente = session.get('idcliente')
        año = str(request.form.get('year'))
        print("año del balance a mostrar", año, "cliente", idcliente)
        session['año'] = año
        try:
            mycursor = db.connection.cursor()
            sql = """
               WITH CuentasConSaldos AS (
                SELECT 
                    pc.idplancuenta AS id_cuenta, 
                    pc.codigo AS codigo_cuenta,
                    pc.descripcion AS descripcion_cuenta,
                    COALESCE(SUM(ad.debe - ad.haber), 0) AS saldo_cuenta
                FROM plancuentas pc
                LEFT JOIN asientodetalle ad ON pc.idplancuenta = ad.plancuentasfk
                LEFT JOIN asientoregistro a ON ad.asientoregistrofk = a.idregistro
                LEFT JOIN clientes c ON a.clientefk = c.idcliente
                WHERE c.idcliente = %s
                GROUP BY pc.idplancuenta, pc.codigo, pc.descripcion  
            )

            -- Cuentas con código '1'
            SELECT
                '1' AS codigo_padre,
                'ACTIVO' AS descripcion_padre,
                COALESCE(SUM(ccs.saldo_cuenta), 0) AS saldo_total
            FROM plancuentas pc
            LEFT JOIN CuentasConSaldos ccs ON pc.idplancuenta = ccs.id_cuenta
            WHERE LEFT(pc.codigo, 2) = '1.'

            UNION ALL

            SELECT
                pc_padre.codigo AS codigo_padre,
                pc_padre.descripcion AS descripcion_padre,
                COALESCE(SUM(ccs.saldo_cuenta), 0) AS saldo_total
            FROM plancuentas pc_padre
            LEFT JOIN CuentasConSaldos ccs ON pc_padre.idplancuenta = ccs.id_cuenta
            WHERE LEFT(pc_padre.codigo, 2) = '1.'
            GROUP BY pc_padre.codigo, pc_padre.descripcion

            UNION ALL

            -- Cuentas con código '2'
            SELECT
                '2' AS codigo_padre,
                'PASIVO' AS descripcion_padre,
                COALESCE(SUM(ccs.saldo_cuenta), 0) AS saldo_total
            FROM plancuentas pc
            LEFT JOIN CuentasConSaldos ccs ON pc.idplancuenta = ccs.id_cuenta
            WHERE LEFT(pc.codigo, 2) = '2.'

            UNION ALL

            SELECT
                pc_padre.codigo AS codigo_padre,
                pc_padre.descripcion AS descripcion_padre,
                COALESCE(SUM(ccs.saldo_cuenta), 0) AS saldo_total
            FROM plancuentas pc_padre
            LEFT JOIN CuentasConSaldos ccs ON pc_padre.idplancuenta = ccs.id_cuenta
            WHERE LEFT(pc_padre.codigo, 2) = '2.'
            GROUP BY pc_padre.codigo, pc_padre.descripcion
            ORDER BY codigo_padre;

                    
                    """
            
            mycursor.execute(sql, (idcliente))
            resultados = mycursor.fetchall()
            print("consulta:", resultados)
           


            # Consulta para obtener los años únicos asociados al cliente
            mycursor = db.connection.cursor()
            sql_years = "SELECT DISTINCT YEAR(fecha) AS year FROM asientoregistro WHERE clientefk = %s"
            mycursor.execute(sql_years, (idcliente,))
            years_data = mycursor.fetchall()

            # Obtén la lista de años desde los resultados
            lis = [year[0] for year in years_data]

            mycursor.close()

            mycursor = db.connection.cursor()
            sql_c = "SELECT idplancuenta, descripcion FROM plancuentas WHERE imputable=1"
            mycursor.execute(sql_c)
            data = mycursor.fetchall()
            mycursor.close()

            return render_template('listar_balance.html', lis=lis, data=data, resultados=resultados)

        except Exception as e:
            print("SQL Error:", str(e))
            return jsonify({'success': False, 'error': str(e)})




# @app.route('/balance_año',methods= ['POST', 'GET'])
# def balance_año():
#     idcliente = session.get('idcliente')
#     año = str(request.form.get('year'))   
#     print("año del balance a mostrar",año,"cliente",idcliente)
#     session['año'] = año 
#     try:
#         mycursor = db.connection.cursor()
#         sql="""
#             WITH CuentasConSaldos AS (
#                 SELECT pc.idplancuenta AS id_cuenta, 
#                     pc.codigo AS codigo_cuenta,
#                     pc.descripcion AS descripcion_cuenta,
#                     COALESCE(SUM(ad.debe - ad.haber), 0) AS saldo_cuenta
#                 FROM plancuentas pc
#                 LEFT JOIN asientodetalle ad ON pc.idplancuenta = ad.plancuentasfk
#                 LEFT JOIN asientoregistro a ON ad.asientoregistrofk = a.idregistro
#                 LEFT JOIN clientes c ON a.clientefk = c.idcliente
#                 WHERE c.idcliente = %s
#                 GROUP BY pc.idplancuenta, pc.codigo, pc.descripcion  
#             )

#             SELECT
#                 '1' AS codigo_padre,
#                 'ACTIVO' AS descripcion_padre,
#                 COALESCE(totals.total_saldos, 0) AS saldo_total
#             FROM plancuentas pc
#             LEFT JOIN
#             (
#                 SELECT SUM(saldo_cuenta) AS total_saldos
#                 FROM CuentasConSaldos
#                 WHERE codigo_cuenta LIKE '1.%'
#             ) totals ON 1=1
#             WHERE pc.codigo = '1'  

#             UNION ALL

#             SELECT
#                 pc_padre.codigo AS codigo_padre,
#                 pc_padre.descripcion AS descripcion_padre,
#                 COALESCE(saldos.saldo_total, 0) AS saldo_total
#             FROM plancuentas pc_padre
#             LEFT JOIN 
#                 (
#                 SELECT id_cuenta, SUM(saldo_cuenta) AS saldo_total
#                 FROM CuentasConSaldos
#                 WHERE codigo_cuenta LIKE '1.%'
#                 GROUP BY id_cuenta
#                 ) saldos ON pc_padre.idplancuenta = saldos.id_cuenta
#             WHERE pc_padre.codigo LIKE '1.%' AND idcliente = %s
#             ORDER BY codigo_padre; 
        


#         """
#         try:
#             mycursor.execute(sql, (idcliente,idcliente,))
#             resultados = mycursor.fetchall()
#             print("consulta:",resultados)
#         except Exception as e:
#                 print("SQL Error:", str(e))
#                 return jsonify({'success': False, 'error': str(e)})
#     #  Consulta para obtener los años únicos asociados al cliente
#         mycursor = db.connection.cursor()
#         sql_years = "SELECT DISTINCT YEAR(fecha) AS year FROM asientoregistro WHERE clientefk = %s"
#         mycursor.execute(sql_years, (idcliente,))
#         years_data = mycursor.fetchall()
        
#         # Obtén la lista de años desde los resultados
#         lis =  [year[0] for year in years_data]
        
        
        
#         mycursor.close()

#         # mycursor = db.connection.cursor()
#         # sql_month = "SELECT DISTINCT fecha FROM asientoregistro WHERE clientefk = %s"
#         # mycursor.execute(sql_month, (idcliente,))
#         # month_data = mycursor.fetchall()

#         # mycursor.close()
#         # unico = set(me[0].strftime('%Y-%m') for me in month_data)
#         # lista = list(unico)
        
        
#         mycursor = db.connection.cursor()
#         sql_c = "SELECT idplancuenta, descripcion FROM plancuentas WHERE imputable=1"
#         mycursor.execute(sql_c)
#         data = mycursor.fetchall()
#         mycursor.close()
    
    
        
#         return render_template('listar_balance.html', lis=lis, data=data,resultados=resultados)



#     except Exception as e:
#                 print("SQL Error:", str(e))
#                 return jsonify({'success': False, 'error': str(e)})



@app.route('/procesar_balance',methods= ['POST', 'GET'])
@login_required
def exportar_balance():
    try:
        idcliente = session.get('idcliente')
        mycursor_cliente = db.connection.cursor()
        sql_cliente = "SELECT nombres, apellidos, razonsocial FROM clientes WHERE idcliente = %s"
        mycursor_cliente.execute(sql_cliente, (idcliente,))
        resultado_cliente = mycursor_cliente.fetchone()

        if resultado_cliente:
            nombres, apellidos, razonsocial = resultado_cliente
            nombre_cliente = f"{nombres} {apellidos}" if nombres or apellidos else razonsocial
        else:
            nombre_cliente = "Cliente Desconocido"

        año = str(request.form.get('year'))
        print("año ", año)
        fecha_hora_actual = datetime.now().strftime("%Y%m%d%H%M%S")

        mycursor = db.connection.cursor()
        sql = """
           SELECT
            Codigo,
            Descripcion,
            SumasDebe,
            SumasHaber,
            SaldosDebe,
            SaldosHaber
            FROM (
            SELECT 
                p.codigo AS Codigo,
                p.descripcion AS Descripcion,
                COALESCE(SUM(d.debe), 0) AS SumasDebe,
                COALESCE(SUM(d.haber), 0) AS SumasHaber,  
                CASE WHEN COALESCE(SUM(d.debe - d.haber), 0) < 0 THEN 0 ELSE COALESCE(SUM(d.debe - d.haber), 0) END AS SaldosDebe,
                CASE WHEN COALESCE(SUM(d.haber - d.debe), 0) < 0 THEN 0 ELSE COALESCE(SUM(d.haber - d.debe), 0) END AS SaldosHaber,
                1 AS Orden
            FROM
                plancuentas p
            LEFT JOIN 
                asientodetalle d ON p.idplancuenta = d.plancuentasfk
            LEFT JOIN
                asientoregistro a ON d.asientoregistrofk = a.idregistro AND
                                    a.clientefk = %s AND 
                                    YEAR(a.fecha) = %s
            GROUP BY 
                p.codigo,
                p.descripcion
                            
            UNION

            SELECT
                '' AS Codigo,
                'Totales' AS Descripcion,
                SUM(COALESCE(SumasDebe, 0)) AS SumasDebe,
                SUM(COALESCE(SumasHaber, 0)) AS SumasHaber,
                SUM(COALESCE(SaldosDebe, 0)) AS SaldosDebe, 
                SUM(COALESCE(SaldosHaber, 0)) AS SaldosHaber,
                
                2 AS Orden
            FROM (
                SELECT
                p.codigo AS Codigo,
                p.descripcion AS Descripcion,
                COALESCE(SUM(d.debe), 0) AS SumasDebe,
                COALESCE(SUM(d.haber), 0) AS SumasHaber,
                CASE WHEN COALESCE(SUM(d.debe - d.haber), 0) < 0 THEN 0 ELSE COALESCE(SUM(d.debe - d.haber), 0) END AS SaldosDebe,
                CASE WHEN COALESCE(SUM(d.haber - d.debe), 0) < 0 THEN 0 ELSE COALESCE(SUM(d.haber - d.debe), 0) END AS SaldosHaber
              
                FROM
                plancuentas p
                LEFT JOIN
                asientodetalle d ON p.idplancuenta = d.plancuentasfk
                LEFT JOIN
                asientoregistro a ON d.asientoregistrofk = a.idregistro
                WHERE a.clientefk = %s AND YEAR(a.fecha) = %s
                GROUP BY
                p.codigo, p.descripcion
            ) AS DetallesTotales
            ) AS DetallesFinal

            ORDER BY Orden, Codigo;
            """
        mycursor.execute(sql, (idcliente, año, idcliente, año))
        # Ejecutar y obtener resultados
        resultados = mycursor.fetchall() 
        print(resultados)
        #df = pd.DataFrame(resultados)
        
        
        df = pd.DataFrame(resultados, columns=['Codigo', 'Descripcion', 'SumasDebe', 'SumasHaber', 'SaldosDebe', 'SaldosHaber'])

        # Reorganizar las columnas según la estructura típica de un balance
        df = df[['Codigo', 'Descripcion', 'SumasDebe', 'SumasHaber', 'SaldosDebe', 'SaldosHaber']]

       
        # Crear un libro de Excel y una hoja de cálculo
        wb = openpyxl.Workbook()
        ws = wb.active

        # Agregar un título general
        ws['A1'] = f"Reporte Cliente: {nombre_cliente}, Año: {año}"
        ws['A1'].font = openpyxl.styles.Font(bold=True)
        # Títulos en dos filas
        ws.append(["Código", "Descripción"])  
        ws.append([None, None, "Sumas", "Sumas", "Saldos", None])
        ws.append([None, None, "Debe", "Haber", "Debe", "Haber"])

                # Unir celdas desde fila 1
        ws.merge_cells(start_row=1, start_column=3, end_row=1, end_column=4)

        # Centrar texto en fila 1
        ws.cell(row=1, column=3).alignment = Alignment(horizontal="center") 

        # Ajustar ancho de columna del nombre  
        ws.column_dimensions['A'].auto_size = True
        # Estilo de celda para centrar texto
        align_center = Alignment(horizontal="center")

        # Aplicar estilos a las celdas
        for row in ws.iter_rows(min_row=1, max_row=2, min_col=1, max_col=6):
            for cell in row:
                cell.font = openpyxl.styles.Font(bold=True)
                cell.alignment = align_center

        # Escribir DataFrame
        for row in df.itertuples(index=False):
            ws.append(list(row))

        # Guardar el archivo Excel
        carpeta_destino = 'C:/Users/Naty/OneDrive/Documentos'
        nombre_archivo = f'reporte_cliente_{nombre_cliente}_anio_{año}_{fecha_hora_actual}.xlsx'
        ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)
        wb.save(ruta_archivo)

        print("Directorio de trabajo actual:", os.getcwd())

        flash("Excel generado con éxito...")
        return send_file(ruta_archivo, as_attachment=True)
    except Exception as e:
        # En caso de error, puedes imprimir o manejar el error de alguna manera
        print(f"Error: {str(e)}")
        
            
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