from datetime import datetime, timedelta  # ✅ Corrected import

from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import uuid
app = Flask(__name__)
app.secret_key = "super_secret_key"

DATA_FILE = "data.json"

# Utility: Load and Save Data
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"donors": [], "finders": [], "requests": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)



@app.route("/logout")
def logout():
    session.clear()
    flash("You’ve been logged out.", "success")
    return redirect("/")



# Route: Landing Page
@app.route("/")
def index():
    data = load_data()
    
    donors = data.get("donors", [])
    requests = data.get("requests", [])

    cities = [d["city"] for d in donors if d.get("status") == "approved" and d.get("city")]
    donors_count = len([d for d in donors if d.get("status") == "approved"])
    lives_saved = sum(1 for r in requests if r.get("status") in ["accepted", "Completed"] and r.get("donor_contact"))
    requests_count = len(requests)
    cities_covered = len(set(c.lower() for c in cities))

    return render_template(
        "index.html",
        cities=cities,
        donors_count=donors_count,
        lives_saved=lives_saved,
        requests_count=requests_count,
        cities_covered=cities_covered
    )

# Admin Panel Routes
@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        flash("Please login as admin first", "danger")
        return redirect(url_for("admin_login"))
    return render_template("adlogin.html")

# Admin Login Route
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Replace with secure credentials in production!
        if username == "admin" and password == "admin123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials", "danger")
    
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Logged out successfully", "success")
    return redirect("/")

@app.route("/admin/approved_donors")
def approved_donors():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    data = load_data()
    approved = [d for d in data["donors"] if d["status"] == "approved"]
    return render_template("approved_donors.html", donors=approved)

@app.route("/admin/pending_donors")
def pending_donors():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    data = load_data()
    pending = [d for d in data["donors"] if d["status"] == "pending"]
    return render_template("pending_donors.html", donors=pending)

@app.route("/admin/pending_finders")
def pending_finders():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    data = load_data()
    pending = [f for f in data["finders"] if f["status"] == "pending"]
    return render_template("pending_finders.html", finders=pending)

# @app.route("/admin/all_requests")
# def all_requests():
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin_login"))
#     data = load_data()
#     return render_template("all_requests.html", requests=data["requests"])

@app.route("/admin/active_requests")
def active_requests():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    data = load_data()
    active = [r for r in data["requests"] if r["status"] == "Active"]
    return render_template("active_requests.html", requests=active)

@app.route("/admin/completed_requests")
def completed_requests():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    data = load_data()
    completed = [r for r in data["requests"] if r["status"] == "Completed"]
    return render_template("completed_requests.html", requests=completed)

@app.route("/admin/accepted_requests")
def accepted_requests():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    data = load_data()
    accepted = [r for r in data["requests"] if r["status"] == "accepted"]
    return render_template("accepted_requests.html", requests=accepted)

@app.route("/admin/approve_donor/<email>", methods=['GET', 'POST'])
def approve_donor(email):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    
    data = load_data()
    for donor in data["donors"]:
        if donor["email"] == email:
            donor["status"] = "approved"
            save_data(data)
            flash(f"Donor {email} approved successfully", "success")
            break
    return redirect(url_for("pending_donors"))

@app.route("/admin/reject_donor/<email>", methods=['GET', 'POST'])
def reject_donor(email):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    
    data = load_data()
    data["donors"] = [d for d in data["donors"] if d["email"] != email]
    save_data(data)
    flash(f"Donor {email} rejected and removed", "info")
    return redirect(url_for("pending_donors"))

@app.route("/admin/approve_finder/<email>")
def approve_finder(email):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    data = load_data()
    for finder in data["finders"]:
        if finder["email"] == email:
            finder["status"] = "approved"
            save_data(data)
            flash(f"Finder {email} approved successfully", "success")
            break
    return redirect(url_for("pending_finders"))

@app.route("/admin/reject_finder/<email>")
def reject_finder(email):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    data = load_data()
    data["finders"] = [f for f in data["finders"] if f["email"] != email]
    save_data(data)
    flash(f"Finder {email} rejected and removed", "info")
    return redirect(url_for("pending_finders"))

@app.route('/remove_donor', methods=['POST'])
def remove_donor():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    email = request.form.get('email')
    data = load_data()
    
    # Remove donor by email
    data['donors'] = [d for d in data['donors'] if d['email'] != email]
    
    save_data(data)
    flash(f'Donor {email} removed successfully', 'success')
    return redirect(url_for('approved_donors'))

