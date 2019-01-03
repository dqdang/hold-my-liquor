from fbpage import page
from fbmq import QuickReply, Template

import os
import re
import json
import requests
import dbhandler as db
import yelp as yelp

password = os.environ["PASSWORD"]

page.greeting("Click Get Started below to subscribe!!")
page.show_starting_button("Subscribe")

def general_query(results):
    rv_name = results["businesses"][0]["name"]
    rv_url = results["businesses"][0]["url"]
    rv = rv_name + "\n_____\n" + rv_url
    return rv

def handle_unsub(sender_id):
    page.send(sender_id, "You are unsubscribed, enter access code to subscribe")

@page.handle_postback
def received_postback(event):    
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_postback = event.timestamp
    payload = event.payload

    page.typing_on(sender_id)

    if(payload == "Subscribe"):
        if not db.user_exists(sender_id):
            handle_unsub(sender_id)
        else:
            page.send(sender_id, "Already subscribed")

    page.typing_off(sender_id)

@page.handle_message
def message_handler(event):
    sender_id = event.sender_id
    message = event.message.get('text').lower()
    message = re.sub("[\W+]", " ", message.upper())

    if not message:
        return

    # "san francisco, hot pot" OR "hot pot"
    split = message.split(", ")
    results = yelp.get_results(split)
    rv = general_query(results)
    page.send(sender_id, rv)
    return "Message processed"

@page.handle_delivery
def received_delivery_confirmation(event):
    delivery = event.delivery
    message_ids = delivery.get("mids")
    watermark = delivery.get("watermark")

    # if message_ids:
    #     for message_id in message_ids:
            # print("Received delivery confirmation for message ID: %s" % message_id)

    # print("All message before %s were delivered." % watermark)

@page.handle_read
def received_message_read(event):
    watermark = event.read.get("watermark")
    seq = event.read.get("seq")
    # print("Received message read event for watermark %s and sequence number %s" % (watermark, seq))

@page.handle_echo
def received_echo(event):
    message = event.message
    message_id = message.get("mid")
    app_id = message.get("app_id")
    metadata = message.get("metadata")
    # print("page id : %s , %s" % (page.page_id, page.page_name))
    # print("Received echo for message %s and app %s with metadata %s" % (message_id, app_id, metadata))
