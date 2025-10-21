from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/reservations.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.setdefault("SECRET_KEY", "dev")


    app.config.from_pyfile("config.py", silent=True)

    db.init_app(app)

    from models import User, Patient, Doctor, Clinic, Service, DoctorService, Slot, Booking  # noqa

    with app.app_context():
        db.create_all()

    @app.get("/")
    def ok():
        return "OK"

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
