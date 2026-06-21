from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.blueprints.libros import libros_bp
from app.blueprints.libros.forms import LibroForm, EjemplarForm
from app.extensions import db
from app.models.libro import Libro
from app.models.ejemplar import Ejemplar


def _requiere_staff():
    if current_user.rol not in ("admin", "bibliotecario"):
        abort(403)


@libros_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    query = Libro.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Libro.titulo.ilike(like),
                Libro.autor.ilike(like),
                Libro.isbn.ilike(like),
            )
        )
    libros = query.order_by(Libro.titulo).all()
    return render_template("libros/index.html", libros=libros, q=q)


@libros_bp.route("/<int:libro_id>")
@login_required
def detalle(libro_id):
    libro = Libro.query.get_or_404(libro_id)
    form_ejemplar = EjemplarForm()
    return render_template(
        "libros/detalle.html", libro=libro, form_ejemplar=form_ejemplar
    )


@libros_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    _requiere_staff()
    form = LibroForm()
    if form.validate_on_submit():
        if form.isbn.data and Libro.query.filter_by(isbn=form.isbn.data).first():
            flash("Ya existe un libro con ese ISBN.", "danger")
            return render_template("libros/form.html", form=form, titulo="Nuevo libro")

        libro = Libro(
            titulo=form.titulo.data.strip(),
            autor=form.autor.data.strip(),
            isbn=form.isbn.data.strip() or None,
            anio_publicacion=form.anio_publicacion.data,
            editorial=form.editorial.data.strip() or None,
            genero=form.genero.data or None,
            descripcion=form.descripcion.data.strip() or None,
        )
        db.session.add(libro)
        db.session.commit()
        flash(f'Libro "{libro.titulo}" agregado al catálogo.', "success")
        return redirect(url_for("libros.detalle", libro_id=libro.id))

    return render_template("libros/form.html", form=form, titulo="Nuevo libro")


@libros_bp.route("/<int:libro_id>/editar", methods=["GET", "POST"])
@login_required
def editar(libro_id):
    _requiere_staff()
    libro = Libro.query.get_or_404(libro_id)
    form = LibroForm(obj=libro)

    if form.validate_on_submit():
        conflicto = Libro.query.filter(
            Libro.isbn == form.isbn.data, Libro.id != libro_id
        ).first()
        if form.isbn.data and conflicto:
            flash("Ese ISBN ya está registrado en otro libro.", "danger")
            return render_template(
                "libros/form.html", form=form, titulo="Editar libro", libro=libro
            )

        libro.titulo = form.titulo.data.strip()
        libro.autor = form.autor.data.strip()
        libro.isbn = form.isbn.data.strip() or None
        libro.anio_publicacion = form.anio_publicacion.data
        libro.editorial = form.editorial.data.strip() or None
        libro.genero = form.genero.data or None
        libro.descripcion = form.descripcion.data.strip() or None
        db.session.commit()
        flash("Libro actualizado correctamente.", "success")
        return redirect(url_for("libros.detalle", libro_id=libro.id))

    return render_template(
        "libros/form.html", form=form, titulo="Editar libro", libro=libro
    )


@libros_bp.route("/<int:libro_id>/eliminar", methods=["POST"])
@login_required
def eliminar(libro_id):
    _requiere_staff()
    libro = Libro.query.get_or_404(libro_id)
    if libro.ejemplares.filter(Ejemplar.estado == "prestado").count() > 0:
        flash("No se puede eliminar: hay ejemplares en préstamo activo.", "danger")
        return redirect(url_for("libros.detalle", libro_id=libro_id))

    db.session.delete(libro)
    db.session.commit()
    flash(f'Libro "{libro.titulo}" eliminado del catálogo.', "success")
    return redirect(url_for("libros.index"))


@libros_bp.route("/<int:libro_id>/ejemplar/nuevo", methods=["POST"])
@login_required
def agregar_ejemplar(libro_id):
    _requiere_staff()
    libro = Libro.query.get_or_404(libro_id)
    form = EjemplarForm()
    if form.validate_on_submit():
        if Ejemplar.query.filter_by(codigo=form.codigo.data.strip()).first():
            flash("Ya existe un ejemplar con ese código.", "danger")
        else:
            ej = Ejemplar(
                libro_id=libro.id,
                codigo=form.codigo.data.strip(),
                condicion=form.condicion.data,
            )
            db.session.add(ej)
            db.session.commit()
            flash(f"Ejemplar {ej.codigo} agregado.", "success")
    return redirect(url_for("libros.detalle", libro_id=libro_id))


@libros_bp.route("/ejemplar/<int:ejemplar_id>/eliminar", methods=["POST"])
@login_required
def eliminar_ejemplar(ejemplar_id):
    _requiere_staff()
    ej = Ejemplar.query.get_or_404(ejemplar_id)
    libro_id = ej.libro_id
    if ej.estado in ("prestado", "reservado"):
        flash("No se puede eliminar: el ejemplar está prestado o reservado.", "danger")
    else:
        db.session.delete(ej)
        db.session.commit()
        flash("Ejemplar eliminado.", "success")
    return redirect(url_for("libros.detalle", libro_id=libro_id))
