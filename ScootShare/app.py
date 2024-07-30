import csv
from flask import Flask, render_template, make_response, redirect, request, jsonify, session
from flask_restful import Api, Resource, reqparse
from db import DatabaseConnector
from flask_site import site
from datetime import datetime, timedelta
from flask_restful import Api, Resource, reqparse
from records import *
import os


def seed_data() -> None:
    existing_customer = db.get_customer_object_by_username("testuser")
    if not existing_customer:
        test_user = Customer(
            username="testuser",
            f_name="John",
            l_name="Doe",
            ph_num="123-456-7890",
            email="john.doe@example.com",
            password="123",
            balance=1000.00
        )
        print('test customer added, Login with username: testuser & pw: 123')
        db.add_customer(test_user)
    else:
        print('User already exists: Login with username: testuser & pw: 123')
#Addeds a new scooter when we run 

    scooters = db.get_scooters_from_db()
    scooter_count = len(scooters)
    if scooter_count < 3: 
        print('scooter added')
        test_scooter = Scooter(
            status="Available",
            make="BrandX",
            color="Red",
            location="Street A",
            power=99,
            cost=10.00,
        )
        db.add_scoooter(test_scooter)
        print(f'scooter added, there are {scooter_count+ 1} scooters in the db')
    else:
        print(f'there are {scooter_count} scooters in the db')

app = Flask(__name__)
app.secret_key = os.urandom(24)
api = Api(app)
db = DatabaseConnector()
db.create_booking_table()
db.create_report_table()
db.create_scooter_table()
db.create_repair_table()
db.create_table()
db.create_staff_table()
db.populate_staff()
seed_data()


def parse_datetime(value: str):
    try:
        # Parse the input string as a datetime object # takes in something like this: "2023-10-05 14:30:00"
        # Adjust the format as needed
        parsed_datetime = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
        return parsed_datetime.strftime('%Y-%m-%d %H:%M:%S')
    # if you attempt to parse a string as a datetime, and the string does not match the expected format, this exception will be raised
    # bad practise to catch general exceptions but for the moment helps in debugging
    except Exception as thrown_exception:
        print(f"Error: {thrown_exception}")

def is_booking_active(bookings):
        current_time = datetime.now()
        for booking in bookings: 
            end_time = booking.start_time + timedelta(minutes=booking.duration)
            if booking.start_time <= current_time <= end_time:
                return booking
            else:
                return booking


class Registration(Resource):
    def __init__(self) -> None:
        super().__init__()
        self._cust_reg_args = reqparse.RequestParser()
        self._cust_reg_args.add_argument(
            "username", type=str, help="username")
        self._cust_reg_args.add_argument(
            "first_name", type=str, help="Customer fName")
        self._cust_reg_args.add_argument(
            "last_name", type=str, help="Customer lName")
        self._cust_reg_args.add_argument(
            "phone_number", type=str, help="phone num")
        self._cust_reg_args.add_argument(
            "email_address", type=str, help="email")
        self._cust_reg_args.add_argument(
            "password", type=str, help="password")
        self._cust_reg_args.add_argument(
            "balance", type=float, help="balance")

    def post(self):
        try:
            args = self._cust_reg_args.parse_args()
            customer_object = Customer(args['username'], args['first_name'], args['last_name'],
                                       args['phone_number'], args['email_address'],
                                       args['password'], args['balance'])
            print("Debug: ", customer_object.username,
                  customer_object.first_name,)
            print(args["username"], args["first_name"],
                  args["last_name"], args["phone_number"])
            # check if we want to do the validation here to check if the customer id already exists,
            # this is already done in the edit customer class so it would be easy to move accross
            # TODO Check if user uses prefixes for admin/engineer
            try:
                db.add_customer(customer_object)
                message = f"Account with username {customer_object.username} created successfully!"
                return message
            except Exception as e:
                # Handle the exception, and provide an error message
                message = "An error occurred while creating the account. Please try again later."
                print(message, e)
        except Exception as e:
            return "An error occurred while making the booking.\n" + str(e)


