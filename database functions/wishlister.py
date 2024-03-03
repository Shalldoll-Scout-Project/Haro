import sqlite3 as sql
import pandas as pd

class Wishlist:
    def __init__(self, db_location, json_location = None, json = None):
        self.db_loc = db_location
        self.dbConnection = sql.connect(self.db_loc)
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