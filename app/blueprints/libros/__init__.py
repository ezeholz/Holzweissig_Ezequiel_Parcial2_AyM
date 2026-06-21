from flask import Blueprint

libros_bp = Blueprint('libros', __name__)

from . import routes  # noqa: E402, F401
