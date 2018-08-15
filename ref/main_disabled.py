# Disabling after initial auth
from flask import render_template
    import auth
# This will be put under Redirect URLs under the oAuth section for you app
# Example https://blarg.com/{callback_url} , https is required
@app.route("/callback", methods=["GET", "POST"])
def callback():
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
    "This route renders the installation page with 'Add to Slack' button."
    return render_template(
        "install.html",
        bot_name=botconfig.bot_name,
        client_id=botconfig.client_id,
        scope=botconfig.bot_scope,
    )
