import requests
import config

redmine_url = config.REDMINE_URL[0:-1] if config.REDMINE_URL[-1] == "/" else config.REDMINE_URL


class NetworkUnauthorizedError(Exception):
    pass


def get_issues(id, api_key):
    method = "/issues/{}.json".format(id)

    req = requests.get(redmine_url + method, headers={"X-Redmine-API-Key": api_key})

    if req.status_code == 401:
        raise NetworkUnauthorizedError()

    return req.json()


def create_time_entries(api_key, issue_id, hours, comment):
    method = "/time_entries.json"
    timeEntrie = {"time_entry": {'issue_id': issue_id, 'hours': hours, 'comments': comment}}

    req = requests.post(redmine_url + method, json=timeEntrie, headers={"X-Redmine-API-Key": api_key})

    if req.status_code == 401:
        raise NetworkUnauthorizedError()
    elif req.status_code != 201:
        raise ConnectionError()

    return req.json()


def get_user_info(api_key):
    method = "/users/current.json"

    req = requests.get(redmine_url + method, headers={"X-Redmine-API-Key": api_key})

    if req.status_code == 401:
        raise NetworkUnauthorizedError()

    return req.json()


if __name__ == '__main__':

    saf = get_issues(24876, "ebf5ba42b3ba39611660f4b9456c952cfbd7273b")
    pass