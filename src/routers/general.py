from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL




app = Flask(__name__)


db= MySQL(app)


@app.route('/balance/<string:ruc>', methods=['GET'])
def activos(ruc):
    mycursor = db.connection.cursor()
    sql = """
        SELECT o.gndevengado
        FROM clientes AS c
        JOIN activos AS a ON c.idcliente = a.cliente_idcliente
        JOIN acorriente AS ac ON a.acorriente_idacorriente = ac.idacorriente
        JOIN otrosactivos AS o ON ac.idacorriente = o.acorriente_idacorriente
        WHERE c.ruc = %s",(ruc,)
    """
    mycursor.execute(sql)
    data = mycursor.fetchall()
    mycursor.close()

    return render_template("balance.html", data=data)





