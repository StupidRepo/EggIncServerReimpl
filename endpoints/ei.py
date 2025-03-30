import base64
import time

from flask import Blueprint, g
from pb import ei_pb2
from utils import common, gen

ei_bp = Blueprint('ei', __name__)

"""
Create's the user's account if it doesn't exist, and returns the user's backup data if it exists.
"""
@ei_bp.route('/first_contact_secure', methods=['POST'])
@common.proto_parser(ei_pb2.EggIncFirstContactRequest, True)
def first_contact_secure(msg: ei_pb2.EggIncFirstContactRequest):
	neoid = common.did_to_nid(msg.device_id)

	response = ei_pb2.EggIncFirstContactResponse()
	response.ei_user_id = neoid

	# check if account is in DB, if not, create  it
	user: dict = g.db.users.find_one({"_id": neoid})
	if user is None:
		print(f"User {neoid} not found, creating new user")

		g.db.users.insert_one({"_id": neoid, "device_id": msg.device_id})
		response.ids_transferred.append(msg.device_id)
	else:
		prev_backup = user.get("backup")
		if prev_backup is not None:
			print("Backup found!")
			backup_msg = ei_pb2.Backup()
			backup_msg.ParseFromString(prev_backup)

			response.backup.CopyFrom(backup_msg)
		else:
			print("No backup found")

	return base64.b64encode(common.make_auth_message(response).SerializeToString())

"""
Save the user's backup data to the server, whilst returning for conflicts if there are any.
"""
@ei_bp.route('/save_backup_secure', methods=['POST'])
@common.proto_parser(ei_pb2.Backup, True)
def save_backup_secure(msg: ei_pb2.Backup):
	response = ei_pb2.SaveBackupResponse()
	response.success = False
	response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.USER_NOT_FOUND

	# if a backup exists, check for conflicts
	user: dict = g.db.users.find_one({"_id": msg.ei_user_id})
	if user is None:
		return base64.b64encode(common.make_auth_message(response).SerializeToString())

	print("User found!")
	prev_backup = user.get("backup")

	if not msg.force_backup and prev_backup is not None:
		db_backup = ei_pb2.Backup()
		db_backup.ParseFromString(prev_backup)

		response.existing_backup.CopyFrom(db_backup)
		if sum(msg.stats.egg_totals) < sum(db_backup.stats.egg_totals): # acts as a db_backup.game.lifetime_earnings replacement as I think that is done on server then appended to the backup, but I'm not sure, so I'm doing this instead lol
			response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.COULD_NOT_OVERWRITE
			response.message = "Remote backup has greater lifetime earnings."
			return base64.b64encode(common.make_auth_message(response).SerializeToString())

		elif msg.game.soul_eggs < db_backup.game.soul_eggs:
			response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.COULD_NOT_OVERWRITE
			response.message = "Remote backup has more soul eggs."
			return base64.b64encode(common.make_auth_message(response).SerializeToString())

		elif msg.game.eggs_of_prophecy < db_backup.game.eggs_of_prophecy:
			response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.COULD_NOT_OVERWRITE
			response.message = "Remote backup has more eggs of prophecy."
			return base64.b64encode(common.make_auth_message(response).SerializeToString())

		elif msg.game.golden_eggs_earned < db_backup.game.golden_eggs_earned:
			response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.COULD_NOT_OVERWRITE
			response.message = "Remote backup has more golden eggs."
			return base64.b64encode(common.make_auth_message(response).SerializeToString())

		elif msg.artifacts.crafting_xp < db_backup.artifacts.crafting_xp:
			response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.COULD_NOT_OVERWRITE
			response.message = "Remote backup has more Artifact Crafting XP."
			return base64.b64encode(common.make_auth_message(response).SerializeToString())

		elif msg.artifacts.inventory_score < db_backup.artifacts.inventory_score:
			response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.COULD_NOT_OVERWRITE
			response.message = "Remote backup has a better Artifact Inventory."
			return base64.b64encode(common.make_auth_message(response).SerializeToString())

	# if no conflicts, update the backup
	response.success = True
	response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.NO_ERROR
	response.existing_backup.Clear()

	g.db.users.update_one({"_id": msg.ei_user_id}, {"$set": {"backup": msg.SerializeToString()}})
	print(f"Backup for {msg.ei_user_id} saved!")

	return base64.b64encode(common.make_auth_message(response).SerializeToString())

"""
Get Egg, Inc. configuration data, such as a boost's golden egg cost, min soul egg to unlock, etc.
"""
@ei_bp.route('/get_config', methods=['POST'])
@common.proto_parser(ei_pb2.ConfigRequest)
def get_config(_: ei_pb2.ConfigRequest):
	response = ei_pb2.ConfigResponse()

	response.live_config.CopyFrom(gen.make_liveconfig())
	response.mail_bag.mail.append(ei_pb2.InGameMail(
		id="custom-server",
		title="Custom Server",
		message="You are currently connected to a custom server.",
		date="now",
		tip=False,
		user_type=ei_pb2.UserType.ALL_USERS,
		app_link=ei_pb2.UILocation.NONE
	))

	return base64.b64encode(common.make_auth_message(response).SerializeToString())

"""
Get the list of time-based things such as events, contracts, etc.
"""
@ei_bp.route('/get_periodicals', methods=['POST'])
@common.proto_parser(ei_pb2.GetPeriodicalsRequest)
def get_periodicals(_: ei_pb2.GetPeriodicalsRequest):
	response = ei_pb2.PeriodicalsResponse()

	events: list[dict] = g.db.events.find()
	for event_db in events:
		event_msg = ei_pb2.EggIncEvent()
		common.json_to_protobuf(event_db, event_msg)

		end_time = event_msg.start_time + event_msg.duration
		event_msg.seconds_remaining = min(max(end_time - time.time(), 0), event_msg.duration)

		if event_msg.seconds_remaining == 0:
			print(f"Event {event_msg.identifier} has ended, deleting.")
			g.db.events.delete_one({"_id": event_db.get("_id")})
			continue

		response.events.events.append(event_msg)

	response.contracts.server_time = time.time()
	response.contracts.warning_message = "Contracts have not yet been implemented into NeoInc."

	return base64.b64encode(common.make_auth_message(response).SerializeToString())