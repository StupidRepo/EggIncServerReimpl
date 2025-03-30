import base64
import functools
import hashlib
from flask import request
from pymongo.database import Database

from pb import ei_pb2
from utils.hash import hash_v1, hash_v2

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


def make_auth_message(proto_msg, use_v2: bool = False) -> ei_pb2.AuthenticatedMessage:
    auth_msg = ei_pb2.AuthenticatedMessage()
    auth_msg.code = hash_v2(proto_msg.SerializeToString()) if use_v2 else hash_v1(proto_msg.SerializeToString())
    auth_msg.message = proto_msg.SerializeToString()

    return auth_msg


def proto_parser(proto_class, is_auth=False):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.form.get('data').replace(' ', '+')  # thanks flask :(
            if not data:
                raise Exception("No data passed!")

            decoded_data = base64.b64decode(data, validate=True)

            final_proto_msg = proto_class()
            if is_auth:
                proto_msg = ei_pb2.AuthenticatedMessage()
                proto_msg.ParseFromString(decoded_data)

                exp = hash_v1(proto_msg.message)
                expv2 = hash_v2(proto_msg.message)
                if proto_msg.code != exp and proto_msg.code != expv2:
                    print("failed to verify hash :(")
                    raise Exception("could not verify hash!")

                final_proto_msg.ParseFromString(proto_msg.message)
            else:
                final_proto_msg.ParseFromString(decoded_data)

            return f(final_proto_msg, *args, **kwargs)

        return decorated_function

    return decorator