from ..base import BasePlugin
from ..decorators import listens_to_command


class Plugin(BasePlugin):
    """
    Rewrite of bangmotivate using the new listens_to_command decorator.

    Notifies people of the excellent work they are doing.

    Let me know who is doing good work:
    (Assuming COMMAND_PREFIX is !)

        !m {{ nick }}

    And I will promptly notify them:

        You are doing good work {{ nick }}

    http://motivate.im/
    """

    @listens_to_command("m")
    def motivate(self, line, args):
        # args[1] will not exist if the user only typed "!m"
        try:
            nick = args[0]
            return u"You're doing good work, {}!".format(nick)
        # We expect an IndexError, everything else is actually bad
        except IndexError:
            pass