class editCustomer(Resource):
    def __init__(self) -> None:
        super().__init__()
        self._cust_post_args = reqparse.RequestParser()

        self._cust_post_args.add_argument(
            "username", type=str, help="customer username")
        self._cust_post_args.add_argument(
            "first_name", type=str, help="Customer fName")
        self._cust_post_args.add_argument(
            "last_name", type=str, help="Customer lName")
        self._cust_post_args.add_argument(
            "phone_number", type=str, help="phone num")
        self._cust_post_args.add_argument(
            "email_address", type=str, help="email")
        self._cust_post_args.add_argument(
            "password", type=str, help="password")
        self._cust_post_args.add_argument(
            "balance", type=float, help="balance")

    def post(self):
        args = self._cust_post_args.parse_args()
        updated_customer_object = Customer(
            args['username'], args['first_name'], args['last_name'],
            args['phone_number'], args['email_address'],
            args['password'], args['balance']
        )

        # Get the original information of this customer
        original_customer_data = db.get_customer_object_by_username(
            args['username'])

        # Perform validation to see what changes were made to any of the attributes
        # add balance,
        changes = {}
        if updated_customer_object.first_name != original_customer_data.first_name:
            changes['first_name'] = updated_customer_object.first_name
        if updated_customer_object.last_name != original_customer_data.last_name:
            changes['last_name'] = updated_customer_object.last_name
        if updated_customer_object.phone_number != original_customer_data.phone_number:
            changes['phone_number'] = updated_customer_object.phone_number
        if updated_customer_object.email_address != original_customer_data.email_address:
            changes['email_address'] = updated_customer_object.email_address
        # if updated_customer_object.username != original_customer_data.username: #Removed as we do not want to change a priamy key,
        # otherwise we'd need to chnage all linked reports ect
            # Check if the new username is available
            # if db.get_customer_by_id(updated_customer_object.username) is None:
            # changes['id'] = updated_customer_object.username
            # else:
            # return "Username is already in use, please choose a different one." #, 400  # Return an error response, don't tink we need this, double check

        # Update the customer's profile based on the changes dictionary
        if changes:
            # Apply the changes to the customer profile in the database
            db.update_customer_profile(
                args['current_id'], changes)
            return "You have successfully updated your profile."  # , #200

        return f"(You have made no changes for this user: {original_customer_data.username})"


class editScooter(Resource):
    def __init__(self) -> None:
        super().__init__()
        self._scooter_post_args = reqparse.RequestParser()
        self._scooter_post_args.add_argument(
            "scooter_id", type=str, help="Scooter id")  # At minimum

        # It may be better practise to get the scooter id and get the most recent data
        self._scooter_post_args.add_argument(
            "status", type=str, help="Scooter status")
        self._scooter_post_args.add_argument(
            "make", type=str, help="Scooter make")
        self._scooter_post_args.add_argument(
            "color", type=str, help="Scooter color")
        self._scooter_post_args.add_argument(
            "location", type=str, help="Scooter location")
        self._scooter_post_args.add_argument(
            "power", type=float, help="Power remaining")
        self._scooter_post_args.add_argument(
            "cost", type=float, help="Cost per min")

    def post(self):
        args = self._scooter_post_args.parse_args()
        updated_scooter_object = Scooter(
            status=args['status'],
            make=args['make'],
            color=args['color'],
            location=args['location'],
            power=args['power'],
            cost=args['cost']
        )
        original_scooter_data = db.get_scooter_by_id(
            args['scooter_id'])  # check this is all good
        # Perform validation to see what changes were made to any of the attributes

        # Note that it is important that these match the tables of the database
        changes = {}
        if updated_scooter_object.status != original_scooter_data.status:
            changes['status'] = updated_scooter_object.status
        if updated_scooter_object.make != original_scooter_data.make:
            changes['make'] = updated_scooter_object.make
        if updated_scooter_object.color != original_scooter_data.color:
            changes['color'] = updated_scooter_object.color
        if updated_scooter_object.location != original_scooter_data.location:
            changes['location'] = updated_scooter_object.location
        if updated_scooter_object.power != original_scooter_data.power:
            changes['power'] = updated_scooter_object.power
        if updated_scooter_object.cost != original_scooter_data.cost:
            changes['cost'] = updated_scooter_object.cost

        # Update the scooter's profile based on the changes dictionary
        if changes:
            # Apply the changes to the scooter profile in the database
            db.update_scooter_data(
                args['current_id'], changes)
            return "You have successfully updated the scooter profile."  # , 200
        else:
            return "You have made no changes for this scooter."


