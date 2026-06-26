import os
import joblib
from flask import Flask
from .config import Config
from .extensions import db, bcrypt, login_manager, csrf


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    model_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "ml", "modelo_mora.joblib"
    )
    app.ml_model = joblib.load(model_path) if os.path.exists(model_path) else None

    from .blueprints.main import main_bp
    from .blueprints.auth import auth_bp
    from .blueprints.libros import libros_bp
    from .blueprints.prestamos import prestamos_bp
    from .blueprints.socios import socios_bp
    from .blueprints.prediccion import prediccion_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(libros_bp, url_prefix="/libros")
    app.register_blueprint(prestamos_bp, url_prefix="/prestamos")
    app.register_blueprint(socios_bp, url_prefix="/socios")
    app.register_blueprint(prediccion_bp, url_prefix="/prediccion")

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template

        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template

        return render_template("errors/404.html"), 404

    with app.app_context():
        db.create_all()

    return app

