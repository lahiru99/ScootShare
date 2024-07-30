import socket
import requests, json
from passlib.hash import sha256_crypt
import datetime
import socket_utils
from records import *
#Import records
BASE = "http://127.0.0.1:5000/" #
#USERNAME = "admin"
#PASSWORD_HASH = sha256_crypt.hash("pass123")
HOST = ""
PORT = 65000
ADDRESS = (HOST, PORT)







def main():
    
    login_data = wait_for_login_input() #Getting this error:too many values to unpack (expected 2)
    if login_data:
        username, password = login_data
        print('about to send to api')
        result = validate_login_from_api(username, password)

        #Now we validate with api
        
        send_login_result(result) #Boolean for true or false if the login was approaved by the api
        if not result:
            print('Failure to sign in') # Restart 
            main() #Wanting to move

        for username,scooter_id in wait_for_scooter_id():      
            booking_object = find_booking_from_api(username, scooter_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            #Send the booking details to client, determine if they are starting the booking #(retruns a true or false)
            if send_booking_determine_ifto_start(booking_object):
                    updateBookingStatus(booking_object.id, 'started') #ensure this matches up with the records class# API method

                    status =wait_for_booking_end()
                    updateBookingStatus(booking_object.booking_id, status)

                #Make a method to wait for the scooter to tell us the booking is over 
    main() #Goes back to the start, check if this is the best way to do this
        



#   Wait for login input
def wait_for_login_input():
    print("Waiting for login details")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(ADDRESS)
        s.listen()

        while True:
            print(f"Listening on {ADDRESS}...")
            conn, addr = s.accept()
            with conn:
               
                # Receive username and hashed password from client
                data = socket_utils.recvJson(conn) #Needs to be an active connection, not s 
                received_username = data.get("username")
                received_hash = data.get("password")
                print(f"Received username: {received_username} Received hash: {received_hash}")

                return received_username,received_hash



#Test login input
def validate_login_from_api(received_username, received_hash):
    endpoint = "/api/booking_login"  # Make sure this matches the API endpoint
    customer_data = {
        "username": received_username,
        "password": received_hash
    }
    response = requests.get(BASE + endpoint, data=json.dumps(customer_data))  #Assumes the api returns true or false #API login method needs to be made
    response_data = response.json()

    #Doube check how we will do the reponse
    if response_data.get("success") is True:
        print("Logged in")
        return True
    else:
        print("Login failed")
        return False

def send_login_result(status):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(ADDRESS)
        print("About to send a reply to say if the login was succesful")
        response = {"Login": "success" if status else "failure"}
        socket_utils.sendJson(socket, response)

            
def wait_for_scooter_id():
    print("Waiting for scooter details")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #s.bind(ADDRESS)
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                data = socket_utils.recvJson(conn)
                scooter_id = data["scooter_id"]
                username = data["username"]  # You can also extract the username
                return username, scooter_id

        
 

def find_booking_from_api(received_username, booked_scooter_id, time):
    endpoint = "/api/get_single_booking" #Need to make this
    booking_data_to_send = {
        "username": received_username,
        "scooter_id":booked_scooter_id
       #"time": time #Time is a datetime and not a string 
    }
    response = requests.get(BASE + endpoint, data=json.dumps(booking_data_to_send))

    if response.status_code == 200: # error code 200 means success 
        booking_data = response.json()
        if booking_data:
            # Create a Booking object if data is present
            booking = Booking( #Add records import 
                
                booking_id=booking_data['booking_id'],
                location=booking_data['location'],
                scooter_id=booking_data['scooter_id'],
                customer=booking_data['username'],
                start_time=booking_data['start_time'],
                duration=booking_data['duration'],
                cost=booking_data['cost'],
                status=booking_data['status']
            )
            return booking
        else:
            # No booking data found
            return None
    else:
        # Handle the API request error here
        print("Error: Unable to retrieve booking data.")
        return None


#Send booking details # Wait for reply , send even if none as that will automically make the reply no. #Wait for reply
def send_booking_determine_ifto_start(booking):
    # Send booking details to Client
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(ADDRESS)
        print("Connected.")
        socket_utils.sendJson(s, booking)

        # Ask if the user wants to start the booking on the client side     #Corresponds with sned_start_message or send_user_no_reply
        s.connect(ADDRESS)
        #s.bind(ADDRESS)
        s.listen()
        conn = s.accept()
        with conn:
            response = socket_utils.recvJson(conn)
            if "no" in response:
                return False
            
            return True



#Update booking status when send_booking_determine_ifto_start() returns true, and when waitforbookingtoend recives a end message
def updateBookingStatus(booking_id, new_status):
    endpoint= "update_booking_status"
    booking_data = {
        "booking_id": booking_id,
        "new_status": new_status
    }
    response = requests.get(BASE + endpoint, data=json.dumps(booking_data)) #consider validation for the reponse
    result = response.json().get("result")
    
    if result:
        print(f"Booking status for booking id: {booking_id} changed to {new_status}")
    else:
        print(f"Failed to update booking status for booking id: {booking_id}")

    


  
def wait_for_booking_end():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(ADDRESS)
        #s.bind(ADDRESS)
        s.listen()
        conn = s.accept()
        with conn:
            print("waitng for the booking to end")
            data = socket_utils.recvJson(conn)
            #See if this needs to return anything
            new_status = data["status"]
            return new_status




main()