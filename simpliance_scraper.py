"""
Simpliance Labour Law Compiler — Full Scraper
=============================================
Website  : https://www.simpliance.in/India/LEI/
Scrapes  : Acts, Rules, Schemes, Regulations, Gazette Notifications,
           Circulars, Labour Welfare Fund, Leaves & Working Hours,
           Holidays, NFH Details, Professional Tax, Labour Codes

Output root : E:\\AICA 2\\LABOUR LAW COMPILER\\
Folder map  :
    acts                  -> acts\\
    labour_codes          -> acts\\labour_codes\\
    rules                 -> rules\\
    gazette_notifications -> notifications\\
    circulars             -> circulars\\
    schemes / regulations -> database\\
    labour_welfare_fund   -> forms\\
    holidays / nfh / pt   -> database\\
    judgments             -> judgments\\
    summaries             -> summaries\\
    faq                   -> faq\\

Install (run once):
    pip install requests beautifulsoup4 lxml pandas openpyxl
    pip install selenium webdriver-manager
"""

import os
import re
import sys
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

# ─── Logging — writes to console AND simpliance_scraper.log ──────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("simpliance_scraper.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
#  ★ CONFIG — edit this section only
# ═══════════════════════════════════════════════════════════════════════════════

BASE_URL    = "https://www.simpliance.in"
BASE_PATH   = "/India/LEI"

# Root output directory (Windows path)
OUTPUT_ROOT = Path(r"E:\AICA 2\LABOUR LAW COMPILER")

# Category slug  →  subfolder under OUTPUT_ROOT
FOLDER_MAP = {
    "acts"                  : "acts",
    "labour_codes"          : r"acts\labour_codes",
    "rules"                 : "rules",
    "schemes"               : "database",
    "regulations"           : "database",
    "gazette_notifications" : "notifications",
    "circulars"             : "circulars",
    "labour_welfare_fund"   : "forms",
    "leaves_working_hours"  : "rules",
    "holidays"              : "database",
    "nfh_details"           : "database",
    "professional_tax"      : "database",
    "judgments"             : "judgments",
    "summaries"             : "summaries",
    "faq"                   : "faq",
}

# Simpliance URL path for each category
CATEGORY_URLS = {
    "acts"                  : f"{BASE_PATH}/acts",
    "labour_codes"          : f"{BASE_PATH}/labour-codes",
    "rules"                 : f"{BASE_PATH}/rules",
    "schemes"               : f"{BASE_PATH}/schemes",
    "regulations"           : f"{BASE_PATH}/regulations",
    "gazette_notifications" : f"{BASE_PATH}/gazette-notifications",
    "circulars"             : f"{BASE_PATH}/circulars",
    "labour_welfare_fund"   : f"{BASE_PATH}/labour-welfare-fund",
    "leaves_working_hours"  : f"{BASE_PATH}/leaves-and-working-hours",
    "holidays"              : f"{BASE_PATH}/holidays",
    "nfh_details"           : f"{BASE_PATH}/nfh-details",
    "professional_tax"      : f"{BASE_PATH}/professional-tax",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.simpliance.in/",
}

DELAY_BETWEEN_PAGES     = 2.0    # polite crawl delay between listing pages
DELAY_BETWEEN_DOWNLOADS = 1.0    # polite delay between file downloads
DELAY_BETWEEN_DETAILS   = 1.5    # delay when visiting individual detail pages
MAX_FILES_PER_CATEGORY  = None   # set to e.g. 5 for a test run; None = unlimited
REQUEST_TIMEOUT         = 30     # HTTP timeout in seconds
MAX_PAGES_PER_CATEGORY  = 300    # safety ceiling on pagination

PDF_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".zip", ".doc"}


# ═══════════════════════════════════════════════════════════════════════════════
#  UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def make_safe_filename(title: str, url: str, default_ext: str = ".pdf") -> str:
    """Return a Windows-safe filename derived from title + URL."""
    name = title.strip() if len(title.strip()) > 6 else ""
    if not name:
        name = urlparse(url).path.rstrip("/").split("/")[-1]
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = re.sub(r"\s+", "_", name).strip("._")[:150]

    _, url_ext = os.path.splitext(urlparse(url).path)
    ext = url_ext.lower() if url_ext.lower() in PDF_EXTENSIONS else default_ext
    if not name.lower().endswith(ext):
        name += ext
    return name


