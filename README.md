# 🛒 MDComputers Product Scraper

A production-ready Python web scraper that extracts product information from the **MDComputers** website based on a search query and exports the results into a structured CSV file.

Built as part of the **AffinityAnswers Full Stack Development Internship Assessment**, this project emphasizes clean architecture, robust error handling, logging, and maintainable code.

---

## 🚀 Features

- 🔍 Search products using any keyword
- 📦 Extract product name
- 💰 Extract product price
- ✅ Detect stock availability
- 🔗 Capture product URL
- 📄 Export data to CSV
- 📝 Detailed logging
- ⚡ Command-line interface (CLI)
- 🔄 Retry mechanism for network failures
- 🛡️ Graceful exception handling
- 🧹 Clean, modular, and readable code

---

## 📸 Demo

### Scraper Execution

![Scraper Demo](screenshots/scraper_demo.png)

---

## 📂 Project Structure

```
mdcomputers-product-scraper/
│
├── output/
│   └── .gitkeep
│
├── screenshots/
│   └── scraper_demo.png
│
├── scraper.py
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.11 | Programming Language |
| Requests | HTTP Requests |
| BeautifulSoup4 | HTML Parsing |
| CSV | Data Export |
| argparse | Command Line Interface |
| Logging | Execution Logs |
| Git & GitHub | Version Control |

---

## 📥 Installation

Clone the repository

```bash
git clone https://github.com/Abhyudai-ajax/mdcomputers-product-scraper.git

cd mdcomputers-product-scraper
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the scraper by providing a search term.

```bash
python scraper.py "external harddrive"
```

Example

```bash
python scraper.py "mouse"
```

```bash
python scraper.py "graphics card"
```

---

## 📤 Output

The scraper exports all extracted products to

```
output/products.csv
```

Each record contains:

| Field | Description |
|--------|-------------|
| Product Name | Name of the Product |
| Price | Product Price |
| Stock Status | In Stock / Out of Stock |
| Product URL | Direct Product Link |

---

## 🖥️ Sample Console Output

```
================================================================================
SCRAPING SUMMARY - Found 20 Products
================================================================================

1. Seagate Expansion 1TB External Hard Drive
   Price: ₹9,140
   Stock: In Stock
   URL: https://mdcomputers.in/...

2. Western Digital Elements 1TB External Hard Drive
   Price: ₹9,299
   Stock: In Stock
   URL: https://mdcomputers.in/...

...

✅ All 20 products exported to output/products.csv
```

---

## ⚙️ Key Engineering Practices

- Modular code structure
- Type hints
- Structured logging
- Exception handling
- Retry mechanism for failed requests
- Configurable CLI arguments
- UTF-8 CSV export
- PEP 8 compliant code
- Easily extendable architecture

---

## 🔄 Workflow

```
User Input
     │
     ▼
Build Search URL
     │
     ▼
Send HTTP Request
     │
     ▼
Parse HTML using BeautifulSoup
     │
     ▼
Extract Product Details
     │
     ▼
Store in Python Objects
     │
     ▼
Export to CSV
```

---

## 📋 Requirements

- Python 3.11+
- Internet Connection

Install all dependencies

```bash
pip install -r requirements.txt
```

---

## 📌 Future Improvements

- Multi-page scraping
- Concurrent requests for faster execution
- Export to Excel and JSON
- Product image extraction
- Price history tracking
- Scheduled scraping
- Web dashboard using Flask/FastAPI

---

## 👨‍💻 Author

**Abhyudai Tiwari**

Third Year CSE Student  
IIIT Kottayam

GitHub

https://github.com/Abhyudai-ajax

Portfolio

https://abhyudai-dev.vercel.app

---

## ⭐ Repository

If you found this project useful, consider giving it a ⭐ on GitHub.

---

## 📄 License

This project is licensed under the MIT License.