# Approved Finders Route
@app.route("/admin/approved_finders")
def approved_finders():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    
    data = load_data()
    approved = [f for f in data["finders"] if f["status"] == "approved"]
    return render_template("approved_finders.html", finders=approved)

# Remove Finder Route
@app.route('/remove_finder', methods=['POST'])
def remove_finder():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    email = request.form.get('email')
    data = load_data()
    
    # Remove finder by email
    data['finders'] = [f for f in data['finders'] if f['email'] != email]
    
    save_data(data)
    flash(f'Finder {email} removed successfully', 'success')
    return redirect(url_for('approved_finders'))

@app.route('/admin/remove_accepted_request/<request_id>', methods=['POST'])
def remove_accepted_request(request_id):
    if not session.get("admin_logged_in"):
        flash("Please login as admin first", "danger")
        return redirect(url_for("admin_login"))
    
    data = load_data()
    
    # Find and remove the request
    for i, req in enumerate(data["requests"]):
        if req.get("id") == request_id and req.get("status") == "accepted":
            del data["requests"][i]
            save_data(data)
            flash("Request removed successfully", "success")
            break
    else:
        flash("Request not found or not accepted", "danger")
    
    return redirect(url_for("accepted_requests"))

@app.route('/admin/remove_active_request/<request_id>', methods=['POST'])
def remove_active_request(request_id):
    if not session.get("admin_logged_in"):
        flash("Please login as admin first", "danger")
        return redirect(url_for("admin_login"))
    
    data = load_data()
    
    # Find and remove the request
    for i, req in enumerate(data["requests"]):
        if req.get("id") == request_id and req.get("status") == "Active":
            del data["requests"][i]
            save_data(data)
            flash("Active request removed successfully", "success")
            break
    else:
        flash("Request not found or not active", "danger")
    
    return redirect(url_for("active_requests"))

@app.route('/admin/remove_completed_request/<request_id>', methods=['POST'])
def remove_completed_request(request_id):
    if not session.get("admin_logged_in"):
        flash("Please login as admin first", "danger")
        return redirect(url_for("admin_login"))
    
    data = load_data()
    
    # Find and remove the completed request
    for i, req in enumerate(data["requests"]):
        if req.get("id") == request_id and req.get("status") == "Completed":
            del data["requests"][i]
            save_data(data)
            flash("Completed request removed successfully", "success")
            break
    else:
        flash("Request not found or not completed", "danger")
    
    return redirect(url_for("completed_requests"))



@app.route("/finder/request/cancel/<int:index>")
def cancel_request(index):
    email = request.args.get("email")
    data = load_data()

    try:
        req = data["requests"][index]
    except IndexError:
        return "Invalid index", 400

    if req.get("email") == email:
        req["status"] = "Cancelled"
        save_data(data)
        return redirect(url_for("finder_dashboard", email=email))
    else:
        return "Request not found", 404





























# Route: Donor Signup
@app.route("/signup/donor", methods=["GET", "POST"])
def donor_signup():
    if request.method == "POST":
        form = request.form
        new_donor = {
            "full_name": form.get("full_name"),
            "email": form.get("email"),
            "password": form.get("password"),
            "phone": form.get("phone"),
            "dob": form.get("dob"),
            "gender": form.get("gender"),
            "city": form.get("city"),
            "address": form.get("address"),
            "blood_type": form.get("blood_type"),
            "weight": form.get("weight"),
            "height": form.get("height"),
            "last_donation": form.get("last_donation"),
            "conditions": request.form.getlist("conditions"),
            "medications": form.get("medications"),
            "allergies": form.get("allergies"),
            "emergency_contact": {
                "name": form.get("emg_name"),
                "phone": form.get("emg_phone"),
                "relationship": form.get("emg_relation")
            },
            "availability": {
                "days": request.form.getlist("available_days"),
                "times": request.form.getlist("preferred_times")
            },
            "travel_radius": form.get("travel_radius"),
            "status": "pending"
        }

        data = load_data()
        data["donors"].append(new_donor)
        save_data(data)

        flash("Thank you for registering! Awaiting admin approval.", "success")
        return redirect(url_for("index"))

    return render_template("donor_signup.html")

