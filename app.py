from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
        
app = Flask(__name__)
app.secret_key = "Mr.Ss-secret-key-elements"
# ========== HOME ==========
@app.route("/")
def index():
    return render_template("index.html")
        
        
# ========== BOOKING ==========
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "GET":
        return render_template("booking.html")

    # ---- Read form data ----
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    date = request.form.get("date")
    time = request.form.get("time")
    guests = int(request.form.get("guests", 0))
    with_wine = float(request.form.get("with_wine", 0))
    without_wine = float(request.form.get("without_wine", 0))
    promo = (request.form.get("promo") or "").strip().lower()

    # ---- Booking limit check ----
    conn = sqlite3.connect("elements.db")
    c = conn.cursor()
    c.execute("SELECT SUM(guests) FROM bookings WHERE date=? AND time=?", (date, time))
    booked_guests = c.fetchone()[0] or 0
    conn.close()

    if booked_guests + guests > 33:
        return render_template("booking.html", error="Fully booked, please choose another date or time.")

    # ---- Pricing ----
    PRICE_WITH_WINE = 250
    PRICE_WITHOUT_WINE = 200

    base_total = (with_wine * PRICE_WITH_WINE) + (without_wine * PRICE_WITHOUT_WINE)
    discount_pct = 0

    # Auto discounts (no promo)
    if guests >= 6:
        discount_pct = 15
    elif 4 <= guests <= 5:
        discount_pct = 10
    elif guests <= 3:
        if promo == "elements@10":
            discount_pct = 10
        elif promo == "elements@15":
            discount_pct = 15

    # Apply discount
    total = base_total - (base_total * discount_pct / 100)

    # ---- Generate reservation pin ----
    from datetime import datetime
    res_pin = f"RES-{name[:2].upper()}{int(datetime.now().timestamp())}"

    # ---- Save booking ----
    conn = sqlite3.connect("elements.db")
    c = conn.cursor()
    query = """
    INSERT INTO bookings (name, email, phone, date, time, guests, with_wine, without_wine, promo, total, res_pin)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    c.execute(query, (name, email, phone, date, time, guests, with_wine, without_wine, promo, total, res_pin))
    conn.commit()
    conn.close()

    # ---- Show thank-you page ----
    booking = {
        "name": name,
        "email": email,
        "date": date,
        "time": time,
        "guests": guests,
        "total": total,
        "res_pin": res_pin
    }

    return render_template("thankyou.html", booking=booking)

    # ---- Save booking ----
    query = """
        INSERT INTO bookings
        (name, email, phone, date, time, guests, with_wine, without_wine, promo, total, res_pin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    c.execute(
        query,
        (name, email, phone, date, time, guests, with_wine, without_wine, promo, total, res_pin)
    )
    conn.commit()
    conn.close()

    # ---- Prepare confirmation data ----
    booking = {
        "name": name,
        "email": email,
        "phone": phone,
        "date": date,
        "time": time,
        "guests": guests,
        "with_wine": with_wine,
        "without_wine": without_wine,
        "promo": promo,
        "discount_pct": discount_pct,
        "total": total,
        "res_pin": res_pin,
    }

    return render_template("thankyou.html", booking=booking)
    
# ========== ADMIN LOGIN ==========
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "elements" and password == "elements123":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
             return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")
@app.route("/admin/logout")  
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))
    
    
# ========== ADMIN DASHBOARD ==========
@app.route("/admin/dashboard", methods=["GET"])
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect("elements.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bookings ORDER BY date, time")
    bookings = c.fetchall()
    conn.close()
    return render_template("admin_dashboard.html",
bookings=bookings)

# ========== ADMIN ACTION ROUTES ==========
@app.route("/admin/save/<int:id>", methods=["POST"])
def admin_save_booking(id):
    # No field editing yet—just redirect (keeps the button alive)
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete/<int:id>", methods=["POST"])
def admin_delete_booking(id):
    conn = sqlite3.connect("elements.db")
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/confirm/<int:id>", methods=["POST"])
def admin_confirm_booking(id):
    conn = sqlite3.connect("elements.db")
    c = conn.cursor()
    # ⬇️ THIS LINE MUST BE ON ONE LINE (no line break inside the quotes)
    c.execute("UPDATE bookings SET promo = 'CONFIRMED' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))
# ===== REFRESH BOOKINGS (Admin) =====
@app.route("/admin_refresh")
def admin_refresh():
    # Only allow refresh if logged in as admin
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("elements.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bookings ORDER BY date, time")
    bookings = c.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", bookings=bookings)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

