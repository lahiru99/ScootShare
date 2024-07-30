import pandas as pd
from records import *
from db_utils import hash_password, verify_password
import pymysql

class DatabaseConnector():
    def __init__(self) -> None:
        #self._ADDRESS = '34.129.153.24' #This is Lachlans 
        self._ADDRESS = '34.151.70.244' #This is Joshuas cloud instance #All details of my cloud instace match user,pw and db name
        self._USER = 'root'
        self._PASSWORD = 'scootshare'
        self._DATABASE = 'scoot_share'

        self._connection = pymysql.connect(host=self._ADDRESS,
                                             user=self._USER,
                                             password=self._PASSWORD,
                                             db=self._DATABASE,
                                             charset='utf8mb4',
                                             cursorclass=pymysql.cursors.Cursor)

    def create_table(self) -> None:
        with self._connection.cursor() as cur:
            # Temporary while db is local
            cur.execute("CREATE TABLE IF NOT EXISTS Customer (  \
                        username VARCHAR(50) PRIMARY KEY,   \
                        first_name VARCHAR(255),            \
                        last_name VARCHAR(255),             \
                        phone_number VARCHAR(20),           \
                        email_address VARCHAR(255),         \
                        password VARCHAR(255),              \
                        balance DECIMAL(10, 2));"
                        )
            self._connection.commit()

    def create_staff_table(self) -> None:
        with self._connection.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS Staff")
            cur.execute("CREATE TABLE IF NOT EXISTS Staff (            \
                        username VARCHAR(50),       \
                        password VARCHAR(255));"
                        )
            self._connection.commit()

    def add_customer(self, new_customer: Customer) -> None:
        with self._connection.cursor() as cur:
            query = "INSERT INTO Customer (username, first_name, last_name, \
                    phone_number, email_address, password, balance) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            customer_data = (new_customer.username,  # username is primary key
                             new_customer.first_name,
                             new_customer.last_name,
                             new_customer.phone_number,
                             new_customer.email_address,
                             hash_password(new_customer.password),
                             new_customer.balance)
            cur.execute(query, customer_data)
            self._connection.commit()

    def get_customer(self, username: str, password: str) -> Customer:
        with self._connection.cursor() as cur:
            # get customer record by username
            query = "SELECT * FROM Customer WHERE username = %s"
            print("Querying database for username:", username)
            cur.execute(query, (username,))
            result = cur.fetchone()
            if result is None:
                # Handle the case where the user is not found
                return None
        # Check if the password matches
        # Get stored password from db result
        stored_password = result[5]
        if not verify_password(stored_password, password):
            # Password does not match
            return None

        # create customer object from db
        customer = Customer(
            result[0], result[1], result[2], result[3], result[4], result[5], result[6])
        # return customer object
        print("username: ", customer.username, "password: ", customer.password)
        return customer

    def get_staff(self, username: str, password: str):
        with self._connection.cursor() as cur:
            query = "SELECT * FROM Staff WHERE username = %s;"
            cur.execute(query, (username,))
            result = cur.fetchone()
            if result is None:
                return None
            stored_password_hash = result[5]
            if not verify_password(stored_password_hash, password):
                return None

            # Create a Staff object and return it
            # Adjust this line to match your Staff class constructor
            staff = Staff(username, password)
            return staff

    def get_customer_object_by_username(self, username):
        """
        Get a customer by their username.

        Args:
            username: The username of the customer to retrieve.

        Returns:
            Customer or None: A Customer object if found, or None if not found.
        """
        with self._connection.cursor() as cur:
            query = "SELECT * FROM Customer WHERE username = %s"
            cur.execute(query, (username,))
            result = cur.fetchone()
            print(result)
            if result:
                username, first_name, last_name, phone_number, email_address, password, balance = result
                return Customer(username, first_name, last_name, phone_number, email_address, password, balance)
            else:
                return None

# Should we add docstrings to our methods? #This may not be needed if i can do it all in the update_customer_prfile method
    def update_balance(self, username, updated_balance):
        """
        Update the balance for a customer.

        Args:
            username (str): The ID of the customer to update.
            updated_balance (float): The new balance for the customer.
        """
        with self._connection.cursor() as cur:
            query = "UPDATE Customer SET balance = %s WHERE username = %s"
            cur.execute(query, (updated_balance, username))
            self._connection.commit()

