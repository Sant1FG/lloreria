import sirope
import flask_login
import werkzeug.security as safe


# Clase que representa a un usuario en la aplicación
#:param login: login del usuario es usado como id del objeto
#:param email: el email del usuario
#:param password: contraseña del usuario encriptada en hash

class UserDto(flask_login.UserMixin):
    def __init__(self, login, email, password):
        self._login = login
        self._email = email
        self._password = safe.generate_password_hash(password)
        self._lloros_oids = []

    @property
    def login(self):
        return self._login

    @property
    def email(self):
        return self._email

    @property
    def oids_lloros(self):
        if not self.__dict__.get("_lloros_oids"):
            self._lloros_oids = []
        return self._lloros_oids

    def get_id(self):
        return self.email

    def chk_password(self, pswd):
        return safe.check_password_hash(self._password, pswd)

    def add_lloro_oid(self, lloro_oid):
        self.oids_lloros.append(lloro_oid)

    @staticmethod
    def current_user():
        usr = flask_login.current_user
        return usr

    @staticmethod
    def save_user(user):
        return flask_login.login_user(user)

    @staticmethod
    def find(s: sirope.Sirope, login: str) -> "UserDto":
        return s.find_first(UserDto, lambda u: u.login == login)