def download_file(url: str, dest_path: Path, verify_ssl: bool = True) -> bool:
    """Stream-download a file. Returns True on success. Skips if already exists."""
    if dest_path.exists() and dest_path.stat().st_size > 0:
        log.info("    [skip] already exists: %s", dest_path.name)
        return True

    dest_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT,
                            stream=True, verify=verify_ssl, allow_redirects=True)
        resp.raise_for_status()

        ct = resp.headers.get("Content-Type", "").lower()
        ok_ct = ("pdf", "msword", "officedocument", "zip", "octet-stream",
                 "force-download", "binary")
        _, url_ext = os.path.splitext(urlparse(url).path)
        if not any(t in ct for t in ok_ct) and url_ext.lower() not in PDF_EXTENSIONS:
            log.warning("    [skip] unexpected content-type=%s  url=%s", ct, url)
            return False

        with open(dest_path, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=16384):
                if chunk:
                    fh.write(chunk)

        size_kb = dest_path.stat().st_size // 1024
        log.info("    [ok] %-65s %d KB", dest_path.name[:65], size_kb)
        return True

    except Exception as exc:
        log.warning("    [fail] %s — %s", url, exc)
        if dest_path.exists():
            dest_path.unlink()
        return False


# ─── HTTP fetchers ────────────────────────────────────────────────────────────

def get_soup(url: str, verify_ssl: bool = True,
             extra_headers: dict | None = None) -> BeautifulSoup | None:
    try:
        h = {**HEADERS, **(extra_headers or {})}
        resp = requests.get(url, headers=h, timeout=REQUEST_TIMEOUT, verify=verify_ssl)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
    except Exception as exc:
        log.error("  [fetch error] %s — %s", url, exc)
        return None


