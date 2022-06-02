import flask
import flask_login
import sirope
from model.userdto import UserDto
from model.llorodto import LloroDto
import app as main


def get_blprint():
    profile = flask.blueprints.Blueprint("profile", __name__,
                                         url_prefix="/profile",
                                         template_folder="templates",
                                         static_folder="static")
    syrp = sirope.Sirope()
    return profile, syrp


profile_blprint, srp = get_blprint()


@flask_login.login_required
@profile_blprint.route('/<profile_id>', methods=["GET"])
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
@profile_blprint.route('/delete', methods=["POST"])
def delete():
    """Recibe un oid seguro que emplea para eliminar el lloro seleccionado por el usuario"""
    usr = UserDto.find(srp, main.usr_login)
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
    return flask.redirect("/profile/" + main.usr_login)
