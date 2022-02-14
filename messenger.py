from fbmessenger import BaseMessenger
from yelpapi import YelpAPI
from zipcode import search

import os
import re
import requests
import dbhandler as db


yelp_api = YelpAPI(os.environ['YELP_KEY'], timeout_s=3.0)


def general_query(results):
    app.logger.info('Results: {}'.format(results))
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
        payload = message['postback']['payload']
        if 'start' in payload:
            db.insert_user(sender_id)
            response = Text(text="Welcome! Search yelp for something like this:\nDISH, LOCATION\n\nChange default location with location=LOCATION")
            return response.to_dict()
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
        app.logger.info('Exception: {}'.format(e))
        return

    if not message:
        return

    split = message.split("  ")
    results = get_results(sender_id, split)
    rv = general_query(results)
    response = Text(text=rv)
    app.logger.info('Response: {}'.format(response))
    return response.to_dict()


class Messenger(BaseMessenger):
    def __init__(self, page_access_token):
        self.page_access_token = page_access_token
        super(Messenger, self).__init__(self.page_access_token)

    def message(self, message):
        sender_id = self.get_user_id()
        action = process_message(sender_id, message)
        if action:
            app.logger.info('Got action: {}'.format(action))
            res = self.send(action, 'RESPONSE')
        app.logger.info('No action.')

    def init_bot(self):
        self.add_whitelisted_domains('https://facebook.com/')
        greeting = GreetingText(text='Get started with the below button!.')
        self.set_messenger_profile(greeting.to_dict())

        get_started = GetStartedButton(payload='start')
        self.set_messenger_profile(get_started.to_dict())
