import numpy
from sqlalchemy import *
import pandas as pd
import requests

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
            "postgresql",
            username=username,
            password=password,  # plain (unescaped) text
            host=hostname,
            database=db_location,
        )
        print(haro_URL)
        self.dbEngine = create_engine(f"postgresql://{username}:{password}@{hostname}/{db_location}", 
                                        pool_size=num_workers)
        assert (json_location != None) ^ (json != None)  # accept only one input.
        self.json_url = json_location # one of these will be None
        self.prod_json = json # handling this in the function is faster.
        self.makeProductsTable()
        self.createUserTable()
        self.createWishlistTable()

    def makeProductsTable(self):
        if self.json_url != None:
            self.prod_json = requests.get(self.json_url).json()
        prod_df = pd.read_json(self.prod_json)
        with self.dbEngine.connect() as conn:
            prod_df.to_sql('Products', conn, if_exists='replace', ) # use pandas built-in db writer
            conn.commit()

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
    hostname = "localhost:5432"
    username = 'tea'
    password = 'haro_db_pw'
    print(username, password)
    db_location = 'haro_db'
    json_location = 'https://raw.githubusercontent.com/Shalldoll-Scout-Project/Haro/main/web_scraping_scripts/hlj/outputs_and_logs/hlj_products_info.json'
    wishlistManager(hostname, username, password, db_location, json_location=json_location)