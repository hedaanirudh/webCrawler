from urllib.parse import urljoin
from bs4 import BeautifulSoup
from urllib import request
from collections import defaultdict
from pandas import DataFrame
import time
from keyWordExtractor import KeyWordExtractor
from excelInteractor import Excel


class WebCrawler:

    def __init__(self):
        self.parsed_urls_dict = defaultdict(int)
        self.document_id = 1
        self.df = DataFrame(columns=["Document ID", "URL", "Keywords", "Parent URL ID"])
        self.total_word_count = 0
        self.index = defaultdict(list)
        self.ignored = set()
        self.failed = 0
        self.total_url_count = 0
        self.unique_urls_encountered = set()
        self.domain = "gatech"
        self.max_pages = 20
        self.start_time = time.time()
        self.previous_time = time.time()
        self.interval = 5
        self.time_tracker = {}
        self.unique_words = set()
        self.keyword_extractor = KeyWordExtractor()
        self.ignore_keywords = set(
            ['a', 'at', 'our', 'you', 'your', 'an', 'the', 'in', 'is', 'am', 'are', 'was', 'were', 'will', 'shall',
             'it', '&',
             'this', 'that', 'of', 'to', 'and', 'on', 'school', 'we', 'schools', 'computer', 'computers', 'science',
             'computing', 'for', 'has', 'georgia', 'tech', 'could', 'would', 'as', 'had', 'good', 'ga', 'better', 'new',
             'study', 'by', 'us'])

    def create_workbook(self, excel):
        final_stats = self.get_final_stats()
        excel.create_workbook(final_stats, self.df, self.index, self.time_tracker)
        return

    # Reads the page and return soup object of page content
    def get_web_page(self, url):
        try:
            httpOpen = request.urlopen(url, timeout=5)
            # content = httpOpen.read().decode(encoding="iso-8859-1")
            content = httpOpen.read().decode(encoding="utf-8")
            soup = BeautifulSoup(content, "html.parser")
            return soup
        except Exception as e:
            return e

    # Returns all page urls with url-text
    def get_page_urls(self, url, soup):
        try:
            links = soup('a')
            urls = set()
            for link in links:
                if ('href' in dict(link.attrs)) and ('mailto' not in link):
                    url = urljoin(url, link['href'])
                    urls.add((url.split('#')[0], link.text))
            self.total_url_count += len(urls)
            unique_urls = list(urls - set(url))
            self.unique_urls_encountered.update(unique_urls)
            return unique_urls
        except Exception as e:
            return None

    # Returns array of words
    def get_words(self, text):
        text = text.lower()
        words = list(self.keyword_extractor.extract_keywords(text).keys())
        # words = text.split()
        self.total_word_count += len(words)
        filtered_words = list(set(words) - self.ignore_keywords)
        self.unique_words.update(filtered_words)
        return filtered_words[:25]

    # Returns urlId if available in database or zero
    def get_url_id(self, url):
        return self.parsed_urls_dict.get(url, 0)

    # Insert new url
    def insert_url(self, url):
        if url not in self.parsed_urls_dict:
            self.parsed_urls_dict[url] = self.document_id
            self.document_id += 1
        return self.parsed_urls_dict[url]

    # Index words and store associated documents per index
    def update_index(self, words, url_id):
        for word in words:
            self.index[word].append(str(url_id))

    # Record statistics for every interval specified
    def record_stats(self):
        doc_no = (self.document_id - 1)
        if doc_no == 0:
            self.previous_time = time.time()
            self.start_time = time.time()
        if doc_no % self.interval == 0 and doc_no > 0:
            print('Crawled ' + str(doc_no) + ' pages')
            current_time = time.time()
            self.time_tracker[doc_no] = {
                "last_time": round(current_time - self.previous_time, 4),
                "total_time": round(current_time - self.start_time, 4),
                "average_keywords": self.total_word_count // doc_no,
                "total_keywords": self.total_word_count,
                "total_unique_keywords": len(self.unique_words),
                "average_unique_keywords": len(self.unique_words) // doc_no,
                "urls_to_be_crawled": len(self.unique_urls_encountered) - doc_no - len(self.ignored) - self.failed
            }
            self.previous_time = time.time()

    # Crawl and index all pages in a website
    def crawl(self, url, last_url_id=None):
        try:
            url_id = self.get_url_id(url)
            if self.domain not in url:
                self.ignored.add(url)
                self.parsed_urls_dict[url] = -1
                return
            if url_id == 0:
                soup = self.get_web_page(url)
                if not soup:
                    self.ignored.add(url)
                    self.parsed_urls_dict[url] = -1
                    return None
                # print('Crawling ', url)
                urls = self.get_page_urls(url, soup)
                try:
                    words = self.get_words(soup.get_text())
                except Exception as e:
                    self.failed += 1
                    self.parsed_urls_dict[url] = -1
                    return None

                self.record_stats()

                url_id = self.insert_url(url)
                self.update_index(words, url_id)
                self.df = self.df.append(
                    {"Document ID": url_id, "URL": url, "Keywords": ', '.join(words), "Parent URL ID": last_url_id},
                    ignore_index=True)

                # recursive call to index all new urls found on this page
                for url in urls:
                    if self.document_id > self.max_pages:
                        break
                    if url not in self.parsed_urls_dict and "pdf" not in url and "jpg" not in url:
                        self.crawl(url[0], url_id)
        except Exception as e:
            self.failed += 1
            self.parsed_urls_dict[url] = -1
            return None

    # Final statistics after the crawler is done executing
    def get_final_stats(self):
        d = {
            "Total URLs Found": self.total_url_count,
            "Unique URLs Found": len(self.unique_urls_encountered),
            "Total URLs Crawled": self.max_pages,
            "URLs To Ve Crawled": (
                        len(self.unique_urls_encountered) - self.max_pages - len(self.ignored) - self.failed),
            "Total URLs Failed": self.failed,
            "Total URLs Ignored": len(self.ignored),
            "URLs Crawled / URLs Remaining": self.max_pages / (
                        len(self.unique_urls_encountered) - self.max_pages - len(self.ignored) - self.failed),
            "Total Keywords Found": self.total_word_count,
            "Average # Keywords Per Page": self.total_word_count // self.max_pages,
            "Unique Keywords Found": len(self.unique_words),
            "Average # Unique Keywords Per Page": len(self.unique_words) // self.max_pages,
            "Total Time (seconds)": time.time() - self.start_time
        }
        return d


if __name__ == '__main__':
    gatech = "https://www.cc.gatech.edu/"
    crawler = WebCrawler()
    excel = Excel()
    crawler.crawl(gatech, 0)
    crawler.record_stats()
    crawler.create_workbook(excel)
    # return final_stats
