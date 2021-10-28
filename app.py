from flask import Flask
from flask.templating import render_template as render
from logging import exception
from flask import Flask, render_template as render
from flask import redirect
from flask import request

from flask import Flask, render_template, request,flash, session,redirect
import sqlite3
import os

from werkzeug.utils import escape

from forms.formularios import Login, Productos, Registro
import hashlib

app = Flask(__name__)

app.secret_key = os.urandom(20)



@app.route("/", methods=["GET"])
def inicio():
    return render("inicio.html")

@app.route("/Cartelera", methods=["GET"])
def cartelera():
    return render("Cartelera.html")

@app.route("/usuario", methods=["GET", "POST"])
def usuario():
    return render("usuario.html")   

@app.route("/pelicula-1", methods=["GET"])
def pelicula():
    return render("pelicula-1.html")

@app.route("/Iniciar-Sesión", methods=["GET", "POST"])
def home():
    frm = Login()
    if frm.validate_on_submit():
        username = escape(frm.username.data)
        password = escape(frm.password.data)
        # Cifra la contraseña
        encrp = hashlib.sha256(password.encode('utf-8'))
        pass_enc = encrp.hexdigest()
        with sqlite3.connect("cine.db") as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM usuario WHERE username = ? AND password =?", [username, pass_enc])
            # cur.execute("SELECT * FROM usuario WHERE username = '" +
            #             username + "' AND password ='" + pass_enc + "'")

            if cur.fetchone():
                session["usuario"] = username
                return redirect("/usuario")
            else:
                redirect ("/Iniciar-Sesión")

    return render_template("Iniciar-Sesión.html", frm=frm)



    
@app.route("/registro", methods=["GET", "POST"])
def registrar():
    frm = Registro()
    if frm.validate_on_submit():
        if frm.enviar:
            username = frm.username.data
            correo = frm.correo.data
            nombre = frm.nombre.data
            password = frm.password.data
            # Cifra la contraseña
            encrp = hashlib.sha256(password.encode('utf-8'))
            pass_enc = encrp.hexdigest()
            # Conecta a la BD
            with sqlite3.connect("cine.db") as con:
                # Crea un cursor para manipular la BD
                cur = con.cursor()
                # Prepara la sentencia SQL
                cur.execute("INSERT INTO usuario (nombre, username, correo, password) VALUES (?,?,?,?)", [
                            nombre, username, correo, pass_enc])
                # Ejecuta la sentencia SQL
                con.commit()
                return  redirect ("/Iniciar-Sesión")


    return render_template("registro.html", frm=frm)





@app.route("/usuario_listar", methods=["GET", "POST"])
def usuario_listar():
    with sqlite3.connect("cine.db") as con:
        con.row_factory = sqlite3.Row  # Lista de diccionario
        cur = con.cursor()
        cur.execute("SELECT * FROM usuario")

        rows = cur.fetchall()

        return render_template("lista-usuarios.html", rows=rows)



@app.route("/usuario_eliminar", methods=["GET", "POST"])
def usuario_eliminar():
    frm = Registro()
    if request.method == "POST":
        username = frm.username.data
        with sqlite3.connect("cine.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM usuario WHERE username = ?", [username])
            con.commit()

            return "Usuario eliminado"
    return render_template("eliminar-usuario.html", frm=frm)


@app.route("/peliculas")
def productos():
    # Verifica si está logueado
    if "usuario" in session:
        frm = Productos()
        return render_template("peliculas.html", frm=frm)
    else:
        return redirect("/")


@app.route("/peliculas/save", methods = ["POST"])
def peli_save():
    frm = Productos()
    nombre = frm.nombre.data
    precio = frm.precio.data
    stock = frm.stock.data
    if len(nombre) > 0:
        if len(precio) > 0:
            if len(stock) > 0:
                with sqlite3.connect("cine.db") as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO productos (nombre,precio,stock) VALUES (?,?,?)", [
                                nombre, precio, stock])
                    con.commit()
                    flash("Guardado con éxito")
            else:
                flash("ERROR: Stock es requerido")
        else:
            flash("ERROR: Precio es requerido")
    else:
        flash("ERROR: Nombre es requerido")

    return render_template("peliculas.html", frm=frm)


@app.route("/peliculas/get", methods=["POST"])
def prod_get():
    frm = Productos()
    nombre = frm.nombre.data
    if len(nombre)> 0:
        with sqlite3.connect("cine.db") as con:
            con.row_factory = sqlite3.Row  # Lista de diccionario
            cur = con.cursor()
            cur.execute("SELECT * FROM productos WHERE nombre = ?",[nombre])
            row = cur.fetchone()
            if row:
                frm.nombre.data = row["nombre"]
                frm.precio.data = row["precio"]
                frm.stock.data = row["stock"]
            else:
                frm.nombre.data = ""
                frm.precio.data = ""
                frm.stock.data = ""
                flash("Pelicula No encontrado")
    
    return render_template("peliculas.html", frm = frm)

@app.route("/peliculas/delete", methods=["POST"])
def peli_delete():
    frm = Productos()
    nombre = escape(frm.nombre.data)
    if nombre:
        with sqlite3.connect("cine.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM productos WHERE nombre = ?", [nombre])
            con.commit()
            if con.total_changes > 0:
                flash("Pelicula Eliminada")
            else:
                flash("Pelicula NO se pudo eliminar")

    return render_template("peliculas.html", frm=frm)


@app.route("/peliculas_listar", methods=["GET", "POST"])
def peliculas_listar():
    with sqlite3.connect("cine.db") as con:
        con.row_factory = sqlite3.Row  # Lista de diccionario
        cur = con.cursor()
        cur.execute("SELECT * FROM productos")

        rows = cur.fetchall()

        return render_template("lista-peliculas.html", rows=rows)



# if __name__=="__main__":
#     app.run(debug=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

app.run(debug=True)
