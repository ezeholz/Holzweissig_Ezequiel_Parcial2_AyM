from flask import Blueprint

prediccion_bp = Blueprint('prediccion', __name__)

from . import routes  # noqa: E402, F401
