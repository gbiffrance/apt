import os

# Local path for datasets storage
RESOURCES_PATH = "/usr/data/"

# Public URL to access the APT server (required)
APT_PUBLIC_URL = os.environ.get("APT_PUBLIC_URL", None)

# GBIF Registry URL (production or UAT)
GBIF_REGISTRY_URL = os.environ.get("GBIF_REGISTRY_URL", "https://api.gbif-uat.org")

# GBIF Publisher Key for this APT (required)
PUBLISHER_KEY = os.environ.get("PUBLISHER_KEY", None)

# GBIF Installation Key for this APT (required)
INSTALLATION_KEY = os.environ.get("INSTALLATION_KEY", None)

# GBIF Registry account (required)
GBIF_REGISTRY_LOGIN = os.environ.get("GBIF_REGISTRY_LOGIN", None)
GBIF_REGISTRY_PASSWORD = os.environ.get("GBIF_REGISTRY_PASSWORD", None)

# Default publication license and language
PUBLICATION_LICENSE = os.environ.get("PUBLICATION_LICENSE", "http://creativecommons.org/licenses/by/4.0/legalcode")
PUBLICATION_LANGUAGE = os.environ.get("PUBLICATION_LANGUAGE", "eng")

# Security Token to access restricted APT endpoints (required)
SECURITY_APY_KEY = os.environ.get("API_KEY", None)

# Authorized IP to access restricted APT endpoints (optional)
SECURITY_AUTHORIZED_IP = os.environ.get("AUTHORIZED_IP")

def has_required_parameters():
    if not APT_PUBLIC_URL:
        print("APT_PUBLIC_URL is required. APT is closing.")
        return False
    if not PUBLISHER_KEY:
        print("PUBLISHER_KEY is required. APT is closing.")
        return False
    if not INSTALLATION_KEY:
        print("INSTALLATION_KEY is required. APT is closing.")
        return False
    if not GBIF_REGISTRY_LOGIN:
        print("GBIF_REGISTRY_LOGIN is required. APT is closing.")
        return False
    if not GBIF_REGISTRY_PASSWORD:
        print("GBIF_REGISTRY_PASSWORD is required. APT is closing.")
        return False
    if not SECURITY_APY_KEY:
        print("SECURITY_APY_KEY is required. APT is closing.")
        return False
    return True

def display_banner():
    print("##############################################################################")
    print("###                                                                        ###")
    print("###                   APT: Automated Publishing Toolkit                    ###")
    print("###                                                                        ###")
    print("##############################################################################")
    print("###")
    print(f"###   APT URL: {APT_PUBLIC_URL}")
    print("###")
    print(f"###   Publisher Key: {PUBLISHER_KEY}")
    print(f"###   GBIF Registry: {GBIF_REGISTRY_URL}")
    print(f"###   GBIF Account: {GBIF_REGISTRY_LOGIN}")
    print("###")
    if SECURITY_APY_KEY:
        print("###   Some APT endpoints are secured by API Key (header X-API-Key)")
    if SECURITY_AUTHORIZED_IP:
        print(f"###   Some APT endpoints can only be called by {SECURITY_AUTHORIZED_IP} address")
    print("###")
    print("##############################################################################")
