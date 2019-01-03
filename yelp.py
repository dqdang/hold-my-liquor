from fbpage import page
from flask import Flask, request

import os
import time
import requests
import dbhandler as db
import yppage as yp

def get_results(query):
    search_results = yp.yelp_api.search_query(term=query[0], location="san jose", sort_by='best_match', limit=1)
    return search_results
                
if  __name__ == "__main__":
    db.create_tables()