# Route: Finder Signup
@app.route("/signup/finder", methods=["GET", "POST"])
def finder_signup():
    if request.method == "POST":
        form = request.form
        new_finder = {
            "full_name": form.get("full_name"),
            "email": form.get("email"),
            "password": form.get("password"),
            "phone": form.get("phone"),
            "organization": form.get("organization"),
            "city": form.get("city"),
            "address": form.get("address"),
            "status": "pending"
        }

        data = load_data()
        data["finders"].append(new_finder)
        save_data(data)

        flash("Thank you for registering! Awaiting admin approval.", "success")
        return redirect(url_for("index"))

    return render_template("finder_signup.html")

# Route: Admin Panel - View Pending Users
@app.route("/admin/pending")
def admin_pending():
    data = load_data()
    pending_donors = [d for d in data["donors"] if d["status"] == "pending"]
    pending_finders = [f for f in data["finders"] if f["status"] == "pending"]
    return render_template("admin_pending.html", donors=pending_donors, finders=pending_finders)

# Route: Admin Approval
@app.route("/admin/approve/<role>/<email>")
def admin_approve(role, email):
    data = load_data()
    updated = False

    if role == "donor":
        for d in data["donors"]:
            if d["email"] == email and d["status"] == "pending":
                d["status"] = "approved"
                updated = True
    elif role == "finder":
        for f in data["finders"]:
            if f["email"] == email and f["status"] == "pending":
                f["status"] = "approved"
                updated = True

    if updated:
        save_data(data)
        flash(f"{role.title()} approved successfully!", "success")
    else:
        flash("User not found or already approved.", "danger")

    return redirect(url_for("admin_pending"))

# Route: Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form = request.form
        email = form.get("email")
        password = form.get("password")
        role = form.get("role")  # either 'donor' or 'finder'

        data = load_data()
        users = data["donors"] if role == "donor" else data["finders"]

        for user in users:
            if user["email"] == email and user["password"] == password:

                if user["status"] != "approved":
                    flash("Your account is still pending approval.", "warning")
                    return redirect(url_for("login"))

                # ✅ Set session inside valid request context
                session["email"] = email
                session["user_type"] = role

                # ✅ Add correct login flag
                if role == "donor":
                    session["donor_logged_in"] = True
                elif role == "finder":
                    session["finder_logged_in"] = True

                flash(f"Welcome, {user['full_name']}!", "success")
                return redirect(url_for(f"{role}_dashboard", email=email))

        flash("Invalid credentials. Please try again.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard/donor/<email>")
def donor_dashboard(email):
    data = load_data()

    # Find the donor by email
    donor = next((d for d in data["donors"] if d["email"] == email), None)
    
    if not donor or donor.get("status") != "approved":
        flash("Access denied or donor not approved.", "danger")
        return redirect(url_for("login"))

    # Calculate eligibility if not already set
    if "is_eligible" not in donor:
        last_donation_str = donor.get("last_donation")
        if last_donation_str:
            last_donation = datetime.strptime(last_donation_str, "%Y-%m-%d")
            next_eligible = last_donation + timedelta(days=90)  # پہلے سے درست ہے
            is_eligible = datetime.now() >= next_eligible
            donor["is_eligible"] = is_eligible
            donor["next_eligible_date"] = next_eligible.strftime("%Y-%m-%d")
        else:
            donor["is_eligible"] = True
            donor["next_eligible_date"] = "Now"

    # Get donation history
    donation_history = [
        r for r in data.get("requests", [])
        if r.get("donor_contact", {}).get("email") == email
        and r.get("status") in ["accepted", "Completed"]
    ]
    
    # Get matching requests (only show if eligible)
    matching_requests = []
    if donor["is_eligible"]:
        matching_requests = [
            r for r in data.get("requests", [])
            if r.get("status", "").lower() == "active"
            and r.get("blood_type") == donor.get("blood_type")
            and r.get("location", "").lower() == donor.get("city", "").lower()
        ]

    return render_template(
        "donor_dashboard.html",
        donor=donor,
        history=sorted(donation_history, key=lambda r: r.get("date"), reverse=True)[:3],
        requests=matching_requests,
        total_donations=donor.get("total_donations", 0),
        lives_saved=donor.get("total_donations", 0)
    )

