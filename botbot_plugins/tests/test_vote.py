# -*- coding: utf-8 -*-
import pytest
from botbot_plugins.base import DummyApp
from botbot_plugins.plugins import vote


@pytest.fixture
def app():
    return DummyApp(test_plugin=vote.Plugin(), command_prefix="!")

def test_no_concurrent_voting(app):
    assert app.respond("!startvote") == ["Voting has started."]
    assert app.respond("!startvote") == [u"repl_user: There’s already a vote going on. Use the “endvote” command to end it before starting a new one."]
    app.respond("!endvote")

def test_no_vote_running(app):
    assert app.respond("+1") == []
    assert app.respond("+something") == []
    assert app.respond("!vote +something") == [u"No vote has been started. Use the “startvote” command to do so."]
    assert app.respond("!countvotes") == [u"No vote has been started. Use the “startvote” command to do so."]
    assert app.respond("!abstain") == [u"No vote has been started. Use the “startvote” command to do so."]
    assert app.respond("!cancelvotes") == [u"No vote has been started. Use the “startvote” command to do so."]
    assert app.respond("!endvote") == [u"No vote has been started. Use the “startvote” command to do so."]

def test_boolean_voting(app):
    assert app.respond("!startvote") == ["Voting has started."]
    app.respond("+1")
    assert app.respond("!countvotes") == ["[+1: repl_user] [-0: ] [\\0: ]"]
    app.respond("\\1")
    assert app.respond("!countvotes") == ["[+0: ] [-0: ] [\\1: repl_user]"]
    app.respond("-1")
    app.respond("\\o")
    assert app.respond("!countvotes") == ["[+0: ] [-1: repl_user] [\\0: ]"]

    # Double-voting
    app.respond("+1")
    app.respond("+1")
    assert app.respond("!countvotes") == ["[+1: repl_user] [-0: ] [\\0: ]"]

    # Explicit voting
    app.respond("!vote -1")
    assert app.respond("!countvotes") == ["[+0: ] [-1: repl_user] [\\0: ]"]
    app.respond("!vote \\1")
    assert app.respond("!countvotes") == ["[+0: ] [-0: ] [\\1: repl_user]"]
    app.respond("!vote +1")
    assert app.respond("!vote \o") == ["The only valid way to abstain is using \\1."]
    assert app.respond("!countvotes") == ["[+1: repl_user] [-0: ] [\\0: ]"]

    # Additional words after
    app.respond("-1 foo bar")
    assert app.respond("!countvotes") == ["[+0: ] [-1: repl_user] [\\0: ]"]
    app.respond("+1 coolio")
    assert app.respond("!countvotes") == ["[+1: repl_user] [-0: ] [\\0: ]"]
    app.respond("!vote -1 foo bar")
    assert app.respond("!countvotes") == ["[+0: ] [-1: repl_user] [\\0: ]"]
    app.respond("!vote +1 coolio")
    assert app.respond("!countvotes") == ["[+1: repl_user] [-0: ] [\\0: ]"]

    # Multiple users
    app.respond("-1", User="jesus")
    assert app.respond("!countvotes") == ["[+1: repl_user] [-1: jesus] [\\0: ]"]
    app.respond("-1")
    assert app.respond("!countvotes") == ["[+0: ] [-2: jesus, repl_user] [\\0: ]"]

    # Invalid option
    assert app.respond("+invalid") == []
    assert app.respond("!vote +invalid") == [u"“invalid” is not a valid option."]

    assert app.respond("!endvote") == ["Voting has ended."]

    # With name
    assert app.respond("!startvote is jesus real?") == [u"Voting has started for proposal “is jesus real?”."]
    assert app.respond("!endvote") == [u"Voting has ended for proposal “is jesus real?”."]

