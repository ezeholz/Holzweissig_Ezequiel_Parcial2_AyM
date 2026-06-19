from app.extensions import db

GENEROS = [
    "Ficción",
    "No ficción",
    "Ciencia ficción",
    "Ficción histórica",
    "Ciencia",
    "Historia",
    "Filosofía",
    "Infantil",
    "Poesía",
    "Clásico",
    "Otro",
]


class Libro(db.Model):
    __tablename__ = "libros"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    anio_publicacion = db.Column(db.Integer)
    editorial = db.Column(db.String(150))
    genero = db.Column(db.String(50))
    descripcion = db.Column(db.Text)

    ejemplares = db.relationship(
        "Ejemplar", backref="libro", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f'<Libro "{self.titulo}">'

    @property
    def total_ejemplares(self) -> int:
        return self.ejemplares.count()

    @property
    def ejemplares_disponibles(self) -> int:
        from app.models.ejemplar import Ejemplar

        return self.ejemplares.filter(Ejemplar.estado == "disponible").count()
