# -*- coding: utf-8 -*-
import csv
import os
import requests

from collections import namedtuple
from lxml import html
from . import sources


class Inet():
    """Inet class"""
    def __init__(self, data_file=None):
        # Naive check for file type based on extension
        # First check filepath is passed as a parameter
        if data_file is not None:
            # Then split off the extension using os
            ext = os.path.splitext(data_file)[-1].lower()
            # then check ends with .csv or .json
            if ext == '.csv':
                self.rows = []
                with open(data_file) as f:
                    f_csv = csv.reader(f)
                    headings = next(f_csv)
                    Row = namedtuple('Row', headings)
                    for r in f_csv:
                        row = Row(*r)
                        self.rows.append(row)
            else:
                raise TypeError("Input file must be of type .csv")
        else:
            raise AttributeError("No data_file path specified as a "
                                 "parameter to Inet object")

        # Access sources from this class
        self.twitter_client = sources.twitter_client
        self.ops_client = sources.ops_client
        self.ch_client = sources.ch_client

    def match_twitter_to_emails(self):
        """Use the emails from the data list to identify
        Twitter accounts"""
        pass

    def match_companies_to_ch(self):
        """Use the supplied company names to match to Companies House
        entries using their API"""
        pass

    def match_people_to_ch(self):
        """Match individuals named in the data to Companies House entries"""
        pass

    def match_companies_to_epo(self):
        """Match companies named in the data to EPO's database"""
        pass

    def match_people_to_epo(self):
        """Match individuals named in the data to EPO's database"""
        pass

    def scrape_html(self, url):
        """Use urls in the data to get company html - specifically
        the homepage, and the about page"""
        about_xpath = ("//a[text()[contains(translate(., 'ABOUT', 'about')," +
                       "'about')]]/@href")
        page = requests.get(url)
        tree = html.fromstring(page.content)
        about_links = tree.xpath(about_xpath)
        about_responses = [requests.get(url) for url in about_links]

