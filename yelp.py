from fbpage import page
from flask import Flask, request

import os
import time
import requests
import dbhandler as db
import yppage as yp

TIMEOUT = 600
def get_results(query):
    if len(query) > 1:
        search_results = yp.yelp_api.search_query(term=query[0], location=query[1], sort_by='best_match', limit=1)
    else:
        search_results = yp.yelp_api.search_query(term=query[0], location="san jose", sort_by='best_match', limit=1)
    return search_results


def pingme(timeout):
    start = time.time()
    while True:
        time.sleep(60 - ((time.time() - start) % 60.0))
if  __name__ == "__main__":
    db.create_tables()
    pingme(TIMEOUT)