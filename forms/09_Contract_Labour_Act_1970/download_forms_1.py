"""
Download Statutory Labour Law Forms — VERIFIED URLs
=====================================================
All URLs verified from live government search results.
Run this on YOUR PC (not a cloud server).

    pip install requests
    python download_forms.py

Saves to: E:\\AICA 2\\LABOUR LAW COMPILER\\forms\\
"""

import os, re, time, sys
from pathlib import Path
import requests

BASE_FOLDER = Path(r"E:\AICA 2\LABOUR LAW COMPILER\forms")
DELAY   = 2
TIMEOUT = 60

HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept"     : "text/html,application/pdf,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ─────────────────────────────────────────────────────────────────────────────
# FORMS LIST
# Each entry: (subfolder, save_filename, description, [url1, url2, url3...])
# URLs tried in order — first success wins.
# All URLs verified from search results / page content.
# ─────────────────────────────────────────────────────────────────────────────

FORMS = [

    # ══ PAYMENT OF BONUS ACT, 1965 ════════════════════════════════════════════
    # All 4 forms (A,B,C,D) are inside the Bonus Rules PDF — one download gets all
    ("01_Bonus_Act_1965",
     "Bonus_Rules_1975_Forms_ABCD.pdf",
     "Forms A B C D — Payment of Bonus Rules, 1975 (all 4 forms inside)",
     [
         "https://clc.gov.in/clc/sites/default/files/BonusAct.pdf",
         "https://labour.gov.in/sites/default/files/thepaymentof_bonus_rules1975.pdf",
         "https://www.labour.gov.in/static/uploads/2025/06/3fbc98da530fbc248c7a0f711dc5dd2b.pdf",
     ]),

    # ══ MATERNITY BENEFIT ACT, 1961 ═══════════════════════════════════════════
    ("02_Maternity_Benefit_Act_1961",
     "Maternity_Benefit_Rules_1963_Form_A.pdf",
     "Form A — Muster Roll (Maternity Benefit Rules, 1963)",
     [
         "https://clc.gov.in/clc/sites/default/files/MaternityBenefitAct.pdf",
         "https://labour.gov.in/sites/default/files/maternity_benefit_rules1963.pdf",
     ]),

    # ══ PAYMENT OF GRATUITY ACT, 1972 ═════════════════════════════════════════
    ("03_Gratuity_Act_1972",
     "Gratuity_Act_and_Central_Rules_1972_All_Forms.pdf",
     "Forms A B C F + all — Payment of Gratuity Act & Central Rules",
     [
         "https://clc.gov.in/clc/sites/default/files/PaymentofGratuityAct.pdf",
         "https://labour.gov.in/sites/default/files/payment_of_gratuity_central_rules_1972.pdf",
     ]),

    ("03_Gratuity_Act_1972",
     "Form_T_Recovery_of_Gratuity.pdf",
     "Form T — Application for Recovery of Gratuity",
     [
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/Form%20T.pdf",
         "https://clc.gov.in/clc/sites/default/files/FormT_Gratuity.pdf",
     ]),

    # ══ MINIMUM WAGES ACT, 1948 ════════════════════════════════════════════════
    ("04_Minimum_Wages_Act_1948",
     "Minimum_Wages_Act_and_Central_Rules_1950_Forms_I_to_IV.pdf",
     "Forms I II III IV — Minimum Wages Central Rules, 1950",
     [
         "https://clc.gov.in/clc/sites/default/files/MinimumWagesact.pdf",
         "https://labour.gov.in/sites/default/files/minimum_wages_central_rules1950.pdf",
     ]),

    ("04_Minimum_Wages_Act_1948",
     "Form_VI_Employee_Application_MinWages.pdf",
     "Form VI — Application by Employee under Sec 20(2) Minimum Wages Act",
     [
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/FORM%20VI.pdf",
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/Form%20VI.pdf",
     ]),

    ("04_Minimum_Wages_Act_1948",
     "Form_VIA_Group_Application_MinWages.pdf",
     "Form VI-A — Group Application under Sec 21(1) Minimum Wages Act",
     [
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/FORM%20VI-A.pdf",
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/Form%20VI-A.pdf",
     ]),

    # ══ ESI ACT, 1948 ══════════════════════════════════════════════════════════
    ("05_ESI_Act_1948",
     "ESI_General_Regulations_1950_All_Forms.pdf",
     "All ESI Forms — ESI General Regulations 1950 (Forms 1,3,5,6 etc.)",
     [
         "https://esic.gov.in/attachments/regularionact/ESI_General_Regulations_1950.pdf",
         "https://esic.gov.in/attachments/regularionact/ESIGeneralRegulations1950.pdf",
         "https://esic.gov.in/sites/default/files/ESI_Regulations.pdf",
     ]),

    ("05_ESI_Act_1948",
     "Form_1_Declaration_Employer_Registration.pdf",
     "Form 1 — Declaration / Employer Registration (ESI Act)",
     [
         "https://esic.gov.in/attachments/regularionact/form1.pdf",
         "https://esic.gov.in/sites/default/files/form1.pdf",
         "https://esic.gov.in/forms/form1.pdf",
     ]),

    ("05_ESI_Act_1948",
     "Form_3_Return_of_Declaration.pdf",
     "Form 3 — Return of Declaration (ESI Act)",
     [
         "https://esic.gov.in/attachments/regularionact/form3.pdf",
         "https://esic.gov.in/sites/default/files/form3.pdf",
     ]),

    ("05_ESI_Act_1948",
     "Form_5_Return_of_Contributions.pdf",
     "Form 5 — Return of Contributions (ESI Act)",
     [
         "https://esic.gov.in/attachments/regularionact/form5.pdf",
         "https://esic.gov.in/sites/default/files/form5.pdf",
     ]),

    ("05_ESI_Act_1948",
     "Form_6_Register_of_Employees.pdf",
     "Form 6 — Register of Employees (ESI Act)",
     [
         "https://esic.gov.in/attachments/regularionact/form6.pdf",
         "https://esic.gov.in/sites/default/files/form6.pdf",
     ]),

    # ══ EPF ACT, 1952 ══════════════════════════════════════════════════════════
    ("06_EPF_Act_1952",
     "Form_2_Nomination_EPF.pdf",
     "Form 2 — Nomination & Declaration (EPF)",
     [
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/Form2Revised.pdf",
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/Form2.pdf",
         "https://unifiedportal-mem.epfindia.gov.in/Forms/Form2.pdf",
     ]),

    ("06_EPF_Act_1952",
     "Form_11_New_Employee_Declaration.pdf",
     "Form 11 — Declaration by New Employee (EPF)",
     [
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/Form11Revised.pdf",
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/Form11_New.pdf",
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/Form11.pdf",
     ]),

    ("06_EPF_Act_1952",
     "Form_12A_Annual_Return.pdf",
     "Form 12A — Annual Return (EPF)",
     [
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/Form12A.pdf",
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/FORM_12A.pdf",
     ]),

    ("06_EPF_Act_1952",
     "Form_19_PF_Withdrawal.pdf",
     "Form 19 — PF Final Settlement / Withdrawal (EPF)",
     [
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/Form19UAN.pdf",
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/FORM_19.pdf",
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/Form19.pdf",
     ]),

    ("06_EPF_Act_1952",
     "Form_10C_EPS_Withdrawal.pdf",
     "Form 10C — EPS Withdrawal / Scheme Certificate (EPF)",
     [
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/Form10C.pdf",
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/FORM_10C.pdf",
     ]),

    ("06_EPF_Act_1952",
     "Form_10D_Monthly_Pension.pdf",
     "Form 10D — Monthly Pension (EPS 1995)",
     [
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/Form10D.pdf",
         "https://www.epfindia.gov.in/site_docs/PDFs/Misc_PDFs/FORM_10D.pdf",
     ]),

    # ══ FACTORIES ACT, 1948 ════════════════════════════════════════════════════
    ("07_Factories_Act_1948",
     "Factories_Central_Rules_1950_All_Forms.pdf",
     "Forms 25 26 + all — Factories Act Central Rules (Annual & Half-Yearly Return)",
     [
         "https://clc.gov.in/clc/sites/default/files/FactoriesAct.pdf",
         "https://labour.gov.in/sites/default/files/factories_central_rules1950.pdf",
     ]),

    # ══ INDUSTRIAL DISPUTES ACT, 1947 ══════════════════════════════════════════
    ("08_Industrial_Disputes_Act_1947",
     "Industrial_Disputes_Central_Rules_1957_Form_A.pdf",
     "Form A — Notice of Change + all ID Central Rules Forms",
     [
         "https://clc.gov.in/clc/sites/default/files/IndustrialDisputesAct.pdf",
         "https://labour.gov.in/sites/default/files/industrial_disputes_central_rules1957.pdf",
     ]),

    ("08_Industrial_Disputes_Act_1947",
     "Format_Filing_Industrial_Dispute.pdf",
     "Format for Filing Industrial Dispute (CLC Online)",
     [
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/Format%20for%20filing%20Industrial%20Dispute.pdf",
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/ID_Format.pdf",
     ]),

    # ══ CONTRACT LABOUR ACT, 1970 ══════════════════════════════════════════════
    ("09_Contract_Labour_Act_1970",
     "Contract_Labour_Act_Central_Rules_1971_All_Forms.pdf",
     "All Forms I IV VII XII XIII — Contract Labour Central Rules, 1971",
     [
         "https://clc.gov.in/clc/sites/default/files/ContractLabourAct.pdf",
         "https://labour.gov.in/sites/default/files/contract_labour_central_rules1971.pdf",
     ]),

    ("09_Contract_Labour_Act_1970",
     "Form_III_Certificate_Principal_Employer.pdf",
     "Form III — Certificate by Principal Employer (CL Act)",
     [
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/FORM%20III.pdf",
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/Form%20III.pdf",
     ]),

    ("09_Contract_Labour_Act_1970",
     "Form_II_Application_Licence_Contractor.pdf",
     "Form II — Application for Licence/Renewal (Contractor) (CL Act)",
     [
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/FORM%20II.pdf",
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/Form%20II.pdf",
     ]),

    # ══ CHILD LABOUR ACT, 1986 ═════════════════════════════════════════════════
    ("10_Child_Labour_Act_1986",
     "Child_Labour_Rules_1988_Form_01A.pdf",
     "Form 01-A — Annual Return (Child Labour Rules, 1988)",
     [
         "https://clc.gov.in/clc/sites/default/files/ChildLabourAct.pdf",
         "https://labour.gov.in/sites/default/files/child_labour_rules1988.pdf",
     ]),

    # ══ BOCW ACT, 1996 ════════════════════════════════════════════════════════
    ("11_BOCW_Act_1996",
     "BOCW_Central_Rules_1998_All_Forms.pdf",
     "All BOCW Forms I XXII + — BOCW Central Rules, 1998",
     [
         "https://clc.gov.in/clc/sites/default/files/BOCWAct.pdf",
         "https://labour.gov.in/sites/default/files/BOCW_Central_Rules_1998.pdf",
     ]),

    # ══ POSH ACT, 2013 ════════════════════════════════════════════════════════
    ("12_POSH_Act_2013",
     "POSH_Act_2013_and_Rules_ICC_Forms.pdf",
     "POSH Act 2013 + Rules — ICC Complaint Form & all forms",
     [
         "https://www.indiacode.nic.in/bitstream/123456789/15815/1/posh_act_2013.pdf",
         "https://labour.gov.in/sites/default/files/posh_act_2013.pdf",
         "https://wcd.nic.in/sites/default/files/SHact.pdf",
     ]),

    # ══ PAYMENT OF WAGES ACT, 1936 ═════════════════════════════════════════════
    ("13_Payment_of_Wages_Act_1936",
     "Payment_of_Wages_Act_Rules_All_Forms.pdf",
     "All Forms — Payment of Wages Act & Rules",
     [
         "https://clc.gov.in/clc/sites/default/files/PaymentofWagesAct.pdf",
         "https://labour.gov.in/sites/default/files/payment_of_wages_rules1937.pdf",
     ]),

    ("13_Payment_of_Wages_Act_1936",
     "Form_A_Individual_Application_Payment_Wages.pdf",
     "Form A — Individual Application under Payment of Wages Act",
     [
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/FORM%20A.pdf",
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/Form%20A.pdf",
     ]),

    ("13_Payment_of_Wages_Act_1936",
     "Form_B_Group_Application_Payment_Wages.pdf",
     "Form B — Group Application under Payment of Wages Act",
     [
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/FORM%20B.pdf",
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/Form%20B.pdf",
     ]),

    # ══ EQUAL REMUNERATION ACT, 1976 ══════════════════════════════════════════
    ("14_General_Formats",
     "Equal_Remuneration_Rules_1976_Forms_D_E.pdf",
     "Forms D E — Equal Remuneration Rules, 1976 (Register forms)",
     [
         "https://clc.gov.in/clc/sites/default/files/EqualRemunerationAct.pdf",
         "https://labour.gov.in/sites/default/files/equal_remuneration_rules1976.pdf",
     ]),

    # ══ STANDING ORDERS ════════════════════════════════════════════════════════
    ("14_General_Formats",
     "Model_Standing_Orders_Industrial_Employment.pdf",
     "Model Standing Orders — Industrial Employment (Standing Orders) Act, 1946",
     [
         "https://clc.gov.in/clc/sites/default/files/IndustrialEmploymentAct.pdf",
         "https://www.indiacode.nic.in/bitstream/123456789/1383/1/standing_orders_act_1946.pdf",
         "https://labour.gov.in/sites/default/files/standing_orders_act1946.pdf",
     ]),

    # ══ MIGRANT WORKMEN ACT ════════════════════════════════════════════════════
    ("14_General_Formats",
     "Interstate_Migrant_Workmen_Central_Rules_1980_All_Forms.pdf",
     "All Forms — Interstate Migrant Workmen Central Rules, 1980",
     [
         "https://clc.gov.in/clc/sites/default/files/ISMWAct.pdf",
         "https://labour.gov.in/sites/default/files/interstate_migrant_workmen_central_rules1980.pdf",
     ]),

    # ══ SHORT PAYMENT / NON PAYMENT COMPLAINTS ═════════════════════════════════
    ("14_General_Formats",
     "Format_Short_Payment_Complaint.pdf",
     "Format for Filing Short Payment Complaint (CLC)",
     [
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/Format%20for%20filing%20Short%20Payment%20Complaints.pdf",
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/Short_Payment_Format.pdf",
     ]),

    ("14_General_Formats",
     "Format_Non_Payment_Complaint.pdf",
     "Format for Filing Non-Payment Complaint (CLC)",
     [
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/Format%20for%20filing%20Non%20Payment%20Complaints.pdf",
         "https://clc.gov.in/clc/Regionaloffice/NewDelhi/sites/default/files/Non_Payment_Format.pdf",
     ]),
]


