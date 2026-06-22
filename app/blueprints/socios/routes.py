from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import desc

from app.blueprints.socios import socios_bp
from app.blueprints.socios.forms import SocioForm
from app.extensions import db, bcrypt
from app.models.usuario import Usuario
from app.models.prestamo import Prestamo


def _requiere_staff():
    if current_user.rol not in ("admin", "bibliotecario"):
        abort(403)


@socios_bp.route("/")
@login_required
def index():
    _requiere_staff()
    q = request.args.get("q", "").strip()
    query = Usuario.query.filter_by(rol="socio")
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Usuario.nombre.ilike(like),
                Usuario.apellido.ilike(like),
                Usuario.email.ilike(like),
                Usuario.nro_documento.ilike(like),
            )
        )
    socios = query.order_by(Usuario.apellido).all()
    return render_template("socios/index.html", socios=socios, q=q)


@socios_bp.route("/<int:socio_id>")
@login_required
def detalle(socio_id):
    _requiere_staff()
    socio = Usuario.query.get_or_404(socio_id)
    historial = Prestamo.query.filter_by(usuario_id=socio_id).order_by(desc(Prestamo.fecha_prestamo)).all()
    return render_template("socios/detalle.html", socio=socio, historial=historial)


@socios_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    _requiere_staff()
    form = SocioForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(email=form.email.data.lower()).first():
            flash("Ya existe un usuario con ese email.", "danger")
            return render_template("socios/form.html", form=form, titulo="Nuevo socio")

        if (
            form.nro_documento.data
            and Usuario.query.filter_by(nro_documento=form.nro_documento.data).first()
        ):
            flash("Ya existe un usuario con ese número de documento.", "danger")
            return render_template("socios/form.html", form=form, titulo="Nuevo socio")

        password = form.password.data or "socio123"
        socio = Usuario(
            nombre=form.nombre.data.strip(),
            apellido=form.apellido.data.strip(),
            email=form.email.data.lower().strip(),
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            rol="socio",
            tipo_documento=form.tipo_documento.data,
            nro_documento=form.nro_documento.data.strip() or None,
            telefono=form.telefono.data.strip() or None,
            estado=form.estado.data,
        )
        db.session.add(socio)
        db.session.commit()
        flash(f"Socio {socio.nombre_completo} registrado correctamente.", "success")
        return redirect(url_for("socios.detalle", socio_id=socio.id))

    return render_template("socios/form.html", form=form, titulo="Nuevo socio")


@socios_bp.route("/<int:socio_id>/editar", methods=["GET", "POST"])
@login_required
def editar(socio_id):
    _requiere_staff()
    socio = Usuario.query.get_or_404(socio_id)
    form = SocioForm(obj=socio)

    if form.validate_on_submit():
        email_conflict = Usuario.query.filter(
            Usuario.email == form.email.data.lower(), Usuario.id != socio_id
        ).first()
        if email_conflict:
            flash("Ese email ya está registrado en otro usuario.", "danger")
            return render_template(
                "socios/form.html", form=form, titulo="Editar socio", socio=socio
            )

        socio.nombre = form.nombre.data.strip()
        socio.apellido = form.apellido.data.strip()
        socio.email = form.email.data.lower().strip()
        socio.tipo_documento = form.tipo_documento.data
        socio.nro_documento = form.nro_documento.data.strip() or None
        socio.telefono = form.telefono.data.strip() or None
        socio.estado = form.estado.data

        if form.password.data:
            socio.password_hash = bcrypt.generate_password_hash(
                form.password.data
            ).decode("utf-8")

        db.session.commit()
        flash("Socio actualizado correctamente.", "success")
        return redirect(url_for("socios.detalle", socio_id=socio.id))

    return render_template(
        "socios/form.html", form=form, titulo="Editar socio", socio=socio
    )


@socios_bp.route("/<int:socio_id>/eliminar", methods=["POST"])
@login_required
def eliminar(socio_id):
    if current_user.rol != "admin":
        abort(403)
    socio = Usuario.query.get_or_404(socio_id)
    if socio.prestamos_activos > 0:
        flash("No se puede eliminar: el socio tiene préstamos activos.", "danger")
        return redirect(url_for("socios.detalle", socio_id=socio_id))

    db.session.delete(socio)
    db.session.commit()
    flash(f"Socio {socio.nombre_completo} eliminado.", "success")
    return redirect(url_for("socios.index"))
