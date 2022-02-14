from fbpage import page
from fbmq import QuickReply, Template
from zipcode import search

import os
import re
import requests
import dbhandler as db
import yelp as yelp

page.greeting("Click Get Started below to get started!")
page.show_starting_button("Get Started")


def general_query(results):
    print(results)
    try:
        rv_name = results["businesses"][0]["name"]
        rv_url = results["businesses"][0]["url"]
        rv = rv_name + "\n_____\n" + rv_url
    except:
        rv = "yelp can't find that shit man."
    return rv


@page.handle_postback
def received_postback(event):
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_postback = event.timestamp
    payload = event.payload

    page.typing_on(sender_id)
    page.send(sender_id, "Welcome! Search yelp for something like this:\nDISH, LOCATION\n\nChange default location with location=LOCATION")
    db.insert_user(sender_id)
    page.typing_off(sender_id)


@page.handle_message
def message_handler(event):
    sender_id = event.sender_id
    try:
        message = event.message.get('text').lower()
        if("=" in message):
            message = message.split("=")[-1]
            if(message.isdigit()):
                message = search.by_zipcode(zipcode)[2]
            message = re.sub("[\W+]", " ", message.upper())
            message = message.strip()
            db.change_location(sender_id, message)
            send = "Changed default location to {}".format(message)
            page.send(sender_id, send)
            return
        message = re.sub("[\W+]", " ", message.upper())
        message = message.strip()
        if("CURRENT LOCATION" in message):
            page.send(sender_id, db.get_location(sender_id))
            return
    except:
        return

    if not message:
        return

    # "hot pot, san francisco" OR "hot pot"
    split = message.split("  ")
    results = yelp.get_results(sender_id, split)
    rv = general_query(results)
    page.send(sender_id, rv)
    return "Message processed"


@page.handle_delivery
def received_delivery_confirmation(event):
    delivery = event.delivery
    message_ids = delivery.get("mids")
    watermark = delivery.get("watermark")


@page.handle_read
def received_message_read(event):
    watermark = event.read.get("watermark")
    seq = event.read.get("seq")


@page.handle_echo
def received_echo(event):
    message = event.message
    message_id = message.get("mid")
    app_id = message.get("app_id")
    metadata = message.get("metadata")
