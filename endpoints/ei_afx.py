import base64
import time
from google.protobuf.json_format import MessageToDict, ParseDict
from flask import Blueprint, g
import consts
import db
from pb import ei_pb2
from utils import common, gen

ei_afx_bp = Blueprint('ei_afx', __name__)

@ei_afx_bp.route('/config', methods=['POST'])
@common.proto_parser(ei_pb2.ArtifactsConfigurationRequest)
def get_afx_config(_: ei_pb2.ArtifactsConfigurationRequest):
    return base64.b64encode(common.make_auth_message(gen.make_afxconfig()).SerializeToString())

# TODO: Figure out better way to do this
# @ei_afx_bp.route('/get_active_missions', methods=['POST'])
# @common.proto_parser(ei_pb2.BasicRequestInfo, True)
# def get_active_missions(msg: ei_pb2.BasicRequestInfo):
#     response = ei_pb2.GetActiveMissionsResponse()
#     response.success = False
#
#     user = db.DBUser(msg.ei_user_id, db.client)
#     if user is None:
#         print("Can't get missions for non-existent user!")
#         return base64.b64encode(common.make_auth_message(response).SerializeToString())
#
#     missions = user.get_missions()
#
#     for mission in missions:
#         remaining = (mission.start_time_derived + mission.duration_seconds) - time.time()
#         remaining = min(max(remaining, 0), mission.duration_seconds)
#         print(f"Mission {mission.identifier} has {remaining} seconds remaining")
#         if remaining <= 0:
#             mission.status = ei_pb2.MissionInfo.Status.RETURNED
#         else:
#             mission.seconds_remaining = remaining
#
#     # filter through list and exclude missions that are not active (status != EXPLORING)
#     missions = [mission for mission in missions if mission.status != ei_pb2.MissionInfo.Status.COMPLETE]
#
#     response.active_missions.extend(missions)
#     response.success = True
#
#     return base64.b64encode(common.make_auth_message(response).SerializeToString())

# TODO: Figure out better way to do this, too
# @ei_afx_bp.route('/launch_mission', methods=['POST'])
# @common.proto_parser(ei_pb2.MissionRequest)
# def launch_mission(msg: ei_pb2.MissionRequest):
#     response = ei_pb2.MissionResponse()
#     response.success = False
#
#     params: ei_pb2.MissionInfo.MissionParameters | None = None
#     seconds = -1
#     for param in consts.MISSION_PARAMETERS:
#         if param.ship == msg.info.ship:
#             params = param
#             break
#
#     if params is None:
#         print("Invalid ship type! Has the code been updated to support it?")
#         return base64.b64encode(common.make_auth_message(response).SerializeToString())
#
#     for duration in params.durations:
#         if duration.duration_type == msg.info.duration_type:
#             seconds = duration.seconds
#             break
#
#     if seconds == -1:
#         print("Invalid duration provided!")
#         return base64.b64encode(common.make_auth_message(response).SerializeToString())
#
#     user = db.DBUser(msg.ei_user_id, db.client)
#     if user is None:
#         print("Can't get missions for non-existent user!")
#         return base64.b64encode(common.make_auth_message(response).SerializeToString())
#
#     mission = ei_pb2.MissionInfo()
#     mission.CopyFrom(msg.info)
#
#     mission.identifier = "mission_" + str(int(time.time()))
#     mission.status = ei_pb2.MissionInfo.Status.EXPLORING
#
#     mission.seconds_remaining = seconds
#     mission.duration_seconds = seconds
#
#     mission.start_time_derived = time.time()
#
#     user.add_mission(mission)
#     print(f"Mission {mission.identifier} launched for {msg.ei_user_id}!")
#
#     response.info.CopyFrom(mission)
#     response.info.start_time_derived = 0 # client doesn't need to know this
#     response.success = True
#
#     return base64.b64encode(response.SerializeToString())