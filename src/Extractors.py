from abc import abstractmethod

from selenium.webdriver.common.by import By


class CitationElement:
    @abstractmethod
    def extract(self, html):
        pass

    @abstractmethod
    def element(self):
        pass

