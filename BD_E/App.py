import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 🔹 Conexión a tu base de datos PostgreSQL local
# Cambia la contraseña "12345" si pusiste otra durante la instalación
DATABASE_URL = "postgresql+psycopg2://postgres:ariana@localhost:5432/Consultorio"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 🔹 MODELOS
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    birthdate = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    specialty = db.Column(db.String(120), nullable=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    patient = db.relationship('Patient', backref=db.backref('appointments', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('appointments', lazy=True))

# 🔹 RUTAS
@app.route("/")
def index():
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    doctors = Doctor.query.order_by(Doctor.name).all()
    appointments = Appointment.query.order_by(Appointment.date.desc()).limit(10).all()
    return render_template("index.html", patients=patients, doctors=doctors, appointments=appointments)

@app.route("/patients/new", methods=["GET", "POST"])
def new_patient():
    if request.method == "POST":
        name = request.form.get("name")
        birth = request.form.get("birthdate") or None
        phone = request.form.get("phone") or None
        bd = None
        if birth:
            bd = datetime.fromisoformat(birth).date()
        p = Patient(name=name, birthdate=bd, phone=phone)
        db.session.add(p)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("new_patient.html")

@app.route("/doctors/new", methods=["GET", "POST"])
def new_doctor():
    if request.method == "POST":
        name = request.form.get("name")
        specialty = request.form.get("specialty")
        d = Doctor(name=name, specialty=specialty)
        db.session.add(d)
        db.session.commit()
        return redirect(url_for("index"))
    return """
    <form method="post">
    <input name="name" placeholder="Nombre del doctor" required>
    <input name="specialty" placeholder="Especialidad">
    <button>Guardar</button>
    </form>
    """

@app.route("/appointments/new", methods=["GET", "POST"])
def new_appointment():
    doctors = Doctor.query.all()
    patients = Patient.query.all()
    if request.method == "POST":
        patient_id = int(request.form.get("patient_id"))
        doctor_id = int(request.form.get("doctor_id"))
        date_str = request.form.get("date")
        notes = request.form.get("notes")
        dt = datetime.fromisoformat(date_str)
        ap = Appointment(patient_id=patient_id, doctor_id=doctor_id, date=dt, notes=notes)
        db.session.add(ap)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("new_appointment.html", doctors=doctors, patients=patients)

# 🔹 EJECUCIÓN
if __name__ == "__main__":
    # Flask 3 ya no usa before_first_request, así que creamos las tablas aquí
    with app.app_context():
        db.create_all()
    app.run(debug=True)
