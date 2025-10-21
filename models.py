# models.py
from enum import Enum as PyEnum
from sqlalchemy import UniqueConstraint, Index
from app import db


# ----- Enums -----
class RoleEnum(PyEnum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"


# ----- Models -----
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    role = db.Column(db.Enum(RoleEnum), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    # 1:1 profilkapcsolatok (child táblában UNIQUE FK)
    patient = db.relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")
    doctor = db.relationship("Doctor", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role.value}>"


class Patient(db.Model):
    __tablename__ = "patient"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    taj = db.Column(db.String(32))  # TAJ szám (opcionális mező volt az eredeti sémában)
    note = db.Column(db.String(1000))

    user = db.relationship("User", back_populates="patient")
    bookings = db.relationship("Booking", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient id={self.id} user_id={self.user_id}>"


class Doctor(db.Model):
    __tablename__ = "doctor"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    license_number = db.Column(db.String(64))
    bio = db.Column(db.String(2000))

    user = db.relationship("User", back_populates="doctor")
    slots = db.relationship("Slot", back_populates="doctor", cascade="all, delete-orphan")
    services_assoc = db.relationship("DoctorService", back_populates="doctor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Doctor id={self.id} user_id={self.user_id}>"


class Clinic(db.Model):
    __tablename__ = "clinic"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    floor_room = db.Column(db.String(255))  # optional

    slots = db.relationship("Slot", back_populates="clinic")

    def __repr__(self):
        return f"<Clinic id={self.id} name={self.name}>"


class Service(db.Model):
    __tablename__ = "service"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    base_duration_min = db.Column(db.Integer, nullable=False)
    base_price = db.Column(db.Integer, nullable=False, default=0)

    bookings = db.relationship("Booking", back_populates="service")
    doctors_assoc = db.relationship("DoctorService", back_populates="service", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Service id={self.id} name={self.name}>"


class DoctorService(db.Model):
    """
    Association object for Doctor <-> Service (N:M) with extra fields.
    """
    __tablename__ = "doctor_service"

    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), primary_key=True)
    price = db.Column(db.Integer)
    duration_min = db.Column(db.Integer)

    doctor = db.relationship("Doctor", back_populates="services_assoc")
    service = db.relationship("Service", back_populates="doctors_assoc")

    __table_args__ = (
        Index("idx_doctor_service_svc", "service_id"),
    )

    def __repr__(self):
        return f"<DoctorService doctor_id={self.doctor_id} service_id={self.service_id}>"


class Slot(db.Model):
    __tablename__ = "slot"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey("clinic.id"))
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    state = db.Column(db.String(30), nullable=False, default="FREE")

    doctor = db.relationship("Doctor", back_populates="slots")
    clinic = db.relationship("Clinic", back_populates="slots")
    booking = db.relationship("Booking", back_populates="slot", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("doctor_id", "starts_at", "ends_at", name="uq_slot_doctor_start_end"),
        Index("idx_slot_doctor_start", "doctor_id", "starts_at"),
    )

    def __repr__(self):
        return f"<Slot id={self.id} doctor_id={self.doctor_id} starts_at={self.starts_at}>"


class Booking(db.Model):
    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    slot_id = db.Column(db.Integer, db.ForeignKey("slot.id"), nullable=False, unique=True)   # 1:1 slot <-> booking
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)          # 1:N patient -> bookings
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)          # 1:N service -> bookings
    status = db.Column(db.String(30), nullable=False, default="NEW")
    note = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    slot = db.relationship("Slot", back_populates="booking")
    patient = db.relationship("Patient", back_populates="bookings")
    service = db.relationship("Service", back_populates="bookings")

    __table_args__ = (
        Index("idx_booking_patient", "patient_id", "created_at"),
    )

    def __repr__(self):
        return f"<Booking id={self.id} slot_id={self.slot_id} patient_id={self.patient_id}>"
