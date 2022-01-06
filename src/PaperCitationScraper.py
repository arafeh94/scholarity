# Load selenium components
import logging
import typing
from abc import abstractmethod
from time import sleep

import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from src.Citation import Citation
from src.Extractors import CitationElement


class TitleExtractor(CitationElement):

    def element(self):
        return 'title'

    def extract(self, html):
        return html.find_element(By.CSS_SELECTOR, 'a').text


class UrlExtractor(CitationElement):

    def element(self):
        return 'url'

    def extract(self, html):
        return html.find_element(By.CSS_SELECTOR, 'a').get_property('href')


class AuthorsExtractor(CitationElement):

    def element(self):
        return 'authors'

    def extract(self, html):
        return html.find_element(By.CSS_SELECTOR, '.gs_a').text.split('-')[0]


class PublicationExtractor(CitationElement):

    def element(self):
        return 'publication'

    def extract(self, html):
        return html.find_element(By.CSS_SELECTOR, '.gs_a').text.split('-')[1].split(',')[0]


class CitedByExtractor(CitationElement):

    def element(self):
        return 'cited_by'

    def extract(self, html):
        cited_by = html.find_element(By.CSS_SELECTOR, '.gs_fl a:nth-child(3)').text.replace('Cited by ', '')
        return cited_by if cited_by.isnumeric() else '0'


class CitationUrlExtractor(CitationElement):

    def element(self):
        return 'citation_url'

    def extract(self, html):
        return html.find_element(By.CSS_SELECTOR, '.gs_fl a:nth-child(3)').get_property('href')


class YearExtractor(CitationElement):

    def element(self):
        return 'year'

    def extract(self, html):
        return html.find_element(By.CSS_SELECTOR, '.gs_a').text.split('-')[-2][-5:]


class PaperCitationScraper:
    def __init__(self, author_url):
        self.url = author_url
        self.last_url = None
        self.citations = []
        self.executed = False
        self.google_page = 0
        self.logger = logging.getLogger('PaperCitationScraper')

    def scrap(self) -> typing.List[Citation]:
        if self.executed:
            return self.citations
        else:
            self._scrap()
            return self.citations

    def _scrap(self):
        page = webdriver.Chrome(ChromeDriverManager().install())
        while self._next(page):
            citations_filter = lambda x: x.get_attribute('class') == 'gs_ri'
            citations_html = filter(citations_filter, page.find_elements(By.TAG_NAME, 'div'))
            citations_html = list(citations_html)
            extractors = [TitleExtractor(), AuthorsExtractor(), UrlExtractor(), CitedByExtractor(), YearExtractor(),
                          PublicationExtractor(), CitationUrlExtractor()]
            for paper_html in tqdm.tqdm(citations_html, 'parsing'):
                try:
                    citation = Citation()
                    for extractor in extractors:
                        citation.__dict__[extractor.element()] = extractor.extract(paper_html)
                    self.citations.append(citation)
                except Exception as e:
                    self.logger.debug(e)
                    pass
        self.executed = True

    def _next(self, page):
        next_url = self.url
        if self.google_page:
            try:
                next_url = page.find_element(By.CSS_SELECTOR, '#gs_n') \
                    .find_element(By.CSS_SELECTOR, 'td:last-child > a').get_property('href')
            except Exception:
                return False
        self.logger.debug(f'extracting url {next_url}')
        page.get(next_url)
        while page.find_elements(By.CSS_SELECTOR, '#gs_captcha_f'):
            sleep(1)
        self.google_page = next_url
        return True

    def __hash__(self):
        return hash(self.url)
