from django.views.generic import TemplateView, DetailView
from scrapesites.helper.DB import RecordManager
from scrapesites.helper.date import HumanReadable
from braces.views import JSONResponseMixin

class HomeView(TemplateView):
    template_name = 'pingdom_check.xml'
    dbManager = RecordManager()

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        if self.dbManager.has_deadlinks():
            context['sites'] = self.dbManager.getActiveSitesWithBrokenLinks()
            context['brokenLinks'] = self.dbManager.getAllBrokenLinks()
        return context


class LogsView(TemplateView):

    dbManager = RecordManager()

    def get_context_data(self, **kwargs):
        context = super(LogsView, self).get_context_data(**kwargs)
        context['title'] = 'Link check - logs'
        if self.dbManager.has_deadlinks():
            context['sites'] = self.dbManager.getActiveSites()
            context['brokenLinks'] = self.dbManager.getAllBrokenLinks()
        return context


class GeckoBoard(JSONResponseMixin, DetailView):
    dbManager = RecordManager()
    timeString = HumanReadable()
    team = ''

    def get(self, request, *args, **kwargs):

        if 'team' in self.request.GET:
            self.team = self.request.GET['team']

        context_dict = self.makeReport(team=self.team)

        return self.render_json_response(context_dict)

    def makeReport(self, team=None):
        geckoList = []

        if team and self.teamExists(team=team):
            sites = self.dbManager.getActiveSitesForTeam(team=team)
        else:
            sites = self.dbManager.getActiveSitesWithBrokenLinks()

        for site in sites:
            site_description = 'It is all Sunny here!'
            colour = 'green'

            if site.broken_link_found:
                site_description = 'It is Bit Cloudy here'
                colour = 'red'

            geckoList.append(
                {"title": {"text": site.site_url},
                           "label": {"name": "WebSite", "color": f'{colour}'},
                           "description": f"{site_description}"
                })
            if site.broken_link_found:
                for link in self.dbManager.getBrokenLinksForSite(site=site.site_url):
                    downtime = self.timeString.EclapsedTime(created_at=link.created_at)
                    geckoList.append(
                        {"title": {"text": link.source_url},
                         "label": {"name": "Source", "color": "#b5712b"},
                         "description":f"Downtime: {downtime} Brokenlink: {link.broken_link}"
                         })
        return geckoList

    def teamExists(self,team=None):
        return self.dbManager.has_team(team=team)

class GeckoBrokenLinkCount(JSONResponseMixin, DetailView):
    dbManager = RecordManager()

    def get(self, request, *args, **kwargs):

        current_broekn_links = self.dbManager.getAllBrokenLinks().count()
        all_links = self.dbManager.getActiveSites().count()

        context_dict = self.makeReport(min=0,max=all_links,current=current_broekn_links)

        return self.render_json_response(context_dict)


    def makeReport(self,min=0,max=100,current=0):
        report = {
            "item": current,
            "min": {
                "value": min,
            },
            "max":{
                "value": max
            }
        }

        return report