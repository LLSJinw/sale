import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
import requests

# --- Manual Mapping for Known Organizations ---
manual_org_map = {
    "กองทัพเรือ": {
        "Sector": "Government / Defense (CII)",
        "Compliance Pressure": "Thai Cyber Law, ISO 27001",
        "Regulator": "NCSA",
        "Recommended Services": "Cyber Risk Assessment (IT/OT), IRP & Playbook, Tabletop Exercise"
    },
    # Add more exact names here if needed
}

# --- Sector Data with Keywords ---
data = [
    {
        "Sector": "Critical Infrastructure (CII)",
        "Keywords": ["EGAT", "AOT", "PEA", "MEA", "PTT"],
        "Compliance Pressure": "Thai Cyber Law, ISO 27001, NCSA",
        "Regulator": "NCSA",
        "Recommended Services": "Cyber Risk Assessment (IT/OT), Tabletop Exercise, IRP & Playbook, Gap Assessment"
    },
    {
        "Sector": "Banking / Finance / Insurance (BFSI)",
        "Keywords": ["Krungthai", "SCB", "Bangkok Bank", "Muang Thai Life", "TMB"],
        "Compliance Pressure": "PDPA, BOT Regulation, OIC Guidelines",
        "Regulator": "BOT, OIC",
        "Recommended Services": "PDPA Consult, Pentest, Awareness Training, Source Code Scan, IRP"
    },
    {
        "Sector": "Healthcare",
        "Keywords": ["Bumrungrad", "BDMS", "Rama Hospital", "Siriraj"],
        "Compliance Pressure": "PDPA, Thai Cyber Law",
        "Regulator": "PDPC, MOPH",
        "Recommended Services": "PDPA Consult, Cyber Risk Assessment, Awareness Training, Backup Review"
    },
    {
        "Sector": "Government / SOE",
        "Keywords": ["Ministry", "Department", "สำนักงาน", "การทางพิเศษ", "การประปา"],
        "Compliance Pressure": "Thai Cyber Law, อว3/อช3, ISO 27001",
        "Regulator": "ETDA, NCSA",
        "Recommended Services": "Cyber Gap Assessment, อว3/อช3 Consult, IRP, Tabletop Exercise"
    },
    {
        "Sector": "Software / SaaS",
        "Keywords": ["LINE MAN", "SCB Tech X", "Appman", "Bitkub"],
        "Compliance Pressure": "PDPA, Secure SDLC, Thai Cyber Law",
        "Regulator": "PDPC, NCSA",
        "Recommended Services": "Source Code Scan, Pentest, Secure SDLC Advisory"
    },
    {
        "Sector": "Retail / SME / Logistics",
        "Keywords": ["Shopee", "Lazada", "Kerry", "Makro"],
        "Compliance Pressure": "PDPA, BCP/DRP",
        "Regulator": "PDPC",
        "Recommended Services": "Phishing Sim, Awareness Training, PDPA Consult, VA Scan"
    },
    {
        "Sector": "Manufacturing / OT-heavy",
        "Keywords": ["SCG", "IRPC", "Thai Union", "PTTGC"],
        "Compliance Pressure": "Thai Cyber Law, ISO 27001, Supply Chain Risk",
        "Regulator": "NCSA",
        "Recommended Services": "Cyber Risk Assessment (IT/OT), IRP, TTX, Backup/Restore Drill"
    }
]

# Convert to DataFrame for keyword-based lookup
df = pd.DataFrame(data)

def query_wikidata_org_info(org_name):
    query = f'''
    SELECT ?item ?itemLabel ?sectorLabel WHERE {{
      ?item ?label "{org_name}"@th.
      OPTIONAL {{ ?item wdt:P31 ?sector. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,th" }}
    }} LIMIT 1
    '''

    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/sparql-results+json"}
    response = requests.get(url, params={"query": query}, headers=headers)

    if response.status_code == 200:
        results = response.json().get("results", {}).get("bindings", [])
        if results:
            label = results[0].get("itemLabel", {}).get("value", "")
            sector = results[0].get("sectorLabel", {}).get("value", "")
            return label, sector
    return None, None

# --- Streamlit App ---
st.title("🔍 Customer Profiling for Cybersecurity Advisory")
st.markdown("Enter a customer name to find matching sector, compliance, and service needs.")

customer_name = st.text_input("Customer Name")

if customer_name:
    # 1. Manual Mapping First
    if customer_name in manual_org_map:
        result = manual_org_map[customer_name]
        st.success(f"✅ Matched Sector: {result['Sector']}")
        st.markdown(f"**Compliance Pressure:** {result['Compliance Pressure']}")
        st.markdown(f"**Regulator(s):** {result['Regulator']}")
        st.markdown(f"**Recommended Services:** {result['Recommended Services']}")

    else:
        matched = None
        for _, row in df.iterrows():
            # Try fuzzy match
            if any(fuzz.partial_ratio(keyword.lower(), customer_name.lower()) > 85 for keyword in row["Keywords"]):
                matched = row
                break

        if matched is not None:
            st.success(f"✅ Matched Sector: {matched['Sector']}")
            st.markdown(f"**Compliance Pressure:** {matched['Compliance Pressure']}")
            st.markdown(f"**Regulator(s):** {matched['Regulator']}")
            st.markdown(f"**Recommended Services:** {matched['Recommended Services']}")
        else:
            # Try querying Wikidata
            label, sector = query_wikidata_org_info(customer_name)
            if label:
                st.success(f"🌐 Wikidata Match: {label}")
                st.markdown(f"**Sector (from Wikidata):** {sector if sector else 'N/A'}")
                st.info("ℹ️ Please map this result manually to services and compliance later.")
            else:
                st.warning("❗ No match found. Please map this organization manually for future lookups.")

st.markdown("---")
st.caption("This tool uses manual, fuzzy, and Wikidata SPARQL logic. Expand mappings for more coverage.")
