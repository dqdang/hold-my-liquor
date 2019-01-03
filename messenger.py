from fbpage import page
from fbmq import QuickReply, Template

import os
import re
import json
import requests
import dbhandler as db
import yelp as yelp

password = os.environ["PASSWORD"]
# admin_key = os.environ["ADMIN_KEY"]

acct_menu_btns = [
        Template.ButtonPostBack("Food", "MENUPAYLOAD/Food"),
        Template.ButtonPostBack("Dessert", "MENUPAYLOAD/Dessert"),
        Template.ButtonPostBack("Bar", "Bar")
]

simple_menu_btns = [
        Template.ButtonPostBack("Current Products", "MENUPAYLOAD/Products"),
]

quick_replies = [
        QuickReply(title="Yes, subscribe", payload="Yes_r"),
        QuickReply(title="No", payload="No")        
]

page.greeting("Click Get Started below to subscribe!!")
page.show_starting_button("Subscribe")

def p_menu():
    acct_menu = {"title":"Popular Choices", "type":"nested"}
    menu = [{"locale": "default", "composer_input_disabled": False, "call_to_actions": [acct_menu]}]
    call_to_actions = []

    for button in Template.Buttons.convert_shortcut_buttons(acct_menu_btns):
        call_to_actions.append({
            "type": "postback",
            "title": button.title,
            "payload": button.payload
        })

    acct_menu["call_to_actions"] = call_to_actions

    page._set_profile_property(pname="persistent_menu", pval=menu)

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

#    if message == admin_key:
#
#        if db.insert_admin(sender_id):
#            page.send(sender_id, "Added you as an admin")
#        else:
#            page.send(sender_id, "Already an Admin")
    # "san francisco, hot pot" OR "hot pot"
    split = message.split(", ")
    print(split)
    results = yelp.get_results(split)
    rv_name = results[0][name]
    rv_url = results[0][url]
    page.send(sender_id, rv_name)
    page.send(sender_id, rv_url)
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

@page.callback(['MENUPAYLOAD/(.+)'])
def callback_clicked_p_menu(payload, event):
    sender_id = event.sender_id
    click_menu = payload.split('/')[1]
    if click_menu == 'Food':
        callback_clicked_food(payload, event)
    elif click_menu == 'Dessert':
        callback_clicked_dessert(payload, event)
    elif click_menu == 'Bar':
        callback_clicked_bar(payload, event)

@page.callback(['Food'])
def callback_clicked_food(payload, event):
    sender_id = event.sender_id
    subs = db.get_subscriptions(sender_id)
    if subs:
        page.send(sender_id, "YOUR SUBS:\n"+"\n".join(subs))
    else:
        handle_unsub(sender_id)

@page.callback(['Dessert'])
def callback_clicked_dessert(payload, event):
    page.send(event.sender_id, "CURRENT PRODUCTS:\n"+"\n".join(db.get_current()))

@page.callback(['Bar'])
def callback_clicked_bar(payload, event):
    sender_id = event.sender_id
    if db.change_state(sender_id, 1):
        page.send(sender_id, "Insert product name. Make sure name is exact (Press 'Current Products' to see product list)")
    else:
        handle_unsub(sender_id)