class addScooter(Resource):
    def __init__(self) -> None:
        super().__init__()
        self._scooter_post_args = reqparse.RequestParser()
        self._scooter_post_args.add_argument(
            "status", type=str, help="Scooter status")
        self._scooter_post_args.add_argument(
            "make", type=str, help="Scooter make")
        self._scooter_post_args.add_argument(
            "color", type=str, help="Scooter color")
        self._scooter_post_args.add_argument(
            "location", type=str, help="Scooter location")
        self._scooter_post_args.add_argument(
            "power", type=float, help="Power remaining")
        self._scooter_post_args.add_argument(
            "cost", type=float, help="Cost per min")

    def post(self):
        args = self._scooter_post_args.parse_args()
        scooter = Scooter(
            status=args['status'],
            make=args['make'],
            color=args['color'],
            location=args['location'],
            power=args['power'],
            cost=args['cost']
        )
        db.add_scoooter(scooter)
        listOfScooters = db.get_scooters_from_db()

        # Loop here to test
        for scooter in listOfScooters:
            print("Status:", scooter.status)
            print("Make:", scooter.make)
            print("Color:", scooter.color)
            # ScooterID will alwaysd be one if the create tables method stays in this class
            print("Scooter ID:", scooter.scooter_id)
            print("-----------")

        return f"You added a new scooter to the db colored {scooter.color} and with a charge of {scooter.power}"

  # No validation yet, this would come in the form of making sure an in progress booking cannot be cancled and a completed booking cannot be cancled
  # Though a way to assit this before it gets to this point is to only allow the user to select bookings to cancle that are valid


class cancelBooking(Resource):
    def __init__(self) -> None:
        super().__init__()
        self._booking_post_args = reqparse.RequestParser()
        # self._booking_post_args.add_argument("username", type=int, help="Customer ID")
        # Double check but all we should need to cancle a booking is the id
        self._booking_post_args.add_argument(
            "booking_id", type=int, help="booking ID")

    def post(self):
        args = self._booking_post_args.parse_args()
        booking_to_cancel_id = args['booking_id']
        db.set_booking_status(
            'canceled', booking_to_cancel_id)  # Change the status to cancled

        return f"You canceled a booking of id: {booking_to_cancel_id}"


class Make_Booking(Resource):
    def __init__(self) -> None:
        super().__init__()
        self._booking_post_args = reqparse.RequestParser()
        # First interation
        self._booking_post_args.add_argument(
            "location", type=str, help="Booking location")
        self._booking_post_args.add_argument(
            "scooter_id", type=int, help="Scooter ID")
        self._booking_post_args.add_argument(
            "username", type=str, help="username")
        # parse the time here so we can do operations to do with the starttime and checking if it conflicts with other bookings# assuming we get the data as a string
        # We should recive a string like this, "2023-10-05 14:30:00". Double check that we we recive data from the api call it will be a
        self._booking_post_args.add_argument(
            "start_time", type=parse_datetime, help="Start time")
        self._booking_post_args.add_argument(
            "duration", type=int, help="Duration")
        self._booking_post_args.add_argument(
            "cost", type=float, help="Booking cost per min")
        self._booking_post_args.add_argument(
            "status", type=str, help="Booking status")

    def post(self):
        try:
            args = self._booking_post_args.parse_args()

            purposed_booking = Booking(
                location=args['location'],
                scooter_id=args['scooter_id'],
                customer=args['username'],
                start_time=args['start_time'],
                duration=args['duration'],
                cost=args['cost'],
                status=args['status']
                )
            booking_customer = db.get_customer_object_by_username(
                args['username'])

            booking_cost = args['duration'] * args['cost']
            if booking_customer.balance - booking_cost < 0:
                # , 400  # Return an error response
                return "Insufficient funds to make the booking."

            # Check if scooter is avalable
            scooter_to_book = db.get_scooter_by_id(
                purposed_booking.scooter_id)

            if scooter_to_book.make != 'Available':
                return f"sorry, your choosen scooter is {scooter_to_book.status}"

            # Purposed booking time cannot conflicts with with booking times of other bookings, meaning the start and end time cannot overlap
            # Addionally a scooter can only be booked if it has the status avalable , it might be under repair or in use
            bookings_for_scooter = db.get_bookings_by_scooter_id(
                args['scooter_id'])
            for existing_booking in bookings_for_scooter:
                # This should be the correct type thanks to the parse datetime method
                existing_start_time = existing_booking.start_time
                existing_end_time = existing_start_time + \
                    timedelta(minutes=existing_booking.duration)

                purposed_start_time = purposed_booking.start_time
                purposed_end_time = purposed_start_time + \
                    timedelta(minutes=purposed_booking.duration)

                # Check if the proposed booking overlaps with any existing booking, # btw \ is a line continuater       #Check if the proposed booking starts while the existing booking is still ongoing.
                if (existing_start_time <= purposed_start_time < existing_end_time) or \
                        (existing_start_time < purposed_end_time <= existing_end_time):  # check if the proposed booking ends while the existing booking is still ongoing.
                    # , 400             Do this for every booking for a the choosen scooter, if no conflics then it is avalable
                    return "Booking time conflicts with an existing booking."

            db.add_booking(purposed_booking)
            return f"You have made a booking!"
        except Exception as e:
            return "An error occurred while making the booking.\n" + str(e)
