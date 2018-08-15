# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import json
from sys import modules, stdout
from flask import Flask, request, jsonify, render_template
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
})
app.cache = cache
with app.app_context():
    # Some of these need to be aware of 'from flask import current_app'
    import event
    import commands
    import libresponse
    import dialog
    import menu
    import libcache
    import botconfig
    from lambda_exception import caught
    import libfox
    import auth
    # PEP8 complains
    menu
    dialog
    libcache

FIELD_OK = 'ok'
FIELD_MSG = 'msg'
FIELD_RESULT = 'result'

LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)
available_loggers = sorted(logging.Logger.manager.loggerDict.keys())
LOG.info(
    "The following Log Instances are Available to Set:\n%s",
    json.dumps(available_loggers, indent=4, separators=(',', ' : '))
)

event_processors = [
    event.pevent,
]


def get_request_data(request):
    if request.data:
        dat = json.loads(request.data)
    elif request.form:
        dat = json.loads(request.form)
    else:
        raise ValueError("post data from {} unavailable".format(request))
    return dat


def pi_token_verify(headers):
    token = headers.get('CTFTOKEN')
    if token and botconfig.CTFTOKEN and token == botconfig.CTFTOKEN:
        return True
    else:
        return False


def slack_token_verify(data):
    token = data.get('token')
    if botconfig.verifcation_token and token and token == botconfig.verifcation_token:
        return True
    else:
        return False


@app.route("/hi", methods=["GET"])
def hi_there():
    """ waves """
    return "hi there"


@app.route("/add_fox", methods=["POST"])
def add_fox():
    """ add new fox """
    if not pi_token_verify(request.headers):
        return libresponse.bad_token(request)
    try:
        data = get_request_data(request)
        LOG.info("revieced update: {}".format(data))
        res = libfox.add_fox(data, request.headers.__dict__)
        res[FIELD_OK] = True
        res[FIELD_MSG] = 'OK'
        return jsonify(res)
    except Exception as e:
        LOG.exception("Error on add_fox")
        return jsonify({
            FIELD_OK: False,
            FIELD_MSG: e.message,
        })


@app.route("/delete_fox", methods=["POST"])
def delete_fox():
    """ update single fox entry"""
    if not pi_token_verify(request.headers):
        return libresponse.bad_token(request)
    try:
        data = get_request_data(request)
        LOG.info("revieced update: {}".format(data))
        res = libfox.delete_fox(data)
        res[FIELD_OK] = True
        res[FIELD_MSG] = 'OK'
        return jsonify(res)
    except Exception as e:
        LOG.exception("Error on add_fox")
        return jsonify({
            FIELD_OK: False,
            FIELD_MSG: e.message,
        })


@app.route("/update_fox", methods=["POST"])
def update_fox():
    """ update single fox entry"""
    if not pi_token_verify(request.headers):
        return libresponse.bad_token(request)
    try:
        data = get_request_data(request)
        LOG.info("revieced update: {}".format(data))
        res = libfox.update_fox(data)
        res[FIELD_OK] = True
        res[FIELD_MSG] = 'OK'
        return jsonify(res)
    except Exception as e:
        LOG.exception("Error on add_fox")
        return jsonify({
            FIELD_OK: False,
            FIELD_MSG: e.message,
        })


@app.route("/foxes", methods=["GET"])
def get_foxes():
    """ return a json list of all foxes """
    if not pi_token_verify(request.headers):
        return libresponse.bad_token(request)
    vals = libfox.get_foxes()
    return jsonify(vals)


