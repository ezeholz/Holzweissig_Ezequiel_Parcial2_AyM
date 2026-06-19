from datetime import datetime
from app.extensions import db


class Multa(db.Model):
    __tablename__ = "multas"

    id = db.Column(db.Integer, primary_key=True)
    prestamo_id = db.Column(db.Integer, db.ForeignKey("prestamos.id"), nullable=False)
    monto = db.Column(db.Float, nullable=False, default=0.0)
    dias_retraso = db.Column(db.Integer, nullable=False, default=0)
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    fecha_generacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_pago = db.Column(db.DateTime)

    ESTADOS = ["pendiente", "pagada", "condonada"]

    def __repr__(self) -> str:
        return f"<Multa #{self.id} ${self.monto:.2f} [{self.estado}]>"
