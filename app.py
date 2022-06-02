import os
import redis
import flask
import flask_login
from flask import Flask, json
import sirope
from model.llorodto import LloroDto
from model.userdto import UserDto
from urllib.parse import urlparse

def create_app():
    flapp = flask.Flask(__name__)
    r = redis.from_url(os.environ.get("REDIS_URL"))
    sirp = sirope.Sirope(r)
    lgmg = flask_login.login_manager.LoginManager()

    flapp.config.from_file("config.json", json.load)
    lgmg.init_app(flapp)
    return flapp, sirp, lgmg


app, srp, lm = create_app()
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

@flask_login.login_required
@app.route("/home")
def home():
    """Devuelve la plantilla base del home de la aplicacion"""
    usr = UserDto.find(srp, usr_login)

    if not usr:
        flask.flash("Es necesario estar logueado")
        return flask.redirect("/login")

    lloros = list(srp.load_all(LloroDto))
    lloros.sort(key=lambda x: x.time, reverse=True)
    sust = {
        "usr": usr,
        "lloros_list": lloros,
    }
    return flask.render_template("base.html", **sust)


@flask_login.login_required
@app.route("/home/save_lloro", methods=["POST"])
def save_lloro():
    """Metodo encargado de almacenar la nueva publicación en la base de datos"""
    txt = flask.request.form.get("inputLloro")
    usr = UserDto.find(srp, usr_login)
    if not usr:
        flask.flash("Es necesario estar logueado")
        return flask.redirect("/login")

    if not txt:
        flask.flash("No puedo crear un lloro vacio")
        return flask.redirect("/home")

    lloroOID = srp.save(LloroDto(txt, usr.login))
    usr.add_lloro_oid(lloroOID)
    srp.save(usr)
    return flask.redirect("/home")

@flask_login.login_required
@app.route('/profile/<profile_id>', methods=["GET"])
def user_profile(profile_id):
    """Recupero una lista de post pertenecientes al usuario logueado"""
    usr = UserDto.find(srp, profile_id)
    if not usr:
        flask.flash("Es necesario estar logueado")
        return flask.redirect("/login")

    misLloros = list(sirope.Sirope().filter(LloroDto, lambda m: m.author == profile_id))
    misLloros.sort(key=lambda x: x.time, reverse=True)

    sust = {
        "usr": usr,
        "lloros_list": misLloros,
        "oids": {i.__oid__: srp.safe_from_oid(i.__oid__) for i in misLloros}
    }
    return flask.render_template("profile.html", **sust)


@flask_login.login_required
@app.route('/profile/delete', methods=["POST"])
def delete():
    """Recibe un oid seguro que emplea para eliminar el lloro seleccionado por el usuario"""
    usr = UserDto.find(srp,usr_login)
    safe_oid = flask.request.form.get("safe_oid")
    oid = srp.oid_from_safe(safe_oid)

    if not usr:
        flask.flash("Es necesario estar logueado")
        return flask.redirect("/login")

    if not oid:
        flask.flash("El oid no existe")
        return flask.redirect("/home")

    usr.oids_lloros.remove(oid)
    srp.save(usr)
    srp.delete(oid)
    return flask.redirect("/profile/" + usr_login)


@flask_login.login_required
@app.route("/search/results", methods=["POST"])
def results():
    """Devuelve las ultimas 5 publicaciones realizadas por el usuario buscado"""
    sust= {}
    msgs = []
    txt_search = flask.request.form.get("inputSearch")
    usr = srp.find_first(UserDto, lambda u: txt_search.strip() in u.login)

    if usr is not None:
        msgs = list(srp.multi_load(usr.oids_lloros))
        msgs.sort(key=lambda x: x.time, reverse=True)
        sust = {
            "usr": usr,
            "lloros_list": msgs,
        }
    else:
        usr = UserDto.find(srp,usr_login)
        sust = {
            "usr": usr,
        }

    return flask.render_template("search_results.html", **sust)


if __name__ == '__main__':
    app.run()
