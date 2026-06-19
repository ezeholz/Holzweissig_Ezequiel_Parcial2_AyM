from app.extensions import db


class Ejemplar(db.Model):
    __tablename__ = "ejemplares"

    id = db.Column(db.Integer, primary_key=True)
    libro_id = db.Column(db.Integer, db.ForeignKey("libros.id"), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="disponible")
    condicion = db.Column(db.String(20), nullable=False, default="bueno")

    prestamos = db.relationship("Prestamo", backref="ejemplar", lazy="dynamic")
    reservas = db.relationship("Reserva", backref="ejemplar", lazy="dynamic")

    ESTADOS = ["disponible", "prestado", "reservado", "baja"]
    CONDICIONES = ["bueno", "regular", "malo"]

    def __repr__(self) -> str:
        return f"<Ejemplar {self.codigo} [{self.estado}]>"
