import base64
import time

from flask import Blueprint, g
from pb import ei_pb2
from utils import common, gen

ei_afx_bp = Blueprint('ei_afx', __name__)

@ei_afx_bp.route('/config', methods=['POST'])
@common.proto_parser(ei_pb2.ArtifactsConfigurationRequest)
def get_afx_config(_: ei_pb2.ArtifactsConfigurationRequest):
    return base64.b64encode(common.make_auth_message(gen.make_afxconfig()).SerializeToString())