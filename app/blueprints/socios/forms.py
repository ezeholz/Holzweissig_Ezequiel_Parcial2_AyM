from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo


class SocioForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    apellido = StringField("Apellido", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    tipo_documento = SelectField(
        "Tipo documento",
        choices=[
            ("DNI", "DNI"),
            ("Pasaporte", "Pasaporte"),
            ("CE", "Cédula de extranjería"),
        ],
    )
    nro_documento = StringField("N° documento", validators=[Optional(), Length(max=30)])
    telefono = StringField("Teléfono", validators=[Optional(), Length(max=20)])
    password = PasswordField(
        "Contraseña",
        validators=[Length(min=6, message="Mínimo 6 caracteres."), Optional()],
    )
    password_confirm = PasswordField(
        "Confirmar contraseña",
        validators=[EqualTo("password", message="Las contraseñas no coinciden.")],
    )
    estado = SelectField(
        "Estado",
        choices=[
            ("activo", "Activo"),
            ("suspendido", "Suspendido"),
            ("inactivo", "Inactivo"),
        ],
    )
    submit = SubmitField("Guardar")
