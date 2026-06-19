from datetime import datetime
from app.extensions import db

TARIFA_MULTA_POR_DIA = 10.0  # pesos por día de retraso


class Prestamo(db.Model):
    __tablename__ = "prestamos"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    ejemplar_id = db.Column(db.Integer, db.ForeignKey("ejemplares.id"), nullable=False)
    fecha_prestamo = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime, nullable=False)
    fecha_devolucion = db.Column(db.DateTime)
    estado = db.Column(db.String(20), nullable=False, default="activo")
    observaciones = db.Column(db.Text)

    multa = db.relationship(
        "Multa", backref="prestamo", uselist=False, cascade="all, delete-orphan"
    )

    ESTADOS = ["activo", "devuelto", "vencido"]

    def __repr__(self) -> str:
        return f"<Prestamo #{self.id} estado={self.estado}>"

    @property
    def esta_vencido(self) -> bool:
        return self.estado == "activo" and datetime.utcnow() > self.fecha_vencimiento

    @property
    def dias_retraso(self) -> int:
        ref = self.fecha_devolucion or datetime.utcnow()
        delta = ref - self.fecha_vencimiento
        return max(0, delta.days)

    @property
    def monto_multa_calculado(self) -> float:
        return self.dias_retraso * TARIFA_MULTA_POR_DIA
