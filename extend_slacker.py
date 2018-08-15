#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import slacker
# https://github.com/os/slacker/pull/135


class SlackerDialogAdd(slacker.BaseAPI):
    def open(self, dialog, trigger_id):
        return self.post(
            'dialog.open',
            data={
                'dialog': json.dumps(dialog),
                'trigger_id': trigger_id,
            }
        )


# Patching to add Dialog
slacker.__all__.append('Dialog')
slacker.Dialog = SlackerDialogAdd


class Slacker(slacker.Slacker):
    def __init__(
            self,
            token,
            incoming_webhook_url=None,
            timeout=10,
            http_proxy=None,
            https_proxy=None,
            session=None,
            rate_limit_retries=0,
    ):
        slacker.Slacker.__init__(
            self,
            token,
            incoming_webhook_url,
            timeout,
            http_proxy,
            https_proxy,
            session,
            rate_limit_retries,
        )
        proxies = self.__create_proxies(http_proxy, https_proxy)
        api_args = {
            'token': token,
            'timeout': timeout,
            'proxies': proxies,
            'session': session,
            'rate_limit_retries': rate_limit_retries,
        }
        self.dialog = SlackerDialogAdd(**api_args)
