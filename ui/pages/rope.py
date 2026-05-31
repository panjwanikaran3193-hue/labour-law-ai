"""rope.py - Rope Climb with SVG stick figure + large unique question pool"""
import streamlit as st, anthropic, json, os, sys, random
from pathlib import Path
from dotenv import load_dotenv
sys.path.insert(0, str(Path(__file__).parents[1]))
from theme import apply_theme, sidebar_nav, back_button, get_time_of_day, TIME_META
load_dotenv()

st.set_page_config(page_title="Rope Climb", page_icon="🧗", layout="wide")
apply_theme()
sidebar_nav("Rope Climb")

api_key = os.getenv("ANTHROPIC_API_KEY","")
tod  = get_time_of_day()
tc   = TIME_META[tod]["title"]
sc   = TIME_META[tod]["sub"]

st.markdown('<div class="page-title">🧗 Rope Climb Challenge</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">10 questions · Score 5 correct to reach the top!</div>', unsafe_allow_html=True)
back_button()

TOTAL_Q=10; PASS_SCORE=5; RUNGS=5

# ── Large pre-built question bank (50 unique questions) ──────
QUESTION_BANK = [
    {"q":"Under the Payment of Gratuity Act 1972, what is the minimum years of continuous service required for gratuity eligibility?","opts":["A) 3 years","B) 5 years","C) 7 years","D) 10 years"],"ans":"B","exp":"Section 4 of the Payment of Gratuity Act 1972 requires a minimum of 5 years of continuous service."},
    {"q":"Under the Factories Act 1948, what is the maximum number of hours an adult worker can work per week?","opts":["A) 40 hours","B) 48 hours","C) 54 hours","D) 60 hours"],"ans":"B","exp":"Section 51 of the Factories Act 1948 limits adult workers to 48 hours per week."},
    {"q":"The Industrial Disputes Act 1947 defines an 'industry' to include which of the following?","opts":["A) Agricultural operations","B) Domestic service","C) Any business trade or undertaking","D) Government departments only"],"ans":"C","exp":"Section 2(j) of the Industrial Disputes Act 1947 broadly defines industry to include any business, trade, undertaking, manufacture or calling."},
    {"q":"Under the Minimum Wages Act 1948, who is empowered to fix minimum wages?","opts":["A) The Supreme Court","B) The appropriate government","C) Trade unions only","D) Employers association"],"ans":"B","exp":"Section 3 of the Minimum Wages Act 1948 empowers the appropriate government (Central or State) to fix minimum wages."},
    {"q":"Under the Maternity Benefit Act 1961, what is the maximum paid maternity leave for a woman with fewer than two surviving children?","opts":["A) 12 weeks","B) 16 weeks","C) 26 weeks","D) 36 weeks"],"ans":"C","exp":"The Maternity Benefit (Amendment) Act 2017 increased maternity leave to 26 weeks for women with fewer than two surviving children."},
    {"q":"The Employees Provident Fund Act 1952 applies to establishments employing how many or more persons?","opts":["A) 5","B) 10","C) 20","D) 50"],"ans":"C","exp":"The EPF Act 1952 applies to every establishment employing 20 or more persons under Section 1(3)."},
    {"q":"Under the Contract Labour (Regulation and Abolition) Act 1970, a principal employer must obtain a registration certificate if contract labourers exceed how many?","opts":["A) 5","B) 10","C) 20","D) 50"],"ans":"C","exp":"Section 7 of the Contract Labour Act 1970 requires registration when 20 or more contract labourers are employed."},
    {"q":"Under the Payment of Wages Act 1936, wages must be paid before which day of the following month for establishments with fewer than 1000 workers?","opts":["A) 5th","B) 7th","C) 10th","D) 15th"],"ans":"B","exp":"Section 5 of the Payment of Wages Act 1936 requires payment by the 7th of the following month for establishments with fewer than 1000 workers."},
    {"q":"Under the Trade Unions Act 1926, what is the minimum number of members required to register a trade union?","opts":["A) 5","B) 7","C) 10","D) 15"],"ans":"B","exp":"Section 4 of the Trade Unions Act 1926 requires at least 7 members to apply for registration of a trade union."},
    {"q":"The Workmen's Compensation Act 1923 was renamed to which act?","opts":["A) Labour Welfare Act","B) Employee Compensation Act 2010","C) Industrial Injury Act","D) Workers Protection Act"],"ans":"B","exp":"The Workmen's Compensation Act 1923 was renamed the Employee's Compensation Act 2010 by an amendment."},
    {"q":"Under the Factories Act 1948, children below what age are prohibited from working in factories?","opts":["A) 12 years","B) 14 years","C) 16 years","D) 18 years"],"ans":"B","exp":"Section 67 of the Factories Act 1948 prohibits employment of children below 14 years of age in any factory."},
    {"q":"Under the Industrial Disputes Act 1947, how many days notice must an employer in a public utility service give before a strike or lockout?","opts":["A) 7 days","B) 14 days","C) 21 days","D) 28 days"],"ans":"B","exp":"Section 22 of the Industrial Disputes Act 1947 requires 14 days notice before a strike or lockout in public utility services."},
    {"q":"The gratuity amount under the Payment of Gratuity Act 1972 is calculated at what rate per year of service?","opts":["A) 7 days wages","B) 10 days wages","C) 15 days wages","D) 30 days wages"],"ans":"C","exp":"Section 4(2) provides that gratuity is calculated at 15 days wages for each completed year of service."},
    {"q":"Under the Maternity Benefit Act 1961, how many weeks before expected delivery can a woman avail maternity leave?","opts":["A) 4 weeks","B) 6 weeks","C) 8 weeks","D) 12 weeks"],"ans":"C","exp":"Section 5 of the Maternity Benefit Act allows a woman to take leave up to 8 weeks before the expected delivery date."},
    {"q":"Under the EPF Act 1952, what percentage of basic wages does the employee contribute to the provident fund?","opts":["A) 8%","B) 10%","C) 12%","D) 15%"],"ans":"C","exp":"The standard employee contribution to the EPF is 12% of basic wages and dearness allowance under the EPF Scheme 1952."},
    {"q":"Under the Industrial Disputes Act 1947, what is the minimum number of workmen required to constitute a 'Works Committee'?","opts":["A) 50","B) 75","C) 100","D) 200"],"ans":"C","exp":"Section 3 of the Industrial Disputes Act 1947 mandates Works Committees in establishments employing 100 or more workmen."},
    {"q":"The Bonus Act (Payment of Bonus Act 1965) applies to establishments employing how many or more persons?","opts":["A) 10","B) 20","C) 50","D) 100"],"ans":"B","exp":"The Payment of Bonus Act 1965 applies to every factory and establishment employing 20 or more persons under Section 1(3)."},
    {"q":"Under the Factories Act 1948, what is the maximum overtime hours an adult worker can work in a quarter?","opts":["A) 50 hours","B) 75 hours","C) 100 hours","D) 150 hours"],"ans":"B","exp":"Section 64 of the Factories Act 1948 limits overtime work to 75 hours in any quarter."},
    {"q":"Under the Payment of Wages Act 1936, what deductions from wages are permissible?","opts":["A) For absence from duty","B) For personal loans","C) At employer's discretion","D) No deductions allowed"],"ans":"A","exp":"Section 7 of the Payment of Wages Act 1936 permits deductions for fines, absence from duty, accommodation provided, and similar specified reasons."},
    {"q":"Under the Industrial Employment (Standing Orders) Act 1946, it applies to industrial establishments employing how many workers?","opts":["A) 50","B) 75","C) 100","D) 200"],"ans":"C","exp":"The Industrial Employment (Standing Orders) Act 1946 applies to industrial establishments employing 100 or more workmen."},
    {"q":"Under the Employees State Insurance Act 1948, the employer's contribution rate is what percentage of wages?","opts":["A) 1.75%","B) 2.25%","C) 3.25%","D) 4.75%"],"ans":"C","exp":"The employer's ESI contribution rate is 3.25% of wages payable to employees covered under the ESI Act 1948."},
    {"q":"Under the Child Labour (Prohibition and Regulation) Act 1986, children below what age cannot be employed in any occupation?","opts":["A) 12 years","B) 14 years","C) 16 years","D) 18 years"],"ans":"B","exp":"The Child Labour Act as amended in 2016 prohibits employment of children below 14 years in any occupation or process."},
    {"q":"The minimum bonus payable under the Payment of Bonus Act 1965 is what percentage of wages?","opts":["A) 4%","B) 7%","C) 8.33%","D) 10%"],"ans":"C","exp":"Section 10 of the Payment of Bonus Act 1965 provides for a minimum bonus of 8.33% of annual wages or salary."},
    {"q":"Under the Industrial Disputes Act 1947, retrenchment compensation is payable at what rate?","opts":["A) 7 days wages per year","B) 10 days wages per year","C) 15 days wages per year","D) 30 days wages per year"],"ans":"C","exp":"Section 25F of the Industrial Disputes Act 1947 requires retrenchment compensation at 15 days average pay for each completed year of service."},
    {"q":"Under the Factories Act 1948, the occupier must serve a written notice to the Chief Inspector before starting a new factory with how many days notice?","opts":["A) 7 days","B) 15 days","C) 30 days","D) 60 days"],"ans":"B","exp":"Section 6 of the Factories Act 1948 requires 15 days written notice to the Chief Inspector before a factory begins operations."},
    {"q":"Under the EPF Act 1952, which authority handles the settlement of disputes?","opts":["A) Labour Court","B) Central Government","C) EPF Appellate Tribunal","D) High Court only"],"ans":"C","exp":"Disputes under the EPF Act are adjudicated by the EPF Appellate Tribunal under Section 7-I of the Act."},
    {"q":"The Equal Remuneration Act 1976 prohibits discrimination in pay on what basis?","opts":["A) Age","B) Religion","C) Gender","D) Caste"],"ans":"C","exp":"The Equal Remuneration Act 1976 mandates equal pay for equal work for men and women, prohibiting gender-based wage discrimination."},
    {"q":"Under the Shops and Establishments Act, establishments must generally close on how many days per week as weekly off?","opts":["A) Half day Saturday","B) One full day","C) Two days","D) No compulsory weekly off"],"ans":"B","exp":"Most State Shops and Establishments Acts require at least one day of weekly rest for every worker."},
    {"q":"Under the Maternity Benefit Act 1961, the nursing break period for a woman who has delivered is for how long after return to work?","opts":["A) 3 months","B) 6 months","C) 12 months","D) 15 months"],"ans":"C","exp":"Section 11 of the Maternity Benefit Act 1961 entitles women to nursing breaks until the child is 15 months old — effectively up to 15 months after delivery."},
    {"q":"Under the Factories Act 1948, the annual leave with wages is calculated at what rate?","opts":["A) 1 day per 10 days worked","B) 1 day per 15 days worked","C) 1 day per 20 days worked","D) 1 day per 30 days worked"],"ans":"C","exp":"Section 79 of the Factories Act 1948 provides 1 day of earned leave for every 20 days of work for adult workers."},
    {"q":"Under the Industrial Disputes Act 1947, which body is empowered to adjudicate industrial disputes?","opts":["A) Works Committee","B) Conciliation Officer","C) Labour Court","D) All of the above"],"ans":"D","exp":"The Industrial Disputes Act 1947 establishes multiple bodies — Works Committees, Conciliation Officers, Boards of Conciliation, Courts of Inquiry, Labour Courts, and Industrial Tribunals."},
    {"q":"The maximum penalty for employing a child in a hazardous occupation under the Child Labour Act is imprisonment up to how many years?","opts":["A) 1 year","B) 2 years","C) 3 years","D) 5 years"],"ans":"C","exp":"The Child Labour (Prohibition and Regulation) Amendment Act 2016 prescribes imprisonment of up to 3 years for employing children in hazardous occupations."},
    {"q":"Under the ESI Act 1948, what is the employee contribution rate?","opts":["A) 0.75%","B) 1.75%","C) 2.25%","D) 3.25%"],"ans":"A","exp":"The employee ESI contribution rate is 0.75% of wages as amended effective 2020."},
    {"q":"Under the Minimum Wages Act 1948, what is the review period for revising minimum wages?","opts":["A) Every year","B) Every 2 years","C) Every 3 years","D) Every 5 years"],"ans":"D","exp":"Section 3(1)(b) of the Minimum Wages Act 1948 requires review and revision of minimum wages at intervals not exceeding 5 years."},
    {"q":"The Unorganised Workers' Social Security Act was enacted in which year?","opts":["A) 2004","B) 2006","C) 2008","D) 2010"],"ans":"C","exp":"The Unorganised Workers' Social Security Act was enacted in 2008 to provide social security to workers in the unorganised sector."},
    {"q":"Under the Payment of Gratuity Act 1972, what is the maximum ceiling on gratuity payable?","opts":["A) Rs 10 lakh","B) Rs 15 lakh","C) Rs 20 lakh","D) Rs 25 lakh"],"ans":"C","exp":"As per the Payment of Gratuity (Amendment) Act 2018, the maximum gratuity ceiling is Rs 20 lakh."},
    {"q":"Under the Industrial Disputes Act 1947, establishments employing how many workers must seek government permission before retrenchment?","opts":["A) 50","B) 100","C) 300","D) 500"],"ans":"B","exp":"Chapter VB of the Industrial Disputes Act 1947 requires prior government permission for retrenchment in establishments employing 100 or more workers."},
    {"q":"The National Floor Level Minimum Wage is fixed by which body?","opts":["A) State Government","B) Central Government","C) Planning Commission","D) Labour Court"],"ans":"B","exp":"The Central Government fixes the National Floor Level Minimum Wage as a benchmark below which no State can fix minimum wages."},
    {"q":"Under the Factories Act 1948, a factory must have a Safety Officer if it employs how many workers?","opts":["A) 500","B) 1000","C) 1500","D) 2000"],"ans":"B","exp":"Section 40-B of the Factories Act 1948 requires appointment of a Safety Officer in factories employing 1000 or more workers."},
    {"q":"Under the Building and Other Construction Workers Act 1996, workers must be registered after how many days of employment?","opts":["A) 30 days","B) 60 days","C) 90 days","D) 180 days"],"ans":"C","exp":"The BOCW Act 1996 requires registration of workers who have been employed for 90 days or more in building or construction work."},
    {"q":"Under the Contract Labour Act 1970, the contractor must issue a service certificate to every worker on termination within how many days?","opts":["A) 7 days","B) 14 days","C) 30 days","D) 60 days"],"ans":"C","exp":"Rule 75 of the Contract Labour (Regulation and Abolition) Central Rules 1971 requires the contractor to issue service certificates within 30 days of termination."},
    {"q":"The Employees Deposit Linked Insurance Scheme (EDLI) 1976 provides life insurance cover linked to which fund?","opts":["A) Gratuity Fund","B) ESI Fund","C) EPF Fund","D) Welfare Fund"],"ans":"C","exp":"The EDLI Scheme 1976 is linked to the Employees Provident Fund and provides life insurance cover to EPF members."},
    {"q":"Under the Trade Unions Act 1926, a registered trade union must spend what minimum percentage of its funds on executive members' emoluments?","opts":["A) No limit","B) Not more than half","C) Not more than one-third","D) Not more than one-fourth"],"ans":"B","exp":"Section 15 of the Trade Unions Act 1926 restricts expenditure on executive members to not more than half of the union's total funds."},
    {"q":"Under the Payment of Bonus Act 1965, the allocable surplus is what percentage of the available surplus?","opts":["A) 50%","B) 60%","C) 67%","D) 75%"],"ans":"C","exp":"Section 2(4) of the Payment of Bonus Act 1965 defines allocable surplus as 67% of the available surplus for non-banking companies."},
    {"q":"The Apprentices Act 1961 requires apprenticeship training in establishments employing how many workers?","opts":["A) 10","B) 25","C) 50","D) 100"],"ans":"B","exp":"The Apprentices Act 1961 applies to establishments employing 25 or more workers, requiring them to engage apprentices in designated trades."},
    {"q":"Under the Maternity Benefit Act 1961, what is the leave entitlement for adopting mothers?","opts":["A) 6 weeks","B) 8 weeks","C) 12 weeks","D) 26 weeks"],"ans":"C","exp":"Section 5(4) of the Maternity Benefit Amendment Act 2017 provides 12 weeks of maternity benefit to women who legally adopt a child below 3 months of age."},
    {"q":"Under the Factories Act 1948, the maximum permissible noise level in a workplace is how many decibels?","opts":["A) 75 dB","B) 85 dB","C) 90 dB","D) 95 dB"],"ans":"C","exp":"Schedule III of the Factories Act specifies that the permissible exposure limit for noise is 90 dB(A) for 8 hours per day."},
    {"q":"The Sexual Harassment of Women at Workplace Act 2013 requires every employer to constitute an Internal Complaints Committee if the organization employs how many workers?","opts":["A) 5","B) 10","C) 20","D) 50"],"ans":"B","exp":"Section 4 of the POSH Act 2013 requires every employer with 10 or more employees to constitute an Internal Complaints Committee."},
    {"q":"Under the Industrial Disputes Act 1947, the conciliation officer must submit a report within how many days of the commencement of conciliation proceedings in a public utility service dispute?","opts":["A) 14 days","B) 21 days","C) 30 days","D) 45 days"],"ans":"A","exp":"Section 12(6) of the Industrial Disputes Act 1947 requires the conciliation officer to submit a report within 14 days in public utility service disputes."},
    {"q":"Under the EPF Act 1952, an employer who defaults on EPF contributions is liable to pay damages at what rate?","opts":["A) 5% per annum","B) 12% per annum","C) Up to 25% of arrears","D) Up to 100% of arrears"],"ans":"C","exp":"Section 14B of the EPF Act 1952 empowers the authority to levy damages of up to 25% of the amount in default, depending on the period of default."},
]

