#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import json
import time
from mock import patch, call
import requests
from botbot_plugins.base import DummyApp
from botbot_plugins.plugins import jira


class FakeProjectResponse(object):
    """Dummy response from JIRA"""
    status_code = 200
    text = json.dumps([{'key': 'TEST'}])


class FakeUserResponse(object):
    """Dummy response from JIRA"""
    def __init__(self, key, summary):
        self.status_code = 200
        self.text = json.dumps({'key': key, 'fields': {'summary': summary}})


def patched_get(*args, **kwargs):
    if args[0] == "https://tickets.test.org/rest/api/2/project":
        return FakeProjectResponse()
    elif args[0] == "https://tickets.test.org/rest/api/2/issue/TEST-123":
        return FakeUserResponse("TEST-123", "Testing JIRA plugin")
    elif args[0] == "https://tickets.test.org/rest/api/2/issue/TEST-234":
        return FakeUserResponse("TEST-234", "Something is being tested again")
    elif args[0] == "https://tickets.test.org/rest/api/2/issue/TEST-453":
        return FakeUserResponse("TEST-453", u"Test unicode: äñĳƺɷϠӃ۳ױ")
    else:
        return FakeUserResponse("TEST-000", "Default Test")


def clear_recent_issues(app):
    ukey = u'{0}:{1}'.format('jira', 'recent_issues'.strip())
    app.storage.delete(ukey)


@pytest.fixture
def app():
    dummy_app = DummyApp(test_plugin=jira.Plugin())
    dummy_app.set_config('jira', {'jira_url': 'https://tickets.test.org', 'bot_name': 'testbot', 'issue_cooldown': 2})

    return dummy_app


def test_jira(app):
    # patch requests.get so we don't need to make a real call to Jira

    # Test project retrival
    with patch.object(requests, 'get') as mock_get:
        mock_get.side_effect = patched_get
        responses = app.respond("@UPDATE:JIRA")
        mock_get.assert_called_with(
            'https://tickets.test.org/rest/api/2/project')
        assert responses == ["Successfully updated projects list"]

    # Test appropriate response
    with patch.object(requests, 'get') as mock_get:
        mock_get.side_effect = patched_get
        responses = app.respond("I just assigned TEST-123 to testuser")
        mock_get.assert_called_with(
            'https://tickets.test.org/rest/api/2/issue/TEST-123')
        assert responses == ["TEST-123: Testing JIRA plugin https://tickets.test.org/browse/TEST-123"]
        clear_recent_issues(app)

    # Test response when issue is mentioned as part of url
    with patch.object(requests, 'get') as mock_get:
        app.storage.delete('recent_issues')
        mock_get.side_effect = patched_get
        responses = app.respond("Check out https://tickets.test.org/browse/TEST-123")
        mock_get.assert_called_with(
            'https://tickets.test.org/rest/api/2/issue/TEST-123')
        assert responses == ["TEST-123: Testing JIRA plugin"]
        clear_recent_issues(app)

    # Test response to [off] messages
    with patch.object(requests, 'get') as mock_get:
        mock_get.side_effect = patched_get
        responses = app.respond("[off] I just assigned TEST-123 to testuser")
        mock_get.assert_called_with(
            'https://tickets.test.org/rest/api/2/issue/TEST-123')
        assert responses == ["[off] TEST-123: Testing JIRA plugin https://tickets.test.org/browse/TEST-123"]
        clear_recent_issues(app)

    # Test response to invalid tickets
    with patch.object(requests, 'get') as mock_get:
        mock_get.side_effect = patched_get
        responses = app.respond("[off] My password is ABC-123")
        assert responses == []
        clear_recent_issues(app)

def test_jira_multiple(app):
    # Test multiple issues in a single message
    with patch.object(requests, 'get') as mock_get:
        clear_recent_issues(app)
        mock_get.side_effect = patched_get
        responses = app.respond("I think TEST-123 and TEST-234 are related")
        expected_calls = [call('https://tickets.test.org/rest/api/2/issue/TEST-123'), call('https://tickets.test.org/rest/api/2/issue/TEST-234')]
        expected_response = ["TEST-123: Testing JIRA plugin https://tickets.test.org/browse/TEST-123", "TEST-234: Something is being tested again https://tickets.test.org/browse/TEST-234"]
        assert mock_get.mock_calls == expected_calls
        assert responses[0].split('\n') == expected_response
        clear_recent_issues(app)


def test_jira_cooldown(app):
    # Test issue cooldown function
    with patch.object(requests, 'get') as mock_get:
        mock_get.side_effect = patched_get
        assert app.respond("I just assigned TEST-123 to testuser") == ["TEST-123: Testing JIRA plugin https://tickets.test.org/browse/TEST-123"]
        assert app.respond("Okay, I will work on TEST-123") == []
        time.sleep(3)
        assert app.respond("TEST-123 is done") == ["TEST-123: Testing JIRA plugin https://tickets.test.org/browse/TEST-123"]
        clear_recent_issues(app)

def test_jira_unicode(app):
    # Test unicode compability
    with patch.object(requests, 'get') as mock_get:
        mock_get.side_effect = patched_get
        responses = app.respond(u"Does this wörk with uñicode? TEST-453")
        mock_get.assert_called_with(
            'https://tickets.test.org/rest/api/2/issue/TEST-453')
        assert responses == [u"TEST-453: Test unicode: äñĳƺɷϠӃ۳ױ https://tickets.test.org/browse/TEST-453"]
        clear_recent_issues(app)
