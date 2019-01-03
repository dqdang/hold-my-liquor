from yelpapi import YelpAPI

import os

yelp_api = YelpAPI(os.environ['YELP_KEY'], timeout_s=0.3)
