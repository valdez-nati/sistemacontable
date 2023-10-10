from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
from config import config
from crud.cliente import insertar, actualizar, borrar
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect


#Modelos
from models.ModelUser import ModelUser

from models.entities.User import User

app = Flask(__name__)

csrf= CSRFProtect(app)

db= MySQL(app)
login_manager_app= LoginManager(app)

# @login_manager_app.unauthorized_handler
# def unauthorized_callback():
#     flash('Debe iniciar sesión para continuar.')
#     return redirect(url_for('login'))
@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db,id)

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method== 'POST':
        #print(request.form['username'])
        #print(request.form['password'])
        user = User(0, request.form['username'], request.form['contraseña'])
        logeado = ModelUser.login(db, user)
        if logeado != None:
            if logeado.contraseña:
                login_user(logeado)
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
        
    
@app.route('/home')
@login_required
def home():

    mycursor = db.connection.cursor()
    sql = "SELECT nombre, apellido,razonsocial, ruc FROM clientes"
    mycursor.execute(sql)
    ver = mycursor.fetchall()
    mycursor.close()
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
        

    return render_template('home.html', data=ver )


# @app.route('/protegida')
# @login_required #para que solo le muestre a los usuarios logueados 
# def protegida():
#     return "<h1>Vista protegida</h1>"
    

def status_401(error):
    return redirect(url_for('login')), 401

def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404
    
    
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
    #mycursor.close()
    return redirect(url_for('home'))
    

    

if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()