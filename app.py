from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()  # ← CSAK ITT hozz létre SQLAlchemy példányt!

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, "reservations.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path.replace("\\", "/")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.setdefault("SECRET_KEY", "dev")
    app.config.from_pyfile("config.py", silent=True)
    app.config["SECRET_KEY"] = "dev"

    from services import bp as services_bp
    app.register_blueprint(services_bp)

    # 1) db-t app-hoz kötjük
    db.init_app(app)

    # 2) csak ezután importáljuk a modelleket
    from models import User, Patient, Doctor, Clinic, Service, DoctorService, Slot, Booking  # noqa

    # 3) táblák létrehozása app kontextusban
    with app.app_context():
        db.create_all()

    # 4) csak ezután importáljuk és regisztráljuk az admin nézeteket
    from admin_views import init_admin
    init_admin(app)

    @app.get("/")
    def home():
        stats = {
            "doctors": Doctor.query.count(),
            "patients": Patient.query.count(),
            "appointments": Booking.query.count(),
            "available_slots": Slot.query.filter_by(state="FREE").count(),
        }
        return render_template("index.html", stats=stats)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
