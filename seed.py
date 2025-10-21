# seed.py
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from app import create_app, db
from models import User, Patient, Doctor, Clinic, Service, DoctorService, Slot, Booking, RoleEnum

app = create_app()

def run():
    with app.app_context():
        db.drop_all()
        db.create_all()

        general_checkup = Service(name="General Checkup", base_duration_min=30, base_price=25000)
        dental          = Service(name="Dental Hygiene", base_duration_min=45, base_price=35000)
        cardio          = Service(name="Cardiology Consultation", base_duration_min=40, base_price=40000)
        db.session.add_all([general_checkup, dental, cardio])

        clinic_a = Clinic(name="Debreceni Egyetem Klinikai Központ", address="Nagyerdei krt. 98", floor_room="2/205")
        clinic_b = Clinic(name="Népkerti Magánklinika", address="Bottyán János u. 3", floor_room="3/312")
        clinic_c = Clinic(name="F Medical Magánklinika", address="Mikszáth Kálmán u. 38", floor_room="1/132")
        db.session.add_all([clinic_a, clinic_b, clinic_c])

        doc_user = User(
            email="dr.kinga@nincsmail.hu",
            password_hash=generate_password_hash("kingakiraly321"),
            name="Dr. Király Kinga",
            phone="+36 20 652 3211",
            role=RoleEnum.DOCTOR,
        )
        doctor = Doctor(user=doc_user, license_number="32912", bio="Szájsebész")

        pat_user = User(
            email="kovacsgizi@nincsmail.hu",
            password_hash=generate_password_hash("giziakovi198"),
            name="Kovács Gizella",
            phone="+36 70 252 3311",
            role=RoleEnum.PATIENT,
        )
        patient = Patient(user=pat_user, taj="141238921", note="Allergiás a mogyoróra.")

        db.session.add_all([doc_user, doctor, pat_user, patient])

        ds = DoctorService(doctor=doctor, service=dental, price=35000, duration_min=45)
        db.session.add(ds)

        now = datetime.now().replace(second=0, microsecond=0)
        base = (now + timedelta(days=1)).replace(hour=9, minute=0)
        slots = []
        for i, clinic in enumerate([clinic_a, clinic_a, clinic_b]):
            start = base + timedelta(hours=i)
            end = start + timedelta(minutes=30)
            slots.append(Slot(doctor=doctor, clinic=clinic, starts_at=start, ends_at=end, state="FREE"))
        db.session.add_all(slots)

        booking = Booking(slot=slots[0], patient=patient, service=general_checkup, status="NEW", note="Első vizit.")
        # slots[0].state = "BOOKED"

        db.session.add(booking)
        db.session.commit()

        print(f"Users: {User.query.count()}, Doctors: {Doctor.query.count()}, Patients: {Patient.query.count()}")
        print(f"Clinics: {Clinic.query.count()}, Services: {Service.query.count()}, Slots: {Slot.query.count()}, Bookings: {Booking.query.count()}")

if __name__ == "__main__":
    run()
