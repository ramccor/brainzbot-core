from ..base import BasePlugin
from ..decorators import listens_to_regex_command


class Plugin(BasePlugin):
    """
    More advanced version of the brainz plugin using the new
    listens_to_regex_command decorator.

    Remembers and recalls arbitrary information.

    To have me remember something for you, ask me in this format:

        {{ command_prefix }}rem thing=stuff I need to remember

    When you want me to recall the information, ask me in this format:

        {{ command_prefix }}rec thing

    I will prompty respond to your request with:

        stuff I need to remember
    """

    @listens_to_regex_command("remember", ur"(?P<key>.+?)=\s*(?P<value>.*)")
    def remember(self, line, key, value):
        self.store(key, value)
        return u'I will remember "{0}" for you {1}.'.format(key, line.user)

    @listens_to_regex_command("recall", ur"(?P<key>.*)")
    def recall(self, line, key):
        value = self.retrieve(key)
        if value:
            return value
        else:
            return u'I\'m sorry, I don\'t remember "{0}".'.format(key)

    @listens_to_regex_command("forget", ur"(?P<key>.*)")
    def forget(self, line, key):
        self.delete(key)
        return u'What was "{0}" all about?'.format(key)
