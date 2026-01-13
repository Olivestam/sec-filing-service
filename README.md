# SEC Filing Service

A data extraction service that fetches the latest 10-K Annual Reports from the SEC EDGAR API and converts them to PDF.

## Prerequisites

- Python 3.8+
- Pip

## Installation

1. **Clone the repository**

   ```bash
   git clone <YOUR_REPO_LINK>
   cd sec-filing-service
   ```

2. **Set up a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Browser Engine**
   This service uses Playwright for PDF generation. You need to install the Chromium binary:

   ```bash
   playwright install chromium
   ```

## Run

Run the main entry point:

```bash
python main.py
```
