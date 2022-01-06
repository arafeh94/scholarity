import logging
import pickle

from src.AuthorCitationScraper import AuthorCitationScraper
from src.Cache import Cache
from src.PaperCitationScraper import PaperCitationScraper

logging.basicConfig(level=logging.DEBUG, filename='log')

scholar_citations = {}
cache = Cache('cache.pkl')
azzam = 'https://scholar.google.com/citations?user=p3DTnQQAAAAJ&hl=en'
author_scraper = cache.get(azzam, AuthorCitationScraper(azzam))
author_scraper.scrap()
cache.put(azzam, author_scraper)
for citation in author_scraper.scrap():
    paper_citations_scraper = cache.get(citation, PaperCitationScraper(citation.citation_url))
    paper_citations_scraper.scrap()
    cache.put(citation, paper_citations_scraper)
    scholar_citations[citation] = paper_citations_scraper.citations
pickle.dump('azzam.pkl', scholar_citations)
