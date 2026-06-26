from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from app.models.libro import GENEROS


class PrediccionForm(FlaskForm):
    dias_miembro = IntegerField(
        "Días registrado como socio",
        validators=[
            DataRequired(),
            NumberRange(min=1, max=9999, message="Debe ser entre 1 y 9999."),
        ],
        description="¿Cuántos días lleva el socio registrado en la biblioteca?",
    )
    prestamos_previos = IntegerField(
        "Préstamos anteriores",
        validators=[DataRequired(), NumberRange(min=0, max=200)],
        description="Cantidad total de préstamos que realizó el socio.",
    )
    multas_previas = IntegerField(
        "Multas acumuladas",
        validators=[DataRequired(), NumberRange(min=0, max=50)],
        description="Cantidad de multas por mora que acumuló el socio.",
    )
    dias_prestamo = SelectField(
        "Duración del préstamo",
        choices=[(7, "7 días"), (14, "14 días"), (21, "21 días")],
        coerce=int,
        default=14,
    )
    genero_id = SelectField(
        "Género del libro",
        choices=[(i, g) for i, g in enumerate(GENEROS)],
        coerce=int,
    )
    submit = SubmitField("Analizar riesgo")