# Takes in a dic of changes and a customerID to make the changes to
    def update_customer_profile(self, username, changes):
        """
        Update a customer's profile in the database with the provided changes.

        Args:
            username: The ID of the customer to update.
            changes (dict): A dictionary of changes to apply to the customer's profile.
        """
        with self._connection.cursor() as cur:
            # Create SQL query to update the customer's profile, #changes is a dictionary, get all keys amd get all values for each key then seperate by a comma
            set_values = ', '.join([f"{key} = ?" for key in changes.keys()])
            query = f"UPDATE Customer SET {set_values} WHERE username = ?"
            # Lets say a dic was put in changes = {  "first_name": "NewFirstName",    "last_name": "NewLastName",  "email_address": "newemail@example.com"
            # The query would end up like this #UPDATE Customer SET first_name = ?, last_name = ?, email_address = ? WHERE id = ?

            # Add values to update and the customer# Values will "contain id = newid, last_name = newlastname, email_address = newemail@example.com"
            values = list(changes.values())
            # append to last to match up with the WHERE id = ?" being last
            values.append(username)

            # Execute the update query with parameters
            cur.execute(query, tuple(values))
            self._connection.commit()


    def get_all_customers(self):
        with self._connection.cursor() as cur:
            query = "SELECT * FROM Customer"
            cur.execute(query)
            results = cur.fetchall()

            customers = []
            for result in results:
                username, f_name, l_name, ph_num, email, password, balance = result
                customer = Customer(username, f_name,
                                    l_name, ph_num, email, password, balance)
                customers.append(customer)

            return customers


# Scooter related database interactions - Bookings, repairs and reports # check if we need to make an individual histroy table

# Discuss if we will merge all the create table methods
# Also this seems to be incrementing incorrectly


    def create_scooter_table(self):
        with self._connection.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS Scooter (  \
                        scooter_id INTEGER PRIMARY KEY AUTO_INCREMENT,         \
                        status VARCHAR(255),          \
                        make VARCHAR(255),          \
                        color VARCHAR(255),         \
                        location VARCHAR(255),      \
                        power DECIMAL(10, 2),       \
                        cost DECIMAL(10, 2));")
            self._connection.commit()

    # This is auto incrementing correctly, though each run of the program is added a new instance to the db

    def create_booking_table(self):
        with self._connection.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS Booking (  \
                        booking_id INTEGER PRIMARY KEY AUTO_INCREMENT,                              \
                        location VARCHAR(255),               \
                        scooter_id INT,                              \
                        username VARCHAR(255),                             \
                        start_time DATETIME,                         \
                        duration DECIMAL(10, 2),                     \
                        cost DECIMAL(10, 2),                         \
                        status VARCHAR(255));")
            self._connection.commit()

    def create_report_table(self):
        with self._connection.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS Report (      \
                        report_id INTEGER PRIMARY KEY AUTO_INCREMENT,  \
                        scooter_id INT,                             \
                        description TEXT,                          \
                        time_of_report DATETIME,                    \
                        status VARCHAR(255));")
            self._connection.commit()

    def create_repair_table(self):
        with self._connection.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS Repair (      \
                        repair_id INTEGER PRIMARY KEY AUTO_INCREMENT,  \
                        scooter_id INT,                             \
                        description TEXT,                          \
                        linked_report_id INT,                      \
                        time_of_repair DATETIME);")

            self._connection.commit()

     # Scooteer related methods

# Simply adds a new scooter instance to the database, #Does not need to include the ID as that is auto incremented in the database

    def add_scoooter(self, new_scooter: Scooter):
        with self._connection.cursor() as cur:
            query = "INSERT INTO Scooter (status, make, color, location, power, cost) VALUES (%s, %s, %s, %s, %s, %s)"
            scooter_data = (
                new_scooter.status,
                new_scooter.make,
                new_scooter.color,
                new_scooter.location,
                new_scooter.power,
                new_scooter.cost)
            cur.execute(query, scooter_data)
            self._connection.commit()

    def update_scooter_data(self, scooter_id, changes):
        """
        Update a scooter's data in the database with the provided changes.

        Args:
            scooter_id (int): The ID of the scooter to update.
            changes (dict): A dictionary of changes to apply to the scooter's profile. Made up of the attribute to change and the new data itself
        """
        with self._connection.cursor() as cur:
            # Create SQL query to update the scooter's profile
            set_values = ', '.join([f"{key} = ?" for key in changes.keys()])
            query = f"UPDATE Scooter SET {set_values} WHERE id = ?"

            # Add values to update and the scooter ID
            values = list(changes.values())
            values.append(scooter_id)

            # Execute the update query with parameters
            cur.execute(query, tuple(values))
            self._connection.commit()
            # return True  # Update successful


# Takes in an id and updates the status of that scooter


    def change_scooter_status(self, scooter_id, new_status):
        with self._connection.cursor() as cur:
            query = "UPDATE Scooter SET status = %s WHERE id = %s"
            cur.execute(query, (new_status, scooter_id))
            self._connection.commit()


# Get a specfic scooter by ID


    def get_scooter_by_id(self, scooter_id):
        with self._connection.cursor() as cur:
            query = "SELECT * FROM Scooter WHERE scooter_id = %s"
            print(scooter_id)
            cur.execute(query, (scooter_id,))
            row = cur.fetchone()

            if row:
                # Map the retrieved data to a Scooter object, id, status, make, color , location, power, cost
                scooter = Scooter(row[0], row[1], row[2],
                                  row[3], row[4], row[5], row[6])
                return scooter
            else:
                return None

