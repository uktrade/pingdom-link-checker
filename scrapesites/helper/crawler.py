import time
from pylinkvalidator.api import crawl_with_options


class Scanner:

    def run(self, site, ignore_prefix="", team=None):
        errors = set()
        print("Scanning: {} is Supported by {}".format(site, team))

        crawl_site = crawl_with_options(
            [site],
            {
                "workers": 10,
                "depth": 4,
                "show-source": True,
                "header": {
                    "Connection": "keep-alive",
                    "Pragma": "no-cache",
                    "Cache-Control": "no-cache",
                    "Upgrade-Insecure-Requests": 1,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36 link-checker-ops",
                    "DNT": 1,
                    "Accept-Encoding": "gzip, deflate"
                },
                "ignore": ignore_prefix
            }
        )

        if not crawl_site.is_ok:
            for error_page in crawl_site.error_pages.values():
                if error_page.status == 404:
                    page = error_page.url_split.geturl()
                    for source in error_page.sources:
                        source_url = source.origin.geturl()
                        broken_link = source.origin_str
                        errors.add((site, source_url, broken_link))

        return errors
