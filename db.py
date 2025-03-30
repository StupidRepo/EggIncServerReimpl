from typing import Any, Mapping

from google.protobuf.json_format import ParseDict, MessageToDict
from pymongo import MongoClient
import os
import dotenv

from pb import ei_pb2

class MyDBClient(MongoClient):
	def __init__(self, yuri, *args, **kwargs):
		super().__init__(yuri, *args, **kwargs)

		self.db = self.get_database("NeoInc")
		self.users_collection = self.db.get_collection("users")
		self.events_collection = self.db.get_collection("events")

class DBUser:
	def __init__(self, nid: str, database: MyDBClient):
		self.nid = nid
		self.db = database
		self.user = None

		user = self.db.users_collection.find_one({"_id": self.nid})
		if user is None:
			raise Exception(f"User {self.nid} not found in DB")

		self.user = user

	def get(self, key: str, default: Any = None) -> Any:
		if self.user is None:
			return default

		return self.user.get(key, default)

	def get_missions(self) -> list[ei_pb2.MissionInfo]:
		if self.user is None:
			return []

		missions_from_db = self.user.get("missions", [])
		missions = [ParseDict(mission, ei_pb2.MissionInfo()) for mission in missions_from_db]

		return missions

	def add_mission(self, mission: ei_pb2.MissionInfo):
		if self.user is None:
			return

		self.db.users_collection.update_one({"_id": self.nid}, {"$push": {"missions": MessageToDict(mission)}})

	def del_mission(self, identifier: str):
		if self.user is None:
			return

		self.db.users_collection.update_one({"_id": self.nid}, {"$pull": {"missions": {"identifier": identifier}}})

	def get_backup(self) -> ei_pb2.Backup | None:
		if self.user is None:
			return None

		backup = self.user.get("backup")
		if backup is None:
			return None

		return ParseDict(backup, ei_pb2.Backup())

	def update_backup(self, backup: ei_pb2.Backup):
		if self.user is None:
			return

		self.db.users_collection.update_one({"_id": self.nid}, {"$set": {"backup": MessageToDict(backup)}})

dotenv.load_dotenv()
uri = os.getenv('MONGO_URI')
if uri is None:
	raise Exception("MONGO_URI is not set")

client = MyDBClient(uri)