def get_soup_selenium(url: str) -> BeautifulSoup | None:
    """Render JS-heavy page with headless Chrome."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        log.warning("Selenium not installed — using plain requests for %s", url)
        return get_soup(url)

    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument(f"user-agent={HEADERS['User-Agent']}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=opts
    )
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)   # let React/Angular finish rendering
        return BeautifulSoup(driver.page_source, "lxml")
    except Exception as exc:
        log.error("  [selenium error] %s — %s", url, exc)
        return None
    finally:
        driver.quit()


def fetch_soup(url: str, use_selenium: bool = True) -> BeautifulSoup | None:
    """Choose fetcher based on flag."""
    return get_soup_selenium(url) if use_selenium else get_soup(url)


# ═══════════════════════════════════════════════════════════════════════════════
#  LINK EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

def extract_links_from_page(soup: BeautifulSoup,
                             page_url: str) -> list[dict]:
    """
    Extract all document and detail-page links from a Simpliance listing page.
    Returns list of {title, url, file_type}.
    """
    records = []
    seen    = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "javascript", "mailto", "tel")):
            continue

        full_url = href if href.startswith("http") else urljoin(BASE_URL, href)
        parsed   = urlparse(full_url)
        ext      = os.path.splitext(parsed.path)[-1].lower()
        title    = a.get_text(separator=" ", strip=True) or parsed.path.split("/")[-1]

        if full_url in seen:
            continue
        seen.add(full_url)

        # ── Direct file link ──────────────────────────────────────────────────
        if ext in PDF_EXTENSIONS:
            records.append({"title": title, "url": full_url,
                            "file_type": ext.lstrip(".")})

        # ── Simpliance detail page (/India/LEI/<cat>/<id or slug>) ────────────
        elif ("simpliance.in" in parsed.netloc and
              BASE_PATH in parsed.path and
              parsed.path.rstrip("/").count("/") >= 4 and
              parsed.path != urlparse(page_url).path):
            records.append({"title": title, "url": full_url,
                            "file_type": "detail_page"})

    return records


def extract_pdfs_from_detail_page(url: str,
                                   use_selenium: bool = True) -> list[dict]:
    """Visit a detail page and scrape the actual PDF download link(s)."""
    soup = fetch_soup(url, use_selenium)
    if not soup:
        return []

    results = []
    seen    = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href:
            continue
        full_url = href if href.startswith("http") else urljoin(BASE_URL, href)
        ext = os.path.splitext(urlparse(full_url).path)[-1].lower()
        if ext in PDF_EXTENSIONS and full_url not in seen:
            seen.add(full_url)
            title = a.get_text(separator=" ", strip=True) or "document"
            results.append({"title": title, "url": full_url,
                            "file_type": ext.lstrip(".")})

    # embedded PDF in <iframe>
    for iframe in soup.find_all("iframe", src=True):
        src = iframe["src"]
        if ".pdf" in src.lower():
            full_url = src if src.startswith("http") else urljoin(BASE_URL, src)
            if full_url not in seen:
                seen.add(full_url)
                results.append({"title": "embedded_pdf", "url": full_url,
                                "file_type": "pdf"})

    return results


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGINATION
# ═══════════════════════════════════════════════════════════════════════════════

def crawl_all_listing_pages(start_url: str,
                             use_selenium: bool = True) -> list[dict]:
    """
    Walk every listing page for a category.
    Returns all extracted link records across all pages.
    """
    all_records: list[dict] = []
    visited: set[str]       = set()
    url = start_url
    page_num = 1

    while url and page_num <= MAX_PAGES_PER_CATEGORY:
        if url in visited:
            break
        visited.add(url)

        log.info("  Page %d → %s", page_num, url)
        soup = fetch_soup(url, use_selenium)
        if not soup:
            break

        records = extract_links_from_page(soup, url)
        all_records.extend(records)
        log.info("    %d links on page %d (total so far: %d)",
                 len(records), page_num, len(all_records))

        time.sleep(DELAY_BETWEEN_PAGES)

        # ── find next-page link ───────────────────────────────────────────────
        next_a = (
            soup.find("a", string=re.compile(r"^\s*(next|›|»)\s*$", re.I))
            or soup.find("a", attrs={"aria-label": re.compile(r"next", re.I)})
        )
        if not next_a:
            # check <li class="next"> or <li class="page-item next">
            li = soup.find("li", class_=re.compile(r"\bnext\b", re.I))
            if li:
                next_a = li.find("a", href=True)

        if next_a and next_a.get("href"):
            href = next_a["href"].strip()
            next_url = href if href.startswith("http") else urljoin(BASE_URL, href)
            if next_url not in visited:
                url = next_url
                page_num += 1
                continue

        # ── try ?page=N fallback ──────────────────────────────────────────────
        sep      = "&" if "?" in start_url else "?"
        next_url = f"{start_url}{sep}page={page_num}"
        if next_url in visited:
            break
        test_soup = fetch_soup(next_url, use_selenium)
        if test_soup:
            test_records = extract_links_from_page(test_soup, next_url)
            if test_records:
                visited.add(next_url)
                all_records.extend(test_records)
                url = next_url
                page_num += 1
                time.sleep(DELAY_BETWEEN_PAGES)
                continue

        break   # no more pages found

    return all_records


# ═══════════════════════════════════════════════════════════════════════════════
#  CATEGORY SCRAPER
# ═══════════════════════════════════════════════════════════════════════════════

def scrape_category(
    category: str,
    use_selenium: bool = True,
    follow_detail_pages: bool = True,
    download_files: bool = True,
) -> pd.DataFrame:

    url_path = CATEGORY_URLS.get(category)
    if not url_path:
        log.warning("Unknown category: %s", category)
        return pd.DataFrame()

    start_url   = BASE_URL + url_path
    dest_folder = OUTPUT_ROOT / FOLDER_MAP.get(category, category)
    dest_folder.mkdir(parents=True, exist_ok=True)

    log.info("")
    log.info("═" * 72)
    log.info("  CATEGORY : %s", category.upper())
    log.info("  URL      : %s", start_url)
    log.info("  FOLDER   : %s", dest_folder)
    log.info("═" * 72)

    # ── Step 1: collect links from all listing pages ──────────────────────────
    raw_records = crawl_all_listing_pages(start_url, use_selenium)

    # deduplicate
    seen: set[str] = set()
    unique: list[dict] = []
    for r in raw_records:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)
    log.info("Unique links after dedup: %d", len(unique))

    # ── Step 2: resolve detail pages → actual file URLs ───────────────────────
    final_records: list[dict] = []
    detail_count = sum(1 for r in unique if r["file_type"] == "detail_page")
    resolved = 0

    for r in unique:
        if r["file_type"] == "detail_page" and follow_detail_pages:
            resolved += 1
            log.info("  Resolving detail %d/%d: %s",
                     resolved, detail_count, r["url"][:80])
            time.sleep(DELAY_BETWEEN_DETAILS)
            found = extract_pdfs_from_detail_page(r["url"], use_selenium)
            if found:
                for f in found:
                    f.setdefault("title", r["title"])
                    final_records.append(f)
            else:
                r["file_type"] = "no_pdf_found"
                final_records.append(r)
        else:
            final_records.append(r)

    log.info("File records to download: %d", len(final_records))

    # ── Step 3: download ──────────────────────────────────────────────────────
    cap         = MAX_FILES_PER_CATEGORY
    to_download = final_records[:cap] if cap else final_records

    for i, rec in enumerate(to_download, 1):
        rec["category"]   = category
        rec["local_path"] = ""
        rec["downloaded"] = False
        rec["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        url = rec.get("url", "")
        ft  = rec.get("file_type", "")

        if not url or ft in ("detail_page", "no_pdf_found"):
            continue
        if not download_files:
            continue

        log.info("  [%d/%d] %s", i, len(to_download), rec.get("title", "")[:80])
        fname     = make_safe_filename(rec.get("title", ""), url)
        dest_path = dest_folder / fname

        ok = download_file(url, dest_path)
        rec["local_path"] = str(dest_path) if ok else ""
        rec["downloaded"] = ok
        time.sleep(DELAY_BETWEEN_DOWNLOADS)

    # fill remaining records that exceeded the cap
    for rec in final_records[cap or len(final_records):]:
        rec.setdefault("category", category)
        rec.setdefault("local_path", "")
        rec.setdefault("downloaded", False)
        rec.setdefault("scraped_at", "")

    df = pd.DataFrame(final_records)
    downloaded = int(df["downloaded"].sum()) if "downloaded" in df.columns else 0
    log.info("Done '%s': %d records | %d downloaded | %d skipped/failed",
             category, len(df), downloaded, len(df) - downloaded)
    return df


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

CATEGORIES_TO_SCRAPE = [
    "acts",
    "labour_codes",
    "rules",
    "gazette_notifications",
    "circulars",
    "schemes",
    "regulations",
    "labour_welfare_fund",
    "leaves_working_hours",
    "holidays",
    "nfh_details",
    "professional_tax",
]


def run_all(
    categories: list[str] | None = None,
    use_selenium: bool = True,
    follow_detail_pages: bool = True,
    download_files: bool = True,
) -> None:
    cats = categories or CATEGORIES_TO_SCRAPE
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    # pre-create all subfolders
    for folder_name in set(FOLDER_MAP.values()):
        (OUTPUT_ROOT / folder_name).mkdir(parents=True, exist_ok=True)

    all_dfs  : dict[str, pd.DataFrame] = {}
    start_ts = datetime.now()

    for cat in cats:
        try:
            df = scrape_category(
                cat,
                use_selenium=use_selenium,
                follow_detail_pages=follow_detail_pages,
                download_files=download_files,
            )
            if not df.empty:
                all_dfs[cat] = df
        except Exception as exc:
            log.error("Category '%s' crashed: %s", cat, exc)

    # ── Save master Excel index ───────────────────────────────────────────────
    if all_dfs:
        ts         = start_ts.strftime("%Y%m%d_%H%M")
        excel_path = OUTPUT_ROOT / f"simpliance_index_{ts}.xlsx"

        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            # Summary tab
            summary = []
            for cat, df in all_dfs.items():
                dl = int(df["downloaded"].sum()) if "downloaded" in df.columns else 0
                summary.append({
                    "Category"      : cat,
                    "Folder"        : str(OUTPUT_ROOT / FOLDER_MAP.get(cat, cat)),
                    "Total Records" : len(df),
                    "Downloaded"    : dl,
                    "Failed/Skipped": len(df) - dl,
                })
            pd.DataFrame(summary).to_excel(writer, sheet_name="Summary", index=False)

            # One tab per category
            for cat, df in all_dfs.items():
                df.to_excel(writer, sheet_name=cat[:31], index=False)

        log.info("")
        log.info("━" * 72)
        log.info("  Excel index : %s", excel_path)
        log.info("  Files saved : %s", OUTPUT_ROOT)
        log.info("  Total time  : %d seconds", (datetime.now() - start_ts).seconds)
        log.info("━" * 72)


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    # ── TEST MODE — uncomment to download only 3 files from 'acts' first ──────
    # MAX_FILES_PER_CATEGORY = 3
    # scrape_category("acts", use_selenium=True, follow_detail_pages=True, download_files=True)
    # sys.exit()
    # ──────────────────────────────────────────────────────────────────────────

    run_all(
        categories=CATEGORIES_TO_SCRAPE,

        # True  → headless Chrome (handles React/Angular pages — RECOMMENDED)
        # False → plain requests  (faster, may miss JS-rendered content)
        use_selenium=True,

        # True  → visit each item's detail page to find the PDF link
        # False → only grab direct .pdf links visible on the listing page
        follow_detail_pages=True,

        # False → dry run: collect URLs only, no actual downloads
        download_files=True,
    )
