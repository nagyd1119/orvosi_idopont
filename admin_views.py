# admin_views.py
from flask import request, url_for
from markupsafe import Markup
from models import User, Patient, Doctor, Clinic, Service, Slot, Booking, DoctorService, RoleEnum
from app import db
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

class ReadOnlyModelView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    column_display_pk = True

class DoctorAdmin(ModelView):
    column_list = ("id", "user", "license_number", "bio", "view_slots")
    form_columns = ("user", "license_number", "bio")

    def _view_slots_formatter(self, _, model, __):
        link = url_for("slot.index_view", doctor_id=model.id)
        return Markup(f'<a href="{link}">View slots</a>')

    column_formatters = {"view_slots": _view_slots_formatter}

class SlotReadOnlyAdmin(ReadOnlyModelView):
    column_list = ("id", "doctor", "clinic", "starts_at", "ends_at", "state")
    column_default_sort = [("starts_at", True)]

    def get_query(self):
        q = super().get_query()
        did = request.args.get("doctor_id", type=int)
        return q.filter(Slot.doctor_id == did) if did else q

    def get_count_query(self):
        q = super().get_count_query()
        did = request.args.get("doctor_id", type=int)
        return q.filter(Slot.doctor_id == did) if did else q

def init_admin(app):
    admin = Admin(app, name="Időpont Admin", template_mode="bootstrap4")
    admin.add_view(DoctorAdmin(Doctor, db.session))
    admin.add_view(SlotReadOnlyAdmin(Slot, db.session, endpoint="slot"))
    admin.add_view(ModelView(Service, db.session))
    admin.add_view(ModelView(Clinic, db.session))
    admin.add_view(ModelView(Booking, db.session))
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Patient, db.session))
    admin.add_view(ModelView(DoctorService, db.session))
