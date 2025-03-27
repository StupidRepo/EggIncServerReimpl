import base64
import functools
import hashlib
from flask import request

import consts
from pb import ei_pb2
from utils.hash import hash_v1


def did_to_nid(input_id):
	"""
	Converts a device ID to a NeoInc ID
	"""
	hash_digest = hashlib.md5(input_id.encode()).digest()
	generated_number = int.from_bytes(hash_digest[:7], byteorder='big') % (10 ** 16)

	return "NI" + str(generated_number).zfill(16)

def json_to_protobuf(json_data, proto_message):
	for key, value in json_data.items():
		if not hasattr(proto_message, key):
			continue
		if isinstance(value, dict):
			json_to_protobuf(value, getattr(proto_message, key))
		elif isinstance(value, list):
			for item in value:
				if isinstance(item, dict):
					json_to_protobuf(item, getattr(proto_message, key).add())
				else:
					getattr(proto_message, key).append(item)
		else:
			setattr(proto_message, key, value)

def make_auth_message(proto_msg) -> ei_pb2.AuthenticatedMessage:
	auth_msg = ei_pb2.AuthenticatedMessage()
	auth_msg.code = hash_v1(proto_msg.SerializeToString())
	auth_msg.message = proto_msg.SerializeToString()

	return auth_msg

def proto_parser(proto_class, is_auth=False):
	def decorator(f):
		@functools.wraps(f)
		def decorated_function(*args, **kwargs):
			data = request.form.get('data').replace(' ', '+') # thanks flask :(
			if not data:
				raise Exception("No data passed!")

			decoded_data = base64.b64decode(data, validate=True)

			final_proto_msg = proto_class()
			if is_auth:
				proto_msg = ei_pb2.AuthenticatedMessage()
				proto_msg.ParseFromString(decoded_data)

				if proto_msg.code != hash_v1(proto_msg.message):
					raise Exception("Something is wrong!")

				final_proto_msg.ParseFromString(proto_msg.message)
			else:
				final_proto_msg.ParseFromString(decoded_data)

			return f(final_proto_msg, *args, **kwargs)

		return decorated_function

	return decorator

def make_liveconfig() -> ei_pb2.LiveConfig:
	live_config = ei_pb2.LiveConfig()
	boosts_config = ei_pb2.LiveConfig.BoostsConfig()
	gift_config = ei_pb2.LiveConfig.GiftConfig()
	misc_config = ei_pb2.LiveConfig.MiscConfig()

	boosts_config.item_configs.extend(consts.BOOST_ITEMS)
	boosts_config.cash_boost_cooloff_time = 30

	gift_config.gift_configs.extend(consts.GIFT_CONFIGS)
	gift_config.package_interval = 250
	gift_config.package_interval_contract = 290
	gift_config.video_offer_interval = 300
	gift_config.video_offer_interval_contract = 330

	misc_config.ask_to_track = False
	misc_config.chicken_run_boost_percentage = 0.05
	misc_config.shells_intro_tickets = 25

	live_config.boosts_config.CopyFrom(boosts_config)
	live_config.gift_config.CopyFrom(gift_config)
	live_config.misc_config.CopyFrom(misc_config)

	return live_config