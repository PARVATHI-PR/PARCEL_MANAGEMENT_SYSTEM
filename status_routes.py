from flask import Blueprint, render_template, request, redirect, url_for, session
import subprocess, csv, os

status_bp = Blueprint("status", __name__)

def load_admins():
    admins = {
        "STAFF001": {"name": "Admin One",  "password": "admin123"},
        "STAFF002": {"name": "Admin Two",  "password": "admin456"},
    }
    if os.path.exists("admins.csv"):
        with open("admins.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                admins[row["staff_id"]] = {"name": row["name"], "password": row["password"]}
    return admins

def load_users():
    users = {}
    if os.path.exists("users.csv"):
        with open("users.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                users[row["phone"]] = {"name": row["name"], "password": row["password"]}
    return users

@status_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        admins = load_admins()
        if username in admins and admins[username]["password"] == password:
            session["role"]       = "admin"
            session["staff_id"]   = username
            session["staff_name"] = admins[username]["name"]
            return redirect(url_for("home"))
        users = load_users()
        if username in users and users[username]["password"] == password:
            session["role"]      = "user"
            session["phone"]     = username
            session["user_name"] = users[username]["name"]
            return redirect(url_for("home"))
        return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

@status_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@status_bp.route("/user_signup", methods=["POST"])
def user_signup():
    name     = request.form.get("name", "").strip()
    phone    = request.form.get("phone", "").strip()
    password = request.form.get("password", "").strip()
    users = load_users()
    if phone in users:
        return render_template("login.html",
            error="Phone already registered.", show_signup=True)
    write_header = not (os.path.exists("users.csv") and os.path.getsize("users.csv") > 0)
    with open("users.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["phone", "name", "password"])
        w.writerow([phone, name, password])
    session["role"]      = "user"
    session["phone"]     = phone
    session["user_name"] = name
    return redirect(url_for("home"))

@status_bp.route("/update_status_page")
def update_status_page():
    if session.get("role") != "admin":
        return redirect(url_for("status.login"))
    return render_template("update_status.html",
                           staff_id=session.get("staff_id"),
                           staff_name=session.get("staff_name"))

@status_bp.route("/update_status", methods=["POST"])
def update_status():
    if session.get("role") != "admin":
        return redirect(url_for("status.login"))
    tracking   = request.form["tracking_number"].strip()
    new_status = request.form["status"].strip()
    location   = request.form["location"].strip()
    staff_id   = session.get("staff_id", "UNKNOWN")
    staff_name = session.get("staff_name", "Unknown")

    exe = "update_status.exe" if os.name == "nt" else "./update_status"
    result = subprocess.run(
        [exe],
        input=f"{tracking}\n{new_status}\n{staff_id}\n{staff_name}\n{location}\n",
        text=True, capture_output=True
    )
    output  = result.stdout
    success = "STATUS_OK" in output
    msg_lines = [l.strip() for l in output.splitlines()
                 if l.strip() and "STATUS_OK" not in l]

    sender_name = sender_phone = receiver_name = receiver_phone = ""
    if os.path.exists("parcels.csv"):
        with open("parcels.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("tracking_number", "").strip() == tracking:
                    sender_name    = row.get("sender_name", "")
                    sender_phone   = row.get("sender_contact", "")
                    receiver_name  = row.get("receiver_name", "")
                    receiver_phone = row.get("receiver_contact", "")
                    break

    return render_template("update_status.html",
                           staff_id=staff_id, staff_name=staff_name,
                           success=success, msg_lines=msg_lines,
                           new_status=new_status, tracking=tracking,
                           sender_name=sender_name, sender_phone=sender_phone,
                           receiver_name=receiver_name, receiver_phone=receiver_phone)

@status_bp.route("/my_parcels")
def my_parcels():
    if session.get("role") != "user":
        return redirect(url_for("status.login"))
    phone = session.get("phone", "")
    sent, received = _parcels_for_phone(phone)
    for p in sent + received:
        p["latest_status"], p["status_datetime"] = _latest_status(p.get("tracking_number","").strip())
    notifications = _notifications_for_phone(phone)
    return render_template("my_parcels.html",
                           phone=phone,
                           user_name=session.get("user_name", phone),
                           sent=sent, received=received,
                           notifications=notifications)

def _latest_status(tracking):
    status, dt = "Booked", ""
    if not os.path.exists("status_log.csv"): return status, dt
    with open("status_log.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("tracking_number","").strip() == tracking:
                status = row.get("status","Booked")
                dt = (row.get("date","") + " " + row.get("time","")).strip()
    return status, dt

def _last_location(tracking):
    loc = ""
    if not os.path.exists("status_log.csv"): return loc
    with open("status_log.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("tracking_number","").strip() == tracking:
                loc = row.get("location","")
    return loc

def _parcels_for_phone(phone):
    sent, received = [], []
    if not os.path.exists("parcels.csv"): return sent, received
    with open("parcels.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("sender_contact","").strip()   == phone: sent.append(dict(row))
            if row.get("receiver_contact","").strip()  == phone: received.append(dict(row))
    return sent, received

def _notifications_for_phone(phone):
    notifs = []
    if not os.path.exists("status_log.csv") or not os.path.exists("parcels.csv"):
        return notifs
    parcel_map = {}
    with open("parcels.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            parcel_map[row.get("tracking_number","").strip()] = row
    with open("status_log.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            trk    = row.get("tracking_number","").strip()
            parcel = parcel_map.get(trk, {})
            sc = parcel.get("sender_contact","").strip()
            rc = parcel.get("receiver_contact","").strip()
            if phone in (sc, rc):
                notifs.append({
                    "tracking":      trk,
                    "status":        row.get("status",""),
                    "location":      row.get("location",""),
                    "date":          row.get("date",""),
                    "time":          row.get("time",""),
                    "role":          "Sender" if phone == sc else "Receiver",
                    "sender_name":   parcel.get("sender_name",""),
                    "receiver_name": parcel.get("receiver_name",""),
                })
    notifs.sort(key=lambda x: (x["date"], x["time"]), reverse=True)
    return notifs