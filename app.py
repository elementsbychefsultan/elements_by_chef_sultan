from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "Mr.Ss-secret-key-elements"


# ========== HOME ==========
@app.route("/")
def index():
    return render_template("index.html")


# ========== BOOKING ==========
@app.route("/booking", methods=["GET"])
def booking_page():
    return render_template("booking.html")


@app.route("/booking", methods=["POST"])
def booking():
    import uuid
    from datetime import datetime

    try:
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        date_str = request.form.get("date")
        time = request.form.get("time")
        meal_guests = int(request.form.get("meal_guests", 0))
        drinks_only = int(request.form.get("drinks_only", 0))
        promo = request.form.get("promo", "").strip()
        res_pin = "RES-" + str(uuid.uuid4())[:8].upper()

        PRICE_PER_MEAL = 130
        total = meal_guests * PRICE_PER_MEAL
        total_guests = meal_guests + drinks_only

        # Save to database
        conn = sqlite3.connect("elements.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO bookings (name, email, phone, date, time, guests_meal, drinks_only, total, promo, 
res_pin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, date_str, time, meal_guests, drinks_only, total, promo, res_pin))
        conn.commit()
        conn.close()

        return render_template(
            "thank_you.html",
            name=name,
            total=total,
            total_guests=total_guests,
            meal_guests=meal_guests,
            drinks_only=drinks_only,
            res_pin=res_pin
        )

    except Exception as e:
        print("❌ Booking Error:", e)
        import traceback
        traceback.print_exc()
        return f"Something went wrong while processing your booking: {e}", 500

        # --- Pricing logic ---
        PRICE_PER_MEAL = 130
        total = meal_guests * PRICE_PER_MEAL

        total_guests = meal_guests + drinks_only

        # --- Save booking ---
        conn = sqlite3.connect("elements.db")
        c = conn.cursor()
        c.execute("""
         INSERT INTO bookings
          (name, email, phone, date, time, guests_meal, guests_drinks, total, promo, res_pin)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, date_str, time, meal_guests, drinks_only, total, promo, res_pin))

        return render_template(
            "thank_you.html",
            name=name,
            total=total,
            total_guests=total_guests,
            meal_guests=meal_guests,
            drinks_only=drinks_only,
            res_pin=res_pin
        )

    except Exception as e:
        print("Booking processing error:", e)
        import traceback
        traceback.print_exc()
        return f"Something went wrong while processing your booking: {e}", 500

        # ===== Load booking restrictions =====
        conn = sqlite3.connect("elements.db")
        c = conn.cursor()
        c.execute("SELECT allowed_days, start_date, end_date FROM settings ORDER BY id DESC LIMIT 1")
        settings = c.fetchone()
        conn.close()

        # Default restrictions if none in DB
        allowed_days = [3, 4, 5]  # Thu, Fri, Sat
        start_date = datetime(2025, 12, 11)
        end_date = datetime(2025, 12, 20)
        if settings and settings[0]:
            try:
                allowed_days = json.loads(settings[0])
            except:
                pass
        if settings and settings[1] and settings[2]:
            start_date = datetime.strptime(settings[1], "%Y-%m-%d")
            end_date = datetime.strptime(settings[2], "%Y-%m-%d")

        # ===== Validate date =====
        booking_date = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.today()

        if booking_date < today.replace(hour=0, minute=0, second=0, microsecond=0):
            return "❌ Booking date cannot be in the past.", 400

        if not (start_date <= booking_date <= end_date):
            return f"❌ Bookings allowed only between {start_date.date()} and {end_date.date()}.", 400

        if booking_date.weekday() not in allowed_days:
            return "❌ Bookings allowed only on Thursday, Friday, or Saturday.", 400

        # ===== Save to DB =====
        conn = sqlite3.connect("elements.db")
        c = conn.cursor()
        c.execute("""
         INSERT INTO bookings
         (name, email, phone, date, time, meal_guests, drinks_only, total, promo, res_pin)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,(name, email, phone, date_str, time, meal_guests, drinks_only, total, request.form.get("promo"), res_pin))
        conn.commit()
        conn.close()

        # ===== Success =====
        return render_template(
            "thank_you.html",
            name=name,
            total=total,
            res_pin=res_pin,
            meal_guests=meal_guests,
            drinks_only=drinks_only,
            total_guests=total_guests
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Something went wrong while processing your booking: {e}", 500


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

    # Fetch current settings (allowed days + date range)
    c.execute("SELECT allowed_days, start_date, end_date FROM settings ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()

    if row:
        import json
        allowed_days = json.loads(row[0])
        start_date = row[1]
        end_date = row[2]
    else:
        allowed_days = [4, 5, 6]
        start_date = "2025-12-11"
        end_date = "2026-02-14"

    # Convert days to human names
    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    allowed_names = [day_names[d] for d in allowed_days]

    return render_template(
        "admin_dashboard.html",
        bookings=bookings,
        allowed_days=allowed_names,
        start_date=start_date,
        end_date=end_date
    )


# ========== EDIT BOOKING ==========
@app.route("/admin/update/<int:id>", methods=["POST"])
def admin_update_booking(id):
    data = request.get_json()
    try:
        conn = sqlite3.connect("elements.db")
        c = conn.cursor()
        c.execute("""
            UPDATE bookings
            SET name = ?, email = ?, phone = ?, date = ?, time = ?,
                guests_meal = ?, guests_drinks = ?, total = ?
            WHERE id = ?
        """, (
            data["name"], data["email"], data["phone"],
            data["date"], data["time"],
            data["guests_meal"], data["guests_drinks"], data["total"], id
        ))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Booking updated successfully!"}
    except Exception as e:
        print("Error updating booking:", e)
        return {"success": False, "message": str(e)}, 500


# ========== DELETE BOOKING ==========
@app.route("/admin/delete/<int:id>", methods=["POST"])
def admin_delete_booking(id):
    try:
        conn = sqlite3.connect("elements.db")
        c = conn.cursor()
        c.execute("DELETE FROM bookings WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        print("Error deleting booking:", e)
        return {"success": False, "message": str(e)}, 500
import json
from flask import jsonify, request



# ===== UPDATE WEEKDAYS =====
@app.route("/admin/set_weekdays", methods=["POST"])
def set_weekdays():
    data = request.get_json()
    allowed_days = json.dumps(data.get("allowed_days", [4, 5, 6]))

    conn = sqlite3.connect("elements.db")
    c = conn.cursor()
    c.execute("UPDATE settings SET allowed_days=? WHERE id=1", (allowed_days,))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Allowed weekdays updated!"})


# ===== UPDATE DATE RANGE =====
@app.route("/admin/set_date_range", methods=["POST"])
def set_date_range():
    data = request.get_json()
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    conn = sqlite3.connect("elements.db")
    c = conn.cursor()
    c.execute("UPDATE settings SET start_date=?, end_date=? WHERE id=1", (start_date, end_date))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Date range updated!"})


# ===== RESET SETTINGS =====
@app.route("/admin/reset_settings", methods=["POST"])
def reset_settings():
    conn = sqlite3.connect("elements.db")
    c = conn.cursor()
    c.execute("UPDATE settings SET allowed_days=?, start_date=?, end_date=?", 
              (json.dumps([0,1,2,3,4,5,6]), None, None))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "All booking restrictions cleared!"})


# ========== MAIN ==========
from flask import jsonify

@app.route("/admin/get_settings", methods=["GET"])
def get_settings():
    """Return allowed weekdays and date range as JSON."""
    conn = sqlite3.connect("elements.db")
    c = conn.cursor()
    c.execute("SELECT allowed_days, start_date, end_date FROM settings ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({
            "allowed_days": [4, 5, 6],  # Thu, Fri, Sat default
            "start_date": "2025-12-11",
            "end_date": "2025-12-20"
        })

    import json
    try:
        allowed_days = json.loads(row[0])
    except Exception:
        allowed_days = [4, 5, 6]

    return jsonify({
        "allowed_days": allowed_days,
        "start_date": row[1],
        "end_date": row[2]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
        
        