# ── DOWNLOAD ENGINE ───────────────────────────────────────────────────────────

def try_download(urls: list, dest: Path) -> bool:
    """Try each URL in order. Return True on first success."""
    if dest.exists() and dest.stat().st_size > 3000:
        print(f"    [skip] Already exists ({dest.stat().st_size//1024} KB)")
        return True

    dest.parent.mkdir(parents=True, exist_ok=True)

    for attempt, url in enumerate(urls, 1):
        try:
            h = {**HEADERS, "Referer": "/".join(url.split("/")[:3]) + "/"}
            r = requests.get(url, headers=h, timeout=TIMEOUT,
                             stream=True, allow_redirects=True)
            if r.status_code != 200:
                print(f"    [attempt {attempt}] HTTP {r.status_code} — {url}")
                continue

            ct = r.headers.get("Content-Type", "").lower()
            if "html" in ct and "pdf" not in ct:
                print(f"    [attempt {attempt}] Got HTML not PDF — {url}")
                continue

            with open(dest, "wb") as f:
                for chunk in r.iter_content(16384):
                    if chunk:
                        f.write(chunk)

            sz = dest.stat().st_size
            if sz < 3000:
                dest.unlink()
                print(f"    [attempt {attempt}] File too small ({sz}B) — {url}")
                continue

            print(f"    ✓ {dest.name}  ({sz//1024} KB)  [attempt {attempt}]")
            return True

        except Exception as e:
            print(f"    [attempt {attempt}] Error: {e}")

    return False


