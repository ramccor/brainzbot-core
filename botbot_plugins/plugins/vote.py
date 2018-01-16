# -*- coding: utf-8 -*-

import json
import re
from functools import wraps
from collections import namedtuple, OrderedDict

from .. import config
from ..base import BasePlugin
from ..decorators import (listens_to_all, listens_to_command,
                          listens_to_regex_command)

DEFAULT_VOTE_OPTION = "__vote__"
ABSTAIN_OPTION = "__abstain__"

ERROR_MESSAGES = {
    "no_vote_started": u"No vote has been started. Use the “startvote” command to do so.",
    "voting_already_running": u"{author}: There’s already a vote going on. Use the “endvote” command to end it before starting a new one.",
    "invalid_option": u"“{option}” is not a valid option.",
    "invalid_abstain": u"The only valid way to abstain is using \\{shortform}."
}
INFO_MESSAGES = {
    "voting_started": u"Voting has started.",
    "voting_started_name": u"Voting has started for proposal “{name}”.",
    "voting_ended": u"Voting has ended.",
    "voting_ended_name": u"Voting has ended for proposal “{name}”."
}

def get_default_vote_template(for_, against, username_sep):
    return (u"[+{number_for}: {for_users}] [-{number_against}: {against_users}]"
            .format(
                number_for=len(for_),
                number_against=len(against),
                for_users=username_sep.join(for_),
                against_users=username_sep.join(against)
            ))

def get_abstain_template(abstainers, username_sep):
    return (u"[\\{num}: {users}]"
            .format(
                num=len(abstainers),
                users=username_sep.join(abstainers)
            ))

def get_section_template(name, for_, against, username_sep):
    template = (u"[{}(+{}, -{}): "
                .format(name, len(for_), len(against)))

    if for_:
        template += username_sep.join(for_)
    if for_ and against:
        template += u"; "
    if against:
        template += username_sep.join(
            u"-" + username for username in against)
    template += u"]"
    return template


COUNTVOTE_TEMPLATES = {
    "default_vote_template": get_default_vote_template,
    "abstain_template": get_abstain_template,
    "section_template": get_section_template
}

FOR_NAME = "for"
AGAINST_NAME = "against"
ABSTAIN_NAME = "abstain"
OPPOSING_VOTE = {
    FOR_NAME: AGAINST_NAME,
    AGAINST_NAME: FOR_NAME
}
# NOTE: This ordering is not meant to represent any kind of racial distinctions
# whatsoever. It's the order and words used by the Unicode Consortium in their
# technical reports. https://www.unicode.org/reports/tr51/#Diversity
VOTE_SHORTCUT_TO_NAME = OrderedDict([
    (u"+", FOR_NAME),
    (u"👍🏻", FOR_NAME),  # Thumbs up (light skin tone)
    (u"👍🏼", FOR_NAME),  # Thumbs up (medium-light skin tone)
    (u"👍🏽", FOR_NAME),  # Thumbs up (medium skin tone)
    (u"👍🏾", FOR_NAME),  # Thumbs up (medium-dark skin tone)
    (u"👍🏿", FOR_NAME),  # Thumbs up (dark skin tone)
    (u"👍", FOR_NAME),  # Regular thumbs up
    (u"😍", FOR_NAME),  # Smiling face with heart eyes
    (u"😻", FOR_NAME),  # Smiling cat face with heart eyes
    (u"-", AGAINST_NAME),
    (u"–", AGAINST_NAME),  # En dash
    (u"—", AGAINST_NAME),  # Em dash
    (u"―", AGAINST_NAME),  # Horizontal bar
    (u"👎🏻", AGAINST_NAME),  # Thumbs down (light skin tone)
    (u"👎🏼", AGAINST_NAME),  # Thumbs down (medium-light skin tone)
    (u"👎🏽", AGAINST_NAME),  # Thumbs down (medium skin tone)
    (u"👎🏾", AGAINST_NAME),  # Thumbs down (medium-dark skin tone)
    (u"👎🏿", AGAINST_NAME),  # Thumbs down (dark skin tone)
    (u"👎", AGAINST_NAME),  # Regular thumbs down
    (u"", FOR_NAME)
])

Vote = namedtuple('Vote', ['voter', 'section', 'vote'])

class Config(config.BaseConfig):

    options_separator = config.Field(help_text="Separator to use when starting a vote with custom options", default=",")
    username_separator = config.Field(help_text="Separator between usernames when printing out votes", default=",")
    boolean_shortform = config.Field(help_text=u"The short option that voters can use in boolean votes", default="1")

