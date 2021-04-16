#! /usr/bin/env python3
from src.privacy_analysis.system_analysis.system_privacy import SystemPrivacy
from src.privacy_analysis.system_analysis.helpers_analysis import get_file_contents
from src.dashboard.alerts.alert import Alert, AlertType, Severity


# Validate the router encryption type is not weak
class SystemPrivacyEncryption(SystemPrivacy):
    def __call__(self):
        weak_encryption_modes = ["none'", "wep", "owe'",
                                 "psk'", "psk+", "psk-",
                                 "wpa'", "wpa+", "wpa-"]
        data = get_file_contents("/etc/config/wireless")
        if data is None:
            return
        for mode in weak_encryption_modes:
            if ("encryption '" + mode) in data:
                alert_obj = Alert(None, f"Weak encryption is in use. Switch to WPA2 from {mode}.", AlertType.PRIVACY,
                                  Severity.ALERT)
                alert_obj.alert()
