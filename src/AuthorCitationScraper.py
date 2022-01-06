# Load selenium components
import logging
import typing
from abc import abstractmethod
from time import sleep

import tqdm as tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from src.Cache import Cache, Cacheable
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
        return html.find_element(By.CSS_SELECTOR, '.gs_gray').text


class PublicationExtractor(CitationElement):

    def element(self):
        return 'publication'

    def extract(self, html):
        return html.find_element(By.CSS_SELECTOR, '.gs_gray').text


class CitedByExtractor(CitationElement):

    def element(self):
        return 'cited_by'

    def extract(self, html):
        return html.find_element(By.CSS_SELECTOR, '.gsc_a_c').text


class CitationUrlExtractor(CitationElement):

    def element(self):
        return 'citation_url'

    def extract(self, html):
        return html.find_element(By.CSS_SELECTOR, '.gs_ibl').get_property('href')


class YearExtractor(CitationElement):

    def element(self):
        return 'year'

    def extract(self, html):
        return html.find_element(By.CSS_SELECTOR, '.gsc_a_y').text


class AuthorCitationScraper:
    def __init__(self, author_url):
        self.url = author_url
        self.citations = set()
        self.executed = False
        self.logger = logging.getLogger('AuthorCitationScraper')

    def scrap(self) -> typing.List[Citation]:
        if self.executed:
            return self.citations
        else:
            self._scrap()
            return self.citations

    def _scrap(self):
        page = webdriver.Chrome(ChromeDriverManager().install())
        self.logger.debug(f'retrieving url {self.url}')
        page.get(self.url)
        self._expand(page)
        citations_filter = lambda x: x.get_attribute('class') == 'gsc_a_tr'
        citations_html = filter(citations_filter, page.find_elements(By.TAG_NAME, 'tr'))
        citations_html = list(citations_html)
        extractors = [TitleExtractor(), AuthorsExtractor(), UrlExtractor(), CitedByExtractor(), YearExtractor(),
                      PublicationExtractor(), CitationUrlExtractor()]
        for paper_html in tqdm.tqdm(citations_html, 'parsing'):
            citation = Citation()
            for extractor in extractors:
                citation.__dict__[extractor.element()] = extractor.extract(paper_html)
            self.citations.add(citation)
        self.executed = True

    def _expand(self, page):
        button = page.find_element(By.ID, 'gsc_bpf_more')
        while not button.get_attribute('disabled'):
            self.logger.debug('expanding citations')
            button.click()
            sleep(1)

    def __hash__(self):
        return hash(self.url)
