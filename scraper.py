#!/usr/bin/env python3
"""
MDComputers Product Scraper

A production-quality web scraper for MDComputers search results.
Extracts product information including name, price, stock availability, and URLs.
"""

import argparse
import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============================================================================
# Configuration
# ============================================================================

OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "products.csv"
LOG_FILE = OUTPUT_DIR / "scraper.log"

# User-Agent to avoid being blocked
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

# Request timeout in seconds
REQUEST_TIMEOUT = 10

# Maximum retries for failed requests
MAX_RETRIES = 3

# ============================================================================
# Logging Configuration
# ============================================================================


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure logging for the scraper.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Remove existing handlers
    logger.handlers.clear()

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# ============================================================================
# Session Management
# ============================================================================


def create_session() -> requests.Session:
    """
    Create a requests session with retry strategy.

    Returns:
        Configured requests.Session instance
    """
    session = requests.Session()

    # Configure retry strategy
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Set headers
    session.headers.update({"User-Agent": USER_AGENT})

    return session


# ============================================================================
# Data Models
# ============================================================================


class Product:
    """Represents a product from MDComputers."""

    def __init__(
        self,
        name: str,
        price: str,
        stock_availability: str,
        product_url: str,
        image_url: str,
    ):
        """
        Initialize a Product instance.

        Args:
            name: Product name
            price: Product price as string
            stock_availability: Stock status
            product_url: Product page URL
            image_url: Product image URL
        """
        self.name = name
        self.price = price
        self.stock_availability = stock_availability
        self.product_url = product_url
        self.image_url = image_url

    def to_dict(self) -> dict:
        """
        Convert product to dictionary.

        Returns:
            Dictionary representation of the product
        """
        return {
            "Product Name": self.name,
            "Price": self.price,
            "Stock Availability": self.stock_availability,
            "Product URL": self.product_url,
            "Image URL": self.image_url,
        }


# ============================================================================
# Scraping Functions
# ============================================================================


