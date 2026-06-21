from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from app.models.libro import GENEROS


class LibroForm(FlaskForm):
    titulo = StringField(
        "Título",
        validators=[DataRequired(message="El título es requerido."), Length(max=255)],
    )
    autor = StringField(
        "Autor/a",
        validators=[DataRequired(message="El autor es requerido."), Length(max=200)],
    )
    isbn = StringField("ISBN", validators=[Optional(), Length(max=20)])
    anio_publicacion = IntegerField(
        "Año de publicación",
        validators=[Optional(), NumberRange(min=1000, max=2100)],
    )
    editorial = StringField("Editorial", validators=[Optional(), Length(max=150)])
    genero = SelectField(
        "Género",
        choices=[("", "— Seleccionar —")] + [(g, g) for g in GENEROS],
        validators=[Optional()],
    )
    descripcion = TextAreaField("Descripción / Sinopsis", validators=[Optional()])
    submit = SubmitField("Guardar")


class EjemplarForm(FlaskForm):
    codigo = StringField(
        "Código de ejemplar",
        validators=[DataRequired(message="El código es requerido."), Length(max=50)],
    )
    condicion = SelectField(
        "Condición",
        choices=[("bueno", "Bueno"), ("regular", "Regular"), ("malo", "Malo")],
    )
    submit = SubmitField("Agregar ejemplar")
