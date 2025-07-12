from django.db import models
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.postgres.search import SearchVectorField
from botbot.apps.bots.utils import channel_url_kwargs


REDACTED_TEXT = '[redacted]'

MSG_TMPL = {
        "JOIN": "{nick} joined the channel",
        "NICK": "{nick} is now known as {text}",
        "QUIT": "{nick} has quit",
        "PART": "{nick} has left the channel",
        "ACTION": "{nick} {text}",
        "SHUTDOWN": "-- BotBot disconnected, possible missing messages --",
        }


class Log(models.Model):
    bot = models.ForeignKey('bots.ChatBot', null=True, on_delete=models.CASCADE)
    channel = models.ForeignKey('bots.Channel', null=True, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(db_index=True)
    nick = models.CharField(max_length=255)
    text = models.TextField()
    action = models.BooleanField(default=False)

    command = models.CharField(max_length=50, null=True, blank=True)
    host = models.TextField(null=True, blank=True)
    raw = models.TextField(null=True, blank=True)

    # freenode chan name length limit is 50 chars, Campfire room ids are ints,
    #  so 100 should be enough
    room = models.CharField(max_length=100, null=True, blank=True)

    search_index = SearchVectorField(null=True)

    class Meta:
        ordering = ('-timestamp',)
        indexes = [
            models.Index(fields=('channel', 'timestamp')),
            # todo: add search vector index
        ]

    def get_absolute_url(self):
        kwargs = channel_url_kwargs(self.channel)
        kwargs['msg_pk'] = self.pk

        return reverse('log_message_permalink', kwargs=kwargs)

    def as_html(self):
        return render_to_string("logs/log_display.html",
                                {'message_list': [self]})
    def get_cleaned_host(self):
        if self.host:
            if '@' in self.host:
                return self.host.split('@')[1]
            else:
                return self.host

    def get_nick_color(self):
        return hash(self.nick) % 32

    def __str__(self):
        if self.command == "PRIVMSG":
            text = ''
            if self.nick:
                text += '{0}: '.format(self.nick)
            text += self.text[:20]
        else:
            try:
                text = MSG_TMPL[self.command].format(nick=self.nick, text=self.text)
            except KeyError:
                text = "{}: {}".format(self.command, self.text)

        return text

    def save(self, *args, **kwargs):
        if self.nick in settings.EXCLUDE_NICKS:
            self.text = REDACTED_TEXT
        return super(Log, self).save(*args, **kwargs)
