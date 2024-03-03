import numpy
from sqlalchemy import *
import pandas as pd

class Wishlist:
    def __init__(
        self,
        hostname,
        username,
        password,
        db_location,
        json_location=None,
        json=None,
        num_workers=10,
    ):
        haro_URL = URL.create(
            "postgresql+pg8000",
            username=username,
            password=password,  # plain (unescaped) text
            host="localhost",
            database=db_location,
        )
        self.dbEngine = create_engine(haro_URL, pool_size=num_workers)
        assert json_location != None ^ json != None  # accept only one input.
        if json_location:
            self.urlProductsTable()
        else:
            self.jsonProductsTable()
        self.createUserTable()
        self.createWishlistTable()

    def urlProductsTable(self):
        # get json from URL
        # convert it to a pandas DF or similar.
        with self.dbEngine.connect() as conn:
            conn.execute() # create table if not exists
            conn.execute() # insert every row into the table (might be loop but i doubt it)
            conn.commit()

    def jsonProductsTable(self):
        # same as URL method but just omit the get request
        pass

    def createUserTable(self):
        pass

    def createWishlistTable(self):
        pass

    def addCustomProduct(self, name, price, size, weight):
        pass
