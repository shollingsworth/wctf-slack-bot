#!/usr/bin/env python
# -*- coding: utf-8 -*-


class User(object):
    def __init__(
        self,
        data,
    ):
        self.raw_data_json = data
        self.color = data.get('color')
        self.deleted = data.get('deleted')
        self.has_2fa = data.get('has_2fa')
        self.id = data.get('id')
        self.is_admin = data.get('is_admin')
        self.is_app_user = data.get('is_app_user')
        self.is_bot = data.get('is_bot')
        self.is_owner = data.get('is_owner')
        self.is_primary_owner = data.get('is_primary_owner')
        self.is_restricted = data.get('is_restricted')
        self.is_ultra_restricted = data.get('is_ultra_restricted')
        self.name = data.get('name')
        self.profile = data.get('profile')
        self.profile_avatar_hash = data.get('profile', {}).get('avatar_hash')
        self.profile_display_name = data.get('profile', {}).get('display_name')
        self.profile_display_name_normalized = data.get('profile', {}).get('display_name_normalized')
        self.profile_email = data.get('profile', {}).get('email')
        self.profile_image_192 = data.get('profile', {}).get('image_192')
        self.profile_image_24 = data.get('profile', {}).get('image_24')
        self.profile_image_32 = data.get('profile', {}).get('image_32')
        self.profile_image_48 = data.get('profile', {}).get('image_48')
        self.profile_image_512 = data.get('profile', {}).get('image_512')
        self.profile_image_72 = data.get('profile', {}).get('image_72')
        self.profile_real_name = data.get('profile', {}).get('real_name')
        self.profile_real_name_normalized = data.get('profile', {}).get('real_name_normalized')
        self.profile_status_emoji = data.get('profile', {}).get('status_emoji')
        self.profile_status_text = data.get('profile', {}).get('status_text')
        self.profile_team = data.get('profile', {}).get('team')
        self.real_name = data.get('real_name')
        self.team_id = data.get('team_id')
        self.tz = data.get('tz')
        self.tz_label = data.get('tz_label')
        self.tz_offset = data.get('tz_offset')
        self.updated = data.get('updated')


# Sample Object
SAMPLE_OBJECT = {
    "profile" : {
        "display_name" : "spengler",
        "status_emoji" : ":books:",
        "team" : "T012AB3C4",
        "real_name" : "Egon Spengler",
        "image_24" : "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "real_name_normalized" : "Egon Spengler",
        "image_512" : "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "display_name_normalized" : "spengler",
        "image_32" : "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_48" : "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_72" : "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "avatar_hash" : "ge3b51ca72de",
        "status_text" : "Print is dead",
        "email" : "spengler@ghostbusters.example.com",
        "image_192" : "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg"
    },
    "updated" : 1502138686,
    "tz" : "America/Los_Angeles",
    "name" : "spengler",
    "deleted" : False,
    "is_app_user" : False,
    "is_bot" : False,
    "tz_label" : "Pacific Daylight Time",
    "real_name" : "Egon Spengler",
    "color" : "9f69e7",
    "team_id" : "T012AB3C4",
    "is_admin" : True,
    "is_ultra_restricted" : False,
    "is_restricted" : False,
    "is_owner" : False,
    "tz_offset" : -25200,
    "has_2fa" : False,
    "id" : "W012A3CDE",
    "is_primary_owner" : False
}


if __name__ == '__main__':
    obj = User(SAMPLE_OBJECT)
    attributes = [i for i in dir(obj) if not i.startswith('__')]
    for i in attributes:
        print(i, getattr(obj, i))
