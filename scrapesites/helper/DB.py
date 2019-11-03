from scrapesites.models import Urllist, Brokenlink, Responsetime


class RecordManager:

    def sites(self):
        return Urllist.objects.all()

    def getActiveSites(self):
        return self.sites().filter(enable=True)

    def getActiveSitesWithBrokenLinks(self):
        return self.sites().filter(enable=True, broken_link_found=True)

    def getAllBrokenLinks(self):
         return Brokenlink.objects.all()

    def getBrokenLinksForSite(self, site):
        return Brokenlink.objects.filter(site_url=site)

    def getBrokenLinksWithPendingSlackSent(self):
        return self.sites().filter(broken_link_found=True, slack_sent=False)

    def updateSlackSentState(self, site=None, slack_sent=None):
        Urllist.objects.filter(site=site).update(slack_sent=slack_sent)

    def updateBrokenLinkState(self, site=None, status=None):
        status_in_db = self.sites().filter(
            site_url=site).values_list('broken_link_found', flat=True)[0]

        if status != status_in_db:
            updateObj = Urllist.objects.filter(
                site_url=site).update(broken_link_found=status)

    def deleteSiteRecordsFromBrokenLinks(self, site=None):
        Brokenlink.objects.filter(site_url=site).delete()

    def has_deadlinks(self):
        if self.sites().filter(broken_link_found=True).values_list('broken_link_found'):
            return True
        return False

    def getResponseTime(self):
        return Responsetime.objects.all()

    def updateResponseRecord(self, response_time=None, previous_check_state=None):
        Responsetime.objects.update_or_create(id=1, defaults={
            "response_time": response_time, "previous_check_state": previous_check_state})

    def updateBrokenLinks(self, site=None, errors=None):
        broken_links_record_in_db = set(self.getBrokenLinksForSite(
            site=site).values_list(
            'site_url', 'source_url', 'broken_link'))

        # All 404 found in current RUN but not in DB
        addRecords = errors.difference(broken_links_record_in_db)
        # All 404 found in DB but not in current RUN
        removeRecords = broken_links_record_in_db.difference(errors)

        # Add New Broken Links to Broken Links Table
        for site, source_url, broken_link in addRecords:
            Brokenlink.objects.create(
                site_url=site, source_url=source_url, broken_link=broken_link)

        # Remove Previously Broken Links from Table
        for site, source_url, broken_link in removeRecords:
            Brokenlink.objects.filter(
                site_url=site, source_url=source_url, broken_link=broken_link).delete()
