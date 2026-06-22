from flask import Blueprint

socios_bp = Blueprint('socios', __name__)

from . import routes  # noqa: E402, F401
