from tkinter.constants import CURRENT
from app import db


def SzerepEnum(Enum):
    ADMIN = "ADMIN"
    ORVOS = "ORVOS"
    BETEG = "BETEG"

class Felhasznalo(db.Model):
    __tablename__ = 'felhasznalo'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    jelszo_hash = db.Column(db.String(100), nullable=False)
    nev = db.Column(db.String(50), nullable=False)
    tel = db.Column(db.String(50))
    szerep = db.Column(db.Enum(SzerepEnum), nullable=False)
    aktiv = db.Column(db.Boolean, default=True)
    letrehozva_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    beteg = db.relationship("Beteg", back_populates="felhasznalo", uselist=False, cascade="all, delete-orphan")
    orvos = db.relationship("Orvos", back_populates="felhasznalo", uselist=False, cascade="all, delete-orphan")


class Beteg(db.Model):
    __tablename__= 'beteg'

    id = db.Column(db.Integer, primary_key=True)
    felhasznalo_id = db.Column(db.Integer, db.ForeignKey('felhasznalo'), nullable=False, unique=True)
    taj = db.Column(db.String(9), nullable=False)
    megjegyzes = db.Column(db.String(500))

    felhasznalo = db.relationship("Felhasznalo", back_populates="beteg")
    foglalas = db.relationship("Foglalas", back_populates="beteg")


class Orvos(db.Model):
    __tablename__ = 'orvos'
    id = db.Column(db.Integer, primary_key=True)
    felhasznalo_id = db.Column(db.Integer, db.ForeignKey('felhasznalo'), nullable=False, unique=True)
    pecset_szam = db.Column(db.String(20))
    bemutatkozas = db.Column(db.String(500))

    felhasznalo = db.relationship("Felhasznalo", back_populates="orvos", cascade="all, delete-orphan")