def test_non_boolean_voting(app):
    assert app.respond("!startvote [port, firewall, app]") == ["Voting has started."]
    app.respond("+port")
    assert app.respond("!countvotes") == ["[app(+0, -0): ] [firewall(+0, -0): ] [port(+1, -0): repl_user] [\\0: ]"]
    app.respond("-firewall")
    assert app.respond("!countvotes") == ["[app(+0, -0): ] [firewall(+0, -1): -repl_user] [port(+1, -0): repl_user] [\\0: ]"]
    app.respond("\\1")
    assert app.respond("!countvotes") == ["[app(+0, -0): ] [firewall(+0, -0): ] [port(+0, -0): ] [\\1: repl_user]"]

    # Double-voting
    app.respond("+app")
    app.respond("+app")
    assert app.respond("!countvotes") == ["[app(+1, -0): repl_user] [firewall(+0, -0): ] [port(+0, -0): ] [\\0: ]"]

    # Explicit voting
    app.respond("!vote -app")
    assert app.respond("!countvotes") == ["[app(+0, -1): -repl_user] [firewall(+0, -0): ] [port(+0, -0): ] [\\0: ]"]
    app.respond("!vote app")
    assert app.respond("!countvotes") == ["[app(+1, -0): repl_user] [firewall(+0, -0): ] [port(+0, -0): ] [\\0: ]"]

    # Closest match
    app.respond("-app is not cool")
    assert app.respond("!countvotes") == ["[app(+0, -1): -repl_user] [firewall(+0, -0): ] [port(+0, -0): ] [\\0: ]"]
    app.respond("+port is a good one")
    assert app.respond("!countvotes") == ["[app(+0, -1): -repl_user] [firewall(+0, -0): ] [port(+1, -0): repl_user] [\\0: ]"]
    app.respond("+app is kinda cool")
    assert app.respond("!countvotes") == ["[app(+1, -0): repl_user] [firewall(+0, -0): ] [port(+1, -0): repl_user] [\\0: ]"]

    # Multiple users
    app.respond("-app", User="jesus")
    assert app.respond("!countvotes") == ["[app(+1, -1): repl_user; -jesus] [firewall(+0, -0): ] [port(+1, -0): repl_user] [\\0: ]"]
    app.respond("+port", User="eladio")
    assert app.respond("!countvotes") == ["[app(+1, -1): repl_user; -jesus] [firewall(+0, -0): ] [port(+2, -0): repl_user, eladio] [\\0: ]"]
    app.respond("+app", User="eladio")
    assert app.respond("!countvotes") == ["[app(+2, -1): repl_user, eladio; -jesus] [firewall(+0, -0): ] [port(+2, -0): repl_user, eladio] [\\0: ]"]
    app.respond("\\1", User="jesus")
    assert app.respond("!countvotes") == ["[app(+2, -0): repl_user, eladio] [firewall(+0, -0): ] [port(+2, -0): repl_user, eladio] [\\1: jesus]"]

    # Invalid option
    assert app.respond("+invalid") == []
    assert app.respond("!vote +invalid") == [u"“invalid” is not a valid option."]

    assert app.respond("!endvote") == ["Voting has ended."]

    # With name
    assert app.respond("!startvote is jesus real? [port, firewall, app]") == [u"Voting has started for proposal “is jesus real?”."]
    assert app.respond("!endvote") == [u"Voting has ended for proposal “is jesus real?”."]

    # Closest match needs to be greedy
    app.respond("!startvote [hello, hello world]")
    app.respond("+hello")
    assert app.respond("!countvotes") == ["[hello(+1, -0): repl_user] [hello world(+0, -0): ] [\\0: ]"]
    app.respond("-hello world")
    assert app.respond("!countvotes") == ["[hello(+1, -0): repl_user] [hello world(+0, -1): -repl_user] [\\0: ]"]
    app.respond("+hello\tworld")
    assert app.respond("!countvotes") == ["[hello(+1, -0): repl_user] [hello world(+1, -0): repl_user] [\\0: ]"]
    app.respond("!endvote")

    # Duplicate options
    app.respond("!startvote [hello, hello, world, world]")
    app.respond("+hello")
    app.respond("-world")
    assert app.respond("!countvotes") == ["[hello(+1, -0): repl_user] [world(+0, -1): -repl_user] [\\0: ]"]
    app.respond("!endvote")

    # With explicitly empty options
    assert app.respond("!startvote []") == ["Voting has started."]
    app.respond("+1")
    assert app.respond("!countvotes") == ["[+1: repl_user] [-0: ] [\\0: ]"]
    app.respond("!endvote")
    assert app.respond("!startvote [      ,     ]") == ["Voting has started."]
    app.respond("+1")
    assert app.respond("!countvotes") == ["[+1: repl_user] [-0: ] [\\0: ]"]
    app.respond("!endvote")
    assert app.respond("!startvote [,]") == ["Voting has started."]
    app.respond("+1")
    assert app.respond("!countvotes") == ["[+1: repl_user] [-0: ] [\\0: ]"]
    app.respond("!endvote")

