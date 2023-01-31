import requests
import json
import re
import time
from urlparse import urljoin
from .. import config
from ..base import BasePlugin
from ..decorators import listens_to_all, listens_to_mentions


class Config(config.BaseConfig):

    jira_url = config.Field(help_text="JIRA Link, eg: 'https://tickets.metabrainz.org'")
    rest_api_suffix = config.Field(help_text="Suffix for the JIRA REST API, eg: 'rest/api/2/project'", default="rest/api/2/project")
    ignored_nicks = config.Field(help_text="comma seperated names of your own bot and other nicks you want to ignore, eg: BrainzBot, github")
    issue_cooldown = config.Field(help_text="Time to wait in seconds before an issue is mentioned again", default=60)


class Plugin(BasePlugin):
    """
    JIRA issue lookup

    Returns the description of a JIRA Issue

        jira:{{projectname}}-{{issuenumber}}
    """

    config_class = Config

    @listens_to_all(ur'(?:.*)\b([A-Z]+-\d+)\b(?:.*)')
    def issue_lookup(self, line):
        """
        Lookup a specified JIRA issue

        Usage:
            Just mention the issue by its {{ISSUENAME}}
            Eg:
                Can you please checkup on PROJECT-123
        """
        if line.user not in self._get_ignored_nicks():
            api_url = urljoin(self.config['jira_url'], self.config['rest_api_suffix'])
            projects = json.loads(self.retrieve('projects'))

            queries = re.findall(r"[A-Z]+-\d+", line.text)
            queries = [query.split("-") for query in queries]
            reply = []

            for query in queries:
                if query[0] in projects:
                    issue_url = urljoin(api_url, "issue/{}-{}".format(query[0], query[1]))
                    response = requests.get(issue_url)

                    if response.status_code == 200:
                        response_text = json.loads(response.text)
                        name = response_text['key']
                        desc = response_text['fields']['summary']

                        # Check if issue has recently been processed
                        if not self._issue_on_cooldown(name):
                            # Only post URL if issue isn't already mentioned as part of one
                            if re.search(ur'(http)(\S*)/({})\b'.format(name), line.text):
                                reply.append(u"{}: {}".format(name, desc))
                            else:
                                return_url = urljoin(self.config['jira_url'], "browse/{}".format(name))
                                reply.append(u"{}: {} {}".format(name, desc, return_url))

            # Only respond if any valid issues were found
            if len(reply) > 0:
                if line.text.lower().startswith("[off]"):
                    return u"[off] {}".format("\n[off] ".join(reply))
                else:
                    return u"\n".join(reply)

    @listens_to_mentions(ur'(.*)\bUPDATE:JIRA')
    def update_projects(self, line):
        """
        Updates projects list on mentioning the bot with the command

        Usage:
            Ping the bot with the command:
            UPDATE:JIRA
        """

        api_url = urljoin(self.config['jira_url'], self.config['rest_api_suffix'])
        project_url = urljoin(api_url, 'project')
        response = requests.get(project_url)

        if response.status_code == 200:
            projects = [project['key'] for project in json.loads(response.text)]
            self.store('projects', json.dumps(projects))
            return "Successfully updated projects list"

        return "Could not update projects list"

    def _get_ignored_nicks(self):
        try:
            ignored_nicks = self.config['ignored_nicks'].split(",")
        except AttributeError:
            ignored_nicks = []
        ignored_nicks = [bot.strip() for bot in ignored_nicks]
        return ignored_nicks

    def _issue_on_cooldown(self, issue):
        recent_issues = {}

        if self.retrieve('recent_issues'):
            recent_issues = json.loads(self.retrieve('recent_issues'))

        # Update issue timestamps
        now = int(time.time())
        for name, timestamp in recent_issues.items():  # Key is issue name, value is int unix timestamp
            if (now - timestamp) > self.config['issue_cooldown']:
                del recent_issues[name]

        if issue in recent_issues:
            return True

        # Add issue to recent ones
        recent_issues[issue] = now
        self.store('recent_issues', json.dumps(recent_issues))

        return False
