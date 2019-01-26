from fbpage import page
from fbmq import QuickReply, Template

import os
import re
import requests
import dbhandler as db
import yelp as yelp

page.greeting("Click Get Started below to get started!!")
page.show_starting_button("Get Started")

def general_query(results):
    rv_name = results["businesses"][0]["name"]
    rv_url = results["businesses"][0]["url"]
    rv = rv_name + "\n_____\n" + rv_url
    return rv

@page.handle_postback
def received_postback(event):    
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_postback = event.timestamp
    payload = event.payload

    page.typing_on(sender_id)
    page.send(sender_id, "Welcome! Search yelp for something like this:\nDish, Location")
    page.typing_off(sender_id)

@page.handle_message
def message_handler(event):
    sender_id = event.sender_id
    try:
        message = event.message.get('text').lower()
        message = re.sub("[\W+]", " ", message.upper())
        message = message.strip()
    except:
        return
    
    if not message:
        return

    # "hot pot, san francisco" OR "hot pot"
    split = message.split("  ")
    results = yelp.get_results(split)
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