@app.route("/donor/accept-request/<request_id>", methods=["POST"])
def accept_request(request_id):
    email = request.args.get("email") or request.form.get("donor_email")
    data = load_data()

    donor = next((d for d in data["donors"] if d["email"] == email), None)
    if not donor or donor.get("status") != "approved":
        flash("Access denied or donor not approved.", "danger")
        return redirect(url_for("login"))

    # Check eligibility before accepting
    if not donor.get("is_eligible", True):
        flash("You are not currently eligible to donate.", "danger")
        return redirect(url_for("donor_dashboard", email=email))

    # Update request status but DON'T update donor's last donation date yet
    for r in data.get("requests", []):
        if r.get("id") == request_id:
            r["status"] = "accepted"
            r["donor_contact"] = {
                "name": donor["full_name"],
                "email": donor["email"],
                "phone": donor["phone"],
                "city": donor["city"]
            }
            break

    save_data(data)
    flash("Request accepted successfully! Your eligibility will update after completion.", "success")
    return redirect(url_for("donor_dashboard", email=email))



@app.route("/donor/edit-profile", methods=["GET", "POST"])
def edit_donor_profile():
    email = request.args.get("email")
    data = load_data()
    donor = next((d for d in data["donors"] if d["email"] == email), None)

    if not donor:
        flash("Donor not found.", "danger")
        return redirect("/")

    if request.method == "POST":
        donor["full_name"] = request.form.get("full_name")  # ✅ added
        donor["city"] = request.form.get("city")            # ✅ added
        donor["phone"] = request.form.get("phone")
        donor["address"] = request.form.get("address")
        donor["weight"] = request.form.get("weight")
        donor["height"] = request.form.get("height")
        save_data(data)
        flash("Profile updated successfully.", "success")
        return redirect(url_for("donor_dashboard", email=email))

    return render_template("edit_donor_profile.html", donor=donor)

@app.route("/donor/profile/update", methods=["POST"])
def update_donor_profile():
    data = load_data()
    email = request.args.get("email") or request.form.get("email")

    donor = next((d for d in data["donors"] if d["email"] == email), None)
    if not donor:
        flash("Donor not found.", "danger")
        return redirect(url_for("login"))

    # Update fields
    donor["full_name"] = request.form.get("full_name")
    donor["city"] = request.form.get("city")
    donor["phone"] = request.form.get("phone")
    donor["address"] = request.form.get("address")
    donor["weight"] = request.form.get("weight")
    donor["height"] = request.form.get("height")

    save_data(data)
    flash("Profile updated successfully.", "success")
    return redirect(url_for("donor_dashboard", email=email))

