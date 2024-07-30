import socket
from records import *
import datetime
import time

#Change to bcrypt 
from passlib.hash import sha256_crypt
import socket_utils
#HOST = input("Enter IP address of server: ") # Defaults to listen on all Ip's
HOST = "192.168.20.11" # This needs to be specfic to the machine the server/main pi is listening on
PORT = 65000
ADDRESS = (HOST, PORT)



def wake_up():
    while True:
        username = input("Enter Username: ")
        password = input("Enter Password: ")
        hashed_password = sha256_crypt.hash(password)  # Change hash algorithm if necessary

        if login(username, hashed_password):  # Assuming login function exists and returns True on success
            booking = look_for_booking(username)  # Assuming look_for_booking function exists
            if booking:
                if confirm_booking_start_with_user():
                    if not start_booking(booking):  # Start timer
                        #change_status(booking.booking_id, "completed")  # Change status and send to database
                        send_user_reply(False)
                        break
                    else:
                        send_user_reply(True)
            else:
                send_user_reply(False)# I need to say that the user said no to the booking if attempt start is false or if booking is None
                break
            break
        else:
            continue  # Restart the login process

    wake_up()



# Login Send and Login wait 
def login(username, password):
    print("Attempting to connect to the server...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(ADDRESS)
        # Send cusotmer_id and hashed password to server
        login_data = {"username": username, "password": password}
        socket_utils.sendJson(s, login_data)

        print("Sent credentials for review")
        print("Waiting for Master Pi reponse")
        s.listen() #Allows us to except connections, see if this is meant to be here
######################

        while(True):
            conn, addr = s.accept()
            with conn:
                object = socket_utils.recvJson(conn)

                if("Login" in object):
                    if object["Login"] == "success":
                        print(f"You have logged in {username}")
                        return True
                print("Login failed. Please re-enter your details.")
                return False

#Booking info send, wait for result
def look_for_booking(username):
    while True:
        scooter_id = input("Enter the scooter ID for your booked scooter: ")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(ADDRESS)
            print("Connected to the server.")

            booking_data = {"scooter_id": scooter_id, "username": username}
            socket_utils.sendJson(s, booking_data)

#Now wait to receive the booking 
        print("Username and booking ID sent, Waiting for Master Pi to send booking data or None")
        booking = socket_utils.recvJson(s)
        
        if booking is None:
            print("No booking was found")   
            return None

        received_booking_data = booking["Booking"]
        received_booking = Booking(
            received_booking_data["location"],
            received_booking_data["scooter_id"],
            received_booking_data["customer_id"],
            received_booking_data["start_time"],
            received_booking_data["duration"],
            received_booking_data["cost"],
            received_booking_data["status"],
            received_booking_data["booking_id"]
        )
        print("Received Booking Object:")
        print(received_booking.__str__)
        return received_booking
       


def confirm_booking_start_with_user():
    while True:
        response = input("Would you like to start the booking? Y or N: ")
        if response == "Y":
            return True
        elif response == "N":
            return False
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")


def send_user_reply(result):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(ADDRESS)
        print("Connected to the server.")

    if not result:
        data = {"reply": "no"}
    else: 
        data = {"reply": "yes"}
    socket_utils.sendJson(s, data)
    


def send_end_booking_message():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(ADDRESS)
        print("Telling the MP the booking has ended")
        data = {"status": "completed"}   
        socket_utils.sendJson(s, data)


#Send request to start, send end request
def start_booking(booking):
    # Get the current time in "%Y-%m-%d %H:%M:%S" format
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calculate the booking end time
    booking_start_time = datetime.datetime.strptime(booking.start_time, "%Y-%m-%d %H:%M:%S")
    booking_end_time = booking_start_time + datetime.timedelta(minutes=booking.duration)
     #manage if duration is represented as a straing or int, such as 10 for 10 mins

    # Check if the current time is after the booking end time
    if current_time <= booking_end_time.strftime("%Y-%m-%d %H:%M:%S"):
        print("Booking can start now.")
        
        # Calculate the time remaining until the booking end time
        time_remaining = (booking_end_time - datetime.datetime.now()).total_seconds()
        #change_status(booking.booking_id,"started")
        # Start a timer for the remaining time  #We will also wanna show a status chnage on the sensehat LED
        while time_remaining > 0:
            print(f"Time remaining: {int(time_remaining / 60)} minutes {int(time_remaining % 60)} seconds", end='\r')
            time.sleep(1)
            time_remaining -= 1
        
        print("Booking has ended.")
        #change_status(booking.booking_id,"completed")
        # Here, you can update the booking status as "completed" in the database
        return True
    else:
        print("Booking cannot now as we are past the endtime")
        return False

   
       


#Decided to do all the status changes on the server side 
#def change_status(booking_id, new_status):
  #  status_data = {"booking_id": booking_id,"new_status": new_status}
   # socket_utils.sendJson(socket, status_data)
   # print(f'Status changed to: {new_status} for bookingid: {booking_id}')








wake_up()












#Beginining notes

#We need a login function , to take username and password
#We need to also ask for the scooter id that the user has booked for

#On login send credentials to MP/server.   #server will contact API and get credentials to match from db
#Recive a true or false to determine if login was successful 


#If the login was successful we now want to deal with booking tracking/activation 
#We need to determine whihch booking in the db is the intented to be used 

#Get all bookings for a scooter id
#Filter those bookings by customer id, that way we have all bookibgs for a particualr user for a particualr scooter 

#Loop through list of these bookings
#If current time  is after the start time of the booking but also before the end time of the booking instance we can determine that this is the booking we are looking for
# 
#  #The booking status also needs to be kept in mind as we will need to change this, aswell as maybe the scooter status\

#One more not iis that a scooter is locked or unlocked, during the duration of a bokking it is set as unlocked - double check this -


#We may need an alarm for endtime
#If the booking status is started/in progress we want to end the booking when the current time = to end time 
# Updated data will also need to be resent to the MP and to the db 