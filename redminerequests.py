import requests
import config
import logging

redmine_url = config.REDMINE_URL[0:-1] if config.REDMINE_URL[-1] == "/" else config.REDMINE_URL


class NetworkUnauthorizedError(Exception):
    pass


class CannotCreateTimeEntries(Exception):
    pass


def get_issues(id, api_key):
    method = "/issues/{}.json".format(id)

    req = requests.get(redmine_url + method, headers={"X-Redmine-API-Key": api_key})

    if req.status_code == 401:
        raise NetworkUnauthorizedError()

    return req.json()


def create_time_entries(api_key, issue_id, hours, comment):
    method = "/time_entries.json"
    time_entrie = {"time_entry": {'issue_id': issue_id, 'hours': hours, 'comments': comment}}

    try:
        req = requests.post(redmine_url + method, json=time_entrie, headers={"X-Redmine-API-Key": api_key})
    except Exception as e:
        logging.exception("Cannot create redmine time entrie")
        raise CannotCreateTimeEntries

    if req.status_code == 401:
        raise NetworkUnauthorizedError()
    elif req.status_code != 201:
        raise CannotCreateTimeEntries()

    return req.json()


def get_user_info(api_key):
    method = "/users/current.json"

    req = requests.get(redmine_url + method, headers={"X-Redmine-API-Key": api_key})

    if req.status_code == 401:
        raise NetworkUnauthorizedError()

    return req.json()
