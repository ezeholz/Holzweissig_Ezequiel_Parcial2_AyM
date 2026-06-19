from datetime import datetime, timedelta
from app.extensions import db

DIAS_EXPIRACION_RESERVA = 3


class Reserva(db.Model):
    __tablename__ = "reservas"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    ejemplar_id = db.Column(db.Integer, db.ForeignKey("ejemplares.id"), nullable=False)
    fecha_reserva = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_expiracion = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(days=DIAS_EXPIRACION_RESERVA),
    )
    estado = db.Column(db.String(20), nullable=False, default="pendiente")

    ESTADOS = ["pendiente", "confirmada", "cancelada", "vencida"]

    def __repr__(self) -> str:
        return f"<Reserva #{self.id} estado={self.estado}>"

    @property
    def esta_vencida(self) -> bool:
        return self.estado == "pendiente" and datetime.utcnow() > self.fecha_expiracion
