import base64
import time

from flask import Blueprint, g
from pb import ei_pb2
from utils import common

ei_afx_bp = Blueprint('ei_afx', __name__)

@ei_afx_bp.route('/config', methods=['POST'])
@common.proto_parser(ei_pb2.ArtifactsConfigurationRequest)
def get_afx_config(msg: ei_pb2.ArtifactsConfigurationRequest):
    pass