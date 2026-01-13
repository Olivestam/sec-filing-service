# --- User-Agent ---
SEC_USER_AGENT = "Anton's Service anton.olivestam@gmail.com"

# --- APP SETTINGS ---
OUTPUT_DIR = "data/10k_reports"
MANIFEST_FILE = "filings_manifest.json"

# SEC rate limit is 10 req/sec. We use 0.15s sleep to be safe (~6-7 req/sec).
RATE_LIMIT_DELAY = 0.15