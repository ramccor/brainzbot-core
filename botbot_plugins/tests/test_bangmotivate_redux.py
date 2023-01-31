import pytest
from botbot_plugins.base import DummyApp
from botbot_plugins.plugins import bangmotivate_redux


@pytest.fixture
def app():
    return DummyApp(test_plugin=bangmotivate_redux.Plugin(), command_prefix="!")


def test_motivate(app):
    responses = app.respond("!m BotBot & that other guy")
    assert responses == ["You're doing good work, BotBot & that other guy!"]


def test_nomotivate(app):
    responses = app.respond("shouldn't !m === false?")
    assert len(responses) == 0
