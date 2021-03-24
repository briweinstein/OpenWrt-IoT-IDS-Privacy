import json
import os
import logging
from typing import List
from dataclasses import dataclass

@dataclass(frozen=True)
class ConfigEmail:
    smtp_server: str
    email_account: str
    email_password: str
    recipient_emails: List[str]


class Config:
    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            filemode='a',
                            format='%(asctime)s %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            filename='/etc/tinyHIPPO/tinyHIPPO_error.log')
        config_path = os.getenv("IOT_IDS_CONFIGPATH", "config.json")
        with open(config_path) as f:
            config_json = json.load(f)
        self.email = ConfigEmail(**config_json["email"])
        self.mac_addrs = config_json["mac_addrs"]
        self.alert_collection_path = config_json["alert_collection_path"]
        self.virustotal_api_key = config_json["virustotal_api_key"]
        self.log_event = logging.getLogger()
            
