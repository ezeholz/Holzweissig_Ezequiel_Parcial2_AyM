from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class PrestamoForm(FlaskForm):
    usuario_id = SelectField("Socio", coerce=int, validators=[DataRequired()])
    ejemplar_id = SelectField("Ejemplar", coerce=int, validators=[DataRequired()])
    dias_prestamo = SelectField(
        "Período de préstamo",
        choices=[(7, "7 días"), (14, "14 días"), (21, "21 días")],
        coerce=int,
        default=14,
    )
    observaciones = TextAreaField("Observaciones", validators=[Optional()])
    submit = SubmitField("Registrar préstamo")


class DevolucionForm(FlaskForm):
    submit = SubmitField("Confirmar devolución")
