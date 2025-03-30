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

def make_gradespec(grade: ei_pb2.Contract.PlayerGrade, mult: float) -> ei_pb2.Contract.GradeSpec:
    grade_spec = ei_pb2.Contract.GradeSpec()
    grade_spec.grade = grade
    grade_spec.goals.append(
        ei_pb2.Contract.Goal(
            type=ei_pb2.GoalType.EGGS_LAID,
            target_amount=1337 * (mult * 0.5),

            reward_type=ei_pb2.RewardType.PIGGY_FILL,
            reward_amount=1234 * (mult * 0.75),
        )
    )

    grade_spec.length_seconds = 120

    return grade_spec

def make_test_contract() -> ei_pb2.Contract:
    contract = ei_pb2.Contract()

    grade_unset = make_gradespec(ei_pb2.Contract.PlayerGrade.GRADE_UNSET, 1)
    grade_c = make_gradespec(ei_pb2.Contract.PlayerGrade.GRADE_C, 2)
    grade_b = make_gradespec(ei_pb2.Contract.PlayerGrade.GRADE_B, 2.25)

    grade_a = make_gradespec(ei_pb2.Contract.PlayerGrade.GRADE_A, 2.3)
    grade_aa = make_gradespec(ei_pb2.Contract.PlayerGrade.GRADE_AA, 2.5)
    grade_aaa = make_gradespec(ei_pb2.Contract.PlayerGrade.GRADE_AAA, 2.55)
    contract.grade_specs.append(grade_unset)
    contract.grade_specs.append(grade_c)
    contract.grade_specs.append(grade_b)

    contract.grade_specs.append(grade_a)
    contract.grade_specs.append(grade_aa)
    contract.grade_specs.append(grade_aaa)

    contract.start_time = 1743004800
    contract.expiration_time = 1743609600
    contract.length_seconds = 120

    contract.chicken_run_cooldown_minutes = 2
    contract.minutes_per_token = 1

    contract.identifier = "test-contract"
    contract.name = "Test Contract"
    contract.description = "Hey!"

    contract.leggacy = True
    contract.debug = True

    return contract