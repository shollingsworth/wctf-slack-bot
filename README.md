# Prerequisites
## AWS Profile
Setup a profile in ~/.aws/credentials

example:
```
[myprofile]
aws_access_key_id = xxxxxxxxxxxxxxxxxxxx
aws_secret_access_key = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## setup virtualenv (assumes bash)
Run:
```
./setup_virtualenv.sh
source ./venv/bin/activate
```

## pre-setup (2) two elastic ips and make a note of their id's
See: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html


-----------------------
# Setup & Teardown of the bot environment
## Setting up DB / VPC
Run the command: (this will likely take ~20 minutes to complete, mostly due to RDS setup)
```
./env_setup/setup_lambda_rds.py --environment dev --profile personal --eip1 eipalloc-xxxxxxxx --eip2 eipalloc-xxxxxxxx --acl 8.8.8.8/32
```

for more flags issue `./env_setup/setup_lambda_rds.py -h`

## Tearing it down
1.) Delete contents of created bucket
2.) Go to cloudformation, delete stack with the label previously assigned in the setup_lambda_rds command

-----------------------
# Setting up the DB / tables
`./env_setup/modify_db.py init --environment dev --sql_user mysqluser`


-----------------------
# Editing environment settings
using example in `./env_setup/dev.json`

## set connection_type to "mysql_rds"
* `"connection_type" : "mysql_rds"`

## generate random token
* `"ctftoken" : "Q4stYvFUQJV0bewIvcuwILD2X0j12IVPbg7dHzsy"`

## set empty events line, see Zappa documentation on the format of the events array
* `"events": []`

## set the default log level - can be any log level logging.setLevel(*) understands
* `"log_level": 'DEBUG'`

## set team_id
* `"team_id": "TXXXXXX"`
    * See https://stackoverflow.com/a/44883343/7049363 on how to grab this from the web UI

-----------------------
# slack bot setup

## Enable callback (will be disabled after)
edit `botconfig.py` and set `ENABLE_CALLBACK` to `True`

## fill out credentials in ./env_setup/dev.json
* "slack_client_id"
* "slack_client_secret"
* "slack_signing_secret"
* "slack_verification_token"
* ![Get App Credential Values](./graphics/Selection_017.png)

## create exception logging channel and webhook
* Create channel `#lambda_bot_exceptions`
* setup webhook for exceptions
    * enter value for key "exception_hook\_url" in `./env_setup/dev.json`
    * ![Webhook Graphic](./graphics/Selection_018.png)

## deploy slack bot lambda
* insert gpg key fingerprint (no spaces) into `./env_setup/gpg.recipients`
* run `./env_setup/genzappa_settings.py`
    * this will generate the `zappa_config.json` and encrypt the config's secrets for storage in source control (if desired)
* run `./setup_virtualenv.sh` and `source ./venv/bin/active` to prep environment
* zappa deploy, make note of the URL for next steps
    * ![Zappa Deploy Graphic](./graphics/Selection_020.png)

## enable bot account
* ![Enable Bot Account](./graphics/Selection_022.png)

## set callback url
* enter callback url with ext `/callback` i.e. `https://xxxxxxx.execute-api.us-east-2.amazonaws.com/dev/callback`
* ![Set Callback URL](./graphics/Selection_023.png)

## set permissions
* ![Set Permissions](./graphics/Selection_024.png)

