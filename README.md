# Web Crawler

This is a simple-focused web crawler designed to crawl 1000 web pages of a specific domain starting from georgia tech's website. It uses DFS to identify URLs and subsequent scrape data from it. It reads the contents, extracts keywords by calculating the TF-IDF scores of the words per page and then finally stores this data, the indexed words and all the statistics captured during the process in an Excel.

File Descirptions - 
### crawler.py
Contains the main crawler class which is responsible for crawling from the source URL to 1000 different URLs, indexing keywords and collecting statistics.

### keyWordExtractor.py
Contains the keyword extractor class, which calculates the TF-IDF score of each word in a page and output the top 25 unique keywords per page to be indexed.

### excelInteractor.py
This file writes all the stats collected by crawler.py in an Excel in a total of 3 sheets. See web_crawler_output.xlsx for example.

Project Set-Up
(Pre-requisites: Python3)
1. Clone the project in your local machine.
2. Open terminal and go to the directory where you cloned the project.
3. Install dependent packages - 'pip install -r requirements.txt'
4. Run Crawler - 'python crawler.py'

## References used
1. https://www.dotnetlovers.com/Article/203/implementing-crawler-using-python--search-engine-implementation-part-1
2. https://www.tutorialspoint.com/beautiful_soup/beautiful_soup_souping_the_page.html
3. https://pknerd.medium.com/develop-your-first-web-crawler-in-python-scrapy-6b2ee4baf954
4. https://www.analyticsvidhya.com/blog/2020/11/words-that-matter-a-simple-guide-to-keyword-extraction-in-python/


