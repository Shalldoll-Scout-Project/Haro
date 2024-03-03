import os
import numpy
from sqlalchemy import *
import pandas as pd
from dotenv import load_dotenv

class wishlistManager:
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
            host=hostname,
            database=db_location,
        )
        print(haro_URL)
        self.dbEngine = create_engine(haro_URL, pool_size=num_workers)
        assert (json_location != None) ^ (json != None)  # accept only one input.
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
            conn.execute('CREATE TABLE IF NOT EXISTS Products') # create table if not exists
            # conn.execute() # insert every row into the table (might be loop but i doubt it)
            conn.commit()

    def jsonProductsTable(self):
        # same as URL method but just omit the get request
        pass

    def createUserTable(self):
        # this basically checks if users table exists and creates one if not
        pass

    def createWishlistTable(self):
        # same as above but for wishlists and creates one if not
        pass

    def addCustomProduct(self, name, price, size, weight):
        # useful for p bandai things i guess. if anyone wants to contribute. 
        # maybe add something there that stores this info somewhere else also?
        pass

    # more functions needed
if __name__ == '__main__':
    # i will load environment variables from a .env file, make your own if you wish to test.
    load_dotenv('/database functions/')
    hostname = 'localhost:5432'
    username = os.getenv('USRNAME')
    password = os.getenv('PSSWRD')
    db_location = '/haro_db'
    json_location = 'https://raw.githubusercontent.com/Shalldoll-Scout-Project/Haro/main/web_scraping_scripts/hlj/outputs_and_logs/hlj_products_info.json'
    wishlistManager(hostname, username, password, db_location, json_location=json_location)