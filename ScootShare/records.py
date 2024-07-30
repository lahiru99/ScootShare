# Store classes

class Customer():
    def __init__(self, username, f_name, l_name, ph_num, email, password, balance) -> None:
        self.username = username
        self.first_name = f_name
        self.last_name = l_name
        self.phone_number = ph_num
        self.email_address = email
        self.password = password
        self.balance = balance

    def __str__(self):
        return f"Username: {self.username}\nFirst Name: {self.first_name}\nLast Name: {self.last_name}\nPhone Number: {self.phone_number}\nEmail Address: {self.email_address}\nBalance: {self.balance}"

# "SELECT status, make, color, location, power, cost, scooter_id FROM Scooter;"


class Scooter():
    def __init__(self, status, make, color, location, power, cost, id=None) -> None:
        self.scooter_id = id
        self.status = status
        self.make = make
        self.color = color
        self.location = location
        self.power = power
        self.cost = cost


class History():
    def __init__(self, id, scooter_id) -> None:
        # Discuss how this will link to the scooter, if we have a scooterID and then get all reports bookings and repairs that relate to that scooter
        self.id = id
        self.scooter_id = scooter_id
        self.bookings = []
        self.reports = []
        self.repairs = []


class Booking():
    def __init__(self, location, scooter_id, customer, start_time, duration, cost, status, booking_id=None) -> None:
        self.location = location
        self.booking_id = booking_id
        self.scooter_id = scooter_id
        self.customer = customer
        self.start_time = start_time
        self.duration = duration
        self.cost = cost
        self.status = status

    def __str__(self):
        return f"Booking ID: {self.booking_id}\nLocation: {self.location}\nScooter ID: {self.scooter_id}\nCustomer ID: {self.customer}\nStart Time: {self.start_time}\nDuration: {self.duration}\nCost: {self.cost}\nStatus: {self.status}"


class Report():
    def __init__(self, scooter_id, description, time_of_report, status, report_id=None) -> None:
        self.id = report_id
        self.scooter_id = scooter_id
        self.description = description
        self.time_of_report = time_of_report
        self.status = status

    def __str__(self):
        return f"Report ID: {self.id}\nScooter ID: {self.scooter_id}\nDescription: {self.description}\nTime of Report: {self.time_of_report}\nStatus: {self.status}"


class Repair():
    def __init__(self, scooter_id, description, linked_report_id, time_of_repair, repair_id=None) -> None:
        self.scooter_id = scooter_id
        self.repair_id = repair_id
        self.description = description
        self.linked_report_id = linked_report_id
        self.time_of_repair = time_of_repair

    def __str__(self):
        return f"Repair ID: {self.repair_id}\nScooter ID: {self.scooter_id}\nDescription: {self.description}\nLinked Report ID: {self.linked_report_id}\nTime of Repair: {self.time_of_repair}"


class Staff():
    def __init__(self, username, password):
        self.username = username
        self.password = password


class Engineer():
    def __init__(self, username, password):
        self.username = username
        self.password = password
