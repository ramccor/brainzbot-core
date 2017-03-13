# -*- coding: utf-8 -*-
import pytest
from botbot_plugins.base import DummyApp
from botbot_plugins.plugins import metabrain



@pytest.fixture
def app():
    return DummyApp(test_plugin=metabrain.Plugin())


def test_remember(app):
    responses = app.respond("!remember the cake=is a lie")
    assert responses == ["I will remember \"the cake\" for you repl_user."]
    responses = app.respond(ur"!recall the cake")
    assert responses == ["is a lie"]
    responses = app.respond("!forget the cake")
    assert responses == ["What was \"the cake\" all about?"]
