"""
Government Circulars & Notifications Scraper — with PDF Download
Targets: CLC (min wages), ESIC (circulars), EPFO (circulars)

Install dependencies first:
    pip install requests beautifulsoup4 lxml pandas openpyxl
    pip install selenium webdriver-manager   # only needed for EPFO

Folder structure created on run:
    govt_circulars/
    ├── CLC/        ← PDFs from CLC
    ├── ESIC/       ← PDFs from ESIC
    ├── EPFO/       ← PDFs from EPFO
    └── govt_circulars_YYYYMMDD_HHMM.xlsx   ← index with all metadata + local paths
"""

import os
import re
import time
import logging
import urllib3
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

OUTPUT_DIR = Path("govt_circulars")      # root output folder
DELAY_BETWEEN_DOWNLOADS = 1.0            # seconds between downloads (be polite to servers)
MAX_PDFS_PER_SOURCE = 200               # safety cap — set None for unlimited


# ─── PDF Download Helpers ─────────────────────────────────────────────────────

def make_safe_filename(title: str, url: str, ext: str = ".pdf") -> str:
    """Create a filesystem-safe filename from the circular title."""
    name = title if len(title) > 8 else urlparse(url).path.split("/")[-1]
    name = re.sub(r'[\\/*?:"<>|]', "_", name)  # strip illegal chars
    name = re.sub(r"\s+", "_", name.strip())
    name = name[:120]                            # cap length
    if not name.lower().endswith(ext):
        name += ext
    return name


def download_pdf(url: str, dest_folder: Path, filename: str,
                 verify_ssl: bool = True) -> str:
    """
    Download a single PDF file.
    Returns local path on success, empty string on failure.
    Skips if file already exists (resume-safe).
    """
    dest_folder.mkdir(parents=True, exist_ok=True)
    dest_path = dest_folder / filename

    if dest_path.exists():
        log.info("  [skip] already exists: %s", filename)
        return str(dest_path)

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30,
                            stream=True, verify=verify_ssl)
        resp.raise_for_status()

        # confirm it's actually a PDF
        content_type = resp.headers.get("Content-Type", "")
        if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
            log.warning("  [skip] not a PDF (Content-Type=%s): %s", content_type, url)
            return ""

        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        size_kb = dest_path.stat().st_size // 1024
        log.info("  [ok] %s (%d KB)", filename, size_kb)
        return str(dest_path)

    except Exception as e:
        log.warning("  [fail] %s — %s", url, e)
        return ""


def download_all_pdfs(records: list, folder: Path,
                      verify_ssl: bool = True) -> list:
    """
    Download PDFs for a list of record dicts (must have 'title' and 'url').
    Adds/updates 'local_path' key in each record in-place.
    Respects MAX_PDFS_PER_SOURCE cap.
    """
    cap = MAX_PDFS_PER_SOURCE
    to_download = records[:cap] if cap else records
    total = len(to_download)

    for i, rec in enumerate(to_download, 1):
        url = rec.get("url", "")
        if not url or ".pdf" not in url.lower():
            rec.setdefault("local_path", "")
            continue
        log.info("Downloading %d/%d: %s", i, total, url)
        filename = make_safe_filename(rec.get("title", ""), url)
        rec["local_path"] = download_pdf(url, folder, filename, verify_ssl=verify_ssl)
        time.sleep(DELAY_BETWEEN_DOWNLOADS)

    for rec in records[cap or len(records):]:
        rec.setdefault("local_path", "")

    return records


# ─────────────────────────────────────────────
# 1. CLC — Minimum Wages Notifications
# ─────────────────────────────────────────────

