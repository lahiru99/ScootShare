# Flask main
from flask import Flask, Blueprint, render_template, make_response, redirect, request, jsonify, session, flash
from records import Customer
from db import DatabaseConnector

site = Blueprint("site", __name__)
# You can change the session type as needed
db = DatabaseConnector()

# Frontend Routes


@site.route("/", methods=['GET'])
def landing_view():
    return render_template("landing.html")


@site.route('/register', methods=["GET", "POST"])
def register_view():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "PUT":
        return "Success"


@site.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        # Assuming you have some logic here to validate the user's credentials
        # Once validated:
        username = request.form.get('username')
        customer = db.get_customer_object_by_username(username)
        if customer:
            session['username'] = username
            session['balance'] = customer.balance
        return redirect(url_for('site.booking_view')) #Check this


@site.route('/booking', methods=['GET'])
def booking_view():
    # Fetch all scooters from the database
    all_scooters = db.get_scooters_from_db()
    # Filter the scooters to only include those with status 'available' (case-insensitive)
    available_scooters = [
        scooter for scooter in all_scooters if scooter.status.lower() == 'available']

    return render_template("booking.html", available_scooters=available_scooters)


@site.route('/dashboard', methods=['GET', 'POST'])
def dashboard_view():
    return render_template("dashboard.html")


@site.route('/engineer_dashboard', methods=['GET', 'POST'])
def engineer_dashboard_view():
    return render_template("engineer_dashboard.html")


@site.route('/report_issue')
def report_issue():
    return render_template('report_issue.html')


@site.route('/submit_issue', methods=['POST'])
def submit_issue():
    return render_template('booking.html')


@site.route('/top-up', methods=['POST'])
def top_up_balance():
    data = request.json
    username = data.get('username')
    top_up_amount = data.get('top_up')

    if not username or not isinstance(top_up_amount, (int, float)) or top_up_amount <= 0:
        return jsonify({"message": "Invalid input. Please provide a valid username and a positive amount."}), 400

    customer = db.get_customer_object_by_username(username)
    if not customer:
        return jsonify({"message": f"Customer with username {username} not found."}), 404

    customer.balance += top_up_amount
    db.update_balance(username, customer.balance)
    session['balance'] = customer.balance  # Update balance in session

    return jsonify({"message": f"You topped up user {username} with an amount of {top_up_amount}. New balance: {customer.balance}"})


@site.route('/balance', methods=['POST'])
def balance():
    data = request.json
    username = data.get('username')

    customer = db.get_customer_object_by_username(username)
    if not customer:
        return jsonify({"message": f"Customer with username {username} not found."}), 404

    session['balance'] = customer.balance  # Update balance in session

    return jsonify({"message": f"You are Logged in as {username}. Your balance is: {customer.balance}"})


@site.route('/get_scooters', methods=['GET'])
def get_scooters():
    # Replace this with your logic to fetch scooter data from the server
    scooter_data = [
        {
            'scooter_id': 1,
            'status': 'Available',
            'make': 'Scooter Make',
            'color': 'Scooter Color',
            'location': 'Scooter Location',
            'power': 'Scooter Power',
            'cost': 10.0,
        },
        # Add more scooter data as needed
    ]
    return render_template('your_template.html', available_scooters=scooter_data)