defaults={"rp_started":False,"rp_pos":0,"rp_score":0,"rp_attempts":0,
          "rp_question":None,"rp_won":False,"rp_lost":False,
          "rp_answered":False,"rp_asked_ids":[],"rp_last":None,
          "rp_shuffled_pool":None}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

def get_next_question():
    """Pick next question from shuffled pool, never repeating."""
    if st.session_state.rp_shuffled_pool is None:
        pool = list(range(len(QUESTION_BANK)))
        random.shuffle(pool)
        st.session_state.rp_shuffled_pool = pool

    pool    = st.session_state.rp_shuffled_pool
    used    = st.session_state.rp_asked_ids
    remaining = [i for i in pool if i not in used]

    if not remaining:
        # All used — reshuffle excluding recently used
        pool = list(range(len(QUESTION_BANK)))
        random.shuffle(pool)
        st.session_state.rp_shuffled_pool = pool
        remaining = pool

    idx = remaining[0]
    st.session_state.rp_asked_ids.append(idx)
    q = QUESTION_BANK[idx]
    return {"question": q["q"], "options": q["opts"], "answer": q["ans"], "explanation": q["exp"]}

def reset():
    for k,v in defaults.items(): st.session_state[k]=v

pos = st.session_state.rp_pos

# ── SVG rope with stick figure ────────────────────────────────
def make_rope_svg(pos, rungs=5):
    import math
    W, H   = 210, 480
    cx     = W // 2
    top_y  = 55
    bot_y  = H - 44
    seg_h  = (bot_y - top_y) / rungs

    # Figure position
    fig_y = bot_y - 12 if pos == 0 else bot_y - pos * seg_h
    head_r = 11
    hy = fig_y - 26 - head_r   # head centre y
    hx = cx

    # Alternating arm/leg pose for climbing feel
    reach_right = (pos % 2 == 0)
    if reach_right:
        la1x,la1y = hx-5, hy+head_r+6
        la2x,la2y = hx+0, hy-14         # right arm UP grabbing rope
        ra1x,ra1y = hx+5, hy+head_r+10
        ra2x,ra2y = hx+18, hy+head_r+22 # left arm down/out
        ll2x,ll2y = cx+16, fig_y+8      # legs alternating
        rl2x,rl2y = cx-6,  fig_y+22
    else:
        la1x,la1y = hx+5, hy+head_r+6
        la2x,la2y = hx+0, hy-14         # left arm UP
        ra1x,ra1y = hx-5, hy+head_r+10
        ra2x,ra2y = hx-18, hy+head_r+22
        ll2x,ll2y = cx-16, fig_y+8
        rl2x,rl2y = cx+6,  fig_y+22

    bob_anim = "animation:bob 1.5s ease-in-out infinite;" if pos < rungs else "animation:celebrate 0.7s ease-in-out infinite;"

    lines = [
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">',
        "<defs>",
        "<style>",
        "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}",
        "@keyframes celebrate{0%,100%{transform:rotate(0deg) scale(1)}25%{transform:rotate(-8deg) scale(1.08)}75%{transform:rotate(8deg) scale(1.08)}}",
        "@keyframes twinkle{0%,100%{opacity:.3}50%{opacity:1}}",
        "</style>",
        '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#0a0e27"/>',
        '<stop offset="55%" stop-color="#1a237e"/>',
        '<stop offset="100%" stop-color="#1b5e20"/>',
        "</linearGradient>",
        '<linearGradient id="rg" x1="0" y1="0" x2="1" y2="0">',
        '<stop offset="0%" stop-color="#5d4037"/>',
        '<stop offset="50%" stop-color="#bcaaa4"/>',
        '<stop offset="100%" stop-color="#5d4037"/>',
        "</linearGradient>",
        "</defs>",
        f'<rect width="{W}" height="{H}" rx="16" fill="url(#bg)"/>',
    ]

    # Twinkling stars
    star_data = [(20,15,1.0),(66,10,1.3),(142,26,1.0),(166,9,1.4),(40,50,1.1),
                 (115,18,1.2),(156,60,1.0),(30,70,1.3),(86,7,1.0),(106,40,1.1),
                 (178,33,1.2),(14,86,0.9)]
    for i,(sx,sy,sr) in enumerate(star_data):
        delay = i * 0.3
        lines.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="rgba(255,255,255,0.8)" style="animation:twinkle {1.5+delay:.1f}s ease-in-out infinite;"/>')

    # Trophy / goal
    lines.append(f'<text x="{cx}" y="32" text-anchor="middle" font-size="22" fill="#FFD700">&#9733;</text>')
    lines.append(f'<text x="{cx}" y="48" text-anchor="middle" font-size="9" fill="#FFE082" font-weight="bold" font-family="sans-serif">TOP</text>')

    # Main rope
    lines.append(f'<line x1="{cx}" y1="{top_y}" x2="{cx}" y2="{bot_y}" stroke="url(#rg)" stroke-width="8" stroke-linecap="round"/>')
    lines.append(f'<line x1="{cx}" y1="{top_y}" x2="{cx}" y2="{bot_y}" stroke="rgba(255,255,255,0.08)" stroke-width="3" stroke-dasharray="6,8"/>')

    # Rungs
    for r in range(1, rungs+1):
        ry     = bot_y - r * seg_h
        done   = pos >= r
        col    = "#FFB300" if done else "rgba(255,255,255,0.25)"
        lcol   = "#FFE082" if done else "rgba(255,255,255,0.38)"
        glow   = ' filter="url(#gl)"' if done else ""
        lines.append(f'<line x1="{cx-30}" y1="{ry}" x2="{cx+30}" y2="{ry}" stroke="{col}" stroke-width="5" stroke-linecap="round"{glow}/>')
        lines.append(f'<text x="{cx+36}" y="{ry+4}" font-size="9" fill="{lcol}" font-family="sans-serif" font-weight="bold">R{r}</text>')

    # Ground
    lines.append(f'<ellipse cx="{cx}" cy="{bot_y+12}" rx="26" ry="6" fill="rgba(46,125,50,0.65)"/>')
    lines.append(f'<text x="{cx}" y="{H-9}" text-anchor="middle" font-size="8" fill="rgba(100,200,100,0.85)" font-family="sans-serif" font-weight="bold">START</text>')

    # Celebration stars if won
    if pos >= rungs:
        for angle in range(0, 360, 60):
            sx2 = hx + 38 * math.cos(math.radians(angle))
            sy2 = hy + 38 * math.sin(math.radians(angle))
            lines.append(f'<text x="{sx2:.0f}" y="{sy2:.0f}" text-anchor="middle" font-size="10" fill="#FFD700" style="animation:twinkle {0.6+angle/500:.2f}s ease-in-out infinite;">&#9733;</text>')

    # Glow halo at top
    if pos >= rungs:
        lines.append(f'<circle cx="{hx}" cy="{hy}" r="32" fill="none" stroke="rgba(255,215,0,0.3)" stroke-width="10"/>')

    # ── Stick figure (animated group) ──
    lines.append(f'<g style="{bob_anim}">')

    # Head
    lines.append(f'<circle cx="{hx}" cy="{hy}" r="{head_r}" fill="none" stroke="#FFFFFF" stroke-width="2.5"/>')
    # Eyes
    lines.append(f'<circle cx="{hx-3.5}" cy="{hy-2}" r="1.5" fill="#FFFFFF"/>')
    lines.append(f'<circle cx="{hx+3.5}" cy="{hy-2}" r="1.5" fill="#FFFFFF"/>')
    # Smile (happy when progressing, bigger when winning)
    if pos >= rungs:
        lines.append(f'<path d="M {hx-5} {hy+3} Q {hx} {hy+9} {hx+5} {hy+3}" fill="none" stroke="#FFD700" stroke-width="1.8" stroke-linecap="round"/>')
    else:
        lines.append(f'<path d="M {hx-4} {hy+3} Q {hx} {hy+7} {hx+4} {hy+3}" fill="none" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round"/>')

    # Helmet at top
    if pos >= rungs:
        lines.append(f'<path d="M {hx-12} {hy-head_r+3} Q {hx} {hy-head_r-15} {hx+12} {hy-head_r+3}" fill="#FFD700" stroke="#FFB300" stroke-width="1.5"/>')

    # Body
    lines.append(f'<line x1="{hx}" y1="{hy+head_r}" x2="{hx}" y2="{fig_y}" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>')

    # Arms (alternate pose to simulate climbing)
    lines.append(f'<line x1="{la1x}" y1="{la1y}" x2="{la2x}" y2="{la2y}" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round"/>')
    lines.append(f'<line x1="{ra1x}" y1="{ra1y}" x2="{ra2x}" y2="{ra2y}" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round"/>')

    # Legs (alternate)
    lines.append(f'<line x1="{cx}" y1="{fig_y}" x2="{ll2x}" y2="{ll2y}" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round"/>')
    lines.append(f'<line x1="{cx}" y1="{fig_y}" x2="{rl2x}" y2="{rl2y}" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round"/>')

    lines.append("</g>")
    lines.append("</svg>")
    return "\n".join(lines)


