import pytest
from botbot_plugins.plugins import bangmotivate
from botbot_plugins.tests.dummy import DummyApp


@pytest.fixture
def app():
    return DummyApp(test_plugin=bangmotivate.Plugin(), command_prefix="!")


def test_motivate(app):
    responses = app.respond("!m BotBot & that other guy")
    assert responses == ["You're doing good work, BotBot & that other guy!"]


def test_nomotivate(app):
    responses = app.respond("shouldn't !m === false?")
    assert len(responses) == 0