class Plugin(BasePlugin):
    """
    A basic proposal voting plugin.

    To start a vote, use the startvote command:

        {{ command_prefix }}startvote optional_name

    By default, this makes a simple, boolean vote,
    where voters can either vote for, against, or abstain.

    You can pass in options:

        {{ command_prefix }}startvote optional_name [option1, option2, option3, ...]

    Keep in mind that only one vote can be run at a time.

    There are two main ways to vote:

    1) Explicitly, using the “vote” command:

        {{ command_prefix }}vote +1

    If you pass in just an option name here, it'll be taken to mean you’re for it.

    2) Implicitly:

        +1
        -1
        +option
        -option

    Here, the symbol in front is required.

    You can always abstain from any vote using the “abstain” command, or voting with “\1”.
    If you want to delete your votes altogether, use the “cancelvotes” command.

    To print a representation of the number of votes currently made for each option,
    use the “countvotes”.

    Finally, to end a vote, use the “endvote” command.
    """

    config_class = Config

    @listens_to_regex_command("startvote",
                              ur"(?P<name>[^\[\]]+?)?\s*(\[(?P<options>.*)\])?\s*$")
    def startvote(self, line, name, options):
        options_sep = self.config["options_separator"]
        if self.retrieve("votes"):
            return (ERROR_MESSAGES["voting_already_running"].
                    format(author=line.user))

        default_options = [DEFAULT_VOTE_OPTION]
        options =\
            filter(bool, [option_name.strip() for option_name
                          in (options.split(options_sep) if options else [])])
        options = options or default_options
        # Abstaining should always be an option
        options.append(ABSTAIN_OPTION)
        options = list(set(options))

        # NOTE: this will create a for and against in __abstain__,
        # but for simplicity's sake we won't try and prevent this.
        # All abstainers will be added to __abstain__.for.
        initial_votes = {
            option_name: {FOR_NAME: [], AGAINST_NAME: []}
            for option_name in options
        }

        self.store("name", json.dumps(name))
        self.store("options", json.dumps(options))
        self.store("votes", json.dumps(initial_votes))
        self.store("changes_since_countvote", json.dumps(False))

        return (INFO_MESSAGES["voting_started_name"].format(name=name)
                if name else INFO_MESSAGES["voting_started"])

    def _depends_on_votestarted(throw_error=True):
        def decorator(func):
            @wraps(func)
            def wrap(*args, **kwargs):
                slf = args[0]
                if slf.retrieve("votes"):
                    return func(*args, **kwargs)
                elif throw_error:
                    return ERROR_MESSAGES["no_vote_started"]
                return ""
            return wrap
        return decorator

    @listens_to_command("endvote")
    @_depends_on_votestarted()
    def endvote(self, line, args):
        name = json.loads(self.retrieve("name"))
        changes_since_countvote = json.loads(
            self.retrieve("changes_since_countvote"))
        reply = (INFO_MESSAGES["voting_ended_name"].format(name=name)
                 if name else INFO_MESSAGES["voting_ended"])
        if changes_since_countvote:
            reply += "\n" + self._print_votes()

        self.delete("name")
        self.delete("options")
        self.delete("votes")
        self.delete("changes_since_countvote")

        return reply

    @listens_to_command("countvotes")
    @_depends_on_votestarted()
    def countvotes(self, line, args):
        self.store("changes_since_countvote", json.dumps(False))
        return self._print_votes()

    escaped_voting_shortcut_pattern = (
        u"|".join(re.escape(str_) for str_ in VOTE_SHORTCUT_TO_NAME.keys()))

    vote_regex_template = (
        u"^((?P<vote>(" +
        escaped_voting_shortcut_pattern +
        u"\\\\){vote_modifier})(?P<option>.*))$")

    @listens_to_regex_command("vote", (vote_regex_template
                                       .format(vote_modifier="?")))
    @_depends_on_votestarted()
    def vote(self, line, vote, option):
        try:
            changes_made = self._add_vote(self._parse_vote(line.user, (vote, option)))
            if changes_made:
                self.store("changes_since_countvote", json.dumps(True))
        except InvalidOptionError as e:
            return unicode(e)

    # This makes the vote symbol (+, -, \, etc) required, since otherwise we can't
    # tell if this is meant to be a vote or not.
    @listens_to_all(vote_regex_template.format(vote_modifier=""))
    @_depends_on_votestarted(throw_error=False)
    def implicit_vote(self, line, vote, option):
        try:
            parsed_vote = self._parse_vote(line.user, (vote, option))
        except InvalidOptionError:
            return  # Don't complain, will generate too many false positives
        changes_made = self._add_vote(parsed_vote)
        if changes_made:
            self.store("changes_since_countvote", json.dumps(True))

    @listens_to_command("abstain")
    @_depends_on_votestarted()
    def abstain(self, line, args):
        self.store("changes_since_countvote", json.dumps(True))
        self._add_vote(self._get_abstain_vote(line.user))

    @listens_to_command("cancelvotes")
    @_depends_on_votestarted()
    def cancelvotes(self, line, args):
        self.store("changes_since_countvote", json.dumps(True))
        votes = json.loads(self.retrieve("votes"))
        votes = self._remove_all_votes(line.user, votes)
        self.store("votes", json.dumps(votes))

    def _parse_vote(self, voter, (vote, option)):
        boolean_shortform = self.config["boolean_shortform"]
        if vote == "\\":
            if (option == boolean_shortform or
                    option == ABSTAIN_NAME):
                return self._get_abstain_vote(voter)
            else:
                raise InvalidOptionError(ERROR_MESSAGES["invalid_abstain"]
                                         .format(shortform=boolean_shortform))
        if option.strip() == "":
            option = boolean_shortform

        options = self._get_valid_options()
        longest_matching_option =\
            self._find_longest_matching_option(option, options)
        if not longest_matching_option:
            raise InvalidOptionError(ERROR_MESSAGES["invalid_option"]
                                     .format(option=option))

        return Vote(
            voter=voter,
            section=(longest_matching_option.strip()
                     if longest_matching_option != boolean_shortform
                     else DEFAULT_VOTE_OPTION),
            vote=VOTE_SHORTCUT_TO_NAME[vote]
        )

    def _find_longest_matching_option(self, user_option, valid_options):
        user_option = user_option.strip().expandtabs(1)

        def matches_user_option(option):
            option = option.strip()
            # In startswith, adding the space ensures that "oreo"
            # is not treated as matching the option "o".
            return (user_option == option or
                    user_option.startswith(option + " "))

        matching_options = filter(matches_user_option, valid_options)
        return (max(matching_options, key=len)
                if matching_options else '')

    def _add_vote(self, parsed_vote):
        votes = json.loads(self.retrieve("votes"))
        voter, section, vote = parsed_vote
        option = votes[section]
        option_vote = option[vote]
        opposing_option_vote = option[OPPOSING_VOTE[vote]]

        if voter in option_vote:
            return False
        elif voter in opposing_option_vote:
            opposing_option_vote.remove(voter)

        if section == ABSTAIN_OPTION:
            votes = self._remove_all_votes(voter, votes)

        try:
            votes[ABSTAIN_OPTION][FOR_NAME].remove(voter)
        except ValueError:
            pass
        option_vote.append(voter.strip())
        self.store("votes", json.dumps(votes))
        return True

    def _print_votes(self):
        votes = json.loads(self.retrieve("votes"))
        section_names = votes.keys()
        section_names = sorted(section_names)
        # Abstain should always be last in the list
        section_names.append(section_names.pop(
            section_names.index(ABSTAIN_OPTION)))

        sections = [self._get_section_repr(section_name, votes[section_name])
                    for section_name in section_names]
        return " ".join(sections)

    def _get_section_repr(self, section_name, section):
        username_sep = self.config["username_separator"] + " "
        for_, against = section[FOR_NAME], section[AGAINST_NAME]

        if section_name == DEFAULT_VOTE_OPTION:
            return COUNTVOTE_TEMPLATES["default_vote_template"](
                for_=for_,
                against=against,
                username_sep=username_sep
            )
        elif section_name == ABSTAIN_OPTION:
            return COUNTVOTE_TEMPLATES["abstain_template"](
                abstainers=for_,
                username_sep=username_sep
            )
        else:
            return COUNTVOTE_TEMPLATES["section_template"](
                name=section_name,
                for_=for_,
                against=against,
                username_sep=username_sep
            )

    def _remove_all_votes(self, voter, votes):
        for section in votes.copy():
            sec = votes[section]
            try:
                sec[FOR_NAME].remove(voter)
            except ValueError:
                pass
            try:
                sec[AGAINST_NAME].remove(voter)
            except ValueError:
                pass
        return votes

    def _get_valid_options(self):
        options = json.loads(self.retrieve("options"))
        if DEFAULT_VOTE_OPTION in options:
            options[options.index(DEFAULT_VOTE_OPTION)] = (
                self.config["boolean_shortform"])
        return options

    def _get_abstain_vote(self, voter):
        return Vote(
            voter=voter,
            section=ABSTAIN_OPTION,
            vote=FOR_NAME
        )


class InvalidOptionError(Exception):
    pass
