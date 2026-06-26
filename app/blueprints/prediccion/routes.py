import numpy as np
from flask import render_template, flash, current_app
from flask_login import login_required

from app.blueprints.prediccion import prediccion_bp
from app.blueprints.prediccion.forms import PrediccionForm
from app.models.libro import GENEROS


def _nivel_riesgo(probabilidad: float) -> tuple[str, str]:
    """Devuelve (etiqueta, clase CSS Bootstrap) según la probabilidad."""
    if probabilidad < 0.25:
        return "Bajo", "success"
    elif probabilidad < 0.55:
        return "Moderado", "warning"
    else:
        return "Alto", "danger"


@prediccion_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = PrediccionForm()
    resultado = None

    if form.validate_on_submit():
        modelo = current_app.ml_model
        if modelo is None:
            flash(
                "El modelo de predicción no está disponible. Ejecute ml/train_model.py para generarlo.",
                "danger",
            )
            return render_template("prediccion/index.html", form=form, resultado=None)

        features = np.array(
            [
                [
                    form.dias_miembro.data,
                    form.prestamos_previos.data,
                    form.multas_previas.data,
                    form.dias_prestamo.data,
                    form.genero_id.data,
                ]
            ]
        )

        prob_mora = float(modelo.predict_proba(features)[0][1])
        etiqueta, css_class = _nivel_riesgo(prob_mora)

        resultado = {
            "probabilidad": prob_mora,
            "porcentaje": f"{prob_mora * 100:.1f}",
            "etiqueta": etiqueta,
            "css_class": css_class,
            "genero": GENEROS[form.genero_id.data],
            "dias_prestamo": form.dias_prestamo.data,
            "recomendacion": _recomendacion(etiqueta, form),
        }

    return render_template("prediccion/index.html", form=form, resultado=resultado)


def _recomendacion(nivel: str, form: PrediccionForm) -> str:
    if nivel == "Alto":
        return (
            "Se recomienda solicitar garantía adicional o reducir el período de préstamo. "
            "Verificar multas pendientes antes de proceder."
        )
    elif nivel == "Moderado":
        return (
            "Puede proceder con el préstamo. Se sugiere recordar la fecha de vencimiento "
            "mediante notificación al socio."
        )
    else:
        return "Perfil de bajo riesgo. El préstamo puede registrarse sin restricciones adicionales."
