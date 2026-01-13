from playwright.sync_api import sync_playwright
import os
import requests
import config


class HtmlToPdfConverter:
    def convert(self, html_content: str, source_url: str, output_path: str) -> bool:
        """
        Converts HTML to PDF. Uses Request Interception to safely download images
        through the authenticated Python session, bypassing browser blocks.
        """
        try:
            print(f"Converting to PDF: {output_path}")

            # Remove file name from to get base URL for relative paths
            base_url = source_url.rsplit("/", 1)[0] + "/"

            # Inject <base> tag to fix relative URLs in HTML content
            if "<head>" in html_content:
                html_content = html_content.replace(
                    "<head>", f'<head><base href="{base_url}">'
                )
            else:
                html_content = f'<base href="{base_url}">' + html_content

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Use Playwright to render and convert to PDF
            with sync_playwright() as p:

                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                def handle_route(route):
                    """
                    This function runs for EVERY network request the browser makes (images, css)
                    We do this since SEC blocks direct browser requests without proper User-Agent
                    """
                    try:
                        # Add custom headers to requests for SEC compliance
                        headers = {
                            "User-Agent": config.SEC_USER_AGENT,
                            "Accept-Encoding": "gzip, deflate",
                        }

                        resp = requests.get(
                            route.request.url, headers=headers, timeout=10
                        )

                        # Feed the data back to the browser
                        route.fulfill(
                            status=resp.status_code,
                            body=resp.content,
                            headers=resp.headers,
                        )
                    except Exception as e:
                        print(f"Failed to fetch resource {route.request.url}: {e}")
                        route.continue_()

                # handle_route will be called for each request in HTML content (e.g., images)
                page.route("**/*", handle_route)

                # Load content and wait for the network to settle
                page.set_content(html_content, wait_until="networkidle")

                page.pdf(
                    path=output_path,
                    format="Letter",
                    margin={
                        "top": "1cm",
                        "right": "1cm",
                        "bottom": "1cm",
                        "left": "1cm",
                    },
                    print_background=True,
                )

                browser.close()

            return True

        except Exception as e:
            print(f"Conversion Error: {e}")
            return False
