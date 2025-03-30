import base64
import time
from datetime import datetime, timedelta

from flask import Blueprint, g
from google.protobuf.json_format import ParseDict

import db
from pb import ei_pb2
from utils import common, gen

ei_bp = Blueprint('ei', __name__)

"""
Creates the user's account if it doesn't exist, and returns the user's backup data if it exists.
"""
@ei_bp.route('/first_contact_secure', methods=['POST'])
@common.proto_parser(ei_pb2.EggIncFirstContactRequest, True)
def first_contact_secure(msg: ei_pb2.EggIncFirstContactRequest):
	neo_id = common.did_to_nid(msg.device_id)

	response = ei_pb2.EggIncFirstContactResponse()
	response.ei_user_id = neo_id

	# check if account is in DB
	try:
		user = db.DBUser(neo_id, db.client)
	except Exception as e:
		print(f"Error getting user {neo_id}: {e}")
		user = None

	# if user is None, create a new account
	if user is None:
		print(f"Creating new user")

		db.client.users_collection.insert_one({"_id": neo_id, "device_id": msg.device_id})
		response.ids_transferred.append(msg.device_id)
	else:
		prev_backup = user.get_backup()
		if prev_backup is not None:
			print("Backup found!")
			response.backup.CopyFrom(prev_backup)
		else:
			print("No backup found for user.")

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
	try:
		user = db.DBUser(msg.ei_user_id, db.client)
	except Exception as e:
		print(f"Error getting user {msg.user_id}: {e}")
		user = None

	if user is None:
		return base64.b64encode(common.make_auth_message(response).SerializeToString())

	prev_backup = user.get_backup()
	if not msg.force_backup and prev_backup is not None:
		response.existing_backup.CopyFrom(prev_backup)
		if sum(msg.stats.egg_totals) < sum(prev_backup.stats.egg_totals): # acts as a Backup.game.lifetime_earnings replacement as I think that is done on server then appended to the backup, but I'm not sure, so I'm doing this instead lol
			response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.COULD_NOT_OVERWRITE
			response.message = "Remote backup has greater lifetime earnings."
			return base64.b64encode(common.make_auth_message(response).SerializeToString())

		elif msg.game.soul_eggs < prev_backup.game.soul_eggs:
			response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.COULD_NOT_OVERWRITE
			response.message = "Remote backup has more soul eggs."
			return base64.b64encode(common.make_auth_message(response).SerializeToString())

		elif msg.game.eggs_of_prophecy < prev_backup.game.eggs_of_prophecy:
			response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.COULD_NOT_OVERWRITE
			response.message = "Remote backup has more eggs of prophecy."
			return base64.b64encode(common.make_auth_message(response).SerializeToString())

		elif msg.game.golden_eggs_earned < prev_backup.game.golden_eggs_earned:
			response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.COULD_NOT_OVERWRITE
			response.message = "Remote backup has more golden eggs."
			return base64.b64encode(common.make_auth_message(response).SerializeToString())

		elif msg.artifacts.crafting_xp < prev_backup.artifacts.crafting_xp:
			response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.COULD_NOT_OVERWRITE
			response.message = "Remote backup has more Artifact Crafting XP."
			return base64.b64encode(common.make_auth_message(response).SerializeToString())

		elif msg.artifacts.inventory_score < prev_backup.artifacts.inventory_score:
			response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.COULD_NOT_OVERWRITE
			response.message = "Remote backup has a better Artifact Inventory."
			return base64.b64encode(common.make_auth_message(response).SerializeToString())

	# if no conflicts, update the backup
	response.success = True
	response.error_code = ei_pb2.SaveBackupResponse.ErrorCodes.NO_ERROR
	response.existing_backup.Clear()

	user.update_backup(msg)
	print(f"Backup for {msg.ei_user_id} saved!")

	return base64.b64encode(common.make_auth_message(response).SerializeToString())

"""
Get Egg, Inc. configuration data, such as a boost's golden egg cost, min soul egg to unlock, etc.
"""
@ei_bp.route('/get_config', methods=['POST'])
@common.proto_parser(ei_pb2.ConfigRequest)
def get_config(msg: ei_pb2.ConfigRequest):
	user = db.DBUser(msg.rinfo.ei_user_id, db.client) # we want to error if the user doesn't exist, so no try/except here
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
	contracts = ei_pb2.ContractsResponse()

	events: list[dict] = db.client.events_collection.find()
	for event_db in events:
		event_msg = ei_pb2.EggIncEvent()
		common.json_to_protobuf(event_db, event_msg)

		end_time = event_msg.start_time + event_msg.duration
		event_msg.seconds_remaining = min(max(end_time - time.time(), 0), event_msg.duration)

		if event_msg.seconds_remaining == 0:
			print(f"Event {event_msg.identifier} has ended, deleting.")
			db.client.events_collection.delete_one({"_id": event_db.get("_id")})
			continue

		response.events.events.append(event_msg)

	contracts.server_time = time.time()
	contracts.warning_message = "Contracts have not been fully implemented into NeoInc." # TODO: Contract implementation

	# contracts_in_db: list[dict] = db.client.contracts_collection.find()
	# for contract_db in contracts_in_db:
	# 	cmsg: ei_pb2.Contract = ParseDict(contract_db, ei_pb2.Contract())
	# 	cmsg.length_seconds = 120 # this would correspond to cmsg.grade_specs -> appropriate one for user's grade -> .length_seconds - for now we just set it to 120 seconds
	#
	# 	contracts.contracts.append(cmsg)
	contracts.contracts.append(gen.make_test_contract())

	response.contracts.CopyFrom(contracts)
	return base64.b64encode(common.make_auth_message(response).SerializeToString())

"""
Simple daily gift info.
"""
@ei_bp.route('/daily_gift_info', methods=['POST'])
def daily_gift_info():
	response = ei_pb2.DailyGiftInfo()
	response.current_day = int(time.strftime("%j", time.gmtime()))

	midnight = datetime.combine(datetime.utcnow().date(), datetime.min.time())
	response.seconds_to_next_day = int((midnight + timedelta(days=1) - datetime.utcnow()).total_seconds())

	print(f"Seconds to next day: {response.seconds_to_next_day}")

	return base64.b64encode(response.SerializeToString())