from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    email = StringField(
        "Correo electrónico",
        validators=[
            DataRequired(message="El email es requerido."),
            Email(message="Email inválido."),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es requerida.")],
    )
    recordarme = BooleanField("Recordarme")
    submit = SubmitField("Ingresar")
