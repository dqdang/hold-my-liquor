from fbmessenger import BaseMessenger
from yelpapi import YelpAPI
from zipcode import search

import os
import re
import requests
import dbhandler as db


yelp_api = YelpAPI(os.environ['YELP_KEY'], timeout_s=3.0)


def general_query(results):
    print(results)
    try:
        rv_name = results["businesses"][0]["name"]
        rv_url = results["businesses"][0]["url"]
        rv = rv_name + "\n_____\n" + rv_url
    except:
        rv = "yelp can't find that shit man."
    return rv


def get_results(sender_id, query):
    if len(query) > 1:
        search_results = yelp_api.search_query(
            term=query[0], location=query[1], sort_by='best_match', limit=1)
    else:
        search_results = yelp_api.search_query(
            term=query[0], location=db.get_location(sender_id), sort_by='best_match', limit=1)
    return search_results


def process_message(message):
    try:
        message = message['message']['text'].lower()
        if("=" in message):
            message = message.split("=")[-1]
            if(message.isdigit()):
                message = search.by_zipcode(zipcode)[2]
            message = re.sub("[\W+]", " ", message.upper())
            message = message.strip()
            db.change_location(sender_id, message)
            send = Text(text="Changed default location to {}".format(message))
            page.send(sender_id, send)
            return response.to_dict()
        message = re.sub("[\W+]", " ", message.upper())
        message = message.strip()
        if("CURRENT LOCATION" in message):
            send = Text(text=db.get_location(sender_id))
            page.send(sender_id, db.get_location(sender_id))
            return response.to_dict()
    except:
        return

    if not message:
        return

    split = message.split("  ")
    results = get_results(sender_id, split)
    rv = general_query(results)
    return response.to_dict()


class Messenger(BaseMessenger):
    def __init__(self, page_access_token):
        self.page_access_token = page_access_token
        super(Messenger, self).__init__(self.page_access_token)

    def message(self, message):
        action = process_message(message)
        if action:
            res = self.send(action, 'RESPONSE')

    def postback(self, message):
        payload = message['postback']['payload']
        sender_id = self.get_user_id()
        page.typing_on(sender_id)
        page.send(sender_id, "Welcome! Search yelp for something like this:\nDISH, LOCATION\n\nChange default location with location=LOCATION")
        db.insert_user(sender_id)
        page.typing_off(sender_id)

    def init_bot(self):
        self.add_whitelisted_domains('https://facebook.com/')
        greeting = GreetingText(text='Get started with the below button!.')
        self.set_messenger_profile(greeting.to_dict())

        get_started = GetStartedButton(payload='Get Started')
        self.set_messenger_profile(get_started.to_dict())
