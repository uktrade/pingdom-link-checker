from django.views.generic import TemplateView
from scrapesites.helper.DB import RecordManager


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
    template_name = 'logs.html'
    dbManager = RecordManager()

    def get_context_data(self, **kwargs):
        context = super(LogsView, self).get_context_data(**kwargs)
        context['title'] = 'Link check - logs'
        if self.dbManager.has_deadlinks():
            context['sites'] = self.dbManager.getActiveSites()
            context['brokenLinks'] = self.dbManager.getAllBrokenLinks()
        return context


    # def scan(request):
    #     return render(request, 'scan-base.html', {})