@app.route("/finder/profile/edit/<email>", methods=["GET", "POST"])
def edit_finder_profile(email):
    data = load_data()
    finder = next((f for f in data["finders"] if f["email"] == email), None)

    if not finder:
        flash("Finder not found.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        finder["full_name"] = request.form.get("full_name")
        finder["phone"] = request.form.get("phone")
        finder["city"] = request.form.get("city")
        finder["address"] = request.form.get("address")
        save_data(data)
        flash("Profile updated successfully!", "success")
        return redirect(url_for("finder_dashboard", email=email))

    return render_template("edit_finder_profile.html", finder=finder)



# Route: Finder Dashboard
@app.route("/dashboard/finder/<email>")
def finder_dashboard(email):
    data = load_data()
    finder = next((f for f in data["finders"] if f["email"] == email), None)

    if not finder or finder["status"] != "approved":
        flash("Access denied or finder not approved.", "danger")
        return redirect(url_for("login"))

    all_requests = data.get("requests", [])
    requests = [
        {**r, "index": i} for i, r in enumerate(all_requests) 
        if r["email"] == email
    ]

    # Standardize status text
    for req in requests:
        if req["status"].lower() == "rejected":
            req["status"] = "Rejected"

    stats = {
        "total": len(requests),
        "active": sum(1 for r in requests if r["status"] == "Active"),
        "completed": sum(1 for r in requests if r["status"] == "Completed"),
        "city": finder["city"]
    }

    return render_template("finder_dashboard.html", 
                         finder=finder, 
                         requests=requests, 
                         stats=stats)

# Route: View Request
@app.route("/finder/request/view/<int:index>")
def view_request(index):
    data = load_data()
    try:
        req = data["requests"][index]
        return render_template("view_request.html", request_data=req)
    except IndexError:
        flash("Request not found.", "danger")
        return redirect("/")

# Route: Mark Request Completed
@app.route("/finder/request/complete/<int:index>")
def complete_request(index):
    data = load_data()
    try:
        request_data = data["requests"][index]
        if request_data["status"] != "Completed":
            request_data["status"] = "Completed"
            
            # Update donor information if request was accepted
            if "donor_contact" in request_data:
                donor_email = request_data["donor_contact"]["email"]
                donor = next((d for d in data["donors"] if d["email"] == donor_email), None)
                
                if donor:
                    # Update last donation date (current date)
                    donor["last_donation"] = datetime.now().strftime("%Y-%m-%d")
                    # Increment donation count
                    donor["total_donations"] = donor.get("total_donations", 0) + 1
                    # Mark as not eligible
                    donor["is_eligible"] = False
                    # Set next eligible date (90 days from now)
                    donor["next_eligible_date"] = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
            
            save_data(data)
            flash("Request marked as completed. Donor status updated to Not Eligible for 90 days.", "success")
    except IndexError:
        flash("Request not found.", "danger")

    user_email = request_data["email"]
    return redirect(url_for("finder_dashboard", email=user_email))

# Route: Edit Request
@app.route("/finder/request/edit/<int:index>", methods=["GET", "POST"])
def edit_request(index):
    data = load_data()

    try:
        req = data["requests"][index]
    except IndexError:
        flash("Request not found.", "danger")
        return redirect("/")

    if request.method == "POST":
        form = request.form
        req["blood_type"] = form.get("blood_type")
        req["location"] = form.get("location")
        req["urgency"] = form.get("urgency")
        req["contact"] = form.get("contact")
        req["date"] = form.get("date")
        save_data(data)

        flash("Request updated successfully.", "success")
        return redirect(url_for("finder_dashboard", email=req["email"]))

    return render_template("edit_request.html", request_data=req, index=index)

# Route: Create New Blood Request
@app.route("/finder/request/new", methods=["GET", "POST"])
def create_blood_request():
    if request.method == "POST":
        form = request.form
        new_request = {
            "id": str(uuid.uuid4()),  # ✅ Add unique request ID
            "email": form.get("email"),
            "blood_type": form.get("blood_type"),
            "location": form.get("location"),
            "urgency": form.get("urgency"),
            "contact": form.get("contact"),
            "date": form.get("date"),
            "status": "Active"
        }

        data = load_data()
        if "requests" not in data:
            data["requests"] = []

        data["requests"].append(new_request)
        save_data(data)

        flash("Blood request created successfully!", "success")
        return redirect(url_for("finder_dashboard", email=form.get("email")))

    email = request.args.get("email")
    data = load_data()
    finder = next((f for f in data["finders"] if f["email"] == email), None)
    return render_template("create_request.html", finder=finder)


@app.route("/map")
def city_map():
    data = load_data()
    donors = data.get("donors", [])

    # Only approved donors with valid city
    locations = [d["city"] for d in donors if d["status"] == "approved" and d["city"]]
    return render_template("map.html", cities=locations)

# @app.route("/donor/accept-request/<request_id>", methods=["POST"])
# def accept_request(request_id):
#     email = request.args.get("email") or request.form.get("donor_email")
#     data = load_data()

#     donor = next((d for d in data["donors"] if d["email"] == email), None)
#     if not donor or donor.get("status") != "approved":
#         flash("Access denied or donor not approved.", "danger")
#         return redirect(url_for("login"))

#     for r in data.get("requests", []):
#         if r.get("id") == request_id:
#             r["status"] = "accepted"
#             r["donor_contact"] = {
#                 "name": donor["full_name"],
#                 "email": donor["email"],
#                 "phone": donor["phone"],
#                 "city": donor["city"]
#             }
#             break

#     save_data(data)
#     flash("Request accepted successfully!", "success")
#     return redirect(url_for("donor_dashboard", email=email))



@app.route("/donor/reject-request/<request_id>", methods=["POST"])
def reject_request(request_id):
    email = request.args.get("email") or request.form.get("donor_email")
    data = load_data()

    for r in data.get("requests", []):
        if r.get("id") == request_id:
            r["status"] = "rejected"
            break

    save_data(data)
    flash("Request rejected.", "info")
    return redirect(url_for("donor_dashboard", email=email))




if __name__ == "__main__":
    app.run(debug=True)