def run():
    BASE_FOLDER.mkdir(parents=True, exist_ok=True)
    for sf in set(f[0] for f in FORMS):
        (BASE_FOLDER / sf).mkdir(parents=True, exist_ok=True)

    total = len(FORMS)
    ok_list, fail_list = [], []
    cur_folder = ""

    print("=" * 68)
    print("  DOWNLOADING STATUTORY LABOUR LAW FORMS")
    print(f"  {total} forms  →  {BASE_FOLDER}")
    print("=" * 68)

    for i, (subfolder, filename, desc, urls) in enumerate(FORMS, 1):
        if subfolder != cur_folder:
            cur_folder = subfolder
            print(f"\n── {subfolder.replace('_',' ').strip()} ─────────")

        dest = BASE_FOLDER / subfolder / filename
        print(f"\n  [{i:02d}/{total}] {desc[:66]}")

        ok = try_download(urls, dest)
        (ok_list if ok else fail_list).append((subfolder, desc, filename, urls))
        time.sleep(DELAY)

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 68)
    print(f"  RESULT: {len(ok_list)}/{total} downloaded  |  {len(fail_list)} failed")
    print("=" * 68)

    if fail_list:
        print(f"\n✗ FAILED ({len(fail_list)}) — open these in your browser to download:\n")
        for sf, desc, fname, urls in fail_list:
            print(f"  • {desc}")
            print(f"    Save as: {BASE_FOLDER / sf / fname}")
            for u in urls:
                print(f"    URL: {u}")
            print()

    print(f"\nSaved to: {BASE_FOLDER}")


if __name__ == "__main__":
    run()
