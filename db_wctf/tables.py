#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from sqlalchemy_json import MutableJson
import sqlalchemy as sa
from base import Base
from datetime import datetime


class FoxTrack(Base):
    __tablename__ = 'foxes'
    bssid = sa.Column(sa.String(256), nullable=False, primary_key=True)
    ssid = sa.Column(sa.String(256), nullable=True)
    created = sa.Column(sa.DateTime, index=True, default=datetime.now)
    updated = sa.Column(
        sa.DateTime,
        index=True,
        onupdate=datetime.now,
        default=datetime.now,
    )
    passphrase = sa.Column(sa.String(256), nullable=True)
    source = sa.Column(MutableJson, nullable=True)


class AuthedTeamsData(Base):
    __tablename__ = 'slack_authed_teams'
    team_id = sa.Column(sa.String(20), nullable=False, primary_key=True)
    team_json = sa.Column(MutableJson)
