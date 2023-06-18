import datetime
import os
import logging
import requests
import getpass
import click
import json
from typing import NamedTuple, Dict, Set, Any, List, Tuple

log = logging.getLogger(__name__)
CERT_PATH = os.path.join(os.path.dirname(__file__), "root.crt")


class Server:

    def __init__(self, url: str, session: requests.Session) -> None:
        self._session = session
        self._url = url
        self._dry_run = False

    @classmethod
    def connect(cls, url: str, user: str, password: str) -> 'Server':
        print("Connecting to: {}".format(url))

        session = requests.Session()
        session.verify = CERT_PATH

        # Do we need to authenticate?
        auth = session.get("{}/status".format(url))
        if auth.status_code == 401:
            session.auth = (user or getpass.getuser(), password or getpass.unix_getpass())
            auth = session.get("{}/status".format(url))

        if auth.status_code == 401:
            raise click.ClickException("Unauthorised!")

        assert auth.ok, "Auth status = {}".format(auth.status_code)
        return Server(session=session, url=url)

    @property
    def all_tiddlers(self) -> Tuple[Dict[str, str]]:

        response = self._session.get(
            "{}/recipes/default/tiddlers.json".format(self._url),
        )
        assert response.ok
        assert response.status_code == 200

        # We are going to use this to work out what to do
        return tuple(json.loads(response.text))

    def delete_tiddler(self, title: str) -> None:
        if self._dry_run:
            print(f"Dry run deleting tiddler: {title}")
            return
        print(f"Deleting tiddler: {title}")
        headers = {
            "x-requested-with": "TiddlyWiki"
        }
        response = self._session.delete(
            "{}/bags/default/tiddlers/{}".format(self._url, title),
            headers=headers,
        )
        assert response.ok, "Got response: {}".format(response.status_code)

    def update_tiddler(self, tiddler: Dict[str, str]) -> None:
        title = tiddler["title"]
        if self._dry_run:
            print("Dry run updating tiddler: {}".format(title))
            return
            
        print("Updating tiddler: {}".format(title))
        headers = {
            "x-requested-with": "TiddlyWiki"
        }
        response = self._session.put(
            "{}/recipes/default/tiddlers/{}".format(self._url, title),
            data=json.dumps(tiddler),
            headers=headers,
        )
        assert response.ok

    def get_tiddler(self, title: str) -> Dict[str, Any]:
        response = self._session.get(
            "{}/recipes/default/tiddlers/{}".format(self._url, title)
        )
        if response.status_code == 404:
            return dict()
        assert response.ok, "Got response: {}".format(response.status_code)
        return json.loads(response.text)

