from datetime import datetime, timezone
import requests
from .constants import unreliable_websites
from langchain_community.document_loaders import WebBaseLoader
import tldextract
import typing as ty
import os


def check_time_difference(timestamp_utc):
    current_time = datetime.now(timezone.utc)
    timestamp_datetime = datetime.fromtimestamp(timestamp_utc, timezone.utc)
    time_difference = current_time - timestamp_datetime
    years_difference = time_difference.days / 365
    is_greater_than_one_year = years_difference > 1
    return is_greater_than_one_year


def get_website_metadata(url: str, api_key: str):
    tld_data = tldextract.extract(url)
    domain = tld_data.registered_domain
    if domain in unreliable_websites:
        return False
    if tld_data.suffix == "com":
        api_url = "https://api.api-ninjas.com/v1/whois?domain={}".format(domain)
        response = requests.get(api_url, headers={"X-Api-Key": api_key})
        if response.status_code == requests.codes.ok:
            json_response = response.json()
            creation_date_type = type(json_response["creation_date"])
            if creation_date_type == list:
                creation_date = json_response["creation_date"][0]
            else:
                creation_date = json_response["creation_date"]
            is_greater_than_one_year = check_time_difference(creation_date)
            if not is_greater_than_one_year:
                return False
            else:
                return True
        else:
            return False
    else:
        return True


def get_website_contents(urls: ty.List[str]):
    loader = WebBaseLoader(
        web_paths=(urls),
    )
    return loader.load()
