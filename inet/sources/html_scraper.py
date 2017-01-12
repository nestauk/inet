# -*- coding: utf-8 -*-
"""
inet.sources.html_scraper
-------------------------

Provides the HtmlScraper class, which contains
methods for scraping websites for relevant information

"""

import logging
import requests

from lxml import html
from lxml.etree import XMLSyntaxError
from urllib.parse import urlparse

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HtmlScraper():
    """Provides html scraping methods"""

    def check_url_scheme(self, url):
        """Check URL validity.

        Checks that urls have a valid scheme, and if not prepends 'http://'.

        Parameters
        ----------
        url: string
            String representation of a URL

        Returns
        -------
        URL string
        """
        if not urlparse(url).scheme:
            url = "http://" + url
        return url

    def get_links_using_xpath(self, tree, xpath):
        """Extract elements from tree using xpath

        Extracts elements matching 'xpath' in 'tree'
        and prepends 'http://' if they aren't present in
        the extracted element.

        Parameters
        ----------
        tree: lxml.html.HtmlElement
            HTML of the website being scraped
        xpath: string
            String represetnation of a valid xpath selector

        Returns
        -------
        list of strings representing urls
        """
        return list(self.check_url_scheme(str(link)) for
                    link in tree.xpath(xpath))

    def request_url(self, url):
        """Wraps the requests.get() method in exception handlers"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError as e:
            log.debug(e)
        except requests.exceptions.TooManyRedirects as e:
            log.debug(e)
        except requests.exceptions.InvalidURL as e:
            log.debug(e)
        except requests.exceptions.HTTPError as e:
            log.debug(e)

    def scrape(self, url, about=True, about_xpath=None,
               twitter_handles=True, twitter_xpath=None):
        """Scrape the HTML of company websites

        Search the html returned by the address specified in 'url'. Extracts
        HTML from any about pages that are present. Also extracts twitter
        handles from the html.

        Parameters
        ----------
        url: string
            A string representing the url of the site to be scraped
        about: Boolean, default True
            Set to False if about pages shouldn't be scraped.
        about_xpath: string, default None
            Custom xpath. If not supplied a preset xpath is used that
            extracts hrefs from occurences of 'about' in <a> elements

        Returns
        -------
        Dictionary of form {'about_html: []', 'twitter_links': []} where
        'about_html' is a list of html documents from the scrape, and
        'twitter_links' is a list of twitter handle links found in the html.
        """

        # Xpath selector for hrefs that contain 'about'
        if about_xpath is None:
            # translate lowercases all upercase A B O U T chars
            about_xpath = ("//a[text()[contains(translate(., 'ABOUT', " +
                           "'about'), 'about')]]/@href")

        if twitter_xpath is None:
            twitter_xpath = ("//a[contains(@href,'twitter.com')]/@href")

        url = self.check_url_scheme(url)

        try:
            page = self.request_url(url)
            tree = html.fromstring(page.content)
        except AttributeError as e:
            # Invalid url or no data returned
            log.debug(e)
            return None
        except XMLSyntaxError as e:
            log.debug(e)
            return None

        about_links = self.get_links_using_xpath(tree, about_xpath)
        twitter_links = self.get_links_using_xpath(tree, twitter_xpath)

        responses = []
        for link in about_links:
            page = self.request_url(link)
            if page:
                responses.append(page.content)

        return responses, twitter_links


html_scraper = HtmlScraper()