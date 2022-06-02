import flask
import flask_login
import sirope
from model.userdto import UserDto
from model.llorodto import LloroDto
import app as main


def get_blprint():
    home = flask.blueprints.Blueprint("home", __name__,
                                      url_prefix="/home",
                                      template_folder="templates",
                                      static_folder="static")
    syrp = sirope.Sirope()
    return home, syrp


home_blprint, srp = get_blprint()


@flask_login.login_required
@home_blprint.route("/")
def home():
    """Devuelve la plantilla base del home de la aplicacion"""
    usr = UserDto.find(srp, main.usr_login)

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
@home_blprint.route("/save_lloro", methods=["POST"])
def save_lloro():
    """Metodo encargado de almacenar la nueva publicación en la base de datos"""
    txt = flask.request.form.get("inputLloro")
    usr = UserDto.find(srp, main.usr_login)
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