# Double check if we want a made report to have any impact on scooter avalbility


class Make_Report(Resource):
    def __init__(self) -> None:
        super().__init__()
        self._report_post_args = reqparse.RequestParser()
        self._report_post_args.add_argument(
            "scooter_id", type=str, help="Scooter ID")
        self._report_post_args.add_argument(
            "description", type=str, help="Description of the repair")
        self._report_post_args.add_argument(
            "linked_report_id", type=str, help="Linked report ID")
        self._report_post_args.add_argument(
            "time_of_report", type=str, help="Time of report")
        self._report_post_args.add_argument(
            "status", type=str, help="Report status")

    def post(self):
        try:
            args = self._report_post_args.parse_args()
            report = Report(
                scooter_id=args["scooter_id"],
                description=args["description"],
                time_of_report=args["time_of_report"],
                status=args["status"]
            )
            db.add_report(report)
            return f"You made a report for scooter: {report.scooter_id} to address: {report.description}"
        except Exception as e:
            return "An error occurred while making the report.\n" + str(e)


class Make_Repair(Resource):
    def __init__(self) -> None:
        super().__init__()
        self._repair_post_args = reqparse.RequestParser()
        self._repair_post_args.add_argument(
            "scooter_id", type=str, help="Scooter ID")
        self._repair_post_args.add_argument(
            "description", type=str, help="Description of the repair")
        self._repair_post_args.add_argument(
            "linked_report_id", type=str, help="Linked report ID")
        self._repair_post_args.add_argument(
            "time_of_repair", type=str, help="Time of repair")
        # Either get this passed in or set it here as 'unaddressed' since that is what it will always be
        self._repair_post_args.add_argument(
            "status", type=str, help="Repair status")

    def post(self):
        try:
            args = self._repair_post_args.parse_args()
            repair = Repair(
                scooter_id=args['scooter_id'],
                description=args['description'],
                linked_report_id=args['linked_report_id'],
                time_of_repair=args['time_of_repair']
            )
            print('repair')
            db.add_repair(repair)
            db.set_report_status(
                repair.linked_report_id, "addressed")  # may not want this hardcoded here
            return f"You did a repair at: {repair.time_of_repair} to address: {repair.description} for scooter {repair.scooter_id}"
        except Exception as e:
            return "An error occurred while making the repair.\n" + str(e)

# This will be needed to top up the balance, though it is editing account details it is seperate from the editcustomer class


class Top_up_Balanace(Resource):
    def __init__(self) -> None:
        super().__init__()
        self._customer_post_args = reqparse.RequestParser()
        self._customer_post_args.add_argument(
            "username", type=str, help="username")
        self._customer_post_args.add_argument(
            "top_up", type=float, help="Amount to add")

    def post(self):
        args = self._customer_post_args.parse_args()
        username = args['username']
        amount = args['top_up']

        # Validate username and amount # decide if we want error messages here
        if not isinstance(amount, float) or amount <= 0:
            return "Invalid input. Please provide a valid customer ID and a positive amount."

        customer = db.get_customer_object_by_username(username)

        if customer is None:
            return f"Customer with ID {username} not found."

        # Update the balance
        customer.balance += amount
        db.update_balance(username, customer.balance)

        return f"You topped up user {username} with an amount of {amount}. New balance: {customer.balance}"


class GetCompleteHistroy(Resource):
    def __init__(self) -> None:
        super().__init__()


class GetAllRepairs(Resource):
    def __init__(self) -> None:
        super().__init__()

    def get(self):
        # Retrieve all repair instances from the database
        repairs = db.get_all_repairs()
        print('--------All repairs prepairing to send---------------')
        for repair in repairs:
            print(repair.__str__())
        print('-----------------------')
        # Format the repairs data as needed
        formatted_repairs = [{"repair_id": repair.repair_id, "scooter_id": repair.scooter_id, "description": repair.description,
                              "linked_report_id": repair.linked_report_id, "time_of_repair": repair.time_of_repair} for repair in repairs]
        return formatted_repairs


