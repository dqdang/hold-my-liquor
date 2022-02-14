from fbmessenger import BaseMessenger
from yelpapi import YelpAPI
from zipcode import search

import os
import re
import requests
import dbhandler as db


yelp_api = YelpAPI(os.environ['YELP_KEY'], timeout_s=3.0)


def general_query(results):
    print('Results: {}'.format(results))
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


def process_message(sender_id, message):
    try:
        message = message['message']['text'].lower()
        if("=" in message):
            message = message.split("=")[-1]
            if(message.isdigit()):
                message = search.by_zipcode(zipcode)[2]
            message = re.sub("[\W+]", " ", message.upper())
            message = message.strip()
            db.change_location(sender_id, message)
            response = Text(text="Changed default location to {}".format(message))
            return response.to_dict()
        message = re.sub("[\W+]", " ", message.upper())
        message = message.strip()
        if("CURRENT LOCATION" in message):
            response = Text(text=db.get_location(sender_id))
            return response.to_dict()
    except Exception as e:
        raise Exception('Exception: {}'.format(e))
        return

    if not message:
        return

    split = message.split("  ")
    raise Exception("{}, {}, {}".format(sender_id, db.user_exists(sender_id), message))
    results = get_results(sender_id, split)
    rv = general_query(results)
    response = Text(text=rv)
    print('Response: {}'.format(response))
    return response.to_dict()


class Messenger(BaseMessenger):
    def __init__(self, page_access_token):
        self.page_access_token = page_access_token
        super(Messenger, self).__init__(self.page_access_token)

    def message(self, message):
        sender_id = self.get_user_id()
        action = process_message(sender_id, message)
        if action:
            raise Exception("Got action: {}".format(action))
            print('Got action: {}'.format(action))
            res = self.send(action, 'RESPONSE')
        raise Exception("No action")
        print('No action.')

    def postback(self, message):
        done = db.insert_user(self.get_user_id())
        raise Exception("{}, ".format(done, db.user_exists(str(self.get_user_id()))))


    def init_bot(self):
        self.add_whitelisted_domains('https://facebook.com/')
        greeting = GreetingText(text='Get started with the below button! Search any keyword.')
        self.set_messenger_profile(greeting.to_dict())

        get_started = GetStartedButton(payload='start')
        self.set_messenger_profile(get_started.to_dict())