# Gets all scooters in the db
    def get_scooters_from_db(self):
        with self._connection.cursor() as cur:
            query = "SELECT status, make, color, location, power, cost, scooter_id FROM Scooter;"
            cur.execute(query)
            scooters_data = cur.fetchall()

        scooters = [Scooter(*row) for row in scooters_data]

        return scooters


    def get_bookings_from_db(self):
        with self._connection.cursor() as cur:
            query = "SELECT * FROM Booking;"
            cur.execute(query)
            booking_data = cur.fetchall()

        bookings = [Booking(*row) for row in booking_data]

        return bookings

    def get_scooter_bookings_for_customer(self, customerID, scooterID):
        with self._connection.cursor() as cur:
            query = "SELECT * FROM Booking WHERE username = %s AND scooter_ID = %s;"
            cur.execute(query, (customerID, scooterID))
            booking_data = cur.fetchall()

        bookings = [Booking(*row) for row in booking_data]

        return bookings



    def get_customers_from_db(self):
        with self._connection.cursor() as cur:
            query = "SELECT username, first_name, last_name, phone_number, email_address, password, balance FROM Customer;"
            cur.execute(query)
            customers_data = cur.fetchall()

        customers = [Customer(*row) for row in customers_data]

        return customers


# Booking related methods
# Takes in a single id and retrives the booking, tho assumes the id is unique


    def get_booking_by_id(self, booking_id):
        with self._connection.cursor() as cur:
            query = "SELECT * FROM Booking WHERE id = %s"
            cur.execute(query, (booking_id))
            row = cur.fetchone()
            # Double check that this maps out correctly when getting the db data in an instance
            if row:
                Booking = Booking(row[0], row[1], row[2],
                                  row[3], row[4], row[5], row[6], row[7])
                return Booking
            else:
                return None

    # Returns all bookings ever made

    def get_all_bookings_orignal(self):
        with self._connection.cursor() as cur:
            query = "SELECT booking_location, scooter_id, customer_id, start_time, duration, cost, status, booking_id FROM Booking"
            cur.execute(query)
            booking_data = cur.fetchall()
            print("------------Showing all existing bookings-----------")
            for row in booking_data:
                booking = Booking(*row)
                print("Location:", booking.location)
                print("Booking ID:", booking.booking_id)
                print("Scooter ID:", booking.scooter_id)
                print("Customer ID:", booking.customer)
                print("Start Time:", booking.start_time)
                print("Duration:", booking.duration)
                print("Cost:", booking.cost)
                print("Status:", booking.status)
                print("-----------")

        bookings = [Booking(*row) for row in booking_data]
        return bookings

    def get_all_bookings(self):
        with self._connection.cursor() as cur:
            query = "SELECT * FROM Booking"
            cur.execute(query)
            results = cur.fetchall()

            bookings = []
            for result in results:
                booking_location, scooter_id, customer_id, start_time, duration, cost, status, booking_id = result
                booking = Booking(booking_location, scooter_id, customer_id,
                                  start_time, duration, cost, status, booking_id)
                print(booking)
                bookings.append(booking)

            return bookings


# Takes in a customerID and gets all bookings attached to that customer
    def get_bookings_by_customer_id(self, customer_id):
        with self._connection.cursor() as cur:
            query = "SELECT * FROM Booking WHERE customer_id = %s"
            cur.execute(query, (customer_id,))
            booking_data = cur.fetchall()

        bookings = [Booking(*row) for row in booking_data]
        return bookings

    # Takes in a scooterID and gets all bookings for that scooter

    def get_bookings_by_scooter_id(self, scooter_id):
        with self._connection.cursor() as cur:
            query = "SELECT * FROM Booking WHERE scooter_id = %s"
            cur.execute(query, (scooter_id,))
            booking_data = cur.fetchall()

        bookings = [Booking(*row) for row in booking_data]
        return bookings


# Takes in a booking instance and sends it to the database, id is left out as it is assinged in the db

    def add_booking(self, new_booking: Booking):
        with self._connection.cursor() as cur:
            query = "INSERT INTO Booking (location, scooter_id, username, start_time, duration, cost, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            booking_data = (new_booking.location,
                            new_booking.scooter_id,
                            new_booking.customer,
                            new_booking.start_time,
                            new_booking.duration,
                            new_booking.cost,
                            new_booking.status)
            cur.execute(query, booking_data)
            self._connection.commit()

    def set_booking_status(self, new_status, booking_id):
        with self._connection.cursor() as cur:
            query = "UPDATE Booking SET status = %s WHERE booking_id = %s"
            cur.execute(query, (new_status, booking_id))
            self._connection.commit()


