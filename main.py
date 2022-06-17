#!/usr/bin/env python

import json
import os

import requests
import yagmail
import gi

gi.require_version('Notify', '0.7')
from gi.repository import Notify

script_path = os.path.dirname(__file__)
os.environ["script_path"] = script_path


def get_data_from_file(file_path: str) -> dict:
    with open(file_path) as my_file:
        return json.load(my_file)


def set_env_var() -> None:
    """
    DISPLAY=":0"
    XAUTHORITY="/run/user/1000/.mutter-Xwaylandauth.LIHWN1"
    XDG_RUNTIME_DIR="/run/user/1000"
    DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
    """

    env_var_data: dict = get_data_from_file(env_var_data_path)

    os.environ["DISPLAY"] = env_var_data['DISPLAY']
    os.environ["XAUTHORITY"] = env_var_data['XAUTHORITY']
    os.environ["XDG_RUNTIME_DIR"] = env_var_data['XDG_RUNTIME_DIR']
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = env_var_data['DBUS_SESSION_BUS_ADDRESS']


def get_web_data(url: str, headers: dict, params: dict) -> str:
    """
    73 - 2 bed dorm
    74 - shared bath mixed dorm
    75 - female dorm
    406 - Mixed dorm en-suite


    curl 'https://api.zostel.com/api/v1/stay/availability/?checkin=2022-06-25&checkout=2022-07-02&property_code=MNLH056&room_ids=406' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0' -H 'Accept: application/json, text/plain, */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Client-App-Id: Something' -H 'Client-User-Id: Something' -H 'Authorization: Bearer Something' -H 'Origin: https://www.zostel.com' -H 'DNT: 1' -H 'Connection: keep-alive' -H 'Referer: https://www.zostel.com/'

    await fetch("https://api.zostel.com/api/v1/stay/availability/?checkin=2022-06-25&checkout=2022-07-02&property_code=MNLH056&room_ids=406", {
        "credentials": "include",
        "headers": {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Client-App-Id": "Something",
            "Client-User-Id": "Something",
            "Authorization": "Bearer Something",
        },
        "method": "GET",
        "mode": "cors"
    });

    """

    return requests.get(url, headers=headers, params=params).text


def check_availability(my_booking_data: dict, website_booking_data: dict) -> bool:
    checkin: str = my_booking_data['checkin']
    room_id: str = my_booking_data['roomid']

    availability = website_booking_data['availability'][0]
    if availability['date'] == checkin \
            and availability['units'] > 0 \
            and str(availability['room_id'] == room_id) \
            and str(availability['bookable'] == 'true'):
        print(f"The Date,{availability}, is available!")
        return True
    return False


def send_notifications(subject: str, text: str, urgency: int):
    Notify.init(subject)
    Hello = Notify.Notification.new(subject, text)

    Hello.set_urgency(urgency)
    Hello.show()


def send_mail(mail_data: dict) -> None:
    from_email = mail_data['from']
    to_email = mail_data['to']
    subject = mail_data['subject']
    body = mail_data['body']
    from_pass = mail_data['from_pass']

    yag = yagmail.SMTP(user=from_email
                       , password=from_pass
                       , host='smtp.office365.com'
                       , port=587
                       , smtp_starttls=True,
                       smtp_ssl=False
                       )

    yag.send(
        to=to_email,
        subject=subject,
        contents=body,
        # attachments=filename
    )


def get_data() -> tuple[dict, dict, dict]:
    mail_data: dict = get_data_from_file(mail_data_path)
    creds_data: dict = get_data_from_file(creds_path)
    booking_data: dict = get_data_from_file(booking_data_path)

    mail_data['from'] = creds_data['from']
    mail_data['to'] = creds_data['to']
    mail_data['from_pass'] = creds_data['from_pass']

    headers["Client-App-Id"] = creds_data['client_App_Id']
    headers["Client-User-Id"] = creds_data['client_User_Id']
    headers["Authorization"] = creds_data['authorization']

    params = {
        "checkin": booking_data['checkin'],
        "checkout": booking_data['checkout'],
        "room_ids": booking_data['roomid'],
        "property_code": booking_data['propertycode'],
    }

    return mail_data, booking_data, params


def start():
    mail_data, booking_data, params = get_data()

    data = get_web_data(api_url, headers, params)
    website_booking_data = json.loads(data)  # dictionary

    is_dorm_available = check_availability(my_booking_data=booking_data, website_booking_data=website_booking_data)

    if is_dorm_available:
        print("Booking available! Here is the summary")
        print(json.dumps(website_booking_data, indent=2))

        print("Sending Mail...")
        availability = website_booking_data['availability'][0]
        pricing = website_booking_data['pricing'][0]

        mail_data['subject'] = "Booking Available! Hurry up and book now"
        mail_data['body'] = f"Hello Hritwik, There is a booking available for {booking_data['checkin']}. " \
                            f"Hurry up and book before its booked again\n" \
                            + "\nUnits: " + str(availability["units"]) \
                            + "\nRoom ID: " + str(availability['room_id']) \
                            + "\nDate: " + str(availability['date']) \
                            + "\nPricing: Rs " + str(pricing['price']) \
                            + "\n"

        mail_data['body'] += "\n\n---------------------------------------------------------------\n\n" \
                             + "If you want more info, here is the summary\n" \
                             + json.dumps(website_booking_data, indent=2)

        send_notifications(mail_data['subject'], mail_data['body'], urgency=2)
        send_mail(mail_data)
        print("Mail sent!")

    else:
        print(f"Sorry not available for {booking_data['checkin']}. Here is the summary")
        print(json.dumps(website_booking_data['availability'], indent=2))
        # send_notifications("Sorry!", "No booking", urgency=0)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    env_var_data_path = f'{script_path}/data/env_var_data'
    set_env_var()

    mail_data_path = f'{script_path}/data/mail_data'
    creds_path = f'{script_path}/data/creds_data'
    booking_data_path = f'{script_path}/data/booking_data'

    api_url = 'https://api.zostel.com/api/v1/stay/availability/'
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
    }

    start()
