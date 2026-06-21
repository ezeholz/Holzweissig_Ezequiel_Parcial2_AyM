from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.blueprints.auth import auth_bp
from app.blueprints.auth.forms import LoginForm
from app.extensions import bcrypt
from app.models.usuario import Usuario


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            if user.estado != "activo":
                flash(
                    "Tu cuenta está suspendida o inactiva. Contacta al administrador.",
                    "danger",
                )
                return redirect(url_for("auth.login"))
            login_user(user, remember=form.recordarme.data)
            next_page = request.args.get("next")
            flash(f"Bienvenido/a, {user.nombre}!", "success")
            return (
                redirect(next_page)
                if next_page
                else redirect(url_for("main.dashboard"))
            )
        flash("Email o contraseña incorrectos.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))