def test_cancelvotes(app):
    assert app.respond("!startvote") == ["Voting has started."]
    app.respond("+1")
    app.respond("+1", User="jesus")
    assert app.respond("!countvotes") == ["[+2: repl_user, jesus] [-0: ] [\\0: ]"]
    app.respond("!cancelvotes")
    assert app.respond("!countvotes") == ["[+1: jesus] [-0: ] [\\0: ]"]
    app.respond("!endvote")

    assert app.respond("!startvote [port, firewall, app]")
    app.respond("+port")
    app.respond("-firewall")
    assert app.respond("!countvotes") == ["[app(+0, -0): ] [firewall(+0, -1): -repl_user] [port(+1, -0): repl_user] [\\0: ]"]
    app.respond("!endvote")

def test_explicit_abstain(app):
    assert app.respond("!startvote") == ["Voting has started."]
    app.respond("!abstain")
    assert app.respond("!countvotes") == ["[+0: ] [-0: ] [\\1: repl_user]"]
    app.respond("!endvote")

def test_endvote_prints_countvote(app):
    assert app.respond("!startvote") == ["Voting has started."]
    app.respond("+1")
    assert app.respond("!endvote")[0].split('\n') == ["Voting has ended.", "[+1: repl_user] [-0: ] [\\0: ]"]

    assert app.respond("!startvote") == ["Voting has started."]
    app.respond("+1")
    assert app.respond("!countvotes") == ["[+1: repl_user] [-0: ] [\\0: ]"]
    app.respond("+1")
    assert app.respond("!endvote") == ["Voting has ended."]

    assert app.respond("!startvote") == ["Voting has started."]
    app.respond("+1")
    assert app.respond("!countvotes") == ["[+1: repl_user] [-0: ] [\\0: ]"]
    app.respond("\\1")
    assert app.respond("!endvote")[0].split('\n') == ["Voting has ended.", "[+0: ] [-0: ] [\\1: repl_user]"]

def test_cancelvote_when_novotes(app):
    assert app.respond("!startvote") == ["Voting has started."]
    assert app.respond("!cancelvotes") == []
    app.respond("!endvote")

def test_unicode(app):
    assert app.respond(u"!startvote Должен ли Владимир Путин стать следующим президентом России? [да, нет, Может быть]") == \
        [u"Voting has started for proposal “Должен ли Владимир Путин стать следующим президентом России?”."]
    app.respond(u"+Может быть")
    assert app.respond("!countvotes") == [u"[Может быть(+1, -0): repl_user] [да(+0, -0): ] [нет(+0, -0): ] [\\0: ]"]
    app.respond(u"-нет")
    assert app.respond("!countvotes") == [u"[Может быть(+1, -0): repl_user] [да(+0, -0): ] [нет(+0, -1): -repl_user] [\\0: ]"]
    app.respond(u"+да", User="Российский патриот")
    assert app.respond("!countvotes") == [u"[Может быть(+1, -0): repl_user] [да(+1, -0): Российский патриот] [нет(+0, -1): -repl_user] [\\0: ]"]
    assert app.respond("!endvote") == [u"Voting has ended for proposal “Должен ли Владимир Путин стать следующим президентом России?”."]

