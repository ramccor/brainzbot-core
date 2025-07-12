class PrivateMessage(object):
    """
    A holder object for sending a private message.
    This is used in botbot.apps.plugins.runner
    """
    def __init__(self, nick, msg):
        self.nick = nick
        self.msg = msg


class Router(object):
    """
    Custom Router object
    """
    def __init__(self, name):
        self.name = name
        self.plugins = {}


class BasePlugin(object):
    "All plugins inherit this class"
    app = None
    config_class = None

    def __init__(self, *args, **kwargs):
        self.slug = self.__module__.split('.')[-1]

    def initialize(self):
        pass

    @property
    def config(self):
        if hasattr(self, 'prod_config'):
            return self.prod_config
        if self.slug in self.app.plugin_configs:
            return self.app.plugin_configs[self.slug].fields
        return None

    def _unique_key(self, key):
        """helper method for namespacing storage keys per plugin"""
        return '{0}:{1}'.format(self.slug, key.strip())

    def store(self, key, value):
        """Stores `value` as a string to `key`

        SET: http://redis.io/commands/set
        """
        ukey = self._unique_key(key)
        self.app.storage.set(ukey, value.encode('utf-8'))

    def retrieve(self, key):
        """Retrieves string stored at `key`

        GET: http://redis.io/commands/get
        """
        ukey = self._unique_key(key)
        value = self.app.storage.get(ukey)
        if value:
            value = value.decode('utf-8')
        return value

    def delete(self, key):
        """Deletes a stored `key`

        DEL: http://redis.io/commands/del
        """
        ukey = self._unique_key(key)
        return self.app.storage.delete(ukey) == 1

    def incr(self, key):
        """Increments counter specified by `key`. If necessary, creates
        counter and initializes to 0.

        INCR http://redis.io/commands/incr
        """
        ukey = self._unique_key(key)
        return self.app.storage.incr(ukey)
