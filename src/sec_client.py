import requests
import time
from typing import Dict, Optional
import config


class SecClient:
    """
    Client class that handles communication with the SEC EDGAR API.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": config.SEC_USER_AGENT,
                "Accept-Encoding": "gzip, deflate",
                "Host": "data.sec.gov",
            }
        )
        self._ticker_map: Dict[str, str] = {}

    def _get(self, url: str, host_override: str = None) -> requests.Response:
        """Helper to handle rate limits and specific host headers."""
        time.sleep(config.RATE_LIMIT_DELAY)

        headers = self.session.headers.copy()
        if host_override:
            headers["Host"] = host_override

        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        return response

    def get_cik_for_ticker(self, ticker: str) -> Optional[str]:
        """Resolves a Ticker (e.g., AAPL) to a CIK (e.g., 0000320193) which is used for fetching 10-K reports."""
        if not self._ticker_map:
            # Lazy load the ticker map only when needed
            print("Fetching company CIK map from SEC...")
            url = "https://www.sec.gov/files/company_tickers.json"
            data = self._get(url, host_override="www.sec.gov").json()

            for entry in data.values():
                # .zfill(10) to zero-pad the CIK to 10 digits (JSON provides it as int)
                self._ticker_map[entry["ticker"]] = str(entry["cik_str"]).zfill(10)

        return self._ticker_map.get(ticker.upper())

    def get_latest_10k_report(self, cik: str) -> Optional[Dict]:
        """Fetches submission history and finds the latest 10-K URL."""
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"

        try:
            data = self._get(url).json()

            filings = data.get("filings", {}).get("recent", {})

            if not filings:
                return None

            # Iterate to find the latest "10-K"
            forms = filings.get("form", [])
            for i, form in enumerate(forms):
                if form == "10-K":

                    accession = filings["accessionNumber"][i]
                    primary_doc = filings["primaryDocument"][i]
                    filing_date = filings["filingDate"][i]

                    # Construct URL
                    clean_accession = accession.replace("-", "")
                    doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{clean_accession}/{primary_doc}"

                    return {"cik": cik, "filing_date": filing_date, "url": doc_url}
            return None

        except requests.RequestException as e:
            print(f"API Error for CIK {cik}: {e}")
            return None

    def download_html(self, url: str) -> str:
        """Downloads raw HTML content from the given URL."""
        return self._get(url, host_override="www.sec.gov").text
