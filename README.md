# Metabrainz BotBot Chatlogger Plugins

To get started:

```
$ pip install -e git+https://github.com/metabrainz/botbot-plugins.git#egg=botbot-plugins
$ botbot-shell
```

Pass a comma-separated list of modules to run a subset of the plugins:

```
$ botbot-shell brain,images
```

## Docs
[![Read the Docs](https://img.shields.io/readthedocs/pip.svg)](https://brainzbot.readthedocs.io/)

BrainzBot's documentation, including information on how to create new plugins, is available on [Read the Docs](https://brainzbot.readthedocs.io).

## Tests

[![Build Status](https://travis-ci.org/metabrainz/botbot-plugins.svg?branch=master)](https://travis-ci.org/metabrainz/botbot-plugins/)

```
py.test botbot_plugins
```

## Contribute!

We want you to contribute your own plugins to make BotBot.me better. Please [read the plugin docs](https://brainzbot.readthedocs.io/en/latest/plugins.html) and review our [contributing guidelines](https://github.com/metabrainz/botbot-plugins/blob/master/CONTRIBUTING.md) prior to getting started to ensure your plugin is accepted.
