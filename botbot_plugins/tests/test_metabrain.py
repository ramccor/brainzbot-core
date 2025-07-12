# -*- coding: utf-8 -*-
import pytest
from botbot_plugins.tests.dummy import DummyApp
from botbot_plugins.plugins import metabrain



@pytest.fixture
def app():
    return DummyApp(test_plugin=metabrain.Plugin(), command_prefix="!")


def test_empty(app):
    responses = app.respond("!braindump")
    assert responses == ["I have no memory yet, use the recall command to make me remember stuff for you."]
    responses = app.respond("!forget the cake")
    assert responses == ["I'm sorry, I don't remember \"the cake\", are you sure I should know about it?"]


def test_remember(app):
    responses = app.respond("!remember the cake=is a lie")
    assert responses == ["I will remember \"the cake\" for you repl_user."]
    responses = app.respond(r"!recall the cake")
    assert responses == ["is a lie"]
    responses = app.respond("!braindump")
    assert responses == ["I remember \"the cake\"."]

    responses = app.respond("!remember ünîcödé=В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!")
    assert responses == ["I will remember \"ünîcödé\" for you repl_user."]
    responses = app.respond(r"!recall ünîcödé")
    assert responses == ["В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!"]
    responses = app.respond("!braindump")
    assert responses == ["I remember \"the cake\" and \"ünîcödé\"."]

    app.respond("!remember third=element")
    responses = app.respond("!braindump")
    assert responses == ["I remember \"the cake\", \"ünîcödé\" and \"third\"."]

    responses = app.respond("!forget the cake")
    assert responses == ["What was \"the cake\" all about?"]
    responses = app.respond("!forget ünîcödé")
    assert responses == ["What was \"ünîcödé\" all about?"]
    app.respond("!forget third")
    responses = app.respond("!braindump")
    assert responses == ["I have no memory yet, use the recall command to make me remember stuff for you."]


def test_whitespace(app):
    responses = app.respond("!remember a=b")
    assert responses == ["I will remember \"a\" for you repl_user."]

    responses = app.respond("!remember a =b")
    assert responses == ["I will remember \"a\" for you repl_user."]

    responses = app.respond("!remember a tree        =       two cakes")
    assert responses == ["I will remember \"a tree\" for you repl_user."]

    responses = app.respond("!recall a tree")
    assert responses == ["two cakes"]
