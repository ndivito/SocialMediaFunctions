# web scraping framework
import scrapy
import os.path
from os import path
# for regular expression
import re

# for selenium request
from scrapy_selenium import SeleniumRequest

# for link extraction
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor


class EmailtrackSpider(scrapy.Spider):
    def __init__(self, url, cleanURL):
        self.url = url
        self.cleanURL = cleanURL
        self.uniqueemail = set()
    # name of spider
    name = 'emailtrack'




    # to have unique email ids
    uniqueemail = set()

    # start_requests sends request to given https://www.geeksforgeeks.org/
    # and parse function is called
    def start_requests(self):
        yield SeleniumRequest(
            url=self.url,
            wait_time=3,
            screenshot=True,
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        # this helps to get all links from source code
        links = LxmlLinkExtractor(allow=()).extract_links(response)

        # Finallinks contains links urk
        Finallinks = [str(link.url) for link in links]

        # links list for url that may have email ids
        links = []

        # filtering and storing only needed url in links list
        # pages that are about us and contact us are the ones that have email ids
        for link in Finallinks:
            if (
                    'Contact' in link or 'contact' in link or 'About' in link or 'about' in link or 'CONTACT' in link or 'ABOUT' in link):
                links.append(link)

        # current page url also added because few sites have email ids on there main page
        links.append(str(response.url))

        # parse_link function is called for extracting email ids
        l = links[0]
        links.pop(0)

        # meta helps to transfer links list from parse to parse_link
        yield SeleniumRequest(
            url=l,
            wait_time=3,
            screenshot=True,
            callback=self.parse_link,
            dont_filter=True,
            meta={'links': links}
        )

    def parse_link(self, response):

        # response.meta['links'] this helps to get links list
        links = response.meta['links']
        flag = 0

        # links that contains following bad words are discarded
        bad_words = ['facebook', 'instagram', 'youtube', 'twitter', 'wiki', 'linkedin']

        for word in bad_words:
            # if any bad word is found in the current page url
            # flag is assigned to 1
            if word in str(response.url):
                flag = 1
                break

        # if flag is 1 then no need to get email from
        # that url/page
        if (flag != 1):
            html_text = str(response.text)
            # regular expression used for email id
            email_list = re.findall('\w+@\w+\.{1}\w+', html_text)
            # set of email_list to get unique
            email_list = set(email_list)
            if (len(email_list) != 0):
                for i in email_list:
                    # adding email ids to final uniqueemail
                    self.uniqueemail.add(i)

        # parse_link function is called till
        # if condition satisfy
        # else move to parsed function
        if (len(links) > 0):
            l = links[0]
            links.pop(0)
            yield SeleniumRequest(
                url=l,
                callback=self.parse_link,
                dont_filter=True,
                meta={'links': links}
            )
        else:
            yield SeleniumRequest(
                url=response.url,
                callback=self.parsed,
                dont_filter=True
            )

    def parsed(self, response):
        # emails list of uniqueemail set
        print('unique emails: ', self.uniqueemail, ' --- url: ', self.url)
        emails = list(self.uniqueemail)
        finalemail = []

        for email in emails:
            # avoid garbage value by using '.in' and '.com'
            # and append email ids to finalemail
            if ('.in' in email or '.com' in email or 'info' in email or 'org' in email or '.net' in email) and 'wixofday@wix.com' != email:
                finalemail.append(email.lower())


        #remove duplicates
        finalemail = [i for n, i in enumerate(finalemail) if i not in finalemail[:n]]
        print(finalemail, ' : finalEmails')
        if path.exists("emailsTemp/"+ self.cleanURL + '.csv'):
            f = open("emailsTemp/"+ self.cleanURL + '.csv', "w")
        else:
            f = open("emailsTemp/"+ self.cleanURL + '.csv', "x")
        for email in finalemail:
            if email == finalemail[-1]:
                f.write(email)
            else:
                f.write(email + ',')
        f.close()

        # final unique email ids from geeksforgeeks site
        print('\n' * 2)
        print("Emails scraped", finalemail)
        print('\n' * 2)
