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

    from .blueprints.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

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

