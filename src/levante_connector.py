import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Any

class LevanteConnector:
    def __init__(self, base_url: str = "https://www.levante.com.br"): # This URL might need adjustment based on actual content structure
        self.base_url = base_url
        self.session = requests.Session()
        # Potentially add headers to mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _get_page_content(self, url: str) -> BeautifulSoup:
        """Fetches the content of a given URL and parses it with BeautifulSoup."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None

    def fetch_latest_reports(self, search_term: str = None, num_reports: int = 5) -> pd.DataFrame:
        """Fetches a list of the latest reports or articles from Levante.
           This is a generic example and will likely need customization based on Levante's actual website structure.
        :param search_term: Optional term to filter reports.
        :param num_reports: Number of reports to try and fetch.
        :return: DataFrame with report titles, links, and potentially dates.
        """
        reports_data = []
        # This URL is a placeholder. You'll need to find the actual URL for reports/articles.
        # Example: a blog page, a news section, or a search results page.
        search_url = f"{self.base_url}/analises-e-relatorios" # Example path, verify on actual site
        if search_term:
            # This part is highly dependent on how Levante implements search or filtering
            # For simplicity, we'll just fetch the main reports page and filter locally.
            print(f"Searching for reports related to \'{search_term}\' on {search_url}")
        else:
            print(f"Fetching latest reports from {search_url}")

        soup = self._get_page_content(search_url)
        if not soup:
            return pd.DataFrame()

        # This is a generic selector. You will need to inspect Levante's website HTML
        # to find the correct CSS selectors for report titles, links, and dates.
        # Example: articles might be within <div class="report-item"> or <article> tags.
        # Look for elements that contain the title and a link.
        report_elements = soup.find_all('a', class_='report-link') # Placeholder class
        if not report_elements:
            report_elements = soup.find_all('h2', class_='entry-title') # Another common pattern
            if report_elements:
                print("Found potential report titles, trying to extract links from parents.")
                report_elements = [h2.find_parent('a') for h2 in report_elements if h2.find_parent('a')]

        for i, element in enumerate(report_elements):
            if len(reports_data) >= num_reports:
                break
            
            title = element.get_text(strip=True) if element else 'N/A'
            link = element['href'] if element and element.has_attr('href') else 'N/A'
            
            # Ensure link is absolute
            if link and not link.startswith('http'):
                link = self.base_url + link

            # Basic filtering by search_term (case-insensitive)
            if search_term and search_term.lower() not in title.lower():
                continue

            reports_data.append({
                'Source': 'Levante',
                'Title': title,
                'Link': link,
                'Date': 'N/A' # Date extraction would require more specific parsing
            })
        
        if not reports_data:
            print(f"No reports found or selectors need adjustment for {search_url}")

        return pd.DataFrame(reports_data)

    def fetch_data(self, query: str = None, num_results: int = 5) -> pd.DataFrame:
        """Generic fetch data method to be used by DataCoordinator."""
        return self.fetch_latest_reports(search_term=query, num_reports=num_results)


if __name__ == '__main__':
    # Example Usage
    levante = LevanteConnector()
    print("\nFetching latest reports from Levante:")
    latest_reports = levante.fetch_latest_reports(num_reports=3)
    print(latest_reports)

    print("\nFetching reports about 'PETR4' from Levante:")
    petr4_reports = levante.fetch_latest_reports(search_term='PETR4', num_reports=2)
    print(petr4_reports)

    print("\nFetching reports about 'Bolsa' from Levante:")
    bolsa_reports = levante.fetch_latest_reports(search_term='Bolsa', num_reports=5)
    print(bolsa_reports)

    # Note: This connector is highly dependent on the actual HTML structure of Levante's website.
    # The current CSS selectors are placeholders and will likely need to be updated after inspecting the site.
    # To inspect: Right-click on a report title on Levante's website -> Inspect Element.
    # Look for unique classes or IDs that contain the report title and its link.