def test_emoji_voting(app):
    app.respond("!startvote")
    app.respond(u"👍", User="thumbs up")
    assert app.respond("!countvotes") == ["[+1: thumbs up] [-0: ] [\\0: ]"]
    app.respond(u"👍🏻", User="light thumbs up")
    assert app.respond("!countvotes") == ["[+2: thumbs up, light thumbs up] [-0: ] [\\0: ]"]
    app.respond(u"👍🏼", User="medium-light thumbs up")
    assert app.respond("!countvotes") == ["[+3: thumbs up, light thumbs up, medium-light thumbs up] [-0: ] [\\0: ]"]
    app.respond(u"👍🏽", User="medium thumbs up")
    assert app.respond("!countvotes") == ["[+4: thumbs up, light thumbs up, medium-light thumbs up, medium thumbs up] [-0: ] [\\0: ]"]
    app.respond(u"👍🏾", User="medium-dark thumbs up")
    assert app.respond("!countvotes") == ["[+5: thumbs up, light thumbs up, medium-light thumbs up, medium thumbs up, medium-dark thumbs up] [-0: ] [\\0: ]"]
    app.respond(u"👍🏿", User="dark thumbs up")
    assert app.respond("!countvotes") == ["[+6: thumbs up, light thumbs up, medium-light thumbs up, medium thumbs up, medium-dark thumbs up, dark thumbs up] [-0: ] [\\0: ]"]
    app.respond(u"😍", User="smiling heart face")
    assert app.respond("!countvotes") == ["[+7: thumbs up, light thumbs up, medium-light thumbs up, medium thumbs up, medium-dark thumbs up, dark thumbs up, smiling heart face] [-0: ] [\\0: ]"]
    app.respond(u"😻", User="smiling cat heart face")
    assert app.respond("!countvotes") == ["[+8: thumbs up, light thumbs up, medium-light thumbs up, medium thumbs up, medium-dark thumbs up, dark thumbs up, smiling heart face, smiling cat heart face] [-0: ] [\\0: ]"]
    app.respond("!endvote")

    app.respond("!startvote")
    app.respond(u"👎", User="thumbs down")
    assert app.respond("!countvotes") == ["[+0: ] [-1: thumbs down] [\\0: ]"]
    app.respond(u"👎🏻", User="light thumbs down")
    assert app.respond("!countvotes") == ["[+0: ] [-2: thumbs down, light thumbs down] [\\0: ]"]
    app.respond(u"👎🏼", User="medium-light thumbs down")
    assert app.respond("!countvotes") == ["[+0: ] [-3: thumbs down, light thumbs down, medium-light thumbs down] [\\0: ]"]
    app.respond(u"👎🏽", User="medium thumbs down")
    assert app.respond("!countvotes") == ["[+0: ] [-4: thumbs down, light thumbs down, medium-light thumbs down, medium thumbs down] [\\0: ]"]
    app.respond(u"👎🏾", User="medium-dark thumbs down")
    assert app.respond("!countvotes") == ["[+0: ] [-5: thumbs down, light thumbs down, medium-light thumbs down, medium thumbs down, medium-dark thumbs down] [\\0: ]"]
    app.respond(u"👎🏿", User="dark thumbs down")
    assert app.respond("!countvotes") == ["[+0: ] [-6: thumbs down, light thumbs down, medium-light thumbs down, medium thumbs down, medium-dark thumbs down, dark thumbs down] [\\0: ]"]
    app.respond(u"–1", User="en dash")
    assert app.respond("!countvotes") == ["[+0: ] [-7: thumbs down, light thumbs down, medium-light thumbs down, medium thumbs down, medium-dark thumbs down, dark thumbs down, en dash] [\\0: ]"]
    app.respond(u"—1", User="em dash")
    assert app.respond("!countvotes") == ["[+0: ] [-8: thumbs down, light thumbs down, medium-light thumbs down, medium thumbs down, medium-dark thumbs down, dark thumbs down, en dash, em dash] [\\0: ]"]
    app.respond(u"―1", User="horizontal bar")
    assert app.respond("!countvotes") == ["[+0: ] [-9: thumbs down, light thumbs down, medium-light thumbs down, medium thumbs down, medium-dark thumbs down, dark thumbs down, en dash, em dash, horizontal bar] [\\0: ]"]
    app.respond("!endvote")
