from flask import Flask, render_template, request, redirect, url_for, flash,jsonify,session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
from config import config
#from crud.cliente import insertar, actualizar, borrar
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect

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
    
# ---------Carga de factura---------------

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
    return render_template('cargar_diario.html', idcliente=idcliente, data=data)

    
@app.route("/cargar_diario/",methods= ['POST', 'GET'])
@login_required
def cargar_diario():
    try:
        idcliente = session.get('idcliente')
        fecha = request.form.get("fecha")
        numeroasiento = request.form.get("numeroasiento")
        descripcion = request.form.get("descripcion")
        importe = request.form.get("importe")
        debe = request.form.get("debe")
        haber = request.form.get("haber")
        cuentas = request.form.get("cuentas")
        print("Fecha",fecha)
        print("Numero de asiento:",numeroasiento)
        print("Descripcion:",descripcion)
        print("Importe:",importe)
        print("Debe:",debe)
        print("Haber:",haber)
        print("Cuenta:",cuentas)
        
        print("CLIENTE:",idcliente)

        mycursor = db.connection.cursor()
        sql = "INSERT INTO asientoregistro (fecha,numeroasiento,descripcion,clientefk) VALUES (%s, %s, %s, %s)"
        val = (fecha,numeroasiento,descripcion,idcliente)
        mycursor.execute(sql, val,)
        db.connection.commit()
        mycursor.close()




        return render_template('cargar_diario.html')
    except Exception as e:
        # En caso de error, puedes imprimir o manejar el error de alguna manera
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route("/venta/")
@login_required
def venta():
    mycursor = db.connection.cursor()

    sql = """
        SELECT 
            'tipoventas' AS tipo, 
            idtipoventa AS id,
            descripcion
        FROM tipoventas

        UNION 

        SELECT
            'ideventas' AS tipo,
            ideventa AS id, 
            descripcion
        FROM ideventas
    """

    mycursor.execute(sql)
    resultados = mycursor.fetchall()

    tipoventas = [r for r in resultados if r[0] == 'tipoventas']
    ideventas = [r for r in resultados if r[0] == 'ideventas']

    print(tipoventas)
 
    print(ideventas)
    return render_template('venta.html',tipoventas=tipoventas,ideventas=ideventas)


            
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