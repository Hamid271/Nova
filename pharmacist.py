from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3

# ✅ Define Flask Blueprint
pharmacist_bp = Blueprint('pharmacist', __name__)

# Route for pharmacist dashboard
@pharmacist_bp.route('/pharmacist')
def pharmacist_dashboard():
    conn = sqlite3.connect("database/pharmacy.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prescriptions WHERE status='Pending'")
    prescriptions = cursor.fetchall()
    conn.close()
    return render_template('pharmacist.html', prescriptions=prescriptions)

# Approve prescription
@pharmacist_bp.route('/approve/<int:prescription_id>', methods=['POST'])
def approve_prescription(prescription_id):
    conn = sqlite3.connect("database/pharmacy.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE prescriptions SET status='Approved' WHERE id=?", (prescription_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('pharmacist.pharmacist_dashboard'))

# Reject prescription
@pharmacist_bp.route('/reject/<int:prescription_id>', methods=['POST'])
def reject_prescription(prescription_id):
    conn = sqlite3.connect("database/pharmacy.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE prescriptions SET status='Rejected' WHERE id=?", (prescription_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('pharmacist.pharmacist_dashboard'))
