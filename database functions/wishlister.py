import numpy
from sqlalchemy import *
import pandas as pd

class Wishlist:
    def __init__(self, username, password, db_location, json_location = None, json = None, num_workers=10):
        url_object = URL.create(
            "postgresql+pg8000",
            username=username,
            password=password,  # plain (unescaped) text
            host="localhost",
            database=db_location,
        )
        self.dbEngine = create_engine(url_object, pool_size=num_workers)
        assert(json_location != None ^ json != None) # accept only one input.
        if json_location:
            self.urlProductsTable()
        else:
            self.jsonProductsTable()
        self.createUserTable()
        self.createWishlist()
    
    def urlProductsTable(self):
        pass
    
    def jsonProductsTable(self):
        pass
    
    def createUserTable(self):
        pass
    
    def createWishlist(self):
        pass
    
    def addCustomProduct(self, name, price, size, weight):
        pass