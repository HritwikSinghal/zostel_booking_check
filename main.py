#!/usr/bin/env python

import json
import os

import requests
import yagmail
import gi

gi.require_version('Notify', '0.7')
from gi.repository import Notify


def get_data(url: str, headers: dict, params: dict) -> str:
    """
    73 - 2 bed dorm
    74 - shared bath
    75 - female dorm
    406 - Mixed dorm ensuite


    curl 'https://api.zostel.com/api/v1/stay/availability/?checkin=2022-06-25&checkout=2022-07-02&property_code=MNLH056&room_ids=406' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0' -H 'Accept: application/json, text/plain, */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Client-App-Id: FrccUQb4' -H 'Client-User-Id: 72b' -H 'Authorization: Bearer Rz6QmuSsdTPi5XfNCPsCJRVMFey0UzrOcRj5tg4bduc' -H 'Origin: https://www.zostel.com' -H 'DNT: 1' -H 'Connection: keep-alive' -H 'Referer: https://www.zostel.com/' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-site' -H 'TE: trailers'

    await fetch("https://api.zostel.com/api/v1/stay/availability/?checkin=2022-06-25&checkout=2022-07-02&property_code=MNLH056&room_ids=406", {
        "credentials": "include",
        "headers": {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Client-App-Id": "FrcIUQb4",
            "Client-User-Id": "72dcfb",
            "Authorization": "Bearer z6QmuSsdTPi5XfNCPsCJRVMFey0UzrOcRj5tg4bduc",
        },
        "method": "GET",
        "mode": "cors"
    });

    """

    return requests.get(url, headers=headers, params=params).text


def check_avail(my_booking_data: dict, website_booking_data: dict) -> bool:
    checkin: str = my_booking_data['checkin']
    room_id: str = my_booking_data['roomid']

    availibility = website_booking_data['availability'][0]
    if availibility['date'] == checkin \
            and availibility['units'] > 0 \
            and str(availibility['room_id'] == room_id) \
            and str(availibility['bookable'] == 'true'):
        print(f"The Date,{availibility}, is available!")
        return True
    return False


def send_notifications(subject: str, text: str):
    Notify.init(subject)
    Hello = Notify.Notification.new(subject, text)
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

    send_notifications(subject, body)


def get_creds(creds_path: str, mail_data: dict):
    with open(creds_path) as creds:
        basics = json.load(creds)
        mail_data['from'] = basics['from']
        mail_data['to'] = basics['from']
        mail_data['from_pass'] = basics['from_pass']


def start():

    """
    DISPLAY=":0"
    XAUTHORITY="/run/user/1000/.mutter-Xwaylandauth.LIHWN1"
    XDG_RUNTIME_DIR="/run/user/1000"
    DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
    """
    os.environ["DISPLAY"] = ":0"
    os.environ["XAUTHORITY"] = "/run/user/1000/.mutter-Xwaylandauth.LIHWN1"
    os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/run/user/1000/bus"

    mail_data = {
        'from': "",
        'from_pass': "",
        'to': "",
        'subject': 'This is test subject',
        'body': "Hello there",
        "filename": "document.pdf"
    }

    creds_path = '/home/hritwik/Projects/zostel_booking/creds'
    get_creds(creds_path, mail_data)

    booking_data = {
        'checkin': '2022-06-25',
        'checkout': '2022-06-26',
        'roomid': '406',
        'propertycode': 'MNLH056'
    }

    url = f'https://api.zostel.com/api/v1/stay/availability/'
    client_App_Id = 'FrcIH2m03QxVgFD037u8oaQczaAImvAN506cUQb4'
    client_User_Id = '72d6d30cfb'
    authorization = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IkFOLTI2ODI3OTciLCJhcHBfaWQiOiJGcmNJSDJtMDNReFZnRkQwMzd1OG9hUWN6YUFJbXZBTjUwNmNVUWI0IiwidXNlcl9pZCI6IjcyZDZkMzBjZmIiLCJhdXRoZW50aWNhdGVkIjpmYWxzZSwiaWF0IjoxNjU1MTkxMjgxfQ.Rz6QmuSsdTPi5XfNCPsCJRVMFey0UzrOcRj5tg4bduc'

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Client-App-Id": client_App_Id,
        "Client-User-Id": client_User_Id,
        "Authorization": authorization,
    }

    params = {
        "checkin": booking_data['checkin'],
        "checkout": booking_data['checkout'],
        "room_ids": booking_data['roomid'],
        "property_code": booking_data['propertycode'],
    }

    data = get_data(url, headers, params)
    website_booking_data = json.loads(data)  # dictionary

    is_dorm_available = check_avail(my_booking_data=booking_data, website_booking_data=website_booking_data)

    if not is_dorm_available:
        print("Booking available! Here is the summary")
        print(json.dumps(website_booking_data, indent=2))

        print("sending mail...")
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
        send_mail(mail_data)
        print("mail sent!")

    else:
        print(f"Sorry not available for {booking_data['checkin']}. Here is the summary")
        print(json.dumps(website_booking_data['availability'], indent=2))
        send_notifications("Sorry!", "No booking")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start()
