"""Test du `User-Agent` du client de l'API 42 (T4.e), sans réseau réel.

Sans cet en-tête, le pare-feu du service refuse la requête (HTTP 403, erreur 1010).
"""

import unittest

from tests.system_sync.sources.fake_server import FakeClock, FakeServer, json_reply, load
from tests.system_sync.sources.test_api42 import (
    CLIENT_ID,
    CLIENT_SECRET,
    CODE,
    GUARD,
    ME_PATH,
    TOKEN_PATH,
    Guarded,
    api42,
)

EXPECTED = "progression-system-sync/1.0"


def setUpModule():
    """Garde le réseau pendant tout le module."""
    GUARD.start()


def tearDownModule():
    """Lève la garde."""
    GUARD.stop()


class UserAgentTest(Guarded):
    def test_token_and_me_requests_carry_generic_user_agent(self):
        clock = FakeClock()
        server = FakeServer(clock=clock.now)
        self.addCleanup(server.close)
        server.route(TOKEN_PATH, json_reply(load("token.json")))
        server.route(ME_PATH, json_reply(load("me_valid.json")))
        client = api42.Api42Client(
            server.url,
            timeout=1.0,
            limiter=api42.RateLimiter(clock=clock.now, sleep=clock.sleep),
            sleep=clock.sleep,
        )
        redirect = "http://127.0.0.1:5615/callback"
        self.assertIsNone(client.exchange_code(CLIENT_ID, CLIENT_SECRET, CODE, redirect))
        self.assertIsNone(client.fetch_me().error)
        sent = server.requests(TOKEN_PATH) + server.requests(ME_PATH)
        self.assertEqual(len(sent), 2)
        for request in sent:
            self.assertEqual(request.headers.get("user-agent"), EXPECTED, request.path)


if __name__ == "__main__":
    unittest.main()
