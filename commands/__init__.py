#!/usr/bin/env python
# -*- coding: utf-8 -*-
import err_response
import available_commands
import help_response

translation_map = {
    'list': 'list_response',
}


def handler(cmd_data):
    cmd_data = cmd_data.copy()  # otherwise we'll get an immutible dict error
    text = cmd_data.get('text').strip()
    if not text:
        text = 'help'
        cmd_data['text'] = 'help'
    elif text in translation_map:
        text = translation_map.get(text)
        cmd_data['text'] = text

    try:
        if text == 'help':
            dest_sub_module = help_response
        else:
            dest_sub_module = getattr(available_commands, text)
    except AttributeError:
        dest_sub_module = err_response

    dest_class = getattr(dest_sub_module, 'Process')
    cl = dest_class(cmd_data)
    return cl.cmd()
