import flask
import flask_login
import sirope
from model.userdto import UserDto
from model.llorodto import LloroDto
import app as main


def get_blprint():
    search = flask.blueprints.Blueprint("search", __name__,
                                         url_prefix="/search",
                                         template_folder="templates",
                                         static_folder="static")
    syrp = sirope.Sirope()
    return search, syrp


search_blprint, srp = get_blprint()


@flask_login.login_required
@search_blprint.route("/results", methods=["POST"])
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
        usr = UserDto.find(srp, main.usr_login)
        sust = {
            "usr": usr,
        }

    return flask.render_template("search_results.html", **sust)
