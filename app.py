import streamlit as st
import requests
import pandas as pd
from rapidfuzz import fuzz

# --- Sector Mapping Table (Thai-sector-specific) ---
sector_data = [
    {
        "Sector": "Critical Infrastructure (CII)",
        "Keywords": ["ไฟฟ้า", "สนามบิน", "น้ำมัน", "ประปา", "EGAT", "AOT", "MEA", "PTT", "electricity", "airport", "refined petroleum"],
        "Recommended Services": "Cyber Risk Assessment (IT/OT), TTX, IRP & Playbook, BCP Alignment"
    },
    {
        "Sector": "Banking / Finance / Insurance (BFSI)",
        "Keywords": ["ธนาคาร", "bank", "insurance", "Krungthai", "SCB", "TMB", "financial", "fintech"],
        "Recommended Services": "PDPA Consult, Pentest, Source Code Scan, IRP & Playbook"
    },
    {
        "Sector": "Healthcare",
        "Keywords": ["hospital", "healthcare", "pharma", "clinic", "ศิริราช", "BDMS", "รพ", "medic", "health"],
        "Recommended Services": "PDPA Consult, IRP, TTX, Backup Review, Phishing Simulation"
    },
    {
        "Sector": "Government / SOE",
        "Keywords": ["government", "กระทรวง", "ministry", "department", "state enterprise", "SOE", "สำนักงาน"],
        "Recommended Services": "อว3/อช3 Consult, TTX, Cyber Gap Assessment, IRP"
    },
    {
        "Sector": "Telco / ISP",
        "Keywords": ["AIS", "NT", "True", "โทรคมนาคม", "telecom", "ISP"],
        "Recommended Services": "Zero Trust Readiness, CSOC, Gap Assessment, IRP"
    },
    {
        "Sector": "Software / SaaS / Tech",
        "Keywords": ["software", "SaaS", "Dev", "Bitkub", "LINE MAN", "Appman", "developer", "platform"],
        "Recommended Services": "Secure SDLC Advisory, Source Code Scan, Pentest"
    },
    {
        "Sector": "Retail / SME / Logistics",
        "Keywords": ["Shopee", "Makro", "Lazada", "ค้าปลีก", "SME", "logistics", "retail", "warehouse"],
        "Recommended Services": "Phishing Sim, VA Scan, PDPA Consult, Awareness Training"
    },
    {
        "Sector": "Manufacturing / OT-heavy",
        "Keywords": ["SCG", "โรงงาน", "factory", "industry", "industrial", "manufacture", "production"],
        "Recommended Services": "Cyber Risk Assessment (IT/OT), IRP, TTX, Backup/Restore Drill"
    }
]

df_sector = pd.DataFrame(sector_data)

# --- Fuzzy Sector Mapping ---
def fuzzy_sector_match(text):
    best_score = 0
    best_sector = None
    for _, row in df_sector.iterrows():
        for keyword in row["Keywords"]:
            score = fuzz.partial_ratio(keyword.lower(), text.lower())
            if score > best_score:
                best_score = score
                best_sector = {
                    "Sector": row["Sector"],
                    "Match Keyword": keyword,
                    "Score": score,
                    "Recommended Services": row["Recommended Services"]
                }
    return best_sector if best_score >= 60 else None

# --- OpenCorporates Lookup ---
def get_opencorporates_data(name):
    try:
        url = f"https://api.opencorporates.com/v0.4/companies/search?q={name}&jurisdiction_code=th"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            items = r.json().get("results", {}).get("companies", [])
            candidates = []
            for c in items[:3]:  # top 3 only
                company = c["company"]
                label = company.get("name", "")
                industry_list = company.get("industry_codes", [])
                industry_desc = industry_list[0]["description"] if industry_list else "N/A"
                sector_result = fuzzy_sector_match(industry_desc) or {}
                candidates.append({
                    "Company Name": label,
                    "Industry": industry_desc,
                    "Sector Match": sector_result.get("Sector", "Unmapped"),
                    "Match Keyword": sector_result.get("Match Keyword", "-"),
                    "Score": sector_result.get("Score", 0),
                    "Recommended Services": sector_result.get("Recommended Services", "N/A")
                })
            return candidates
    except:
        return []
    return []

# --- UI Layout ---
st.title("🔎 Thai Company Sector Matcher (Hybrid Intelligence)")
st.markdown("Input a company name to discover matching sector and advisory services.")

user_input = st.text_input("Enter Thai org name or abbreviation:")

if user_input:
    st.markdown("---")
    st.markdown("### 🧠 External Intelligence (OpenCorporates)")
    top_candidates = get_opencorporates_data(user_input)

    if top_candidates:
        df_results = pd.DataFrame(top_candidates)
        st.dataframe(df_results[["Company Name", "Industry", "Sector Match", "Recommended Services"]])
    else:
        st.warning("No result from OpenCorporates.")

    st.markdown("---")
    st.markdown("### 🔍 Local Fuzzy Matching (Backup)")
    local_match = fuzzy_sector_match(user_input)
    if local_match:
        st.success(f"Local Match: **{local_match['Sector']}**")
        st.markdown(f"**Keyword Matched:** {local_match['Match Keyword']}")
        st.markdown(f"**Recommended Services:** {local_match['Recommended Services']}")
    else:
        st.warning("No strong local keyword match. Try expanding keyword table.")