# Process form input
@app.route("/form", methods=["POST"])
def formprocess():
    data = request.form.getlist('payload')
    assert len(data) == 1, "Error, form data length != 1 @ {}".format(
        len(data)
    )
    data = [json.loads(i) for i in data][0]
    if not slack_token_verify(data):
        return libresponse.bad_token(request)

    LOG.debug(
        "/form\n%s",
        json.dumps(data, indent=4, separators=(',', ' : '))
    )
    response_url = data.get('response_url')
    if not response_url:
        raise Exception("Error, no response url detected")
    callback = data.get('callback_id')
    try:
        mymodule = modules[__name__]
        func_name = callback.split('.')[-1]
        import_chain = callback.split('.')[:-1]
        for mod in import_chain:
            mymodule = getattr(mymodule, mod)
        cb_func = getattr(mymodule, func_name)
        process_data = cb_func(data)
        error_list = process_data['error_list']
        if error_list:
            retarr = {
                'errors': error_list,
            }
            pretty = json.dumps(retarr, indent=4, separators=(',', ' : '))
            LOG.error("Returning Validation Error: {}".format(pretty))
            return jsonify(retarr)
        process_data['func'](process_data['data'])
        return libresponse.ok_say()
    except Exception as e:
        LOG.exception("Form Exception")
        caught(e, data, response_url)
        return libresponse.error(e.message)


# Process menu calls
@app.route("/menu", methods=["POST"])
def menuprocess():
    data = request.form.getlist('payload')
    assert len(data) == 1, "Error, form data length != 1 @ {}".format(
        len(data)
    )
    data = [json.loads(i) for i in data][0]
    if not slack_token_verify(data):
        return libresponse.bad_token(request)

    try:
        mymodule = modules[__name__]
        func_name = data.get('name').split('.')[-1]
        import_chain = data.get('name').split('.')[:-1]
        for mod in import_chain:
            mymodule = getattr(mymodule, mod)
        cb_func = getattr(mymodule, func_name)
        return cb_func(data)
    except Exception as e:
        LOG.exception("Menu Exception")
        caught(e, data)


@app.route("/cmd", methods=["POST"])
def docmd():
    data = request.form
    if not data:
        raise Exception("Error, data is empty in request")
    if not slack_token_verify(data):
        return libresponse.bad_token(request)

    LOG.debug(
        "/cmd\n%s",
        json.dumps(data, indent=4, separators=(',', ' : '))
    )
    response_url = data.get('response_url')
    try:
        commands.handler(data)
        return libresponse.ok_say()
    except Exception as e:
        LOG.exception("Command Exception")
        caught(e, data, response_url)
        return libresponse.error(e.message)


@app.route("/event", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    if request.data:
        slack_event = json.loads(request.data)
    elif request.form:
        slack_event = json.loads(request.form)
    else:
        raise Exception("Error, request.data/form not present")
    stdout.flush()

    LOG.debug("EVENT {}".format(
        (json.dumps(slack_event, indent=4, separators=(',', ' : ')))
    ))

    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        challenge = slack_event.get('challenge')
        return jsonify(challenge)

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if not slack_token_verify(slack_event):
        return libresponse.bad_token(request)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    if "event" not in slack_event:
        return libresponse.not_found(
            "[NO EVENT IN SLACK REQUEST] These are not the droids you're looking for.",
        )

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    process_errors = []
    for processor in event_processors:
        try:
            processor.Process(slack_event).process_event()
        except Exception as e:
            LOG.exception("Event Exception")
            process_errors.append("Error processing event: {} error:{}\n{}".format(
                processor.__name__,
                e,
                slack_event,
            ))
            caught(e, slack_event)
    if process_errors:
        return libresponse.error("\n".join(process_errors))
    return libresponse.ok_say()


@app.route("/callback", methods=["GET", "POST"])
def callback():
    if not botconfig.ENABLE_CALLBACK:
        return libresponse.error("no cb")
    # Let's grab that temporary authorization code Slack's sent us from
    # the request's parameters.
    code_arg = request.args.get('code')
    if not code_arg:
        raise Exception(
            "Error, code not specified during oauth setup, see: {}".format(
                'https://api.slack.com/docs/slack-button',
            )
        )
    # The bot's auth method to handles exchanging the code for an OAuth token
    auth.application_auth(code_arg)
    return render_template("thanks.html")


# This is pretty simple, pretty much a static html page based on class varibles
@app.route("/install", methods=["GET"])
def pre_install():
    if not botconfig.ENABLE_CALLBACK:
        return libresponse.error("no cb")
    "This route renders the installation page with 'Add to Slack' button."
    return render_template(
        "install.html",
        bot_name=botconfig.bot_name,
        client_id=botconfig.client_id,
        scope=botconfig.bot_scope,
    )
