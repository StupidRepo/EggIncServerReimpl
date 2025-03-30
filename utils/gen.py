import time

import consts
from pb import ei_pb2

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

def make_afxconfig() -> ei_pb2.ArtifactsConfigurationResponse:
    afx_config = ei_pb2.ArtifactsConfigurationResponse()
    
    afx_config.mission_parameters.extend(consts.MISSION_PARAMETERS)

    return afx_config


def make_subscription() -> ei_pb2.UserSubscriptionInfo:
    subscription = ei_pb2.UserSubscriptionInfo()
    subscription.subscription_level = ei_pb2.UserSubscriptionInfo.Level.PRO
    subscription.status = ei_pb2.UserSubscriptionInfo.Status.ACTIVE

    subscription.first_subscribed = time.time() - 1000000
    subscription.last_updated = time.time() - 200
    subscription.period_end = time.time() + 1000000

    subscription.auto_renew = False
    subscription.platform = ei_pb2.Platform.DROID
    return subscription