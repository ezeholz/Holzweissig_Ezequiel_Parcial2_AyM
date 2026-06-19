from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, login_manager


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="socio")
    tipo_documento = db.Column(db.String(20))
    nro_documento = db.Column(db.String(30), unique=True)
    telefono = db.Column(db.String(20))
    estado = db.Column(db.String(20), nullable=False, default="activo")
    fecha_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    prestamos = db.relationship("Prestamo", backref="socio", lazy="dynamic")
    reservas = db.relationship("Reserva", backref="socio", lazy="dynamic")

    ROLES = {
        "admin": "Administrador",
        "bibliotecario": "Bibliotecario",
        "socio": "Socio",
    }
    ESTADOS = ["activo", "suspendido", "inactivo"]

    def __repr__(self) -> str:
        return f"<Usuario {self.nombre} {self.apellido} [{self.rol}]>"

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    @property
    def tiene_multas_pendientes(self) -> bool:
        from app.models.multa import Multa

        return (
            Multa.query.join(Multa.prestamo)
            .filter(
                Multa.estado == "pendiente",
            )
            .count()
            > 0
        )

    @property
    def prestamos_activos(self) -> int:
        from app.models.prestamo import Prestamo

        return self.prestamos.filter(Prestamo.estado == "activo").count()


@login_manager.user_loader
def load_user(user_id: str) -> "Usuario":
    return db.session.get(Usuario, int(user_id))
