from pymongo import MongoClient
import os
import dotenv

dotenv.load_dotenv()
uri = os.getenv('MONGO_URI')
if uri is None:
	raise Exception("MONGO_URI is not set")

client = MongoClient(uri)
db = client.get_database("NeoInc")