from datetime import datetime
from .database import db

class Treino(db.Model):
    __tablename__ = 'treinos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    objetivo = db.Column(db.String(255), nullable=False)
    nivel = db.Column(db.String(50), nullable=False, default='iniciante')
    treino_gerado = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Treino {self.id} - {self.objetivo} ({self.nivel})>"
