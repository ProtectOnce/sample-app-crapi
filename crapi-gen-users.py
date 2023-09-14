import requests
import string
import random
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("crapi_url", help="Crapi url with a trailing slash at the end. e.g. http://crapi/")
parser.add_argument("mailhog_url", help="Mailhog url with a trailing slash at the end e.g. http://mailhog:8025/")
parser.add_argument("user_count", help="Number of users e.g. 7",default=2)
args = parser.parse_args()
config = vars(args)

def registerUsers():
    global config
    webbase = config["crapi_url"]
    mailhog = config["mailhog_url"]
    user_count = int(config["user_count"])
    print(config)
    N = 6
    ctr = 0
    register_url = webbase + "identity/api/auth/signup"
    mails = mailhog + "api/v1/messages"

    while ctr<user_count:
        # Register a new account
        print("Creating a new account...")
        name = ''.join(random.choices(string.ascii_lowercase, k=N))
        num = str(random.randint(1,99999))
        data = {"email": "test+" + name +"@test.com", "name": name, "number": num, "password": "Test@123"}
        print("E-mail: " + data["email"])
        res = requests.post(register_url, json=data)
        print("Status Code: ", res.status_code)
        ctr = ctr + 1

        # Get the VIN and pincode for that account
        mails = requests.get(mailhog + "api/v2/messages").json()
        mailContent = mails["items"][0]["Content"]["Body"]
        mailContent = mailContent.replace("=\r\n","")
        first_split = (mailContent.split("VIN: </font><font face=3D'calibri' font color=3D'#0000ff'>"))[1]
        second_split = first_split.split("</font>")

        vin = second_split[0]
        first_split = (mailContent.split("Pincode: <font face=3D'calibri' font color=3D'#0000ff'>"))[1]
        second_split = first_split.split("</font>")
        pincode = second_split[0]
        print("Fetching the vin and pin...")

        # register the vehicle with vin and pincode
        print('Logging in...')
        creds = {"email": data["email"], "password": "Test@123"}
        res = requests.post(webbase + "identity/api/auth/login", json=creds).json()
        token = res["token"]
        car_details = {"vin":vin,"pincode":pincode}
        print(car_details)
        headers = {"Authorization":"Bearer " + token}
        requests.post(webbase + "identity/api/v2/vehicle/add_vehicle", json=car_details,headers=headers).json()

        # delete all mails
        requests.delete(mailhog+"api/v1/messages")

        # Writing users to file
        f = open("users.txt", "a")
        f.write("test+" + name +"@test.com\n")

    f.close()

open('users.txt', 'w').close()
registerUsers()