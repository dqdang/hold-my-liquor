from uszipcode import SearchEngine

search = SearchEngine(simple_zipcode=True)

def find_zip(zipcode):
    return search.by_zipcode(zipcode)[2]

def return_all(zipcode):
    return search.values()
