from flask import Flask, render_template, request, redirect, url_for, flash  
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
 
    
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
        


def status_401(error):
    return redirect(url_for('login')), 401

def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404

# Pagina principal
@app.route('/home')
@login_required
def home():
    #username = current_user.username 

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


@app.route("/editarcliente",methods= ['POST', 'GET'])# tiene que lamarse igual la funcion y la url/
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
    return render_template('cargar.html', idcliente=idcliente)

    
@app.route("/compra/")
@login_required
def compra():
    return render_template('fact.html')

@app.route("/venta/")
@login_required
def venta():
    return render_template('venta.html')

@app.route("/asiento_compra/",methods= ['POST', 'GET'])# tiene que lamarse igual la funcion y la url/
@login_required
def asiento_compra():
    if request.method == 'POST':
        selected_tipoc = request.form.get('tipoc')
        fecha_value = request.form.get('fecha')
        timbrado_value = request.form.get('timbrado')
        ncomprobante_value = request.form.get('ncomprobante')
        monto_gravado_10_value = request.form.get('monto_gravado_10')
        monto_impuesto_10_value = request.form.get('monto_impuesto_10')
        # Extract other values as needed

        # Print or use the extracted values as required
        print(f'Tipo de Comprobantes: {selected_tipoc}')
        print(f'Fecha: {fecha_value}')
        print(f'Timbrado: {timbrado_value}')
        print(f'Numero de comprobante: {ncomprobante_value}')
        print(f'Monto Gravado 10%: {monto_gravado_10_value}')
        print(f'Monto Impuesto 10%: {monto_impuesto_10_value}')
        return redirect(url_for('home'))
    
if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()