def scrape_clc(download_pdfs: bool = True) -> pd.DataFrame:
    """
    Scrapes the CLC minimum wages table and downloads linked PDFs.
    Each table row may contain an anchor tag pointing to a PDF.
    """
    url = "https://clc.gov.in/clc/min-wages"
    log.info("Scraping CLC: %s", url)

    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # ── DEBUG: uncomment to inspect raw HTML structure ──
    # print(soup.find("table"))

    rows, headers_found, pdf_urls = [], [], []

    table = soup.find("table")
    if not table:
        log.warning("CLC: No <table> found — check live page structure.")
        return pd.DataFrame()

    for i, tr in enumerate(table.find_all("tr")):
        cells = [td.get_text(separator=" ", strip=True)
                 for td in tr.find_all(["th", "td"])]
        if not cells:
            continue
        if i == 0:
            headers_found = cells
            continue
        rows.append(cells)

        # pick first PDF link in this row (if any)
        pdf_in_row = ""
        for a in tr.find_all("a", href=True):
            href = a["href"].strip()
            if ".pdf" in href.lower():
                pdf_in_row = href if href.startswith("http") else urljoin(url, href)
                break
        pdf_urls.append(pdf_in_row)

    df = pd.DataFrame(rows, columns=headers_found if headers_found else None)
    df["pdf_url"] = pdf_urls
    df["source"] = "CLC"
    df["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    df["local_path"] = ""

    if download_pdfs:
        records = [
            {"title": str(df.iloc[i, 0]) if headers_found else f"clc_row_{i}",
             "url": df.at[i, "pdf_url"]}
            for i in range(len(df))
            if df.at[i, "pdf_url"]
        ]
        download_all_pdfs(records, OUTPUT_DIR / "CLC")
        path_map = {r["url"]: r["local_path"] for r in records}
        df["local_path"] = df["pdf_url"].map(path_map).fillna("")

    log.info("CLC: %d rows, %d PDFs linked, %d downloaded",
             len(df), df["pdf_url"].astype(bool).sum(),
             df["local_path"].astype(bool).sum())
    return df


# ─────────────────────────────────────────────
# 2. ESIC — Circulars
# ─────────────────────────────────────────────

def scrape_esic(download_pdfs: bool = True) -> pd.DataFrame:
    """
    Scrapes ESIC circulars listing and downloads PDFs.
    """
    url = "https://esic.gov.in/circulars"
    log.info("Scraping ESIC: %s", url)

    resp = requests.get(url, headers=HEADERS, timeout=20, verify=False)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # try known Drupal/CMS container classes first, fall back to <main>/<body>
    container = (
        soup.find("div", class_="view-content")
        or soup.find("div", class_="field-items")
        or soup.find("main")
        or soup.find("body")
    )

    records = []
    seen_urls = set()
    for link in container.find_all("a", href=True):
        title = link.get_text(separator=" ", strip=True)
        href = link["href"].strip()

        if not title:
            continue
        if not any(kw in href.lower()
                   for kw in [".pdf", "circular", "notification", "order"]):
            continue

        if href.startswith("/"):
            href = "https://esic.gov.in" + href
        elif not href.startswith("http"):
            href = "https://esic.gov.in/" + href

        if href in seen_urls:
            continue
        seen_urls.add(href)

        records.append({
            "title": title,
            "url": href,
            "source": "ESIC",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "local_path": "",
        })

    if download_pdfs:
        pdf_records = [r for r in records if ".pdf" in r["url"].lower()]
        download_all_pdfs(pdf_records, OUTPUT_DIR / "ESIC", verify_ssl=False)

    df = pd.DataFrame(records)
    log.info("ESIC: %d circulars, %d downloaded",
             len(df), df["local_path"].astype(bool).sum() if not df.empty else 0)
    return df


# ─────────────────────────────────────────────
# 3. EPFO — Circulars (JS-heavy site)
# ─────────────────────────────────────────────

def _parse_epfo_links(soup: BeautifulSoup, base_url: str) -> list:
    seen, records = set(), []
    for link in soup.find_all("a", href=True):
        title = link.get_text(separator=" ", strip=True)
        href = link["href"].strip()

        if not title or len(title) < 5:
            continue
        if not any(kw in href.lower()
                   for kw in [".pdf", "circular", "notification"]):
            continue

        if href.startswith("/"):
            href = "https://www.epfo.gov.in" + href
        elif not href.startswith("http"):
            href = urljoin(base_url, href)

        if href in seen:
            continue
        seen.add(href)

        records.append({
            "title": title,
            "url": href,
            "source": "EPFO",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "local_path": "",
        })
    return records


def scrape_epfo_requests(download_pdfs: bool = True) -> pd.DataFrame:
    """Attempt 1 — plain requests. Fast; works if EPFO page is server-rendered."""
    url = "https://www.epfo.gov.in/circulars/"
    log.info("Scraping EPFO (requests): %s", url)

    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    records = _parse_epfo_links(soup, url)

    if download_pdfs and records:
        pdf_records = [r for r in records if ".pdf" in r["url"].lower()]
        download_all_pdfs(pdf_records, OUTPUT_DIR / "EPFO")

    df = pd.DataFrame(records)
    log.info("EPFO (requests): %d circulars, %d downloaded",
             len(df), df["local_path"].astype(bool).sum() if not df.empty else 0)
    return df


def scrape_epfo_selenium(download_pdfs: bool = True) -> pd.DataFrame:
    """Attempt 2 — headless Chrome via Selenium. Use when requests returns empty."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        log.error("Selenium not installed. Run: pip install selenium webdriver-manager")
        return pd.DataFrame()

    url = "https://www.epfo.gov.in/circulars/"
    log.info("Scraping EPFO (Selenium): %s", url)

    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"user-agent={HEADERS['User-Agent']}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=opts
    )
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )
        time.sleep(2)   # let lazy-loaded content settle
        soup = BeautifulSoup(driver.page_source, "lxml")
    finally:
        driver.quit()

    records = _parse_epfo_links(soup, url)

    if download_pdfs and records:
        pdf_records = [r for r in records if ".pdf" in r["url"].lower()]
        download_all_pdfs(pdf_records, OUTPUT_DIR / "EPFO")

    df = pd.DataFrame(records)
    log.info("EPFO (Selenium): %d circulars, %d downloaded",
             len(df), df["local_path"].astype(bool).sum() if not df.empty else 0)
    return df


# ─────────────────────────────────────────────
# 4. Main runner
# ─────────────────────────────────────────────

def run_all(
    download_pdfs: bool = True,
    use_selenium_for_epfo: bool = False,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    try:
        results["CLC_MinWages"] = scrape_clc(download_pdfs=download_pdfs)
    except Exception as e:
        log.error("CLC failed: %s", e)

    try:
        results["ESIC_Circulars"] = scrape_esic(download_pdfs=download_pdfs)
    except Exception as e:
        log.error("ESIC failed: %s", e)

    try:
        if use_selenium_for_epfo:
            results["EPFO_Circulars"] = scrape_epfo_selenium(download_pdfs=download_pdfs)
        else:
            df_epfo = scrape_epfo_requests(download_pdfs=download_pdfs)
            if df_epfo.empty:
                log.info("EPFO requests empty — falling back to Selenium...")
                results["EPFO_Circulars"] = scrape_epfo_selenium(download_pdfs=download_pdfs)
            else:
                results["EPFO_Circulars"] = df_epfo
    except Exception as e:
        log.error("EPFO failed: %s", e)

    if not results:
        log.error("No data collected.")
        return

    # Save Excel index (one sheet per source)
    fname = OUTPUT_DIR / f"govt_circulars_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    with pd.ExcelWriter(fname, engine="openpyxl") as writer:
        for sheet_name, df in results.items():
            if df is not None and not df.empty:
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                downloaded = (df["local_path"].astype(bool).sum()
                              if "local_path" in df.columns else 0)
                log.info("  Sheet '%s': %d rows, %d PDFs saved",
                         sheet_name, len(df), downloaded)

    log.info("Excel index: %s", fname)
    log.info("PDF folder:  %s/", OUTPUT_DIR)
    log.info("")
    log.info("Folder layout:")
    log.info("  govt_circulars/CLC/   ← CLC PDFs")
    log.info("  govt_circulars/ESIC/  ← ESIC PDFs")
    log.info("  govt_circulars/EPFO/  ← EPFO PDFs")


if __name__ == "__main__":
    run_all(
        download_pdfs=True,           # False → only collect metadata, skip downloads
        use_selenium_for_epfo=False,  # True  → force Selenium for EPFO
    )