# ── Layout ────────────────────────────────────────────────────
left, right = st.columns([1, 2])

with left:
    st.markdown("""
    <style>
    .svgwrap{display:flex;justify-content:center;margin-bottom:6px;}
    .svgwrap svg{border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,0.6);}
    .stat-row{display:flex;gap:6px;margin-top:8px;}
    .stat-cell{flex:1;text-align:center;padding:6px 2px;
        background:rgba(0,0,0,0.5);border-radius:10px;
        border:1px solid rgba(255,255,255,0.18);}
    .stat-val{font-size:1.3rem;font-weight:900;line-height:1.2;}
    .stat-lbl{font-size:9px;font-weight:700;opacity:0.7;letter-spacing:1px;}
    .prog-wrap{width:100%;background:rgba(255,255,255,0.15);border-radius:20px;height:7px;margin-top:8px;overflow:hidden;}
    .prog-fill{height:100%;border-radius:20px;background:linear-gradient(90deg,#66bb6a,#FFB300);transition:width 0.6s ease;}
    .prog-txt{font-size:9px;font-weight:700;text-align:center;margin-top:4px;opacity:0.7;font-family:sans-serif;}
    </style>
    """, unsafe_allow_html=True)

    svg = make_rope_svg(pos, RUNGS)
    st.markdown(f'<div class="svgwrap">{svg}</div>', unsafe_allow_html=True)

    pct = int(pos/RUNGS*100)
    st.markdown(
        '<div class="stat-row">'
        f'<div class="stat-cell"><div class="stat-val" style="color:{tc};">{st.session_state.rp_score}</div><div class="stat-lbl" style="color:{sc};">CORRECT</div></div>'
        f'<div class="stat-cell"><div class="stat-val" style="color:{tc};">{st.session_state.rp_attempts}</div><div class="stat-lbl" style="color:{sc};">TRIED</div></div>'
        f'<div class="stat-cell"><div class="stat-val" style="color:{tc};">{TOTAL_Q-st.session_state.rp_attempts}</div><div class="stat-lbl" style="color:{sc};">LEFT</div></div>'
        '</div>'
        f'<div class="prog-wrap"><div class="prog-fill" style="width:{pct}%;"></div></div>'
        f'<div class="prog-txt" style="color:{sc};">{pos}/{RUNGS} rungs &bull; need {PASS_SCORE} to win</div>',
        unsafe_allow_html=True)

