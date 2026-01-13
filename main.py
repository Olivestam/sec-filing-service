from src.service import FilingService


def main():
    # The list of companies required by the assignment
    companies = ["AAPL", "META", "GOOGL", "AMZN", "NFLX", "GS"]

    service = FilingService()
    service.fetch_10k_reports(companies)


if __name__ == "__main__":
    main()
