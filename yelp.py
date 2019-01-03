from fbpage import page
from flask import Flask, request

import os
import time
import requests
import dbhandler as db
import yppage as yp

def get_results(query):
    search_results = yp.yelp_api.search_query(query)
    return search_results

def get_current():
    url = "https://yelp.com"
    
    # while True:

    #     print("Checking if new products are on ACRNM on proxy: {}".format(site.proxy_used))
    #     if not site.get().ok:
    #         print("Proxy or website is unresponsive. Trying again...")
    #         failures += 1
    #         site.proxy_used = site.sockets.pop(0)
    #         continue
    #     else:
    #         failures = 0
        
    #     tree = html.fromstring(str(site))
    #     tree.make_links_absolute(url)

    #     prod_names = tree.xpath("//div[@class='name']/text()")
    #     prod_urls = tree.xpath("//a[contains(concat(' ', normalize-space(@class), ' '), ' tile ')]/@href")

    #     new, restock = db.new_items(prod_names, prod_urls)

    #     if new:
    #         new = list(zip(*new))
    #         notify(new[1], restock)
    #         db.insert_products(new[0])
    #     else:
    #         notify(new, restock)

    #     db.insert_current(prod_names, prod_urls)
                
if  __name__ == "__main__":
    db.create_tables()
    get_current()