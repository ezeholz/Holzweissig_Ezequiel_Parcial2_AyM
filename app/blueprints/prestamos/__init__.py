from flask import Blueprint

prestamos_bp = Blueprint('prestamos', __name__)

from . import routes  # noqa: E402, F401
