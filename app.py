import flask
import flask_login
from flask import Flask, json
import sirope
from flask_login import login_manager

import home_view
import profile_view
import search_view
from model.userdto import UserDto


def create_app():
    flapp = flask.Flask(__name__)
    sirp = sirope.Sirope()
    lgmg = flask_login.login_manager.LoginManager()

    flapp.config.from_file("config.json", json.load)
    lgmg.init_app(flapp)
    return flapp, sirp, lgmg


app, srp, lm = create_app()
app.register_blueprint(home_view.home_blprint)
app.register_blueprint(profile_view.profile_blprint)
app.register_blueprint(search_view.search_blprint)
global usr_login
usr_login = None


@app.route('/')
def get_index():  # put application's code here
    return flask.render_template("main.html")


@lm.user_loader
def user_loader(login):
    return UserDto.find(srp, login)


@lm.unauthorized_handler
def unauthorized_handler():
    flask.flash("Unauthorized")
    return flask.redirect("/")


@app.route("/login")
def login_form():
    """Devuelve la plantilla con el formulario de login"""
    return flask.render_template("login.html")


@app.route("/register")
def register_form():
    """Devuelve la plantilla con el formulario de registro"""
    return flask.render_template("register.html")


@app.route("/logout", methods=["POST"])
def log_out():
    """Elimina la sesión actual volviendo a la pantalla de inicio"""
    flask_login.logout_user()
    global usr_login
    usr_login = None
    return flask.redirect("/")


@app.route("/register", methods=["POST"])
def register_user():
    """Función encargada de registrar a un usuario en la aplicación
    comprueba cada uno de los parametros y en caso de éxito registra la nuevo usuario
    redirigiendo al home de la aplicación"""
    login = flask.request.form.get("inputLogin")
    email = flask.request.form.get("inputEmail")
    password = flask.request.form.get("inputPassword")

    if not login:
        flask.flash("El login esta vacío")
        return flask.redirect(flask.request.url)

    elif not email:
        flask.flash("El email esta vacío")
        return flask.redirect(flask.request.url)
    elif not password:
        flask.flash("La contraseña esta vacia")
        return flask.redirect(flask.request.url)

    usr = UserDto.find(srp, login)
    if usr:
        flask.flash("El usuario con esos datos ya existe")
        return flask.redirect(flask.request.url)
    else:
        usr = UserDto(login, email, password)
        srp.save(usr)

    UserDto.save_user(usr)
    global usr_login
    usr_login = usr.login
    return flask.redirect("/home")


@app.route("/login", methods=["POST"])
def login_user():
    """Función encargada de loguear a un usuario en la aplicación
    comprueba cada uno de los parametros y en caso de éxito loguea al usuario
    redirigiendo al home de la aplicación"""
    login = flask.request.form.get("inputLogin")
    password = flask.request.form.get("inputPassword")

    if not login:
        flask.flash("El login esta vacío")
        return flask.redirect(flask.request.url)
    elif not password:
        flask.flash("La contraseña esta vacia")
        return flask.redirect(flask.request.url)

    usr = UserDto.find(srp, login)
    if not usr:
        flask.flash("No existe un usuario con estos datos")
        return flask.redirect(flask.request.url)
    elif not usr.chk_password(password):
        flask.flash("Contraseña incorrecta")
        return flask.redirect(flask.request.url)

    UserDto.save_user(usr)
    global usr_login
    usr_login = usr.login
    return flask.redirect("/home")


if __name__ == '__main__':
    app.run()
