import os
import json
from .sec_client import SecClient
from .converter import HtmlToPdfConverter
import config


class FilingService:
    def __init__(self):
        self.client = SecClient()
        self.converter = HtmlToPdfConverter()

    def fetch_10k_reports(self, tickers: list):
        """
        Main workflow: Resolve CIK -> Fetch Metadata -> Download -> Convert -> Report
        """
        results = []

        print(f"Starting job for tickers: {tickers}")

        for ticker in tickers:
            print(f"\nProcessing {ticker}...")

            # 1. Resolve CIK
            cik = self.client.get_cik_for_ticker(ticker)
            if not cik:
                print(f"Skipping {ticker}: CIK not found.")
                continue

            # 2. Get Metadata
            metadata = self.client.get_latest_10k_report(cik)
            if not metadata:
                print(f"Skipping {ticker}: No 10-K found.")
                continue

            # 3. Define Paths
            filename = f"{ticker}_10K_{metadata['filing_date']}.pdf"
            output_path = os.path.join(config.OUTPUT_DIR, filename)

            # 4. Download HTML
            html_content = self.client.download_html(metadata["url"])

            # 5. Convert
            success = self.converter.convert(html_content, metadata["url"], output_path)

            if success:
                print(f"SUCCESS: Saved to {output_path}")
                results.append(
                    {
                        "ticker": ticker,
                        "cik": cik,
                        "filing_date": metadata["filing_date"],
                        "local_path": output_path,
                        "source_url": metadata["url"],
                    }
                )
            else:
                print(f"FAILED: Could not convert {ticker}")

        self._save_manifest(results)
        return results

    def _save_manifest(self, data):
        """Exposes the processing results as a JSON manifest."""
        manifest_path = os.path.join(config.OUTPUT_DIR, config.MANIFEST_FILE)
        with open(manifest_path, "w") as f:
            json.dump(data, f, indent=2)
