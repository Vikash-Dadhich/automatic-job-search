"""Check candidate Workday career sites before adding them to targets.yaml.

One search request per site ("intern"). Prints which sites answer and how many
internship titles there look like product, consulting or strategy roles. Reads
only; no scoring, no database.
"""

from __future__ import annotations

import asyncio
import sys

import httpx

from config.targets import parse_workday_url
from scraper.title_family import CONSULTING, PRODUCT, STRATEGY, title_family

CANDIDATES = {
    "Accenture": "https://accenture.wd103.myworkdayjobs.com/AccentureCareers",
    "PwC": "https://pwc.wd3.myworkdayjobs.com/Global_Experienced_Careers",
    "PwC US Campus": "https://pwc.wd3.myworkdayjobs.com/US_Entry_Level_Careers",
    "KPMG": "https://kpmg.wd5.myworkdayjobs.com/KPMG_US_Careers",
    "Guidehouse": "https://guidehouse.wd1.myworkdayjobs.com/External",
    "Huron": "https://huron.wd1.myworkdayjobs.com/huroncareers",
    "ZS Associates": "https://zs.wd1.myworkdayjobs.com/ZS_Careers",
    "Marsh McLennan (Oliver Wyman)": "https://mmc.wd1.myworkdayjobs.com/MMC",
    "Kearney": "https://kearney.wd3.myworkdayjobs.com/Kearney",
    "Ankura": "https://ankura.wd5.myworkdayjobs.com/Ankura",
    "FTI Consulting": "https://fticonsulting.wd1.myworkdayjobs.com/FTI_Careers",
    "Alvarez & Marsal": "https://alvarezandmarsal.wd1.myworkdayjobs.com/AM",
    "Slalom": "https://slalom.wd5.myworkdayjobs.com/Slalom_Careers",
    "West Monroe": "https://westmonroe.wd1.myworkdayjobs.com/WestMonroe",
    "Capgemini": "https://capgemini.wd3.myworkdayjobs.com/Capgemini_Careers",
    "Gartner": "https://gartner.wd5.myworkdayjobs.com/EXT",
    "Cognizant": "https://cognizant.wd1.myworkdayjobs.com/Cognizant_Careers",
    "Booz Allen": "https://bah.wd1.myworkdayjobs.com/BAH_Jobs",
    "Grant Thornton": "https://gt.wd1.myworkdayjobs.com/GT_Careers",
    "RSM": "https://rsm.wd1.myworkdayjobs.com/RSMCareers",
    "Protiviti": "https://roberthalf.wd1.myworkdayjobs.com/Protiviti",
    "Bain": "https://bain.wd1.myworkdayjobs.com/Bain_Careers",
    "L.E.K.": "https://lek.wd1.myworkdayjobs.com/LEK",
    "Intel": "https://intel.wd1.myworkdayjobs.com/External",
    "Cisco": "https://cisco.wd5.myworkdayjobs.com/Cisco_Careers",
    "Visa": "https://visa.wd5.myworkdayjobs.com/Visa_Early_Careers",
    "Mastercard": "https://mastercard.wd1.myworkdayjobs.com/CorporateCareers",
    "PayPal": "https://paypal.wd1.myworkdayjobs.com/jobs",
    "Expedia": "https://expedia.wd108.myworkdayjobs.com/search",
    "T-Mobile": "https://tmobile.wd1.myworkdayjobs.com/External",
    "Walmart": "https://walmart.wd5.myworkdayjobs.com/WalmartExternal",
    "Target": "https://target.wd5.myworkdayjobs.com/targetcareers",
    "Dell": "https://dell.wd1.myworkdayjobs.com/External",
    "HP": "https://hp.wd5.myworkdayjobs.com/ExternalCareerSite",
    "Capital One": "https://capitalone.wd12.myworkdayjobs.com/Capital_One",
    "American Express": "https://aexp.wd1.myworkdayjobs.com/AEXP",
    "Autodesk": "https://autodesk.wd1.myworkdayjobs.com/Ext",
    "Intuit": "https://intuit.wd1.myworkdayjobs.com/Intuit",
    "Qualcomm": "https://qualcomm.wd5.myworkdayjobs.com/External",
    "Nordstrom": "https://nordstrom.wd501.myworkdayjobs.com/nordstrom_careers",
    "Starbucks": "https://starbucks.wd1.myworkdayjobs.com/StarbucksCareers",
    "Costco": "https://costco.wd5.myworkdayjobs.com/Costco",
}

_WANTED = {PRODUCT, CONSULTING, STRATEGY}


async def check(client: httpx.AsyncClient, name: str, url: str) -> str:
    try:
        parts = parse_workday_url(url)
    except ValueError as exc:
        return f"{name}: bad url ({exc})"
    endpoint = f"https://{parts.host}/wday/cxs/{parts.tenant}/{parts.site}/jobs"
    payload = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": "intern"}
    try:
        response = await client.post(endpoint, json=payload)
    except Exception as exc:
        return f"{name}: error {type(exc).__name__}"
    if response.status_code != 200:
        return f"{name}: HTTP {response.status_code}"
    try:
        data = response.json()
    except ValueError:
        return f"{name}: not JSON"
    postings = data.get("jobPostings") or []
    useful = [
        str(item.get("title"))
        for item in postings
        if isinstance(item, dict) and title_family(str(item.get("title"))) in _WANTED
    ]
    sample = "; ".join(title[:40] for title in useful[:3])
    return f"{name}: OK total={data.get('total')} relevant={len(useful)} {sample}"


async def main() -> None:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
        results = []
        for name, url in CANDIDATES.items():
            results.append(await check(client, name, url))
    ok = [line for line in results if ": OK" in line]
    bad = [line for line in results if ": OK" not in line]
    for index in range(0, len(ok), 8):
        print("::notice title=workday ok::" + " | ".join(ok[index : index + 8]))
    print("::notice title=workday not working::" + " | ".join(bad)[:3500])
    sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
