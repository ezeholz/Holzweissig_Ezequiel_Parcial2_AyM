from datetime import datetime
from flask import render_template
from flask_login import login_required

from app.blueprints.main import main_bp
from app.models.libro import Libro
from app.models.prestamo import Prestamo
from app.models.usuario import Usuario
from app.models.multa import Multa


@main_bp.route("/")
@main_bp.route("/dashboard")
@login_required
def dashboard():
    total_libros = Libro.query.count()
    prestamos_activos = Prestamo.query.filter_by(estado="activo").count()
    total_socios = Usuario.query.filter_by(rol="socio").count()
    multas_pendientes = Multa.query.filter_by(estado="pendiente").count()

    vencidos = Prestamo.query.filter(
        Prestamo.estado == "activo",
        Prestamo.fecha_vencimiento < datetime.utcnow(),
    ).count()

    ultimos_prestamos = (
        Prestamo.query.order_by(Prestamo.fecha_prestamo.desc()).limit(5).all()
    )

    return render_template(
        "main/dashboard.html",
        total_libros=total_libros,
        prestamos_activos=prestamos_activos,
        total_socios=total_socios,
        multas_pendientes=multas_pendientes,
        vencidos=vencidos,
        ultimos_prestamos=ultimos_prestamos,
    )
