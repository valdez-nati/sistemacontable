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
@login_required
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
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    mycursor = db.connection.cursor()
    sql = "SELECT * FROM clientes"
    mycursor.execute(sql)
    data = mycursor.fetchall()
    mycursor.close()


    return render_template('home.html', data=data )


    
    

# Insertar borrar y actualizar clientes
@app.route('/nuevocliente', methods=['GET', 'POST'])
def nuevocliente():   
    if request.method == 'POST': #para que inserte en la base de datos cuando trae informacion
        insertar()
        flash("Guardado con exito...")
        return redirect(url_for('home'))   


@app.route("/editarcliente",methods= ['POST', 'GET'])# tiene que lamarse igual la funcion y la url/
def editarcliente():
    if request.method == 'POST':
        actualizar()
        flash("Actualizado con exito...")
        return redirect(url_for('home'))

@app.route("/borrarcliente/<string:ruc>", methods=['GET'])
def borrarcliente(ruc):
    flash("Cliente eliminado")
    mycursor = db.connection.cursor() #para asegurar la coneccion y el cierre se usa .connection
    mycursor.execute( "DELETE FROM clientes WHERE ruc= %s",(ruc,))
    db.connection.commit()
    mycursor.close()
    return redirect(url_for('home'))
    
# ---------Carga de factura---------------

@app.route("/cargar/")
def fact():
    return render_template('cargar.html')

    
@app.route("/compra/")
def compra():
    return render_template('fact.html')

@app.route("/venta/")
def venta():
    return render_template('venta.html')

    
if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()