class GetAllReports(Resource):
    def __init__(self) -> None:
        super().__init__()

    def get(self):
        try:
            # Retrieve all report instances from the database
            reports = db.get_all_reports()
            print('---------ALL REPORTS prepairing to send--------------')
            for report in reports:
                print(report.__str__())
            print('-----------------------')
            # Format the reports data as needed
            formatted_reports = [{"report_id": report.id, "scooter_id": report.scooter_id, "description": report.description,
                                  "time_of_report": str(report.time_of_report), "status": report.status} for report in reports]
            return formatted_reports
        except Exception as e:
            return "An error occurred while getting all reports.\n" + str(e)


class GetAllBookings(Resource):
    def __init__(self) -> None:
        super().__init__()

    def get(self):
        bookings = db.get_all_bookings()
        print('--------All booki gs to be sent to API requester-------')
        for booking in bookings:
            print(booking.__str__())
        print('-----------------------')
        formatted_bookings = [
            {
                "location": booking.location,
                "scooter_id": booking.scooter_id,
                "username": booking.customer,
                "start_time": booking.start_time,
                "duration": booking.duration,
                "cost": booking.cost,
                "status": booking.status,
                "booking_id": booking.booking_id
            }
            for booking in bookings
        ]
        return formatted_bookings


class GetAllScooters(Resource):
    def __init__(self) -> None:
        super().__init__()

    def get(self):
        scooters = db.get_scooters_from_db()
        print('--------All scooters to be sent to API requester-------')
        for scooter in scooters:
            print(scooter.__str__())
        print('-----------------------')
        formatted_scooters = [
            {
                "status": scooter.status,
                "make": scooter.make,
                "color": scooter.color,
                "location": scooter.location,
                "power": scooter.power,
                "cost": scooter.cost,
                "scooter_id": scooter.scooter_id
            }
            for scooter in scooters
        ]
        # Double check this can be sent of if we need to use json.dump()
        return formatted_scooters


class GetAllCustomers(Resource):
    def __init__(self) -> None:
        super().__init__()

    def get(self):
        customers = db.get_all_customers()
        print('--------All customers to be sent to API requester-------')
        for customer in customers:
            print(customer.__str__())
        print('-----------------------')
        formatted_customers = [
            {
                "username": customer.username,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "email_address": customer.email_address,
                "balance": customer.balance
            }
            for customer in customers
        ]
        return formatted_customers


class GetSingleCustomerByID(Resource):
    def __init__(self) -> None:
        super().__init__()
        self._cust_post_args = reqparse.RequestParser()
        self._cust_post_args.add_argument(
            "username", type=str, help="CustomerID")

    def get(self):
        try:
            args = self._cust_post_args.parse_args()
            customer_to_find_id = args["username"]
            customer_object = db.get_customer_object_by_username(
                customer_to_find_id)

            if customer_object:
                formatted_customer = {
                    "username": customer_object.username,
                    "first_name": customer_object.first_name,
                    "last_name": customer_object.last_name,
                    "phone_number": customer_object.phone_number,
                    "email_address": customer_object.email_address,
                    "password": customer_object.password,
                    "balance": float(customer_object.balance)
                }
                return formatted_customer
            else:
                return {"message": "Customer not found"}  # , 404
        except Exception as e:
            return "An error occurred while getting the customer.\n" + str(e)


class Login(Resource):
    def __init__(self) -> None:
        super().__init__()
        self._cust_login_args = reqparse.RequestParser()
        self._cust_login_args.add_argument(
            "username", type=str, help="username")
        self._cust_login_args.add_argument(
            "password", type=str, help="password")

    def post(self):
        try:
            args = self._cust_login_args.parse_args()
            username = args['username']
            password = args['password']
            if username.startswith('~'):
                # The username starts with ~, indicating an admin
                staff = db.get_staff(username, password)
                if staff:
                    print(f"Successfully signed in as admin: {staff.username}")
                    response_data = {'user_type': 'admin',
                                        'username': staff.username}
                    return jsonify(response_data)
            elif username.startswith('_'):
                # The username starts with _, indicating an engineer
                staff = db.get_staff(username, password)
                if staff:
                    print(f"Successfully signed in as engineer: {staff.username}")
                    response_data = {'user_type': 'engineer',
                                        'username': staff.username}
                    return jsonify(response_data)
            else:
                print("Check if the username exists among regular customers")
                customer = db.get_customer(username, password)
                if customer:
                    print(
                        f"Successfully signed in as customer: {customer.username}")
                    response_data = {'user_type': 'customer',
                                        'username': customer.username}
                    return jsonify(response_data)

                # If the user is not found in any category, return an error response
                error_response = {'error': 'Invalid credentials'}
                return jsonify(error_response), 401
        except Exception as e:
            print(e)
            return "An error occurred while logging in.\n" + str(e)