## set api token usage to the two EIP's defined previously
* ![Set API EIP's](./graphics/Selection_025.png)

## install to workspace by clicking the "Add to Slack" button
* Add to workspace
    * ![Click Add to Slack for workspace](./graphics/Selection_027.png)
* Set Default bot channel
    * ![Add bot default channel](./graphics/Selection_026.png)
* verify the authdata is there with the command: `zappa invoke scheduled_tasks.show_authed_teams`
    * you should see a json output with the newly created auth data!

## backup authdata (set with callback)
* run: `./env_setup/data_import_export.py export -e dev -d ./env_setup`
* move the file to ./env\_setup/authed-data.json, and edit out all tables other than `authed_data`

## enable form / menu interactive components
* enter base url for request component url `/form` i.e. `https://xxxxxxx.execute-api.us-east-2.amazonaws.com/dev/form`
* enter base url for options load url `/menu` i.e. `https://xxxxxxx.execute-api.us-east-2.amazonaws.com/dev/menu`
* ![Set Interactive Component URLs](./graphics/Selection_019.png)

## create "slash" command
* enter base url with extension `/cmd` i.e. `https://xxxxxxx.execute-api.us-east-2.amazonaws.com/dev/cmd`
* ![Set Slash Command URL's](./graphics/Selection_021.png)

-----------------------
# Disable Callback
edit `botconfig.py` and set `ENABLE_CALLBACK` to `False`
* update environment by issuing: `zappa update dev`


-----------------------
# Test bot operation with add command
* ![Test bot with Add command](./graphics/Selection_028.png)

-----------------------
# Example Configs
## environment config (dev.json.gpg)
```
{
    "dbport" : "3306",
    "slack_client_secret" : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "igwsub1" : "subnet-xxxxxxxa",
    "igwsub2" : "subnet-xxxxxxxb",
    "s3bucket" : "wctf-vpc-rds-vpc-xxxxxxxx",
    "profile_name" : "myprofile",
    "connection_type" : "mysql_rds",
    "slack_client_id" : "000000000000.000000000000",
    "sql_password" : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "sglambda" : "sg-xxxxxxxx",
    "log_level" : "DEBUG",
    "slack_verification_token" : "xxxxxxxxxxxxxxxxxxxxxxxx",
    "master_password" : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "sql_user" : "normal_user",
    "sgrdsinternal" : "sg-xxxxxxxa",
    "sgrdsexternal" : "sg-xxxxxxxb",
    "vpc" : "vpc-xxxxxxxx",
    "slack_signing_secret" : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "dbinstance" : "xxxxxxxxxxxxxxx",
    "base_name" : "wctf-vpc-rds",
    "exception_hook_url": "https://hooks.slack.com/services/TXXXXXXXX/BXXXXXXXX/xxxxxxxxxxxxxxxxxxxxxxxx",
    "endpoint_address" : "xxxxxxxxxxxxxxx.bbbbbbbbbbbb.us-east-2.rds.amazonaws.com",
    "privsub1" : "subnet-xxxxxxxa",
    "privsub2" : "subnet-xxxxxxxb",
    "region" : "us-east-2",
    "master_user" : "master_user",
    "ctftoken": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "events": [
        {
            "function": "scheduled_tasks.show_countdown",
            "expression": "cron(0 19 * * ? *)"
        }
    ]
}
```
## authdata restore config
example `./env_setup/authdata-dev.json`

```
{
    "db_wctf" : {
        "slack_authed_teams" : [
            {
                "team_id" : "TXXXXXXXX",
                "team_json" : {
                    "py/object" : "sqlalchemy.ext.mutable.MutableDict",
                    "py/state" : {
                        "team_id" : "TXXXXXXXX",
                        "ok" : true,
                        "scope" : "identify,bot,commands,incoming-webhook",
                        "access_token" : "xoxp-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                        "user_id" : "UXXXXXXXX",
                        "team_name" : "Super Awesome WCTF Team",
                        "bot" : {
                            "bot_user_id" : "UXXXXXXXX",
                            "bot_access_token" : "xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx"
                        },
                        "incoming_webhook" : {
                            "url" : "https://hooks.slack.com/services/TXXXXXXXX/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                            "channel_id" : "CXXXXXXXX",
                            "channel" : "#lambda_bot_exceptions",
                            "configuration_url" : "https://awesome-team-name.slack.com/services/BXXXXXXXX"
                        }
                    }
                }
            }
        ]
    }
}
```