with right:
    qbox = 'background:rgba(0,0,0,0.5);backdrop-filter:blur(14px);border:2px solid rgba(255,255,255,0.22);border-radius:18px;padding:1.5rem;'

    if st.session_state.rp_won:
        st.balloons()
        st.markdown(
            f'<div style="{qbox}border-color:rgba(255,179,0,0.55);text-align:center;">'
            '<div style="font-size:3rem;margin-bottom:0.5rem;">&#9733;</div>'
            f'<div style="font-family:Cormorant Garamond,serif;font-size:1.8rem;font-weight:900;color:#FFD700;text-shadow:0 2px 16px rgba(255,179,0,0.7);">YOU REACHED THE TOP!</div>'
            f'<div style="color:{sc};margin-top:0.5rem;">Outstanding knowledge of Indian Labour Law!</div>'
            '</div>', unsafe_allow_html=True)
        if st.button("🔄 Play Again", use_container_width=True): reset(); st.rerun()

    elif st.session_state.rp_lost:
        st.markdown(
            f'<div style="{qbox}text-align:center;">'
            '<div style="font-size:2.5rem;margin-bottom:0.5rem;">&#128218;</div>'
            f'<div style="font-family:Cormorant Garamond,serif;font-size:1.3rem;font-weight:700;color:{tc};">{st.session_state.rp_score}/{TOTAL_Q} — Keep Studying!</div>'
            f'<div style="color:{sc};margin-top:0.5rem;">Need {PASS_SCORE} correct — {PASS_SCORE-st.session_state.rp_score} more next time!</div>'
            '</div>', unsafe_allow_html=True)
        if st.button("🔄 Try Again", use_container_width=True): reset(); st.rerun()

    elif not st.session_state.rp_started:
        st.markdown(
            f'<div style="{qbox}text-align:center;">'
            '<div style="font-size:2.5rem;margin-bottom:0.8rem;">&#x1F9D7;</div>'
            f'<div style="font-family:Cormorant Garamond,serif;font-size:1.4rem;font-weight:900;color:{tc};">Ready to Climb?</div>'
            f'<div style="color:{sc};margin-top:0.8rem;font-size:0.9rem;line-height:1.8;">'
            '10 questions &bull; score 5 correct to win<br>'
            'Stick figure climber rises with every correct answer<br>'
            '50 unique questions &bull; never repeats in a session</div></div>',
            unsafe_allow_html=True)
        st.write("")
        if st.button("🚀 Start Climbing!", use_container_width=True):
            st.session_state.rp_started = True
            q = get_next_question()
            st.session_state.rp_question = q
            st.rerun()

    else:
        q   = st.session_state.rp_question
        att = st.session_state.rp_attempts
        if q:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">'
                f'<span style="font-size:0.78rem;color:{sc};font-weight:700;text-shadow:0 1px 4px rgba(0,0,0,0.9);">Question {att+1} of {TOTAL_Q}</span>'
                f'<span style="font-size:0.78rem;color:{tc};font-weight:700;text-shadow:0 1px 4px rgba(0,0,0,0.9);">{st.session_state.rp_score} correct</span>'
                f'</div>'
                f'<div style="{qbox}">'
                f'<div style="font-family:Cormorant Garamond,serif;font-size:1.12rem;font-weight:700;line-height:1.55;color:{tc};">&#10067; {q["question"]}</div>'
                f'</div>',
                unsafe_allow_html=True)

            if not st.session_state.rp_answered:
                choice = st.radio("Choose your answer:", q["options"], key="rope_"+str(att), index=None)
                if choice:
                    st.session_state.rp_attempts += 1
                    correct = choice[0] == q["answer"]
                    if correct:
                        st.session_state.rp_score += 1
                        st.session_state.rp_pos = min(st.session_state.rp_score, RUNGS)
                    st.session_state.rp_last     = (correct, q["answer"], q["explanation"])
                    st.session_state.rp_answered  = True
                    if st.session_state.rp_score >= PASS_SCORE:   st.session_state.rp_won  = True
                    elif st.session_state.rp_attempts >= TOTAL_Q: st.session_state.rp_lost = True
                    st.rerun()
            else:
                ok, ans, exp = st.session_state.rp_last
                if ok: st.success("✅ Correct! Climber moves up a rung!")
                else:  st.error(f"❌ Wrong. Correct answer: {ans}")
                st.info(f"💡 {exp}")
                if not st.session_state.rp_won and not st.session_state.rp_lost:
                    if st.button("➡️ Next Question", use_container_width=True):
                        st.session_state.rp_answered = False
                        st.session_state.rp_question = get_next_question()
                        st.rerun()

st.markdown('<div class="grass-strip">🌱🌿🍃🌾🌿🌱🌾🍃🌿🌱</div>', unsafe_allow_html=True)
