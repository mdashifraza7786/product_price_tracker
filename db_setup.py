from pymongo import MongoClient

def get_db():
    client = MongoClient("mongodb+srv://producttracker:1IX583XS2r8ti8Gg@pricetracker.3xiaz.mongodb.net/productpricetrackerproject?retryWrites=true&w=majority")
    return client['productpricetrackerproject']
