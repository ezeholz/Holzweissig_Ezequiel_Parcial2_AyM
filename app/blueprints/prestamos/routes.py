from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.blueprints.prestamos import prestamos_bp
from app.blueprints.prestamos.forms import PrestamoForm, DevolucionForm
from app.extensions import db
from app.models.usuario import Usuario
from app.models.ejemplar import Ejemplar
from app.models.prestamo import Prestamo
from app.models.multa import Multa


def _requiere_staff():
    if current_user.rol not in ("admin", "bibliotecario"):
        abort(403)


@prestamos_bp.route("/")
@login_required
def index():
    estado = request.args.get("estado", "activo")
    query = Prestamo.query
    if estado in Prestamo.ESTADOS:
        query = query.filter_by(estado=estado)

    if current_user.rol == "socio":
        query = query.filter_by(usuario_id=current_user.id)

    prestamos = query.order_by(Prestamo.fecha_prestamo.desc()).all()

    for p in prestamos:
        if p.esta_vencido:
            p.estado = "vencido"
    db.session.commit()

    return render_template(
        "prestamos/index.html", prestamos=prestamos, estado_filtro=estado
    )


@prestamos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    _requiere_staff()
    form = PrestamoForm()

    socios = (
        Usuario.query.filter_by(rol="socio", estado="activo")
        .order_by(Usuario.apellido)
        .all()
    )
    form.usuario_id.choices = [
        (s.id, f"{s.apellido}, {s.nombre} — {s.nro_documento}") for s in socios
    ]

    disponibles = (
        Ejemplar.query.filter_by(estado="disponible")
        .join(Ejemplar.libro)
        .order_by(db.text("libros.titulo"))
        .all()
    )
    form.ejemplar_id.choices = [
        (e.id, f"{e.libro.titulo} [{e.codigo}]") for e in disponibles
    ]

    if form.validate_on_submit():
        socio = db.session.get(Usuario, form.usuario_id.data)
        ejemplar = db.session.get(Ejemplar, form.ejemplar_id.data)

        if socio.tiene_multas_pendientes:
            flash(
                "El socio tiene multas pendientes. Debe regularizarlas antes de realizar un préstamo.",
                "danger",
            )
            return render_template("prestamos/form.html", form=form)

        if socio.prestamos_activos >= 3:
            flash("El socio ya tiene 3 préstamos activos (límite máximo).", "danger")
            return render_template("prestamos/form.html", form=form)

        if ejemplar.estado != "disponible":
            flash("El ejemplar seleccionado ya no está disponible.", "danger")
            return render_template("prestamos/form.html", form=form)

        dias = form.dias_prestamo.data
        prestamo = Prestamo(
            usuario_id=socio.id,
            ejemplar_id=ejemplar.id,
            fecha_prestamo=datetime.utcnow(),
            fecha_vencimiento=datetime.utcnow() + timedelta(days=dias),
            observaciones=form.observaciones.data,
        )
        ejemplar.estado = "prestado"
        db.session.add(prestamo)
        db.session.commit()
        flash(
            f'Préstamo registrado. Vence el {prestamo.fecha_vencimiento.strftime("%d/%m/%Y")}.',
            "success",
        )
        return redirect(url_for("prestamos.index"))

    return render_template("prestamos/form.html", form=form)


@prestamos_bp.route("/<int:prestamo_id>/devolver", methods=["GET", "POST"])
@login_required
def devolver(prestamo_id):
    _requiere_staff()
    prestamo = Prestamo.query.get_or_404(prestamo_id)

    if prestamo.estado == "devuelto":
        flash("Este préstamo ya fue devuelto.", "info")
        return redirect(url_for("prestamos.index"))

    form = DevolucionForm()
    if form.validate_on_submit():
        ahora = datetime.utcnow()
        prestamo.fecha_devolucion = ahora
        prestamo.estado = "devuelto"
        prestamo.ejemplar.estado = "disponible"

        if prestamo.dias_retraso > 0:
            multa = Multa(
                prestamo_id=prestamo.id,
                dias_retraso=prestamo.dias_retraso,
                monto=prestamo.monto_multa_calculado,
            )
            db.session.add(multa)
            flash(
                f"Devolución registrada con {prestamo.dias_retraso} días de retraso. "
                f"Multa generada: ${multa.monto:.2f}",
                "warning",
            )
        else:
            flash("Devolución registrada sin retraso.", "success")

        db.session.commit()
        return redirect(url_for("prestamos.index"))

    return render_template("prestamos/devolucion.html", prestamo=prestamo, form=form)
