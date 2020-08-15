import argparse
import json
import logging
import os
import sys

from lib.parameter_store import parameter_store
from lib import helpers
from lib import log as log_module
from lib.log import log


class Config:
    config_fn = helpers.fname_to_path("config.json")

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.add_default_arguments()

    def add_default_arguments(self):
        self.parser.add_argument("--log-level",
                                 help="Set log level to debug, info, warning, error, or critical")
        self.parser.add_argument("--single-ip", action="store_true",
                                 help="Register BUNQ device-server with a single IP address " +
                                 "instead of a wildcard for all IPs.")
        self.parser.add_argument("-v", "--verbose", action="store_true",
                                 help="Shortcut for '--log-level debug'")

    def load(self):

        # Parse command line settings
        args = self.parser.parse_args()
        if args.verbose:
            log_module.set_log_level("-v argument", "debug")
        elif args.log_level:
            log_module.set_log_level("--log-level argument", args.log_level)

        if os.environ.get("LOG_LEVEL"):
            log_module.set_log_level("environment", os.environ["LOG_LEVEL"])

        if os.environ.get("SSM_PARAM"):
            log.info('Reading config from SSM Path: {0}'.format(
                os.environ["SSM_PARAM"]))
            self.read_ssm_config(os.environ["SSM_PARAM"])
        else:
            self.read_json_config()

        # Override config.json with command line settings
        for k, v in vars(args).items():
            self.config[k] = v

        if config["log_level"]:
            log_module.set_log_level("file config.json", config["log_level"])

    def __getitem__(self, name):
        if not hasattr(self, "config"):
            raise Exception("Load config before using it")
        if not name in self.config:
            raise Exception("Unknown configuration \"{}\"".format(name))
        return self.config[name]

    def get(self, name, default=None):
        if not hasattr(self, "config"):
            raise Exception("Load config before using it")
        return self.config.get(name, default)

    def read_ssm_config(self, ssmpath):
        try:
            resp = parameter_store.fetch_parameter(ssmpath)
            conf = json.loads(resp)
            log.debug('Fetched configuration')
            self.config.update(conf)
        except Exception as e:
            log.critical("Error loading configuration from SSM Parameter: {}: {}"
                         .format(ssmpath, e))
            sys.exit(1)

    def read_json_config(self):
        if not os.path.exists(self.config_fn):
            example_config = {
                "api_token": "enter bunq api key here",
                "personal_access_token": "enter ynab token here",
                "accounts": [{
                    "bunq_account_name": "enter bunq account ere",
                    "ynab_budget_name": "enter ynab budget here",
                    "ynab_account_name": "enter ynab account here"
                }]
            }
            with open(self.config_fn, "w") as f:
                json.dump(example_config, f, indent=4)
            log.critical("Missing configuration.  Example created, please " +
                         "edit " + self.config_fn)
            sys.exit(1)

        try:
            with open(self.config_fn) as f:
                conf = json.load(f)
                self.config.update(conf)
        except Exception as e:
            log.critical("Error loading configuration {}: {}"
                         .format(self.config_fn, e))
            sys.exit(1)

        if (self.config["api_token"] == "enter bunq api key here" or
                self.config["personal_access_token"] == "enter ynab token here"):
            log.critical("Configuration incomplete, please edit " +
                         self.config_fn)
            sys.exit(1)


config = Config()
