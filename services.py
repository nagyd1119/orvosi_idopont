# services.py (Blueprint vagy simán app.py)
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Service, Slot, Booking
from werkzeug.exceptions import NotFound

bp = Blueprint("services", __name__, url_prefix="/services")

@bp.get("/")
def list_services():
    q = request.args.get("q")
    query = Service.query
    if q:
        query = query.filter(Service.name.ilike(f"%{q}%"))
    items = query.order_by(Service.name.asc()).all()
    return render_template("services/list.html", items=items, q=q)


@bp.route("/new", methods=["GET", "POST"])
def create_service():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        base_duration_min = int(request.form.get("base_duration_min", "0") or 0)
        base_price = int(request.form.get("base_price", "0") or 0)

        if not name:
            flash("A név kötelező.", "danger")
            return redirect(url_for("services.create_service"))

        s = Service(name=name, base_duration_min=base_duration_min, base_price=base_price)
        db.session.add(s)
        db.session.commit()
        flash("Szolgáltatás létrehozva.", "success")
        return redirect(url_for("services.list_services"))

    return render_template("services/form.html", item=None)


@bp.route("/<int:service_id>/edit", methods=["GET", "POST"])
def edit_service(service_id):
    s = Service.query.get_or_404(service_id)

    if request.method == "POST":
        s.name = request.form.get("name", s.name).strip()
        s.base_duration_min = int(request.form.get("base_duration_min", s.base_duration_min) or s.base_duration_min)
        s.base_price = int(request.form.get("base_price", s.base_price) or s.base_price)

        db.session.commit()
        flash("Szolgáltatás frissítve.", "success")
        return redirect(url_for("services.list_services"))

    return render_template("services/form.html", item=s)

@bp.post("/<int:service_id>/delete")
def delete_service(service_id):
    s = Service.query.get_or_404(service_id)
    db.session.delete(s)
    db.session.commit()
    flash("Szolgáltatás törölve.", "warning")
    return redirect(url_for("services.list_services"))

@bp.route("/bookings/new", methods=["POST"])
def create_booking():
    slot_id = int(request.form["slot_id"])
    service_id = int(request.form["service_id"])
    patient_id = int(request.form["patient_id"])

    slot = Slot.query.get_or_404(slot_id)
    if slot.state != "FREE":
        flash("A választott időpont már foglalt.", "danger")
        return redirect(request.referrer or url_for("services.list_services"))

    # ... minden más redirect:
    return redirect(url_for("services.list_services"))

    booking = Booking(slot_id=slot_id, service_id=service_id, patient_id=patient_id, status="NEW")
    slot.state = "BOOKED"

    db.session.add(booking)
    db.session.commit()
    flash("Foglalás rögzítve.", "success")
    return redirect(url_for("bookings.list_bookings"))

@bp.post("/bookings/<int:booking_id>/status")
def update_booking_status(booking_id):
    b = Booking.query.get_or_404(booking_id)
    new_status = request.form["status"]  # "CONFIRMED", "CANCELED", "DONE" stb.

    b.status = new_status
    # ha lemondják, felszabadítjuk a slotot:
    if new_status == "CANCELED":
        b.slot.state = "FREE"

    db.session.commit()
    flash("Foglalás státusza frissítve.", "info")
    return redirect(url_for("bookings.list_bookings"))

@bp.post("/bookings/<int:booking_id>/delete")
def delete_booking(booking_id):
    b = Booking.query.get_or_404(booking_id)
    # biztonság kedvéért:
    if b.slot and b.slot.state == "BOOKED":
        b.slot.state = "FREE"

    db.session.delete(b)
    db.session.commit()
    flash("Foglalás törölve.", "warning")
    return redirect(url_for("bookings.list_bookings"))