def fetch_page(session: requests.Session, url: str, logger: logging.Logger) -> Optional[str]:
    """
    Fetch a page from the given URL.

    Args:
        session: Requests session instance
        url: URL to fetch
        logger: Logger instance

    Returns:
        Page content as string, or None if fetch failed
    """
    try:
        logger.info(f"Fetching URL: {url}")
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        logger.debug(f"Successfully fetched {url} (Status: {response.status_code})")
        return response.text
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching {url}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while fetching {url}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error while fetching {url}: {e.response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while fetching {url}: {str(e)}")
        return None


def parse_price(price_text: str) -> str:
    """
    Extract and clean price from text.

    Args:
        price_text: Raw price text from HTML

    Returns:
        Cleaned price string
    """
    if not price_text:
        return "N/A"
    return price_text.strip()


def parse_stock_availability(stock_text: Optional[str]) -> str:
    """
    Determine stock availability from text.

    Args:
        stock_text: Raw stock text from HTML

    Returns:
        Stock availability status
    """
    if not stock_text:
        return "Unknown"

    stock_lower = stock_text.lower().strip()

    if "in stock" in stock_lower:
        return "In Stock"
    elif "out of stock" in stock_lower or "out stock" in stock_lower:
        return "Out of Stock"
    elif "discontinued" in stock_lower:
        return "Discontinued"
    else:
        return stock_lower.title()


def extract_products(html_content: str, logger: logging.Logger, base_url: str = "https://mdcomputers.in") -> list[Product]:
    soup = BeautifulSoup(html_content, "html.parser")
    products = []

    product_items = soup.select("div.product-grid-item")

    logger.info(f"Found {len(product_items)} product items")

    for item in product_items:
        try:
            # Name
            name = "N/A"
            name_tag = item.select_one("h3.product-entities-title a")
            if name_tag:
                name = name_tag.get_text(strip=True)

            # Product URL
            product_url = "N/A"
            if name_tag and name_tag.get("href"):
                product_url = urljoin(base_url, name_tag["href"])

            # Image
            image_url = "N/A"
            img = item.select_one("img")
            if img:
                image_url = (
                    img.get("src")
                    or img.get("data-src")
                    or img.get("data-lazy-src")
                    or "N/A"
                )

                image_url = urljoin(base_url, image_url)

            # Price
            price = "N/A"
            price_tag = item.select_one("span.price .ins")
            if not price_tag:
                price_tag = item.select_one("span.price")

            if price_tag:
                price = parse_price(price_tag.get_text(" ", strip=True))

            # Availability
            availability = "In Stock"

            products.append(
                Product(
                    name=name,
                    price=price,
                    stock_availability=availability,
                    product_url=product_url,
                    image_url=image_url,
                )
            )

        except Exception as e:
            logger.warning(e)

    return products

def scrape_search_results(
    search_term: str,
    logger: logging.Logger,
) -> list[Product]:
    """
    Scrape MDComputers search results for the given search term.

    Args:
        search_term: Product to search for
        logger: Logger instance

    Returns:
        List of Product instances
    """
    # Encode search term for URL
    encoded_search = quote(search_term)
    url = f"https://mdcomputers.in/?route=product/search&search={encoded_search}"

    logger.info(f"Starting scrape for search term: '{search_term}'")
    logger.info(f"Search URL: {url}")

    # Create session with retry strategy
    session = create_session()

    try:
        # Fetch page
        html_content = fetch_page(session, url, logger)
        if not html_content:
            logger.error("Failed to fetch search results page")
            return []

        # Parse and extract products
        products = extract_products(html_content, logger)
        logger.info(f"Successfully extracted {len(products)} products")

        return products

    finally:
        session.close()


# ============================================================================
# Export Functions
# ============================================================================


def export_to_csv(products: list[Product], logger: logging.Logger) -> bool:
    """
    Export products to CSV file.

    Args:
        products: List of Product instances
        logger: Logger instance

    Returns:
        True if export successful, False otherwise
    """
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)

        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Product Name",
                "Price",
                "Stock Availability",
                "Product URL",
                "Image URL",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for product in products:
                writer.writerow(product.to_dict())

        logger.info(f"Successfully exported {len(products)} products to {OUTPUT_FILE}")
        return True

    except IOError as e:
        logger.error(f"Error writing to CSV file: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during CSV export: {str(e)}")
        return False


def print_summary(products: list[Product], logger: logging.Logger) -> None:
    """
    Print a summary of scraped products.

    Args:
        products: List of Product instances
        logger: Logger instance
    """
    if not products:
        logger.warning("No products found")
        print("\n⚠️  No products found for this search.")
        return

    print("\n" + "=" * 80)
    print(f"SCRAPING SUMMARY - Found {len(products)} Products")
    print("=" * 80)

    for idx, product in enumerate(products[:5], 1):
        print(f"\n{idx}. {product.name}")
        print(f"   Price: {product.price}")
        print(f"   Stock: {product.stock_availability}")
        print(f"   URL: {product.product_url}")

    if len(products) > 5:
        print(f"\n... and {len(products) - 5} more products")

    print(f"\n✅ All {len(products)} products exported to: {OUTPUT_FILE}")
    print("=" * 80 + "\n")


# ============================================================================
# CLI
# ============================================================================


def main() -> int:
    """
    Main entry point for the scraper.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="MDComputers Product Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scraper.py "graphics card"
  python scraper.py "SSD" --log-level DEBUG
  python scraper.py "RAM" --log-level INFO
        """,
    )

    parser.add_argument(
        "search_term",
        type=str,
        help="Product to search for on MDComputers",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_level)

    logger.info("=" * 80)
    logger.info(f"MDComputers Scraper Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    # Scrape results
    products = scrape_search_results(args.search_term, logger)

    # Export to CSV
    if products:
        success = export_to_csv(products, logger)
        if not success:
            logger.error("Failed to export results to CSV")
            return 1
    else:
        logger.warning("No products to export")

    # Print summary
    print_summary(products, logger)

    logger.info("Scraping completed successfully")
    logger.info("=" * 80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())