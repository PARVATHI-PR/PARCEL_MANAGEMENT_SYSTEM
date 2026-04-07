from flask import Flask, render_template, request, session, redirect, url_for
import subprocess
import csv
import os

app = Flask(__name__)
app.secret_key = "parcel_secret_key_007"

# ─── Constants ────────────────────────────────────────────────
ADMIN_ID       = "admin007"
ADMIN_PASSWORD = "csk"
ADMIN_NAME     = "Admin"
PARCELS_CSV    = "parcels.csv"
USERS_CSV      = "users.csv"
STATUS_CSV     = "status_log.csv"

# ─── Helpers ──────────────────────────────────────────────────

def load_users():
    """Load users from users.csv → {phone: {name, password}}"""
    users = {}
    if not os.path.exists(USERS_CSV):
        return users
    with open(USERS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users[row["phone"]] = {"name": row["name"], "password": row["password"]}
    return users

def save_user(name, phone, password):
    """Append a new user to users.csv"""
    file_exists = os.path.exists(USERS_CSV)
    with open(USERS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "phone", "password"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({"name": name, "phone": phone, "password": password})

def load_parcels():
    """Load parcels.csv, skipping conflict-marker lines"""
    parcels = []
    if not os.path.exists(PARCELS_CSV):
        return parcels
    with open(PARCELS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # skip git conflict marker rows
            first_val = list(row.values())[0] if row else ""
            if first_val.startswith("<<<<") or first_val.startswith(">>>>") or first_val.startswith("===="):
                continue
            parcels.append(row)
    return parcels

def load_status_log():
    """Load status_log.csv → list of dicts"""
    logs = []
    if not os.path.exists(STATUS_CSV):
        return logs
    with open(STATUS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            logs.append(row)
    return logs

def get_latest_status(tracking):
    """Get the latest status entry for a tracking number"""
    logs = load_status_log()
    entries = [l for l in logs if l.get("tracking_number","").strip() == tracking.strip()]
    if not entries:
        return None
    return entries[-1]

def get_user_parcels(phone):
    """Return sent and received parcels for a user by phone number"""
    parcels = load_parcels()
    sent, received = [], []
    for p in parcels:
        s_contact = p.get("sender_contact","").strip().strip('"')
        r_contact = p.get("receiver_contact","").strip().strip('"')
        tracking  = p.get("tracking_number","").strip().strip('"')
        latest    = get_latest_status(tracking)
        p["latest_status"]   = latest["status"]   if latest else "Booked"
        p["status_datetime"] = (latest["date"] + " " + latest["time"]) if latest else None
        if s_contact == phone:
            sent.append(p)
        if r_contact == phone:
            received.append(p)
    return sent, received

def get_notifications(phone):
    """Get status update notifications where user is sender or receiver"""
    logs  = load_status_log()
    parcels = load_parcels()
    parcel_map = {p.get("tracking_number","").strip().strip('"'): p for p in parcels}
    notifications = []
    for log in reversed(logs):
        tracking = log.get("tracking_number","").strip()
        p = parcel_map.get(tracking)
        if not p:
            continue
        s_contact = p.get("sender_contact","").strip().strip('"')
        r_contact = p.get("receiver_contact","").strip().strip('"')
        if s_contact == phone:
            log["role"] = "Sender"
            notifications.append(log)
        elif r_contact == phone:
            log["role"] = "Receiver"
            notifications.append(log)
    return notifications[:10]  # latest 10 only

def login_required(role=None):
    """Check session, optionally enforce role"""
    if "user" not in session:
        return False
    if role and session.get("role") != role:
        return False
    return True

# ─── Auth Routes ──────────────────────────────────────────────

@app.route("/")
def index():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("index.html",
                           role=session.get("role"),
                           user_name=session.get("name"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # Admin check
        if username == ADMIN_ID and password == ADMIN_PASSWORD:
            session["user"]  = ADMIN_ID
            session["name"]  = ADMIN_NAME
            session["role"]  = "admin"
            return redirect(url_for("index"))

        # User check
        users = load_users()
        if username in users and users[username]["password"] == password:
            session["user"]  = username
            session["name"]  = users[username]["name"]
            session["role"]  = "user"
            return redirect(url_for("index"))

        return render_template("login.html", error="Invalid ID or password.")

    return render_template("login.html", error=None)

@app.route("/user_signup", methods=["POST"])
def user_signup():
    name     = request.form["name"].strip()
    phone    = request.form["phone"].strip()
    password = request.form["password"].strip()

    if len(phone) != 10 or not phone.isdigit():
        return render_template("login.html", error="Phone must be exactly 10 digits.")

    users = load_users()
    if phone in users:
        return render_template("login.html", error="Phone number already registered.")

    save_user(name, phone, password)
    return render_template("login.html", error="Registration successful! Please login.")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ─── Parcel Registration (Admin only) ─────────────────────────

@app.route("/register")
def register():
    if not login_required("admin"):
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/book", methods=["POST"])
def book():
    if not login_required("admin"):
        return redirect(url_for("login"))

    sender_name    = request.form["senderName"]
    sender_phone   = request.form["senderPhone"]
    sender_address = request.form["senderAddress"]
    sender_city    = request.form["senderCity"]
    receiver_name    = request.form["receiverName"]
    receiver_phone   = request.form["receiverPhone"]
    receiver_address = request.form["receiverAddress"]
    receiver_city    = request.form["receiverCity"]
    weight           = request.form["weight"]
    parcel_type      = request.form["parcelType"]
    spl_instruction  = request.form["specialInstructions"]

    result = subprocess.run(
        ["program.exe"],
        input=(f"{sender_name}\n{sender_address}\n{sender_city}\n{sender_phone}\n"
               f"{receiver_name}\n{receiver_address}\n{receiver_city}\n{receiver_phone}\n"
               f"{weight}\n{parcel_type}\n{spl_instruction}\n"),
        text=True,
        capture_output=True
    )

    output = result.stdout
    tracking        = "Null"
    booking_datetime = "Not Found"
    for line in output.splitlines():
        line = line.strip()
        if "Tracking No" in line:
            tracking = line.split(":", 1)[1].strip()
        if "Date" in line:
            booking_datetime = line.split(":", 1)[1].strip()

    return render_template("confirm.html",
        sender_name=sender_name,
        sender_phone=sender_phone,
        sender_address=sender_address,
        sender_city=sender_city,
        receiver_name=receiver_name,
        receiver_phone=receiver_phone,
        receiver_address=receiver_address,
        receiver_city=receiver_city,
        weight=weight,
        parcel_type=parcel_type,
        spl_instruction=spl_instruction,
        date=booking_datetime,
        tracking=tracking
    )

# ─── Search ───────────────────────────────────────────────────

def parse_search_output(output):
    results = []
    current = {}
    for line in output.splitlines():
        line = line.strip()
        if line == "RESULT_START":
            current = {}
        elif line == "RESULT_END":
            if current:
                results.append(current)
        elif line.startswith("Tracking No:"):
            current["tracking"] = line.split(":",1)[1].strip()
        elif line.startswith("Sender:"):
            parts = line.split(":",1)[1].strip().split(" | ")
            current["sender_name"]    = parts[0] if len(parts) > 0 else ""
            current["sender_contact"] = parts[1] if len(parts) > 1 else ""
            current["sender_address"] = parts[2] if len(parts) > 2 else ""
            current["sender_city"]    = parts[3] if len(parts) > 3 else ""
        elif line.startswith("Receiver:"):
            parts = line.split(":",1)[1].strip().split(" | ")
            current["receiver_name"]    = parts[0] if len(parts) > 0 else ""
            current["receiver_contact"] = parts[1] if len(parts) > 1 else ""
            current["receiver_address"] = parts[2] if len(parts) > 2 else ""
            current["receiver_city"]    = parts[3] if len(parts) > 3 else ""
        elif line.startswith("Weight:"):
            current["weight"] = line.split(":",1)[1].strip()
        elif line.startswith("Type:"):
            current["parcel_type"] = line.split(":",1)[1].strip()
        elif line.startswith("Instructions:"):
            current["instructions"] = line.split(":",1)[1].strip()
        elif line.startswith("Date:"):
            current["date"] = line.split(":",1)[1].strip()
        elif line.startswith("Time:"):
            current["time"] = line.split(":",1)[1].strip()
    return results

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search/tracking', methods=['POST'])
def search_by_tracking():
    tracking_number = request.form.get('tracking_number', '').strip()
    result = subprocess.run(
        ["search.exe", "tracking", tracking_number],
        capture_output=True, text=True
    )
    results = parse_search_output(result.stdout)
    return render_template('search_results.html',
        results=results,
        search_type="Tracking Number",
        search_query=tracking_number
    )

@app.route('/search/location', methods=['POST'])
def search_by_location():
    origin      = request.form.get('origin', '').strip()
    destination = request.form.get('destination', '').strip()
    city = destination if destination else origin
    result = subprocess.run(
        ["search.exe", "location", city],
        capture_output=True, text=True
    )
    results = parse_search_output(result.stdout)
    return render_template('search_results.html',
        results=results,
        search_type="Location",
        search_query=f"City: {city}"
    )

@app.route('/search/date', methods=['POST'])
def search_by_date():
    from_date = request.form.get('from_date', '').strip()
    to_date   = request.form.get('to_date', '').strip()
    result = subprocess.run(
        ["search.exe", "date", from_date, to_date],
        capture_output=True, text=True
    )
    results = parse_search_output(result.stdout)
    return render_template('search_results.html',
        results=results,
        search_type="Date Range",
        search_query=f"{from_date} to {to_date}"
    )

# ─── Update Status (Admin only) ───────────────────────────────

@app.route("/update_status", methods=["GET", "POST"])
def update_status():
    if not login_required("admin"):
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("update_status.html",
                               staff_name=session.get("name"),
                               staff_id=session.get("user"),
                               success=None, msg_lines=[],
                               tracking=None,
                               sender_name=None, sender_phone=None,
                               receiver_name=None, receiver_phone=None)

    # POST
    tracking_number = request.form["tracking_number"].strip()
    status          = request.form["status"].strip()
    location        = request.form["location"].strip()
    staff_id        = session.get("user")
    staff_name      = session.get("name")

    result = subprocess.run(
        ["update_status.exe"],
        input=f"{tracking_number}\n{status}\n{staff_id}\n{staff_name}\n{location}\n",
        text=True,
        capture_output=True
    )

    output    = result.stdout
    lines     = [l.strip() for l in output.splitlines() if l.strip()]
    success   = "STATUS_OK" in output

    # Find sender/receiver info for notification display
    sender_name = sender_phone = receiver_name = receiver_phone = "N/A"
    parcels = load_parcels()
    for p in parcels:
        if p.get("tracking_number","").strip().strip('"') == tracking_number:
            sender_name   = p.get("sender_name","N/A").strip().strip('"')
            sender_phone  = p.get("sender_contact","N/A").strip().strip('"')
            receiver_name  = p.get("receiver_name","N/A").strip().strip('"')
            receiver_phone = p.get("receiver_contact","N/A").strip().strip('"')
            break

    return render_template("update_status.html",
                           staff_name=staff_name,
                           staff_id=staff_id,
                           success=success,
                           msg_lines=lines,
                           tracking=tracking_number,
                           sender_name=sender_name,
                           sender_phone=sender_phone,
                           receiver_name=receiver_name,
                           receiver_phone=receiver_phone)

# ─── My Parcels (User only) ───────────────────────────────────

@app.route("/my_parcels")
def my_parcels():
    if not login_required("user"):
        return redirect(url_for("login"))

    phone  = session.get("user")
    name   = session.get("name")
    sent, received    = get_user_parcels(phone)
    notifications     = get_notifications(phone)

    return render_template("my_parcels.html",
                           user_name=name,
                           phone=phone,
                           sent=sent,
                           received=received,
                           notifications=notifications)

# ─── Run ──────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)