class console_Login(Resource):
    def __init__(self) -> None:
        super().__init__()
        self._cust_login_args = reqparse.RequestParser()
        self._cust_login_args.add_argument(
            "username", type=str, help="username")
        self._cust_login_args.add_argument(
            "password", type=str, help="password")

    def post(self):
        try:
            args = self._cust_login_args.parse_args()
            username = args['username']
            password = args['password']

            customer = db.get_customer(username, password)

            if customer is not None:
                return {"success": True}

        except Exception as e:
            print(e)
            print("An error occurred while logging in through AP.\n" + str(e))
            return {"success": False}

class console_find_Booking():
     def __init__(self) -> None:
        super().__init__()
        self._cust_booking_args = reqparse.RequestParser()
        self._cust_booking_args.add_argument(
            "customer", type=str, help="bookings username")
        self._cust_booking_args.add_argument(
            "scooter_id", type=int, help="scooter id of booking")
        
    
     def post(self):
        try:
            args = self._cust_booking_args.parse_args()
            bookings = db.get_scooter_bookings_for_customer(args['customer'], args['scooter_id'])
            booking = is_booking_active(bookings)

            formatted_booking={
                "location": booking.location,
                "scooter_id": booking.scooter_id,
                "username": booking.customer,
                "start_time": booking.start_time,
                "duration": booking.duration,
                "cost": booking.cost,
                "status": booking.status,
                "booking_id": booking.booking_id
            }
            return formatted_booking

        except Exception as e:
            print(e)
            print("An error occurred while logging in through AP.\n" + str(e))
            return None
        

class update_booking_status():
    def __init__(self) -> None:
        super().__init__()
        self._booking_args = reqparse.RequestParser()
        self._booking_args.add_argument(
            "booking_id", type=int, help="booking id to update")
        self._booking_args.add_argument(
            "new_status", type=str, help="new status of booking")
        
    def post(self):
                try: 
                    args = self._booking_args.parse_args()
                    db.set_booking_status(args['new_status'],args['booking_id'] )
                    return {"result: True"}
                except Exception as e:
                    print(e)
                    print("An error occurred while logging in through AP.\n" + str(e))
                    return {"result": False}



# Console API calls

#api.add_resource(console_Login, "/api/booking_login")
#api.add_resource(console_find_Booking, "/api/get_single_booking")
#api.add_resource(update_booking_status, "/api/update_booking_status")



# Retreives
api.add_resource(GetAllRepairs, "/api/all_repairs")
api.add_resource(GetAllReports, "/api/all_reports")
api.add_resource(GetAllBookings, "/api/all_bookings")
api.add_resource(GetAllScooters, "/api/all_scooters")
api.add_resource(GetAllCustomers, "/api/all_customers")

# Need to check this one is done right
api.add_resource(GetSingleCustomerByID, "/api/get_customer")

# Actions
api.add_resource(addScooter, '/api/add_scooter', methods=['POST'])
api.add_resource(Make_Booking, "/api/add_booking", methods=['POST'])
api.add_resource(Make_Report, "/api/new_report", methods=['POST'])
api.add_resource(Make_Repair, "/api/new_repair", methods=['POST'])
api.add_resource(Top_up_Balanace, "/api/top_up", methods=['POST'])
api.add_resource(editScooter, '/api/edit_scooter', methods=['POST'])
api.add_resource(editCustomer, "/api/edit_customer", methods=['POST'])
api.add_resource(cancelBooking, "/api/cancel_booking", methods=['POST'])

api.add_resource(Registration, '/api/register', methods=['POST'])
api.add_resource(Login, '/api/login', methods=['GET', 'POST'])

app.register_blueprint(site)






if __name__ == "__main__":
    # app.run(host="0.0.0.0", debug=True)
    app.run(debug=True)

    
    

    
