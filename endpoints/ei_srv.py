import base64
from flask import Blueprint, g
import db
from pb import ei_pb2
from utils import common, gen

ei_srv = Blueprint('ei_srv', __name__)

@ei_srv.route('/subscription_status/<user_id>', methods=['POST'])
def subscription_status(user_id):
	response = ei_pb2.UserSubscriptionInfo()

	user = db.DBUser(user_id, db.client)
	if user is None:
		print("Can't get subscription status for non-existent user!")
		return base64.b64encode(common.make_auth_message(response).SerializeToString())

	subscription: bool = user.get('subscribed', False)
	if subscription:
		response.CopyFrom(gen.make_subscription())
	else:
		response.status = ei_pb2.UserSubscriptionInfo.Status.UNKNOWN

	return base64.b64encode(common.make_auth_message(response).SerializeToString())