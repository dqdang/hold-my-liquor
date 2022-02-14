from messenger import run

import os
import time
import dbhandler as db
import yppage as yp


def get_results(sender_id, query):
    if len(query) > 1:
        search_results = yp.yelp_api.search_query(
            term=query[0], location=query[1], sort_by='best_match', limit=1)
    else:
        search_results = yp.yelp_api.search_query(
            term=query[0], location=db.get_location(sender_id), sort_by='best_match', limit=1)
    return search_results


def pingme():
    start = time.time()
    while True:
        time.sleep(60 - ((time.time() - start) % 60.0))


if __name__ == "__main__":
    db.create_tables()
    pingme()
