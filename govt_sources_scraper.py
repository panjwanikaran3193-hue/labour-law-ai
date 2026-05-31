"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         LABOUR LAW COMPILER — Government Sources Scraper                   ║
║         Free • No Login • Official PDFs                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  SOURCE 1 → indiacode.nic.in    Acts + Rules + Notifications (Central)     ║
║  SOURCE 2 → labour.gov.in       Ministry Acts & Rules                      ║
║  SOURCE 3 → egazette.gov.in     Official Gazette Notifications             ║
║  SOURCE 4 → epfindia.gov.in     EPFO Circulars                             ║
║  SOURCE 5 → esic.gov.in         ESIC Circulars                             ║
║  SOURCE 6 → clc.gov.in          Min Wages / CLC Notifications              ║
║  SOURCE 7 → legislative.gov.in  Central Acts (backup)                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  OUTPUT → E:\\AICA 2\\LABOUR LAW COMPILER\\                                   ║
║           acts\\ rules\\ notifications\\ circulars\\ database\\                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Install (one time):
    pip install requests beautifulsoup4 lxml pandas openpyxl selenium webdriver-manager
"""

import os, re, sys, time, logging, urllib3
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("govt_scraper.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
#  ★  CONFIG — edit here only
# ═══════════════════════════════════════════════════════════════════════════════

OUTPUT_ROOT = Path(r"E:\AICA 2\LABOUR LAW COMPILER")

# Subfolder for each category
FOLDERS = {
    "acts"          : OUTPUT_ROOT / "acts",
    "labour_codes"  : OUTPUT_ROOT / "acts" / "labour_codes",
    "rules"         : OUTPUT_ROOT / "rules",
    "notifications" : OUTPUT_ROOT / "notifications",
    "circulars"     : OUTPUT_ROOT / "circulars",
    "database"      : OUTPUT_ROOT / "database",
    "forms"         : OUTPUT_ROOT / "forms",
    "judgments"     : OUTPUT_ROOT / "judgments",
    "summaries"     : OUTPUT_ROOT / "summaries",
    "logs"          : OUTPUT_ROOT / "logs",
}

HEADERS = {
    "User-Agent"     : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept"         : "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

DELAY        = 1.5   # seconds between requests (be polite)
TIMEOUT      = 30    # seconds
MAX_PER_CAT  = None  # set e.g. 10 to test; None = unlimited
FILE_EXTS    = {".pdf", ".docx", ".doc", ".xlsx", ".zip"}


# ═══════════════════════════════════════════════════════════════════════════════
#  KNOWN DIRECT PDF URLS — indiacode.nic.in
#  Pattern: /bitstream/123456789/{ID}/1/{filename}.pdf
# ═══════════════════════════════════════════════════════════════════════════════

INDIACODE_ACTS = [
    # ── CENTRAL ACTS ──────────────────────────────────────────────────────────
    # (Act Name,  indiacode handle ID,  pdf filename,  folder)
    ("The Employees Provident Funds And Miscellaneous Provisions Act, 1952",
        "2152",  "epf_act_1952.pdf",            "acts"),
    ("The Code on Wages, 2019",
        "15793", "code_on_wages_2019.pdf",       "labour_codes"),
    ("The Code on Social Security, 2020",
        "16823", "social_security_code_2020.pdf","labour_codes"),
    ("The Industrial Relations Code, 2020",
        "22040", "industrial_relations_code_2020.pdf","labour_codes"),
    ("The Occupational Safety, Health And Working Conditions Code, 2020",
        "22041", "osh_code_2020.pdf",            "labour_codes"),
    ("The Child And Adolescent Labour (Prohibition And Regulation) Act, 1986",
        "1848",  "child_labour_act_1986.pdf",    "acts"),
    ("The Bonded Labour System (Abolition) Act, 1976",
        "1491",  "bonded_labour_act_1976.pdf",   "acts"),
    ("The Labour Laws Simplification Act, 1988",
        "1687",  "labour_laws_simplification_1988.pdf","acts"),
    ("The Provident Funds Act, 1925",
        "2383",  "provident_funds_act_1925.pdf", "acts"),
    ("The Contract Labour (Regulation And Abolition) Act, 1970",
        "14038", "contract_labour_act.pdf",      "acts"),
    # ── More Central acts — discovered by browsing indiacode ─────────────────
    ("The Minimum Wages Act, 1948",
        "1380",  "minimum_wages_act_1948.pdf",   "acts"),
    ("The Payment Of Wages Act, 1936",
        "1403",  "payment_of_wages_act_1936.pdf","acts"),
    ("The Payment Of Gratuity Act, 1972",
        "1370",  "payment_of_gratuity_act_1972.pdf","acts"),
    ("The Payment Of Bonus Act, 1965",
        "1369",  "payment_of_bonus_act_1965.pdf","acts"),
    ("The Maternity Benefit Act, 1961",
        "1353",  "maternity_benefit_act_1961.pdf","acts"),
    ("The Employees State Insurance Act, 1948",
        "1385",  "esi_act_1948.pdf",             "acts"),
    ("The Employees Compensation Act, 1923",
        "1373",  "employees_compensation_act.pdf","acts"),
    ("The Factories Act, 1948",
        "1382",  "factories_act_1948.pdf",       "acts"),
    ("The Industrial Disputes Act, 1947",
        "1384",  "industrial_disputes_act_1947.pdf","acts"),
    ("The Industrial Employment (Standing Orders) Act, 1946",
        "1383",  "standing_orders_act_1946.pdf", "acts"),
    ("The Apprentices Act, 1961",
        "1350",  "apprentices_act_1961.pdf",     "acts"),
    ("The Equal Remuneration Act, 1976",
        "1375",  "equal_remuneration_act_1976.pdf","acts"),
    ("The Maternity Benefit Act, 1961",
        "1353",  "maternity_benefit_act_1961.pdf","acts"),
    ("The InterState Migrant Workmen Act, 1979",
        "1388",  "interstate_migrant_workmen_act.pdf","acts"),
    ("The Building And Other Construction Workers Act, 1996",
        "1364",  "bocw_act_1996.pdf",            "acts"),
    ("The BOCW Welfare Cess Act, 1996",
        "1365",  "bocw_cess_act_1996.pdf",       "acts"),
    ("The Sexual Harassment Of Women At Workplace Act, 2013",
        "15815", "posh_act_2013.pdf",            "acts"),
    ("The Rights Of Persons With Disabilities Act, 2016",
        "15613", "rpwd_act_2016.pdf",            "acts"),
    ("The Transgender Persons (Protection Of Rights) Act, 2019",
        "17190", "transgender_protection_act_2019.pdf","acts"),
    ("Employment Exchanges (Compulsory Notification Of Vacancies) Act, 1959",
        "1374",  "employment_exchanges_act_1959.pdf","acts"),
    ("The Sales Promotion Employees (Conditions Of Service) Act, 1976",
        "1404",  "sales_promotion_employees_act.pdf","acts"),
]

# ── PDF filename auto-builder from indiacode ──────────────────────────────────
def indiacode_pdf_url(handle_id: str, pdf_filename: str) -> str:
    return f"https://www.indiacode.nic.in/bitstream/123456789/{handle_id}/1/{pdf_filename}"

def indiacode_browse_url(handle_id: str) -> str:
    return f"https://www.indiacode.nic.in/handle/123456789/{handle_id}?view_type=browse"


# ═══════════════════════════════════════════════════════════════════════════════
#  STATE PAGES ON INDIACODE — browse each state for labour acts
# ═══════════════════════════════════════════════════════════════════════════════

STATE_HANDLES = {
    "Andaman and Nicobar Islands": "2454",
    "Andhra Pradesh"             : "2486",
    "Arunachal Pradesh"          : "2487",
    "Assam"                      : "2513",
    "Bihar"                      : "2488",
    "Chandigarh"                 : "2489",
    "Chhattisgarh"               : "2490",
    "Delhi"                      : "2493",
    "Goa"                        : "2514",
    "Gujarat"                    : "2455",
    "Haryana"                    : "2193",
    "Himachal Pradesh"           : "2494",
    "Jammu and Kashmir"          : "2495",
    "Jharkhand"                  : "2515",
    "Karnataka"                  : "2485",
    "Kerala"                     : "2516",
    "Ladakh"                     : "14011",
    "Madhya Pradesh"             : "2497",
    "Maharashtra"                : "2517",
    "Manipur"                    : "2498",
    "Meghalaya"                  : "2499",
    "Mizoram"                    : "2500",
    "Nagaland"                   : "2501",
    "Odisha"                     : "2502",
    "Puducherry"                 : "2503",
    "Punjab"                     : "2504",
    "Rajasthan"                  : "2505",
    "Sikkim"                     : "2506",
    "Tamil Nadu"                 : "2507",
    "Telangana"                  : "2508",
    "Tripura"                    : "2509",
    "Uttar Pradesh"              : "2510",
    "Uttarakhand"                : "2511",
    "West Bengal"                : "2512",
}

# Labour-related keywords — used to filter state act listings
LABOUR_KEYWORDS = [
    "labour", "labor", "wages", "wage", "shops", "establishment",
    "factory", "factories", "employment", "employee", "workmen",
    "workers", "industrial", "profession", "trade", "welfare",
    "maternity", "gratuity", "bonus", "provident", "insurance",
    "apprentice", "contract", "dispute", "standing order",
    "holiday", "leave", "compensation", "minimum", "migrant",
    "construction", "building", "equal remuneration",
]


# ═══════════════════════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def safe_name(title: str, url: str, ext: str = ".pdf") -> str:
    name = title.strip() if len(title.strip()) > 6 else urlparse(url).path.split("/")[-1]
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = re.sub(r"\s+", "_", name).strip("._")[:140]
    url_ext = os.path.splitext(urlparse(url).path)[-1].lower()
    final_ext = url_ext if url_ext in FILE_EXTS else ext
    if not name.lower().endswith(final_ext):
        name += final_ext
    return name


def get(url: str, verify=True) -> requests.Response | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT,
                         verify=verify, allow_redirects=True)
        r.raise_for_status()
        return r
    except Exception as e:
        log.warning("  GET failed: %s — %s", url, e)
        return None


def soup(url: str, verify=True) -> BeautifulSoup | None:
    r = get(url, verify)
    return BeautifulSoup(r.text, "lxml") if r else None


def download(url: str, dest: Path, verify=True) -> bool:
    if dest.exists() and dest.stat().st_size > 500:
        log.info("    [skip] %s", dest.name)
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT,
                         stream=True, verify=verify, allow_redirects=True)
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "").lower()
        ok = any(t in ct for t in ("pdf","msword","officedocument","zip",
                                    "octet","binary","force-download"))
        url_ext = os.path.splitext(urlparse(url).path)[-1].lower()
        if not ok and url_ext not in FILE_EXTS:
            log.warning("    [skip] bad content-type=%s  %s", ct[:40], url)
            return False
        with open(dest, "wb") as f:
            for chunk in r.iter_content(16384):
                if chunk: f.write(chunk)
        kb = dest.stat().st_size // 1024
        log.info("    [ok] %-70s %d KB", dest.name[:70], kb)
        return True
    except Exception as e:
        log.warning("    [fail] %s — %s", url, e)
        if dest.exists(): dest.unlink()
        return False


def is_labour_related(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in LABOUR_KEYWORDS)


# ═══════════════════════════════════════════════════════════════════════════════
#  SOURCE 1 — indiacode.nic.in  (Central Acts with known IDs)
# ═══════════════════════════════════════════════════════════════════════════════

def scrape_indiacode_central(download_files=True) -> list[dict]:
    """Download all Central Labour Acts using known handle IDs."""
    log.info("━"*70)
    log.info("SOURCE 1a — indiacode.nic.in  Central Acts")
    records = []

    for i, (name, hid, fname, folder) in enumerate(INDIACODE_ACTS, 1):
        pdf_url   = indiacode_pdf_url(hid, fname)
        page_url  = indiacode_browse_url(hid)
        dest_path = FOLDERS[folder] / fname

        log.info("[%d/%d] %s", i, len(INDIACODE_ACTS), name[:75])

        ok = False
        if download_files:
            ok = download(pdf_url, dest_path)
            # if direct PDF URL fails, visit browse page to find actual PDF link
            if not ok:
                log.info("  Trying browse page: %s", page_url)
                s = soup(page_url)
                if s:
                    for a in s.find_all("a", href=True):
                        href = a["href"]
                        if "bitstream" in href and href.endswith(".pdf"):
                            full = href if href.startswith("http") else \
                                   "https://www.indiacode.nic.in" + href
                            actual_name = safe_name(name, full)
                            ok = download(full, FOLDERS[folder] / actual_name)
                            if ok:
                                dest_path = FOLDERS[folder] / actual_name
                                break
        records.append({
            "Sr No": i, "Document Name": name,
            "Source": "indiacode.nic.in",
            "Category": "Acts" if folder=="acts" else "Labour Codes",
            "State/Central": "Central",
            "Folder": str(FOLDERS[folder]),
            "PDF URL": pdf_url, "Browse URL": page_url,
            "Local File": str(dest_path) if ok else "",
            "Downloaded": ok,
            "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        time.sleep(DELAY)
    return records


def scrape_indiacode_states(states=None, download_files=True) -> list[dict]:
    """
    For each state on indiacode.nic.in:
    1. Browse the state's act listing page
    2. Filter acts that are labour-related
    3. Find PDF link on each act's detail page
    4. Download PDF
    """
    log.info("━"*70)
    log.info("SOURCE 1b — indiacode.nic.in  State Acts")

    target_states = states or list(STATE_HANDLES.keys())
    records = []

    for state in target_states:
        hid = STATE_HANDLES.get(state)
        if not hid:
            continue
        browse_url = (f"https://www.indiacode.nic.in/handle/123456789/{hid}/"
                      f"browse?type=title&order=ASC&rpp=100")
        log.info("  State: %-25s  %s", state, browse_url)

        s = soup(browse_url)
        if not s:
            time.sleep(DELAY)
            continue

        # find act rows in the browse table
        act_links = []
        for a in s.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if ("/handle/123456789/" in href and
                    "browse" not in href and
                    "view_type" not in href and
                    is_labour_related(text) and
                    len(text) > 10):
                full = ("https://www.indiacode.nic.in" + href
                        if not href.startswith("http") else href)
                act_links.append((text, full))

        log.info("    Found %d labour-related acts for %s", len(act_links), state)
        cap = MAX_PER_CAT
        for j, (act_name, act_page) in enumerate(act_links[:cap] if cap else act_links, 1):
            time.sleep(DELAY)
            act_soup = soup(act_page)
            if not act_soup:
                continue

            # find PDF bitstream link on the act detail page
            pdf_link = ""
            for a in act_soup.find_all("a", href=True):
                href = a["href"]
                if "bitstream" in href and href.endswith(".pdf"):
                    pdf_link = ("https://www.indiacode.nic.in" + href
                                if not href.startswith("http") else href)
                    break

            ok = False
            dest_path = Path("")
            if pdf_link and download_files:
                fname     = safe_name(act_name, pdf_link)
                dest_path = FOLDERS["acts"] / state.replace(" ", "_") / fname
                ok = download(pdf_link, dest_path)

            records.append({
                "Sr No": len(records)+1,
                "Document Name": act_name,
                "Source": "indiacode.nic.in",
                "Category": "Acts",
                "State/Central": state,
                "Folder": str(FOLDERS["acts"] / state.replace(" ","_")),
                "PDF URL": pdf_link,
                "Browse URL": act_page,
                "Local File": str(dest_path) if ok else "",
                "Downloaded": ok,
                "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
    return records


# ═══════════════════════════════════════════════════════════════════════════════
#  SOURCE 2 — labour.gov.in  (Ministry of Labour Acts & Rules)
# ═══════════════════════════════════════════════════════════════════════════════

def scrape_labour_gov(download_files=True) -> list[dict]:
    log.info("━"*70)
    log.info("SOURCE 2 — labour.gov.in  Acts & Rules")
    records = []

    pages = [
        ("https://labour.gov.in/acts-rules",          "acts",   "Acts & Rules"),
        ("https://labour.gov.in/labour-codes",         "labour_codes", "Labour Codes"),
        ("https://labour.gov.in/gazette-notifications","notifications","Gazette Notifications"),
        ("https://labour.gov.in/circulars",            "circulars",   "Circulars"),
    ]

    for url, folder, cat in pages:
        log.info("  Page: %s", url)
        s = soup(url)
        if not s:
            time.sleep(DELAY)
            continue

        for a in s.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(separator=" ", strip=True)
            ext  = os.path.splitext(urlparse(href).path)[-1].lower()

            if ext not in FILE_EXTS or not text:
                continue
            full_url = href if href.startswith("http") else urljoin("https://labour.gov.in", href)

            ok = False
            dest = FOLDERS[folder] / safe_name(text, full_url)
            if download_files:
                ok = download(full_url, dest)

            records.append({
                "Sr No": len(records)+1,
                "Document Name": text,
                "Source": "labour.gov.in",
                "Category": cat,
                "State/Central": "Central",
                "Folder": str(FOLDERS[folder]),
                "PDF URL": full_url,
                "Browse URL": url,
                "Local File": str(dest) if ok else "",
                "Downloaded": ok,
                "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            time.sleep(DELAY)
    return records


# ═══════════════════════════════════════════════════════════════════════════════
#  SOURCE 3 — egazette.gov.in  (Official Gazette Notifications)
# ═══════════════════════════════════════════════════════════════════════════════

def scrape_egazette(download_files=True) -> list[dict]:
    log.info("━"*70)
    log.info("SOURCE 3 — egazette.gov.in  Gazette Notifications")
    records = []

    # eGazette search for Labour & Employment ministry
    search_urls = [
        "https://egazette.gov.in/WriteReadData/2025/Labour",
        "https://egazette.gov.in/WriteReadData/2024/Labour",
        "https://egazette.gov.in/SearchGazette.aspx",
    ]

    # Also try direct browse
    base = "https://egazette.gov.in"
    s = soup(base + "/WriteReadData/2025/")
    if not s:
        s = soup(base)

    if s:
        for a in s.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(separator=" ", strip=True)
            ext  = os.path.splitext(href)[-1].lower()
            if ext == ".pdf" and text and is_labour_related(text):
                full_url = href if href.startswith("http") else urljoin(base, href)
                ok = False
                dest = FOLDERS["notifications"] / safe_name(text, full_url)
                if download_files:
                    ok = download(full_url, dest)
                records.append({
                    "Sr No": len(records)+1,
                    "Document Name": text,
                    "Source": "egazette.gov.in",
                    "Category": "Gazette Notifications",
                    "State/Central": "Central",
                    "Folder": str(FOLDERS["notifications"]),
                    "PDF URL": full_url,
                    "Browse URL": base,
                    "Local File": str(dest) if ok else "",
                    "Downloaded": ok,
                    "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                time.sleep(DELAY)
    return records


# ═══════════════════════════════════════════════════════════════════════════════
#  SOURCE 4 — epfindia.gov.in  (EPFO Circulars)
# ═══════════════════════════════════════════════════════════════════════════════

def scrape_epfo(download_files=True) -> list[dict]:
    log.info("━"*70)
    log.info("SOURCE 4 — epfindia.gov.in  EPFO Circulars")
    records = []

    pages = [
        "https://www.epfindia.gov.in/site_en/Circulars.php",
        "https://www.epfindia.gov.in/site_en/Notifications.php",
        "https://www.epfindia.gov.in/site_en/Whatsnew.php",
    ]

    for url in pages:
        s = soup(url)
        if not s:
            time.sleep(DELAY)
            continue
        for a in s.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(separator=" ", strip=True)
            ext  = os.path.splitext(urlparse(href).path)[-1].lower()
            if ext not in FILE_EXTS or len(text) < 5:
                continue
            full_url = href if href.startswith("http") else urljoin("https://www.epfindia.gov.in", href)

            ok = False
            dest = FOLDERS["circulars"] / "EPFO" / safe_name(text, full_url)
            if download_files:
                ok = download(full_url, dest)

            records.append({
                "Sr No": len(records)+1,
                "Document Name": text,
                "Source": "epfindia.gov.in",
                "Category": "Circulars",
                "State/Central": "Central",
                "Folder": str(FOLDERS["circulars"] / "EPFO"),
                "PDF URL": full_url,
                "Browse URL": url,
                "Local File": str(dest) if ok else "",
                "Downloaded": ok,
                "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            time.sleep(DELAY)
    return records


# ═══════════════════════════════════════════════════════════════════════════════
#  SOURCE 5 — esic.gov.in  (ESIC Circulars)
# ═══════════════════════════════════════════════════════════════════════════════

def scrape_esic(download_files=True) -> list[dict]:
    log.info("━"*70)
    log.info("SOURCE 5 — esic.gov.in  ESIC Circulars")
    records = []

    pages = [
        "https://esic.gov.in/circulars",
        "https://esic.gov.in/notifications",
        "https://esic.gov.in/orders",
    ]

    for url in pages:
        s = soup(url, verify=False)
        if not s:
            time.sleep(DELAY)
            continue
        for a in s.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(separator=" ", strip=True)
            ext  = os.path.splitext(urlparse(href).path)[-1].lower()
            if ext not in FILE_EXTS or len(text) < 5:
                continue
            full_url = (href if href.startswith("http")
                        else urljoin("https://esic.gov.in", href))

            ok = False
            dest = FOLDERS["circulars"] / "ESIC" / safe_name(text, full_url)
            if download_files:
                ok = download(full_url, dest, verify=False)

            records.append({
                "Sr No": len(records)+1,
                "Document Name": text,
                "Source": "esic.gov.in",
                "Category": "Circulars",
                "State/Central": "Central",
                "Folder": str(FOLDERS["circulars"] / "ESIC"),
                "PDF URL": full_url,
                "Browse URL": url,
                "Local File": str(dest) if ok else "",
                "Downloaded": ok,
                "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            time.sleep(DELAY)
    return records


# ═══════════════════════════════════════════════════════════════════════════════
#  SOURCE 6 — clc.gov.in  (CLC Min Wages + Notifications)
# ═══════════════════════════════════════════════════════════════════════════════

def scrape_clc(download_files=True) -> list[dict]:
    log.info("━"*70)
    log.info("SOURCE 6 — clc.gov.in  Min Wages & Notifications")
    records = []

    pages = [
        ("https://clc.gov.in/clc/min-wages",      "database",     "Minimum Wages"),
        ("https://clc.gov.in/clc/notifications",   "notifications","Notifications"),
        ("https://clc.gov.in/clc/circulars",       "circulars",    "Circulars"),
        ("https://clc.gov.in/clc/acts-rules",      "acts",         "Acts & Rules"),
    ]

    for url, folder, cat in pages:
        s = soup(url)
        if not s:
            time.sleep(DELAY)
            continue

        # extract table rows
        for tr in s.find_all("tr"):
            cells = tr.find_all(["td","th"])
            row_text = " ".join(c.get_text(strip=True) for c in cells)
            if not row_text or len(row_text) < 5:
                continue

            for a in tr.find_all("a", href=True):
                href = a["href"].strip()
                ext  = os.path.splitext(urlparse(href).path)[-1].lower()
                if ext not in FILE_EXTS:
                    continue
                text = a.get_text(strip=True) or row_text[:100]
                full_url = href if href.startswith("http") else urljoin("https://clc.gov.in", href)

                ok = False
                dest = FOLDERS[folder] / "CLC" / safe_name(text, full_url)
                if download_files:
                    ok = download(full_url, dest)

                records.append({
                    "Sr No": len(records)+1,
                    "Document Name": text,
                    "Source": "clc.gov.in",
                    "Category": cat,
                    "State/Central": "Central",
                    "Folder": str(FOLDERS[folder] / "CLC"),
                    "PDF URL": full_url,
                    "Browse URL": url,
                    "Local File": str(dest) if ok else "",
                    "Downloaded": ok,
                    "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                time.sleep(DELAY)
    return records


# ═══════════════════════════════════════════════════════════════════════════════
#  SOURCE 7 — legislative.gov.in  (Acts backup)
# ═══════════════════════════════════════════════════════════════════════════════

def scrape_legislative_gov(download_files=True) -> list[dict]:
    log.info("━"*70)
    log.info("SOURCE 7 — legislative.gov.in  Central Acts (backup)")
    records = []
    url = "https://legislative.gov.in/document-category/list-of-central-acts/"

    s = soup(url)
    if not s:
        return records

    for a in s.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(separator=" ", strip=True)
        ext  = os.path.splitext(urlparse(href).path)[-1].lower()
        if ext not in FILE_EXTS or not is_labour_related(text):
            continue
        full_url = href if href.startswith("http") else urljoin("https://legislative.gov.in", href)

        ok = False
        dest = FOLDERS["acts"] / "Central" / safe_name(text, full_url)
        if download_files:
            ok = download(full_url, dest)

        records.append({
            "Sr No": len(records)+1,
            "Document Name": text,
            "Source": "legislative.gov.in",
            "Category": "Acts",
            "State/Central": "Central",
            "Folder": str(FOLDERS["acts"] / "Central"),
            "PDF URL": full_url,
            "Browse URL": url,
            "Local File": str(dest) if ok else "",
            "Downloaded": ok,
            "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        time.sleep(DELAY)
    return records


# ═══════════════════════════════════════════════════════════════════════════════
#  MASTER RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def run_all(
    download_files  : bool       = True,
    include_states  : bool       = True,
    target_states   : list | None = None,   # None = all states
    sources         : list | None = None,   # None = all sources
):
    """
    Run all scrapers.

    Quick test:
        run_all(download_files=True, include_states=False, sources=["indiacode_central"])

    Full run:
        run_all(download_files=True, include_states=True)
    """
    # create all folders
    for f in FOLDERS.values():
        f.mkdir(parents=True, exist_ok=True)

    all_records: list[dict] = []
    start = datetime.now()

    active = sources or ["indiacode_central", "indiacode_states",
                         "labour_gov", "egazette", "epfo",
                         "esic", "clc", "legislative"]

    if "indiacode_central" in active:
        all_records += scrape_indiacode_central(download_files)

    if "indiacode_states" in active and include_states:
        all_records += scrape_indiacode_states(target_states, download_files)

    if "labour_gov" in active:
        all_records += scrape_labour_gov(download_files)

    if "egazette" in active:
        all_records += scrape_egazette(download_files)

    if "epfo" in active:
        all_records += scrape_epfo(download_files)

    if "esic" in active:
        all_records += scrape_esic(download_files)

    if "clc" in active:
        all_records += scrape_clc(download_files)

    if "legislative" in active:
        all_records += scrape_legislative_gov(download_files)

    # ── Save Excel index ──────────────────────────────────────────────────────
    if all_records:
        df = pd.DataFrame(all_records)
        ts = start.strftime("%Y%m%d_%H%M")
        xlsx = OUTPUT_ROOT / f"download_log_{ts}.xlsx"

        with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
            # Summary
            summary = (df.groupby(["Source","Category"])
                         .agg(Total=("Document Name","count"),
                              Downloaded=("Downloaded","sum"))
                         .reset_index())
            summary["Failed"] = summary["Total"] - summary["Downloaded"]
            summary.to_excel(writer, sheet_name="Summary", index=False)

            # Full log
            df.to_excel(writer, sheet_name="All Records", index=False)

            # Per-source sheets
            for src in df["Source"].unique():
                sub = df[df["Source"]==src]
                sub.to_excel(writer, sheet_name=src[:31], index=False)

        log.info("")
        log.info("━"*70)
        log.info("  Total records : %d", len(df))
        log.info("  Downloaded    : %d", df["Downloaded"].sum())
        log.info("  Failed        : %d", len(df) - df["Downloaded"].sum())
        log.info("  Log saved     : %s", xlsx)
        log.info("  Time taken    : %ds", (datetime.now()-start).seconds)
        log.info("━"*70)
    else:
        log.warning("No records collected.")


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    # ── STEP 1: TEST with just Central Acts from indiacode (fastest) ──────────
    # Uncomment these 3 lines, run, check E:\AICA 2\LABOUR LAW COMPILER\acts\
    # MAX_PER_CAT = 5
    # run_all(download_files=True, include_states=False, sources=["indiacode_central"])
    # sys.exit()

    # ── STEP 2: Add EPFO + ESIC + CLC (Central circulars) ────────────────────
    # run_all(download_files=True, include_states=False,
    #         sources=["indiacode_central","epfo","esic","clc","labour_gov"])
    # sys.exit()

    # ── STEP 3: FULL RUN — all sources + all 34 states ───────────────────────
    run_all(
        download_files = True,
        include_states = True,
        target_states  = None,   # or list e.g. ["Karnataka","Maharashtra"]
    )