# Repair methods


    def get_repairs_by_scooter_id(self, scooter_id):
        with self._connection.cursor() as cur:
            query = "SELECT * FROM Repair WHERE scooter_id = %s"
            cur.execute(query, (scooter_id,))
            repair_data = cur.fetchall()

        repairs = [Repair(*row) for row in repair_data]
        return repairs

    def get_all_repairs(self):
        with self._connection.cursor() as cur:
            query = "SELECT scooter_id, description, linked_report_id, time_of_repair, repair_id FROM Repair"

            cur.execute(query)
            results = cur.fetchall()

            repairs = []
            for result in results:
                scooter_id, description, linked_report_id, time_of_repair, repair_id = result
                repair = Repair(scooter_id, description,
                                linked_report_id, time_of_repair, repair_id)
                print('--------------ALL REPAIRS-------')
                print(repair.__str__())
                repairs.append(repair)

            return repairs

    def add_repair(self, new_repair: Repair):
        with self._connection.cursor() as cur:
            query = "INSERT INTO Repair (scooter_id, description, linked_report_id, time_of_repair) VALUES (%s, %s, %s, %s)"
            repair_data = (new_repair.scooter_id, new_repair.description,
                           new_repair.linked_report_id, new_repair.time_of_repair)
            cur.execute(query, repair_data)
            self._connection.commit()


# Report methods


    def add_report(self, new_report: Report):
        print(new_report.__str__())
        with self._connection.cursor() as cur:
            query = "INSERT INTO Report (scooter_id, description, time_of_report, status) VALUES (%s, %s, %s, %s)"
            report_data = (new_report.scooter_id, new_report.description,
                           new_report.time_of_report, new_report.status)
            cur.execute(query, report_data)
            self._connection.commit()


# returns a report based on a reportID


    def get_report(self, report_id):
        with self._connection.cursor() as cur:
            query = "SELECT scooter_id, description, time_of_report, status, report_id FROM Report WHERE id = %s"
            cur.execute(query, (report_id,))
            result = cur.fetchone()
            if result:
                scooter_id, description, time_of_report, status, report_id = result
               # return Report(report_id, scooter_id, description, time_of_report, status)
                # Spent ages trying to figure this out, was assinging the values incorrectly
                return Report(scooter_id, description, time_of_report, status, report_id)
            else:
                return None

    def set_report_status(self, report_id, new_status):
        with self._connection.cursor() as cur:
            query = "UPDATE Report SET status = %s WHERE report_id = %s"
            cur.execute(query, (new_status, report_id))
            self._connection.commit()

    def change_report_status(self, report_id, new_status):
        with self._connection.cursor() as cur:
            query = "UPDATE Report SET status = %s WHERE id = %s"
            cur.execute(query, (new_status, report_id))
            self._connection.commit()

    def get_all_reports(self):
        with self._connection.cursor() as cur:
            # query = "SELECT * FROM Report" #This does not gureentee order
            query = "SELECT scooter_id, description, time_of_report, status, report_id FROM Report"
            cur.execute(query)
            results = cur.fetchall()

            reports = []
            for result in results:
                scooter_id, description, time_of_report, status, report_id = result
                report = Report(scooter_id, description,
                                time_of_report, status, report_id)
                reports.append(report)

            return reports

    def get_reports_by_scooter_id(self, scooter_id):
        with self._connection.cursor() as cur:
            query = "SELECT * FROM Report WHERE scooter_id = %s"
            cur.execute(query, (scooter_id,))
            report_data = cur.fetchall()

        reports = [Report(*row) for row in report_data]
        return reports

    # Double check where the we are getting username and password from

    def populate_staff(self):
        with self._connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM Staff")
            row = cur.fetchone()
            if row is not None:
                count = row[0]
                if count == 0:
                    query = "INSERT INTO Staff (username, password) VALUES (%s, %s)"
                    staff_data = [
                        ('~admin', hash_password('admin')),
                        ('_engineer', hash_password('engineer'))
                    ]
                    cur.executemany(query, staff_data)
                    self._connection.commit()
   
   
    #TODO : Compare with get-Staff
    def get_engineer(self, username: str, password: str) -> Engineer:
            with self._connection.cursor() as cur:
                # get engineer record by username
                query = "SELECT * FROM Engineer WHERE username = %s;"
                print("Querying database for username:", username)
                cur.execute(query, (username,))
                result = cur.fetchone()
                if result is None:
                    # Handle the case where the user is not found
                    return None

                # Check if the password matches
                # Get stored password from db result
                stored_password = result[1]
                if not verify_password(stored_password, password):
                    # Password does not match
                    return None

                # create engineer object from db
                engineer = Engineer(
                    result[0], result[1])
                # return customer object
                return engineer
            

