# LloroDtoDTO
from datetime import datetime


# Clase que representa a una publicación en la aplicacion
#:param msg: el mensaje a almacenar
#:param oid: el oid del usuario que escribio el mensaje

class LloroDto:

    def __init__(self, msg, author):
        self._msg = msg
        self._time = datetime.now().replace(microsecond=0)
        self._author = author

    @property
    def msg(self):
        return self._msg

    @property
    def time(self):
        return self._time

    @property
    def author(self):
        return self._author

    def __str__(self):
        return f"{self.time}: \"{self.msg}\ \"{self.author}\""
