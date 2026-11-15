"""Synthetic demo data. EVERYTHING here is invented: people are fictional, and company
figures / filings / transcripts are illustrative, NOT the real companies' disclosures.
Live snapshots in data/live/ override this fallback data."""
import datetime as dt
import random
import zlib

# ticker, name, sector, cap, weight %, base price, aliases
COMPANIES = [
    ("RELIANCE", "Reliance Industries", "Energy & Conglomerate", "Large", 8, 2900, ["Reliance", "RIL", "Jio"]),
    ("TCS", "Tata Consultancy Services", "IT Services", "Large", 7, 4100, ["TCS"]),
    ("HDFCBANK", "HDFC Bank", "Banking", "Large", 9, 1650, ["HDFC Bank"]),
    ("INFY", "Infosys", "IT Services", "Large", 5, 1800, ["Infosys"]),
    ("SBIN", "State Bank of India", "Banking", "Large", 5, 820, ["SBI", "State Bank"]),
    ("LT", "Larsen & Toubro", "Capital Goods / EPC", "Large", 7, 3600, ["L&T", "Larsen"]),
    ("SUNPHARMA", "Sun Pharmaceutical", "Pharma", "Large", 6, 1750, ["Sun Pharma"]),
    ("TATAMOTORS", "Tata Motors", "Auto", "Large", 6, 960, ["Tata Motors"]),
    ("ASIANPAINT", "Asian Paints", "Paints / Consumer", "Large", 5, 2350, ["Asian Paints"]),
    ("DEEPAKNTR", "Deepak Nitrite", "Specialty Chemicals", "Mid", 6, 2600, ["Deepak Nitrite"]),
    ("KPITTECH", "KPIT Technologies", "Auto Software", "Mid", 5, 1450, ["KPIT"]),
    ("BAJFINANCE", "Bajaj Finance", "NBFC", "Large", 6, 7100, ["Bajaj Finance"]),
    ("TITAN", "Titan Company", "Consumer / Jewellery", "Large", 5, 3400, ["Titan", "Tanishq"]),
    ("ULTRACEMCO", "UltraTech Cement", "Cement", "Large", 5, 11200, ["UltraTech"]),
    ("ITC", "ITC", "FMCG", "Large", 5, 470, ["ITC"]),
    ("PIDILITIND", "Pidilite Industries", "Adhesives / Specialty Chem", "Large", 5, 3050, ["Pidilite"]),
    ("POLYCAB", "Polycab India", "Electricals", "Mid", 5, 6400, ["Polycab"]),
]

RELATIONS = {
    "ASIANPAINT": {"competitors": ["Berger Paints", "Kansai Nerolac", "Akzo Nobel India"], "suppliers": ["Deepak Nitrite"], "customers": []},
    "DEEPAKNTR": {"competitors": ["Aarti Industries", "SRF", "Navin Fluorine", "Atul"], "suppliers": [], "customers": ["Asian Paints", "UPL"]},
    "KPITTECH": {"competitors": ["Tata Elxsi", "LTTS", "Persistent Systems"], "suppliers": [], "customers": ["Tata Motors", "Mercedes-Benz R&D India"]},
    "TITAN": {"competitors": ["Kalyan Jewellers", "Senco Gold"], "suppliers": ["MMTC-PAMP"], "customers": []},
    "TATAMOTORS": {"competitors": ["Mahindra & Mahindra", "Maruti Suzuki"], "suppliers": ["Bosch India", "Minda Industries"], "customers": []},
    "HDFCBANK": {"competitors": ["ICICI Bank", "Axis Bank", "Kotak Mahindra Bank"], "suppliers": [], "customers": []},
    "SBIN": {"competitors": ["Bank of Baroda", "PNB"], "suppliers": [], "customers": []},
    "TCS": {"competitors": ["Wipro", "HCLTech", "Accenture India"], "suppliers": [], "customers": []},
    "INFY": {"competitors": ["Wipro", "Cognizant India", "HCLTech"], "suppliers": [], "customers": []},
    "LT": {"competitors": ["Tata Projects", "BHEL"], "suppliers": [], "customers": ["NHAI"]},
    "SUNPHARMA": {"competitors": ["Dr. Reddy's", "Cipla", "Lupin"], "suppliers": [], "customers": []},
    "ULTRACEMCO": {"competitors": ["Ambuja Cements", "Shree Cement"], "suppliers": ["Coal India"], "customers": []},
    "ITC": {"competitors": ["HUL", "Nestle India"], "suppliers": [], "customers": []},
    "PIDILITIND": {"competitors": ["Astral", "Berger Paints"], "suppliers": [], "customers": []},
    "POLYCAB": {"competitors": ["Havells", "KEI Industries"], "suppliers": [], "customers": []},
    "BAJFINANCE": {"competitors": ["Shriram Finance", "HDB Financial"], "suppliers": [], "customers": []},
    "RELIANCE": {"competitors": ["Bharti Airtel", "Nayara Energy"], "suppliers": [], "customers": []},
}


def H(org, role, s, e=None):
    return {"org": org, "role": role, "start": s, "end": e}


# People in the investor's own relationship_graph (fictional)
PEOPLE = [
    dict(id="p01", name="Rohit Menon", org="Lakeview Capital", role="Partner", strength=4, last=18,
         met="Co-investor; met at 2024 consumer summit", themes=["paints", "decor", "consumer"],
         history=[H("Asian Paints", "Category Head", 2013, 2018), H("Lakeview Capital", "Partner", 2018)],
         edu=[("IIM Ahmedabad", 2008)], knows=["p05", "p16"]),
    dict(id="p02", name="Meera Krishnan", org="Verity Software", role="CFO", strength=3, last=140,
         met="Former colleague at Infosys", themes=["IT services", "finance"],
         history=[H("Infosys", "VP Finance", 2012, 2019), H("Verity Software", "CFO", 2019)],
         edu=[("SRCC", 2006)], knows=["x01"]),
    dict(id="p03", name="Arvind Kulkarni", org="Independent", role="Industry consultant", strength=5, last=35,
         met="Plant visits during 2023 chemicals diligence", themes=["specialty chemicals", "fluorochemicals", "plant operations"],
         history=[H("Aarti Industries", "VP Operations", 2009, 2016), H("SRF", "President, Chemicals", 2016, 2021), H("Independent", "Consultant", 2021)],
         edu=[("IIT Bombay", 1998)], knows=["x02"]),
    dict(id="p04", name="Neha Bansal", org="Greenfield Advisors", role="Principal", strength=3, last=95,
         met="Introduced by Rohit, 2025", themes=["jewellery", "retail", "consumer"],
         history=[H("Titan Company", "Strategy Lead", 2016, 2020), H("Greenfield Advisors", "Principal", 2020)],
         edu=[("ISB", 2015)], knows=["p01"]),
    dict(id="p05", name="Karan Shah", org="Shah Family Office", role="Managing Director", strength=4, last=12,
         met="Long-standing friend; BITS batchmate", themes=["banking", "NBFC", "capital markets"],
         history=[H("Kotak Mahindra Bank", "Institutional Equities", 2009, 2016), H("Shah Family Office", "MD", 2016)],
         edu=[("BITS Pilani", 2007)], knows=["x01", "p09"]),
    dict(id="p06", name="Dr. Sunita Rao", org="RegBridge Consulting", role="Founder", strength=4, last=60,
         met="Expert call, 2025", themes=["pharma", "USFDA", "regulatory"],
         history=[H("Sun Pharmaceutical", "Head, Regulatory Affairs", 2012, 2020), H("RegBridge Consulting", "Founder", 2020)],
         edu=[("ICT Mumbai", 2004)], knows=["x03"]),
    dict(id="p07", name="Aditya Verma", org="Mercedes-Benz R&D India", role="VP Engineering", strength=3, last=50,
         met="Auto software panel, 2024", themes=["auto software", "SDV", "EV"],
         history=[H("KPIT Technologies", "Program Director", 2014, 2019), H("Mercedes-Benz R&D India", "VP Engineering", 2019)],
         edu=[("IIT Delhi", 2005)], knows=[]),
    dict(id="p08", name="Pooja Nair", org="Tata Motors", role="Senior Manager, Strategy", strength=2, last=200,
         met="Alumni relationship_graph", themes=["auto", "EV"],
         history=[H("McKinsey", "Associate", 2015, 2019), H("Tata Motors", "Sr Manager, Strategy", 2019)],
         edu=[("IIM Calcutta", 2015)], knows=[]),
    dict(id="p09", name="Siddharth Rao", org="Peak Asset Management", role="Fund Manager", strength=5, last=9,
         met="IIT Delhi hostel mate; speak weekly", themes=["banking", "rural lending", "microfinance", "credit"],
         history=[H("HDFC Bank", "Credit Risk", 2011, 2016), H("Peak Asset Management", "Fund Manager", 2016)],
         edu=[("IIT Delhi", 2007)], knows=["p05", "p10"]),
    dict(id="p10", name="Farah Khan", org="Agrilend", role="Founder", strength=4, last=70,
         met="Fintech demo day", themes=["rural lending", "NBFC", "agri-credit"],
         history=[H("Bajaj Finance", "Zonal Head, Rural", 2015, 2021), H("Agrilend", "Founder", 2021)],
         edu=[("XLRI", 2010)], knows=[]),
    dict(id="p11", name="Manish Gupta", org="InfraSpan", role="CEO", strength=4, last=28,
         met="IIT Delhi alumni; site visits", themes=["infra", "EPC", "capex cycle"],
         history=[H("Larsen & Toubro", "GM Projects", 2008, 2020), H("InfraSpan", "CEO", 2020)],
         edu=[("IIT Delhi", 2002)], knows=["x02"]),
    dict(id="p12", name="Tanvi Desai", org="Ambuja Cements", role="VP Strategy", strength=3, last=110,
         met="Cement sector roundtable", themes=["cement", "logistics", "coal"],
         history=[H("UltraTech Cement", "Head, Logistics", 2012, 2021), H("Ambuja Cements", "VP Strategy", 2021)],
         edu=[("NITIE", 2011)], knows=[]),
    dict(id="p13", name="Rajiv Malhotra", org="Accenture India", role="Managing Director", strength=3, last=45,
         met="Client dinner", themes=["IT services", "deal flow", "GenAI"],
         history=[H("Wipro", "VP Delivery", 2008, 2018), H("Accenture India", "MD", 2018)],
         edu=[("IIT Bombay", 2000)], knows=[]),
    dict(id="p14", name="Ishita Joshi", org="Berger Paints", role="Director, Marketing", strength=2, last=160,
         met="Conference panel", themes=["paints", "brand", "decor"],
         history=[H("Pidilite Industries", "Brand Manager", 2012, 2018), H("Berger Paints", "Director Marketing", 2018)],
         edu=[("MICA", 2011)], knows=[]),
    dict(id="p15", name="Nikhil Agarwal", org="NitraChem Labs", role="Founder", strength=4, last=22,
         met="Founder friend; invested angel round", themes=["specialty chemicals", "nitration", "intermediates"],
         history=[H("Deepak Nitrite", "Business Head", 2015, 2021), H("NitraChem Labs", "Founder", 2021)],
         edu=[("ICT Mumbai", 2005)], knows=[]),
    dict(id="p16", name="Shreya Kapoor", org="Dhaaga Foods", role="CMO", strength=3, last=85,
         met="Rohit's introduction", themes=["FMCG", "consumer", "D2C"],
         history=[H("ITC", "Brand Manager", 2013, 2018), H("Dhaaga Foods", "CMO", 2018)],
         edu=[("SRCC", 2010)], knows=[]),
    dict(id="p17", name="Anil Pillai", org="Independent", role="Banking consultant", strength=3, last=130,
         met="Ex-banker, family friend", themes=["PSU banks", "rural lending", "credit"],
         history=[H("State Bank of India", "DGM", 2005, 2018), H("Independent", "Consultant", 2018)],
         edu=[("Delhi University", 1995)], knows=[]),
    dict(id="p18", name="Divya Chandra", org="Orbit Ventures", role="Associate", strength=3, last=75,
         met="IIM batch event", themes=["telecom", "retail", "energy transition"],
         history=[H("Reliance Retail", "Strategy", 2017, 2022), H("Orbit Ventures", "Associate", 2022)],
         edu=[("IIM Bangalore", 2016)], knows=[]),
    dict(id="p19", name="Harsh Vardhan", org="Havells", role="VP Sales", strength=3, last=100,
         met="Trade-show contact", themes=["cables", "electricals", "copper"],
         history=[H("Polycab India", "Sales Head", 2012, 2019), H("Havells", "VP Sales", 2019)],
         edu=[("NIT Surathkal", 2006)], knows=[]),
    dict(id="p20", name="Leena Thomas", org="Zephyr Capital", role="Portfolio Manager", strength=5, last=7,
         met="Peer PM; weekly call", themes=["compounders", "semiconductors", "quant"],
         history=[H("Zephyr Capital", "PM", 2014)], edu=[("IIT Delhi", 2010)], knows=[]),
    dict(id="p21", name="Ravi Subramanian", org="SiliconLeaf", role="Founder", strength=4, last=40,
         met="Angel investor in his fabless startup", themes=["semiconductors", "EDA", "automotive silicon"],
         history=[H("Intel India", "Design Manager", 2008, 2017), H("SiliconLeaf", "Founder", 2018)],
         edu=[("IISc Bangalore", 2006)], knows=["p07"]),
    dict(id="p22", name="Kavita Reddy", org="Independent", role="Pharma BD consultant", strength=3, last=55,
         met="Expert relationship_graph", themes=["pharma", "generics", "US pricing"],
         history=[H("Cipla", "Head, BD", 2014, 2021), H("Independent", "Consultant", 2021)],
         edu=[("ISB", 2012)], knows=["p06"]),

    # --- current employees at portfolio companies (fictional)
    dict(id="p23", name="Amit Saxena", org="Reliance Industries", role="VP, Corporate Strategy", strength=3, last=55,
         met="Met at an energy-transition roundtable, 2025", themes=["energy transition", "telecom", "retail"],
         history=[H("Bain & Company", "Manager", 2012, 2019), H("Reliance Industries", "VP, Corporate Strategy", 2019)],
         edu=[("IIT Delhi", 2010)], knows=["p18"]),
    dict(id="p24", name="Priyanka Iyer", org="Tata Consultancy Services", role="Delivery Head, BFSI", strength=3, last=38,
         met="Client-side contact from a bank diligence", themes=["IT services", "BFSI", "GenAI"],
         history=[H("Cognizant India", "Senior Director", 2010, 2016), H("Tata Consultancy Services", "Delivery Head, BFSI", 2016)],
         edu=[("NIT Trichy", 2008)], knows=["p13"]),
    dict(id="p25", name="Vikram Sethi", org="HDFC Bank", role="Zonal Head, Rural Banking", strength=3, last=80,
         met="Introduced by Siddharth Rao", themes=["banking", "rural lending", "credit"],
         history=[H("ICICI Bank", "Regional Manager", 2010, 2017), H("HDFC Bank", "Zonal Head, Rural Banking", 2017)],
         edu=[("IIM Lucknow", 2009)], knows=["p09"]),
    dict(id="p26", name="Anjali Deshpande", org="Infosys", role="AVP, Client Partner (BFSI)", strength=2, last=150,
         met="Conference contact", themes=["IT services", "GenAI"],
         history=[H("Accenture India", "Associate Director", 2011, 2018), H("Infosys", "AVP, Client Partner", 2018)],
         edu=[("Pune University", 2007)], knows=["p02"]),
    dict(id="p27", name="Rakesh Jain", org="State Bank of India", role="Chief Manager, MSME & Agri Credit", strength=3, last=95,
         met="Rural-lending field visit, 2024", themes=["PSU banks", "rural lending", "credit"],
         history=[H("State Bank of India", "Chief Manager, MSME & Agri Credit", 2012)],
         edu=[("Delhi University", 2003)], knows=["p17"]),
    dict(id="p28", name="Nandini Rao", org="Larsen & Toubro", role="Head, BD - Heavy Civil Infrastructure", strength=4, last=21,
         met="IIT Delhi alumni; site visits with Manish", themes=["infra", "EPC", "capex cycle"],
         history=[H("Tata Projects", "GM, Business Development", 2008, 2015), H("Larsen & Toubro", "Head, BD - Heavy Civil", 2015)],
         edu=[("IIT Delhi", 2005)], knows=["p11"]),
    dict(id="p29", name="Pranav Bhatt", org="Sun Pharmaceutical", role="AVP, Quality Assurance", strength=3, last=62,
         met="Pharma quality panel, 2025", themes=["pharma", "USFDA", "quality"],
         history=[H("Lupin", "Senior Manager, Quality", 2008, 2018), H("Sun Pharmaceutical", "AVP, Quality Assurance", 2018)],
         edu=[("ICT Mumbai", 2006)], knows=["x03", "p06"]),
    dict(id="p30", name="Kunal Mehra", org="Asian Paints", role="Head, Home Decor Business", strength=3, last=44,
         met="Consumer summit, introduced by Rohit", themes=["paints", "decor", "consumer"],
         history=[H("Hindustan Unilever", "Category Manager", 2012, 2019), H("Asian Paints", "Head, Home Decor", 2019)],
         edu=[("IIM Ahmedabad", 2011)], knows=["p01"]),
    dict(id="p31", name="Sneha Patil", org="Deepak Nitrite", role="Head, Business Development (Intermediates)", strength=3, last=58,
         met="Chemicals conference; follows up on diligence questions", themes=["specialty chemicals", "agro intermediates"],
         history=[H("UPL", "Manager, Sourcing", 2013, 2021), H("Deepak Nitrite", "Head, BD (Intermediates)", 2021)],
         edu=[("ICT Mumbai", 2012)], knows=["x02", "p15"]),
    dict(id="p32", name="Rahul Chitnis", org="KPIT Technologies", role="Director, Software-Defined Vehicle Programs", strength=4, last=15,
         met="Auto software panel, 2024", themes=["auto software", "SDV", "EV"],
         history=[H("Tata Elxsi", "Senior Manager", 2013, 2020), H("KPIT Technologies", "Director, SDV Programs", 2020)],
         edu=[("IIT Bombay", 2009)], knows=["x01", "p07"]),
    dict(id="p33", name="Gauri Khanna", org="Bajaj Finance", role="Head, Rural Credit Policy", strength=3, last=72,
         met="Fintech demo day", themes=["NBFC", "rural lending", "credit"],
         history=[H("Shriram Finance", "Regional Credit Head", 2010, 2018), H("Bajaj Finance", "Head, Rural Credit Policy", 2018)],
         edu=[("XLRI", 2009)], knows=["p10"]),
    dict(id="p34", name="Varun Malhotra", org="Titan Company", role="VP, Tanishq Retail Strategy", strength=3, last=36,
         met="Introduced by Neha Bansal", themes=["jewellery", "retail", "consumer"],
         history=[H("Trent", "Senior Manager, Strategy", 2011, 2017), H("Titan Company", "VP, Tanishq Retail Strategy", 2017)],
         edu=[("ISB", 2013)], knows=["p04"]),
    dict(id="p35", name="Suresh Ramanathan", org="UltraTech Cement", role="Head, Supply Chain & Fuel Sourcing", strength=4, last=33,
         met="Cement sector roundtable", themes=["cement", "logistics", "coal"],
         history=[H("ACC", "Manager, Logistics", 2006, 2014), H("UltraTech Cement", "Head, Supply Chain & Fuel", 2014)],
         edu=[("NITIE", 2005)], knows=["p12"]),
    dict(id="p36", name="Madhuri Sen", org="ITC", role="Head, Strategy (FMCG Businesses)", strength=2, last=120,
         met="Alumni relationship_graph", themes=["FMCG", "consumer", "D2C"],
         history=[H("Nestle India", "Senior Manager, Strategy", 2009, 2016), H("ITC", "Head, Strategy (FMCG)", 2016)],
         edu=[("SRCC", 2008)], knows=["p16"]),
    dict(id="p37", name="Tarun Bhasin", org="Pidilite Industries", role="GM, Raw Material Sourcing", strength=3, last=66,
         met="Specialty chemicals conference", themes=["specialty chemicals", "adhesives", "procurement"],
         history=[H("Asian Paints", "Manager, Procurement", 2009, 2015), H("Pidilite Industries", "GM, Raw Material Sourcing", 2015)],
         edu=[("NITIE", 2008)], knows=["p15"]),
    dict(id="p38", name="Ritu Agarwal", org="Polycab India", role="VP Finance & Investor Relations", strength=3, last=48,
         met="Investor day, 2025", themes=["cables", "electricals", "copper"],
         history=[H("Havells", "Senior Manager, Finance", 2010, 2017), H("Polycab India", "VP Finance & IR", 2017)],
         edu=[("SRCC", 2009)], knows=["p19"]),
]

# People who appear in filings (not in relationship_graph) - synthetic public-profile stand-ins
EXT_PEOPLE = [
    dict(id="x01", name="Ananya Rao", org="KPIT Technologies", role="Chief Financial Officer (incoming)",
         history=[H("Deloitte", "Senior Manager", 2008, 2015), H("Infosys", "VP Finance", 2015, 2021), H("Mphasis", "Sr Director Finance", 2021, 2026)],
         edu=[("IIM Ahmedabad", 2008), ("SRCC", 2005)], knows=[]),
    dict(id="x02", name="Sandeep Joshi", org="Deepak Nitrite", role="Chief Operating Officer (incoming)",
         history=[H("Aarti Industries", "Plant Head / VP Ops", 2010, 2016), H("SRF", "Business Head, Chemicals", 2016, 2026)],
         edu=[("IIT Bombay", 1999)], knows=[]),
    dict(id="x03", name="Rajesh Kulkarni", org="Sun Pharmaceutical", role="Whole-time Director (outgoing)",
         history=[H("Sun Pharmaceutical", "Whole-time Director", 2011, 2026), H("Ranbaxy", "VP Technical Ops", 2003, 2011)],
         edu=[("ICT Mumbai", 1996)], knows=[]),
]

THEMES = ["specialty chemicals", "paints", "semiconductors", "rural lending", "banking", "pharma", "cement", "IT services",
          "auto software", "jewellery", "infra", "FMCG", "electricals"]

# ---------------------------------------------------------------- fundamentals
QL = ["Q3FY25", "Q4FY25", "Q1FY26", "Q2FY26", "Q3FY26", "Q4FY26", "Q1FY27", "Q2FY27"]


def _tx(q, date, intro, g1, g2, extra):
    return {"quarter": q, "date": date, "text":
            f"Opening remarks. {intro} Let me turn to the outlook. {g1} {g2} {extra} "
            "Analyst: Can you comment on demand and pricing? Management: We remain focused on execution; "
            "the environment is competitive but we are comfortable with our plans."}


def _fund(t, name, summary, segments, rev, ebitda, pat, ann, notes, tx):
    return dict(ticker=t, name=name, source="SYNTHETIC DEMO DATA", business=dict(summary=summary, segments=segments),
                quarters=dict(labels=QL, revenue=rev, ebitda=ebitda, pat=pat), annual=ann, ar_notes=notes, transcripts=tx)


def _ann(rev_hist, ebitda_hist, pat_hist, q, **kw):
    s = lambda a: round(sum(a[2:6]), 1)
    d = dict(years=["FY22", "FY23", "FY24", "FY25", "FY26"],
             revenue=rev_hist + [s(q[0])], ebitda=ebitda_hist + [s(q[1])], pat=pat_hist + [s(q[2])])
    d.update(kw)
    return d


FUNDAMENTALS = {}

_q = ([1850.2, 1912.6, 1925.8, 1987.5, 2040.3, 2105.9, 2180.2, 2310.4],
      [265.1, 278.9, 275.4, 289.4, 312.5, 331.8, 351.5, 398.2],
      [160.2, 168.7, 170.9, 178.3, 196.8, 208.3, 224.8, 255.6])
FUNDAMENTALS["DEEPAKNTR"] = _fund(
    "DEEPAKNTR", "Deepak Nitrite",
    "Makes chemical intermediates (phenol, acetone, nitro-aromatics) for agro, dyes, pharma and paints; has been adding capacity in phenol and fluorine chains.",
    [dict(name="Basic chemicals (phenol/acetone)", pct=52), dict(name="Advanced intermediates", pct=40), dict(name="Other", pct=8)],
    *_q,
    _ann([5440, 6980, 6890, 7390], [1180, 1030, 1040, 1105], [820, 770, 640, 660], _q,
         cfo=[610, 300, 780, 520, 430], capex=[260, 610, 640, 720, 810], debt=[610, 980, 1240, 1480, 1760],
         equity=[3180, 3790, 4210, 4710, 5400], receivable_days=[58, 64, 62, 67, 74],
         inventory_days=[44, 52, 49, 55, 60], payable_days=[60, 66, 63, 66, 64]),
    dict(contingent=dict(text="Disputed indirect-tax and a customer claim, appealed; no provision made.", amount=412),
         rpt="Purchases of Rs 310 crore from an entity controlled by the promoter family (about 4% of revenue).",
         auditor="Unmodified opinion. Emphasis of matter on timing of capitalisation of the new phenol line."),
    [_tx("Q2FY26", "2025-11-04", "Volumes held up in advanced intermediates.",
         "We expect H2 FY26 revenue growth of 8-10% YoY.", "For next year we see capex of around Rs 800 crore.", ""),
     _tx("Q3FY26", "2026-02-05", "Phenol spreads were firm.",
         "We expect Q4 FY26 EBITDA margin of 17-18%.", "Debottlenecking should add volumes progressively.", ""),
     _tx("Q4FY26", "2026-05-06", "FY26 closed with improved mix.",
         "We expect FY27 revenue growth of 14-16% YoY.", "We plan capex of Rs 900 crore in FY27 for the new capacity.", ""),
     _tx("Q1FY27", "2026-08-05", "New line ramp-up is on track.",
         "We expect Q2 FY27 EBITDA margin of 16-17%.", "Working capital should normalise over the year.", "")])

_q = ([8100, 8260, 8180, 8395, 8420, 8480, 8510, 8740],
      [1620, 1590, 1640, 1720, 1560, 1540, 1535, 1590],
      [1030, 1010, 1050, 1140, 985, 970, 960, 1030])
FUNDAMENTALS["ASIANPAINT"] = _fund(
    "ASIANPAINT", "Asian Paints",
    "Decorative and industrial paints, plus home-decor and waterproofing; sells through a large dealer relationship_graph.",
    [dict(name="Decorative paints (India)", pct=88), dict(name="International", pct=8), dict(name="Industrial / other", pct=4)],
    *_q,
    _ann([29100, 34500, 35300, 33160], [5200, 5300, 6900, 6660], [3100, 3450, 4100, 4320], _q,
         cfo=[3600, 3050, 5400, 4800, 4300], capex=[900, 1300, 1350, 1500, 1100], debt=[150, 140, 130, 120, 110],
         equity=[14500, 16100, 18200, 20400, 22300], receivable_days=[34, 36, 33, 35, 36],
         inventory_days=[74, 84, 78, 80, 85], payable_days=[58, 60, 61, 62, 60]),
    dict(contingent=dict(text="Customs and sales-tax disputes under appeal.", amount=620),
         rpt="Royalty and service fees with group entities, within disclosed limits.",
         auditor="Unmodified opinion; no emphasis of matter."),
    [_tx("Q2FY26", "2025-11-06", "Demand was uneven across regions.",
         "We expect H2 FY26 revenue growth of 10-12% YoY.", "", ""),
     _tx("Q3FY26", "2026-02-07", "Input costs stayed elevated.",
         "We expect Q4 FY26 EBITDA margin of 19-20%.", "", ""),
     _tx("Q4FY26", "2026-05-08", "We are investing in distribution and decor.",
         "We expect FY27 revenue growth of 9-11% YoY.", "Capex of around Rs 1,200 crore is planned for FY27.", ""),
     _tx("Q1FY27", "2026-08-07", "Monsoon affected the quarter.",
         "We expect Q2 FY27 EBITDA margin of around 19%.", "", "")])

_q = ([1480, 1560, 1610, 1680, 1795, 1890, 1985, 2080],
      [288, 305, 322, 338, 360, 384, 404, 430],
      [190, 203, 214, 226, 243, 262, 277, 298])
FUNDAMENTALS["KPITTECH"] = _fund(
    "KPITTECH", "KPIT Technologies",
    "Engineering and software services for automotive OEMs: software-defined vehicle, electrification, ADAS, middleware.",
    [dict(name="Software-defined vehicle", pct=44), dict(name="Electrification", pct=26), dict(name="Autonomous / ADAS", pct=18), dict(name="Other", pct=12)],
    *_q,
    _ann([3000, 3850, 4950, 5890], [560, 780, 990, 1190], [380, 520, 690, 820], _q,
         cfo=[320, 430, 820, 880, 1010], capex=[120, 160, 210, 240, 300], debt=[150, 170, 200, 230, 210],
         equity=[1300, 1850, 2450, 3150, 3950], receivable_days=[88, 85, 80, 76, 74],
         inventory_days=[2, 2, 2, 2, 2], payable_days=[32, 34, 33, 35, 36]),
    dict(contingent=dict(text="Minor tax matters under appeal.", amount=55),
         rpt="No material related-party transactions beyond remuneration.", auditor="Unmodified opinion."),
    [_tx("Q2FY26", "2025-11-03", "Mobility programs are ramping.",
         "We expect H2 FY26 revenue growth of 18-20% YoY.", "", ""),
     _tx("Q3FY26", "2026-02-04", "Wins in SDV continued.",
         "We expect Q4 FY26 EBITDA margin of 20-21%.", "", ""),
     _tx("Q4FY26", "2026-05-05", "Order book is healthy.",
         "We expect FY27 revenue growth of 22-24% YoY.", "Capex of around Rs 320 crore is planned for FY27.", ""),
     _tx("Q1FY27", "2026-08-04", "Utilisation improved.",
         "We expect Q2 FY27 EBITDA margin of around 21%.", "", "")])

_q = ([11040, 11250, 11530, 12115.8, 12640, 13120, 13420.2, 14980.5],
      [1180, 1210, 1236, 1306.0, 1330, 1380, 1402.7, 1540.3],
      [800, 830, 850, 859.5, 880, 905, 911.4, 1002.7])
FUNDAMENTALS["TITAN"] = _fund(
    "TITAN", "Titan Company",
    "Jewellery (Tanishq and others), watches and wearables, eyecare; most revenue is gold jewellery sold through own stores.",
    [dict(name="Jewellery", pct=84), dict(name="Watches & wearables", pct=7), dict(name="Eyecare", pct=3), dict(name="Other", pct=6)],
    *_q,
    _ann([28800, 35600, 40800, 43790], [2800, 3600, 4300, 4600], [2000, 2750, 3180, 3300], _q,
         cfo=[900, 600, 1400, 1200, 800], capex=[400, 600, 900, 1100, 1300], debt=[6500, 9500, 12800, 15500, 18200],
         equity=[7700, 9200, 11800, 14000, 16100], receivable_days=[4, 5, 5, 5, 6],
         inventory_days=[180, 190, 185, 195, 215], payable_days=[20, 21, 19, 20, 18]),
    dict(contingent=dict(text="Customs-duty and GST disputes under appeal.", amount=380),
         rpt="Rent and service transactions with promoter-linked entities, disclosed.",
         auditor="Unmodified opinion."),
    [_tx("Q2FY26", "2025-11-05", "Festive demand was strong.",
         "We expect H2 FY26 revenue growth of 12-14% YoY.", "", ""),
     _tx("Q3FY26", "2026-02-06", "Studded share improved.",
         "We expect Q4 FY26 EBITDA margin of 11-12%.", "", ""),
     _tx("Q4FY26", "2026-05-07", "Store expansion continues.",
         "We expect FY27 revenue growth of 15-17% YoY.", "Capex of around Rs 1,400 crore is planned for FY27.", ""),
     _tx("Q1FY27", "2026-08-06", "Gold price volatility remains a watch item.",
         "We expect Q2 FY27 EBITDA margin of 11-11.5%.", "", "")])

# ---------------------------------------------------------------- announcements
def _table(t, hdr_dates):
    f = FUNDAMENTALS[t]["quarters"]
    rows = {"Revenue from operations": f["revenue"], "EBITDA": f["ebitda"], "Profit before tax": None, "Profit after tax": f["pat"]}
    pbt = [round(x / 0.75, 1) for x in f["pat"]]
    lines = ["Particulars | " + " | ".join(hdr_dates), ]
    for k, arr in rows.items():
        arr = arr or pbt
        v = [arr[7], arr[6], arr[3]]
        lines.append(f"{k} | " + " | ".join(f"{x:,.1f}" for x in v))
    return "Unaudited standalone results (Rs crore)\n" + "\n".join(lines)


_hdr = ["30-Sep-26", "30-Jun-26", "30-Sep-25"]

# (id, ticker, hours_ago, subject, body, person)
ANNOUNCEMENTS = [
    ("a16", "DEEPAKNTR", 2, "Appointment of Mr. Sandeep Joshi as Chief Operating Officer", "Board has approved the appointment of Mr. Sandeep Joshi as Chief Operating Officer, effective 1 December 2026.", "Sandeep Joshi"),
    ("a1", "DEEPAKNTR", 3, "Outcome of Board Meeting - Unaudited Financial Results for the quarter ended September 30, 2026", _table("DEEPAKNTR", _hdr), None),
    ("a13", "RELIANCE", 4, "Press release: partnership announced for new energy storage line", "Company announced a partnership to set up battery storage manufacturing.", None),
    ("a10", "ITC", 5, "Declaration of interim dividend of Rs 7.50 per share; record date 21 November 2026", "", None),
    ("a2", "KPITTECH", 6, "Appointment of Ms. Ananya Rao as Chief Financial Officer", "Board has appointed Ms. Ananya Rao as CFO, effective 1 December 2026. Outgoing CFO moves to an advisory role.", "Ananya Rao"),
    ("a14", "SBIN", 7, "Notice of Postal Ballot", "Postal ballot notice for appointment of independent directors.", None),
    ("a3", "TATAMOTORS", 8, "Disclosure of pledge of shares by promoter under Reg 31", "Promoter entity has created pledge on 1.9 crore shares.", None),
    ("a11", "INFY", 9, "Intimation of earnings conference call - schedule", "Conference call to discuss Q2 results.", None),
    ("a4", "SUNPHARMA", 10, "Receipt of Warning Letter from US FDA regarding Halol facility", "The company received a warning letter citing GMP observations at the Halol facility.", None),
    ("a5", "LT", 12, "Acquisition of 74% equity stake in GreenGrid Engineering Pvt Ltd", "Board approved acquisition of 74% stake in a renewable EPC company, consideration Rs 1,150 crore.", None),
    ("a6", "TITAN", 14, "Outcome of Board Meeting - Unaudited Financial Results for the quarter ended September 30, 2026", _table("TITAN", _hdr), None),
    ("a15", "TCS", 15, "Allotment of equity shares pursuant to ESOP", "", None),
    ("a7", "ULTRACEMCO", 16, "Board approves capex of Rs 4,200 crore for 6 MTPA capacity expansion", "Greenfield and brownfield capacity addition in the east and central regions.", None),
    ("a8", "BAJFINANCE", 18, "CRISIL reaffirms AAA/Stable rating on long-term debt programme", "", None),
    ("a9", "ASIANPAINT", 20, "Disclosure under Reg 7 - sale of shares by promoter group entity", "Promoter group entity sold 0.4% equity.", None),
    ("a12", "HDFCBANK", 22, "Schedule of analyst / institutional investor meetings", "", None),
    ("a18", "POLYCAB", 26, "Board approves fund raising of up to Rs 2,000 crore through QIP", "", None),
    ("a17", "SUNPHARMA", 30, "Resignation of Mr. Rajesh Kulkarni, Whole-time Director", "Mr. Kulkarni has resigned citing personal reasons.", "Rajesh Kulkarni"),
    ("a19", "PIDILITIND", 40, "Notice of Annual General Meeting", "", None),
    ("a20", "ASIANPAINT", 48, "Outcome of Board Meeting - Unaudited Financial Results for the quarter ended September 30, 2026", _table("ASIANPAINT", _hdr), None),
    ("a21", "TCS", 70, "Buyback of equity shares up to Rs 17,000 crore", "", None),
    ("a22", "ITC", 100, "Clarification on news item", "Company clarifies media report; no undisclosed information.", None),
]

# ---------------------------------------------------------------- prices
def last_trading_day(today=None):
    d = (today or dt.date.today())
    d -= dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def gen_prices(days=130):
    end = last_trading_day()
    dates = []
    d = end
    while len(dates) < days:
        if d.weekday() < 5:
            dates.append(d)
        d -= dt.timedelta(days=1)
    dates.reverse()
    out = {}
    # planted unusual moves on the latest day: ticker -> (pct move, volume multiple)
    plant = {"TATAMOTORS": (-5.1, 2.8), "DEEPAKNTR": (6.4, 3.1), "ULTRACEMCO": (1.2, 2.3), "SUNPHARMA": (-3.2, 1.8)}
    for t, _, _, _, _, base, _ in COMPANIES:
        r = random.Random(zlib.crc32(t.encode()))
        px, vol0 = base, r.randint(8, 40) * 100000
        series = []
        for i, day in enumerate(dates):
            chg = r.gauss(0.0004, 0.012)
            vol = int(vol0 * r.uniform(0.7, 1.3))
            if i == len(dates) - 1 and t in plant:
                chg, mult = plant[t][0] / 100, plant[t][1]
                vol = int(vol0 * mult)
            close = round(px * (1 + chg), 2)
            series.append(dict(d=day.isoformat(), c=close, v=vol))
            px = close
        out[t] = series
    return out


# Challenge-specific independent demo universe. All profiles and filings below are synthetic.
COMPANIES = [
    ("CONCOR", "Container Corporation of India", "Shipping & logistics", "Large", 8, 820, ["CONCOR", "Container Corp"]),
    ("BLUEDART", "Blue Dart Express", "Shipping & logistics", "Mid", 4, 6900, ["Blue Dart"]),
    ("GICRE", "General Insurance Corporation", "Insurance", "Large", 5, 420, ["GIC Re", "GIC"]),
    ("STARHEALTH", "Star Health and Allied Insurance", "Insurance", "Large", 5, 510, ["Star Health"]),
    ("SOBHA", "Sobha", "Real estate", "Mid", 5, 1650, ["Sobha"]),
    ("OBEROIRLTY", "Oberoi Realty", "Real estate", "Large", 5, 2100, ["Oberoi Realty"]),
    ("BHEL", "Bharat Heavy Electricals", "Capital goods", "Large", 6, 250, ["BHEL"]),
    ("ABB", "ABB India", "Capital goods", "Large", 6, 7200, ["ABB"]),
    ("VOLTAS", "Voltas", "Consumer durables", "Large", 4, 1450, ["Voltas"]),
    ("WHIRLPOOL", "Whirlpool of India", "Consumer durables", "Mid", 3, 1350, ["Whirlpool"]),
    ("SUZLON", "Suzlon Energy", "Renewable energy", "Large", 7, 68, ["Suzlon"]),
    ("ZEEL", "Zee Entertainment", "Media", "Mid", 3, 145, ["Zee", "ZEEL"]),
    ("PVRINOX", "PVR INOX", "Hospitality", "Mid", 4, 1600, ["PVR INOX", "PVR", "Inox"]),
    ("TRIDENT", "Trident", "Textiles", "Mid", 3, 38, ["Trident"]),
    ("PIIND", "PI Industries", "Agrochemicals", "Large", 7, 3900, ["PI Industries", "PI"]),
    ("ULTRACEMCO", "UltraTech Cement", "Cement", "Large", 8, 11800, ["UltraTech Cement", "UltraTech"]),
    ("BHARATFORG", "Bharat Forge", "Auto ancillaries", "Large", 7, 1450, ["Bharat Forge"]),
]

THEMES = [
    "logistics", "shipping", "supply chain", "renewables", "capital goods", "auto ancillaries",
    "real estate", "insurance", "consumer durables", "cement", "agrochemicals", "textiles",
    "hospitality", "media", "risk", "capex", "project finance", "robotics"
]

RELATIONS = {t: {"competitors": [], "suppliers": [], "customers": []} for t, *_ in COMPANIES}
RELATIONS.update({
    "CONCOR": {"competitors": ["Gateway Distriparks", "Adani Ports"], "suppliers": ["BLUEDART"], "customers": []},
    "BLUEDART": {"competitors": ["Delhivery", "FedEx India"], "suppliers": [], "customers": ["CONCOR"]},
    "SUZLON": {"competitors": ["Inox Wind", "Siemens Gamesa"], "suppliers": [], "customers": ["BHEL", "NTPC"]},
    "BHARATFORG": {"competitors": ["Motherson", "Endurance Technologies"], "suppliers": [], "customers": ["ABB", "Tata Motors"]},
    "ULTRACEMCO": {"competitors": ["Shree Cement", "Ambuja Cements"], "suppliers": [], "customers": ["CONCOR", "Sobha", "Oberoi Realty"]},
    "BHEL": {"competitors": ["Siemens India", "Larsen & Toubro"], "suppliers": ["BHARATFORG"], "customers": ["SUZLON"]},
    "ABB": {"competitors": ["Schneider Electric", "Siemens India"], "suppliers": [], "customers": ["BHEL", "BHARATFORG"]},
    "SOBHA": {"competitors": ["Prestige Estates", "Brigade Enterprises"], "suppliers": ["ULTRACEMCO"], "customers": []},
    "OBEROIRLTY": {"competitors": ["Godrej Properties", "Lodha Group"], "suppliers": ["ULTRACEMCO"], "customers": []},
    "VOLTAS": {"competitors": ["Blue Star", "Daikin India"], "suppliers": [], "customers": []},
    "WHIRLPOOL": {"competitors": ["VOLTAS", "LG Electronics"], "suppliers": [], "customers": []},
    "STARHEALTH": {"competitors": ["Care Health", "Niva Bupa"], "suppliers": [], "customers": []},
    "GICRE": {"competitors": ["Munich Re India", "Swiss Re India"], "suppliers": [], "customers": ["STARHEALTH"]},
    "PIIND": {"competitors": ["Dhanuka Agritech", "UPL"], "suppliers": [], "customers": []},
    "TRIDENT": {"competitors": ["Welspun Living", "Indo Count"], "suppliers": [], "customers": []},
    "ZEEL": {"competitors": ["Sun TV", "Sony Pictures India"], "suppliers": [], "customers": []},
    "PVRINOX": {"competitors": ["Cinepolis India"], "suppliers": [], "customers": []},
})

PEOPLE = [
    dict(id="p01", name="Maya Iyer", org="Blue Dart Express", role="VP, Network Strategy", strength=5, last=19, met="Worked together on a warehousing diligence", themes=["logistics", "supply chain"], history=[H("DHL Supply Chain", "Regional Planning Lead", 2018, 2022), H("Blue Dart Express", "VP, Network Strategy", 2022)], edu=[("ISB", 2016)], knows=["x01", "x04", "p23"]),
    dict(id="p02", name="Arjun Mehta", org="Independent", role="Former CFO", strength=4, last=83, met="Introduced by the industrials fund", themes=["auto ancillaries", "capital allocation"], history=[H("Tata Motors", "Finance Director", 2015, 2020), H("Bharat Forge", "Former CFO", 2020, 2025)], edu=[("IIM Bangalore", 2009)], knows=["x01", "p22", "p32"]),
    dict(id="p03", name="Sofia Laurent", org="Northstar Capital", role="Partner, Infrastructure", strength=4, last=41, met="Met at a climate-finance roundtable", themes=["renewables", "project finance"], history=[H("Vestas", "Commercial Strategy", 2016, 2021), H("Northstar Capital", "Partner", 2021)], edu=[("HEC Paris", 2011)], knows=["p07", "x02", "p21"]),
    dict(id="p04", name="Rohan Kulkarni", org="UltraTech Cement", role="Head of Investor Relations", strength=3, last=12, met="Former colleague of the investor", themes=["cement", "capex"], history=[H("Larsen & Toubro", "IR Manager", 2017, 2021), H("UltraTech Cement", "Head of IR", 2021)], edu=[("IIT Bombay", 2010)], knows=["p25", "p14"]),
    dict(id="p05", name="Nandita Bose", org="Star Health", role="Chief Risk Officer", strength=5, last=27, met="Classmate at ISB", themes=["insurance", "risk"], history=[H("AIG", "Actuarial Lead", 2014, 2019), H("Star Health", "Chief Risk Officer", 2019)], edu=[("ISB", 2012)], knows=["p11", "p24", "p31"]),
    dict(id="p06", name="Daniel Okafor", org="Harbor Logistics", role="Operating Partner", strength=3, last=116, met="Introduced through Maya Iyer", themes=["shipping", "ports"], history=[H("Maersk", "Country Operations", 2013, 2019), H("Harbor Logistics", "Operating Partner", 2019)], edu=[("Lagos Business School", 2010)], knows=["p01", "p13"]),
    dict(id="p07", name="Kavya Menon", org="Suzlon Energy", role="Director, Projects", strength=4, last=58, met="Former project teammate", themes=["renewables", "capex"], history=[H("ReNew Power", "Project Director", 2016, 2022), H("Suzlon Energy", "Director, Projects", 2022)], edu=[("IIT Madras", 2011)], knows=["p03", "p21"]),
    dict(id="p08", name="Leila Haddad", org="Atlas Growth", role="Investment Director", strength=4, last=66, met="Met during a farm-input study", themes=["agrochemicals", "rural demand"], history=[H("Syngenta", "Market Access", 2015, 2020), H("Atlas Growth", "Investment Director", 2020)], edu=[("Oxford", 2013)], knows=["p17", "p29"]),
    dict(id="p09", name="Ishaan Kapoor", org="Oberoi Realty", role="Head of Projects", strength=4, last=31, met="Met through a Mumbai redevelopment diligence", themes=["real estate", "project execution"], history=[H("Lodha Group", "Project Director", 2014, 2020), H("Oberoi Realty", "Head of Projects", 2020)], edu=[("IIM Ahmedabad", 2012)], knows=["p04", "p16", "p26"]),
    dict(id="p10", name="Mariam Fernandes", org="Voltas", role="VP, Consumer Products", strength=3, last=74, met="Former category strategy peer", themes=["consumer durables", "pricing"], history=[H("Whirlpool India", "Category Lead", 2016, 2021), H("Voltas", "VP, Consumer Products", 2021)], edu=[("SPJIMR", 2014)], knows=["p20", "p30"]),
    dict(id="p11", name="Kabir Sen", org="GIC Re", role="Chief Underwriting Officer", strength=4, last=47, met="Introduced by an insurance analyst", themes=["insurance", "risk"], history=[H("Swiss Re", "Senior Underwriter", 2012, 2019), H("GIC Re", "Chief Underwriting Officer", 2019)], edu=[("National University of Singapore", 2011)], knows=["p05", "p31"]),
    dict(id="p12", name="Ananya Pillai", org="Trident", role="Director, Sustainable Textiles", strength=5, last=24, met="Met at a circular-economy working group", themes=["textiles", "sustainability"], history=[H("Welspun Living", "Sustainability Lead", 2015, 2020), H("Trident", "Director, Sustainable Textiles", 2020)], edu=[("Cambridge", 2013)], knows=["p08", "p28"]),
    dict(id="p13", name="Rajesh Singhania", org="Container Corporation of India", role="Chief Operating Officer", strength=4, last=14, met="Site diligence at Dadri ICD", themes=["shipping", "logistics", "supply chain"], history=[H("Gateway Distriparks", "VP Operations", 2011, 2017), H("Container Corporation of India", "Chief Operating Officer", 2017)], edu=[("IIT Roorkee", 2004)], knows=["p06", "p23"]),
    dict(id="p14", name="Vikramaditya Rao", org="Bharat Heavy Electricals", role="Executive Director, Power Systems", strength=4, last=33, met="Met during boiler-turbine tech review", themes=["capital goods", "capex", "manufacturing"], history=[H("Larsen & Toubro", "GM Heavy Engineering", 2010, 2018), H("Bharat Heavy Electricals", "Executive Director", 2018)], edu=[("IIT Kharagpur", 2002)], knows=["p04", "x05"]),
    dict(id="p15", name="Priya Nambiar", org="ABB India", role="Head of Robotics & Automation", strength=4, last=22, met="Smart factory panel speaker", themes=["capital goods", "robotics", "manufacturing"], history=[H("Siemens India", "Lead Automation Architect", 2012, 2018), H("ABB India", "Head of Robotics", 2018)], edu=[("BITS Pilani", 2008)], knows=["p27"]),
    dict(id="p16", name="Gaurav Chawla", org="Sobha", role="VP, Corporate Finance & Treasury", strength=3, last=88, met="Real estate debt structuring discussion", themes=["real estate", "project finance", "capital allocation"], history=[H("Prestige Estates", "Treasury Head", 2014, 2019), H("Sobha", "VP Corporate Finance", 2019)], edu=[("IIM Bangalore", 2011)], knows=["p09", "x06"]),
    dict(id="p17", name="Dr. Devika Sundaram", org="PI Industries", role="Head of Global CSM & Synthesis", strength=5, last=18, met="Custom synthesis diligence in Udaipur", themes=["agrochemicals", "csm", "rural demand"], history=[H("Syngenta", "Lead Chemist", 2010, 2017), H("PI Industries", "Head of CSM", 2017)], edu=[("ICT Mumbai", 2006)], knows=["p08", "p29"]),
    dict(id="p18", name="Sameer Merchant", org="Zee Entertainment", role="EVP, Content & Digital Distribution", strength=3, last=95, met="Broadcast rights summit", themes=["media", "ott", "advertising"], history=[H("Star India", "VP Programming", 2013, 2019), H("Zee Entertainment", "EVP Content", 2019)], edu=[("MICA", 2009)], knows=["x03", "p19"]),
    dict(id="p19", name="Alok Tandon", org="PVR INOX", role="Chief Development Officer", strength=4, last=44, met="Multiplex screen rollout review", themes=["hospitality", "cinemas", "consumer"], history=[H("Cinepolis India", "Director Expansion", 2012, 2018), H("PVR INOX", "Chief Development Officer", 2018)], edu=[("XLRI", 2005)], knows=["x03", "p18"]),
    dict(id="p20", name="Siddharth Bansal", org="Whirlpool of India", role="Director, Supply Chain & Sourcing", strength=4, last=39, met="White goods supply chain roundtable", themes=["consumer durables", "supply chain", "pricing"], history=[H("Voltas", "Procurement Manager", 2012, 2018), H("Whirlpool of India", "Director Supply Chain", 2018)], edu=[("NITIE", 2010)], knows=["p10", "p30"]),
    dict(id="p21", name="Natasha Verghese", org="Inox Wind", role="VP, Commercial & Strategy", strength=3, last=62, met="Wind turbine order book check", themes=["renewables", "wind", "capex"], history=[H("Suzlon Energy", "Sr Manager Commercial", 2014, 2020), H("Inox Wind", "VP Commercial", 2020)], edu=[("IIT Delhi", 2012)], knows=["p07", "x02"]),
    dict(id="p22", name="Tarun Mathur", org="Endurance Technologies", role="VP, Auto Component Sales", strength=4, last=52, met="Auto expo supplier meetings", themes=["auto ancillaries", "forging", "ev"], history=[H("Bharat Forge", "DGM Marketing", 2013, 2019), H("Endurance Technologies", "VP Sales", 2019)], edu=[("IIT Bombay", 2007)], knows=["p02", "x01"]),
    dict(id="p23", name="Arvind Subramanian", org="Gateway Distriparks", role="Managing Director", strength=4, last=77, met="Port logistics diligence", themes=["shipping", "logistics", "ports"], history=[H("Container Corporation of India", "Regional Head", 2009, 2016), H("Gateway Distriparks", "MD", 2016)], edu=[("IIM Calcutta", 2003)], knows=["p13", "p01"]),
    dict(id="p24", name="Meenakshi Sundaram", org="Care Health Insurance", role="Chief Actuary", strength=3, last=105, met="Health claims loss ratio debate", themes=["insurance", "risk", "actuarial"], history=[H("Star Health", "VP Actuarial", 2012, 2018), H("Care Health", "Chief Actuary", 2018)], edu=[("Institute of Actuaries", 2008)], knows=["p05", "p11"]),
    dict(id="p25", name="Sandeep Bhasin", org="Shree Cement", role="Joint President, Plant Operations", strength=4, last=48, met="Kiln energy efficiency benchmark", themes=["cement", "coal", "logistics"], history=[H("UltraTech Cement", "AVP Operations", 2011, 2018), H("Shree Cement", "Joint President", 2018)], edu=[("IIT BHU", 2005)], knows=["p04"]),
    dict(id="p26", name="Rashmi Deshmukh", org="Godrej Properties", role="Regional Head, Redevelopment", strength=3, last=69, met="South Mumbai society redevelopment pitch", themes=["real estate", "residential", "project execution"], history=[H("Oberoi Realty", "Senior Director", 2015, 2021), H("Godrej Properties", "Regional Head", 2021)], edu=[("ISB", 2014)], knows=["p09"]),
    dict(id="p27", name="Neil D'Souza", org="Siemens India", role="GM, Industrial Automation", strength=3, last=91, met="Digital enterprise symposium", themes=["capital goods", "manufacturing", "robotics"], history=[H("ABB India", "Product Lead", 2013, 2019), H("Siemens India", "GM Automation", 2019)], edu=[("NIT Surathkal", 2009)], knows=["p15"]),
    dict(id="p28", name="Sunita Parekh", org="Welspun Living", role="VP, Global Sourcing & ESG", strength=4, last=36, met="US retail export buyer check", themes=["textiles", "sustainability", "exports"], history=[H("Trident", "Head Sourcing", 2014, 2020), H("Welspun Living", "VP Sourcing", 2020)], edu=[("SRCC", 2010)], knows=["p12"]),
    dict(id="p29", name="Amitav Ghosh", org="Dhanuka Agritech", role="Director, Strategy & M&A", strength=3, last=124, met="Agri-inputs consolidation dinner", themes=["agrochemicals", "rural demand"], history=[H("PI Industries", "Strategic Planning Lead", 2013, 2019), H("Dhanuka Agritech", "Director Strategy", 2019)], edu=[("IIM Lucknow", 2012)], knows=["p17", "p08"]),
    dict(id="p30", name="Radhika Iyer", org="Blue Star", role="VP, Commercial Air Conditioning", strength=3, last=82, met="HVAC dealer network survey", themes=["consumer durables", "pricing"], history=[H("Voltas", "Regional Head West", 2013, 2019), H("Blue Star", "VP Commercial", 2019)], edu=[("SPJIMR", 2011)], knows=["p10", "p20"]),
    dict(id="p31", name="Pradeep Saxena", org="Munich Re India", role="Head of Treaty Reinsurance", strength=4, last=53, met="Reinsurance renewals conference", themes=["insurance", "risk", "underwriting"], history=[H("GIC Re", "DGM Underwriting", 2008, 2017), H("Munich Re India", "Head Treaty Reinsurance", 2017)], edu=[("Delhi University", 2001)], knows=["p11", "p05"]),
    dict(id="p32", name="Aditya Kothari", org="Motherson Group", role="Global Account Director (EV Programs)", strength=4, last=26, met="Lightweighting components review", themes=["auto ancillaries", "ev", "forging"], history=[H("Tata Motors", "Procurement Manager", 2014, 2019), H("Motherson Group", "Global Account Director", 2019)], edu=[("IIT Delhi", 2013)], knows=["p02", "x01"]),
]

EXT_PEOPLE = [
    dict(id="x01", name="Vikram Sethi", org="Bharat Forge", role="Incoming CFO", strength=0, last=0, met="", themes=["auto ancillaries", "capital allocation"], history=[H("Tata Motors", "Head of FP&A", 2014, 2019), H("ZF Group", "Finance VP", 2019, 2026)], edu=[("LSE", 2012)], knows=["p02", "p32"]),
    dict(id="x02", name="Elena Petrov", org="Suzlon Energy", role="Incoming Independent Director", strength=0, last=0, met="", themes=["renewables", "project finance"], history=[H("Siemens Gamesa", "Regional CFO", 2017, 2025)], edu=[("INSEAD", 2010)], knows=["p03", "p21"]),
    dict(id="x03", name="Harish Nair", org="PVR INOX", role="CEO Designate", strength=0, last=0, met="", themes=["hospitality", "media"], history=[H("IHCL", "Chief Operating Officer", 2019, 2026)], edu=[("IIM Kozhikode", 2014)], knows=["p19", "p18"]),
    dict(id="x04", name="Nikhil Varma", org="Blue Dart Express", role="Incoming COO", strength=0, last=0, met="", themes=["logistics", "supply chain"], history=[H("DHL Supply Chain", "Regional Operations Director", 2016, 2026)], edu=[("INSEAD", 2015)], knows=["p01"]),
    dict(id="x05", name="Sanjay Agarwal", org="Bharat Heavy Electricals", role="Incoming Director, Projects", strength=0, last=0, met="", themes=["capital goods", "capex"], history=[H("Larsen & Toubro", "VP Power Projects", 2015, 2026)], edu=[("IIT Roorkee", 2003)], knows=["p14"]),
    dict(id="x06", name="Ritu Singhal", org="Sobha", role="Incoming Chief Legal Officer", strength=0, last=0, met="", themes=["real estate", "project execution"], history=[H("Prestige Estates", "Head of Legal & Land", 2016, 2026)], edu=[("NLSIU", 2008)], knows=["p16"]),
]

_hdr = ["30-Sep-26", "30-Jun-26", "30-Sep-25"]
def _make_table(rev_cur, rev_qoq, rev_yoy, ebitda_cur, ebitda_qoq, ebitda_yoy, pat_cur, pat_qoq, pat_yoy):
    pbt_cur = round(pat_cur / 0.75, 1)
    pbt_qoq = round(pat_qoq / 0.75, 1)
    pbt_yoy = round(pat_yoy / 0.75, 1)
    lines = [
        "Particulars | " + " | ".join(_hdr),
        f"Revenue from operations | {rev_cur:,.1f} | {rev_qoq:,.1f} | {rev_yoy:,.1f}",
        f"EBITDA | {ebitda_cur:,.1f} | {ebitda_qoq:,.1f} | {ebitda_yoy:,.1f}",
        f"Profit before tax | {pbt_cur:,.1f} | {pbt_qoq:,.1f} | {pbt_yoy:,.1f}",
        f"Profit after tax | {pat_cur:,.1f} | {pat_qoq:,.1f} | {pat_yoy:,.1f}",
    ]
    return "Unaudited standalone results (Rs crore)\n" + "\n".join(lines)

ANNOUNCEMENTS = [
    ("b01", "BHEL", 4, "Board approves Rs 3,400 crore capex for new heavy power turbine manufacturing line", "Board approves greenfield turbine plant in Madhya Pradesh. Commercial operations targeted by FY28.", None),
    ("b02", "BHARATFORG", 7, "Appointment of Mr. Vikram Sethi as Chief Financial Officer", "Board has approved the appointment of Mr. Vikram Sethi as Chief Financial Officer, effective 1 December 2026.", "Vikram Sethi"),
    ("b03", "SUZLON", 14, "Outcome of Board Meeting - Unaudited Financial Results for Q2 ended September 30, 2026", _make_table(2095.4, 1845.0, 1417.2, 342.1, 288.6, 214.5, 218.4, 178.2, 112.6), None),
    ("b04", "ULTRACEMCO", 18, "Capacity expansion: Board approves Rs 4,800 crore brownfield capex across 3 grinding units", "Capacity expansion to add 7.2 MTPA to reach domestic target ahead of FY28.", None),
    ("b05", "STARHEALTH", 22, "ICRA reaffirms [ICRA] AAA rating with Stable outlook on subordinated debt", "Rating reaffirmed following statutory claims solvency check.", None),
    ("b06", "CONCOR", 28, "Strategic logistics partnership signed for 4 multimodal rail terminals", "Partnering with shipping consortium to boost Western DFC container turnaround.", None),
    ("b07", "PIIND", 35, "Declaration of interim dividend of Rs 6.00 per share; record date 28 November 2026", "Board declared interim dividend for FY27.", None),
    ("b08", "PVRINOX", 42, "Appointment of Mr. Harish Nair as CEO Designate", "Board appoints hospitality veteran Harish Nair as CEO designate, effective January 2027.", "Harish Nair"),
    ("b09", "BLUEDART", 48, "Outcome of Board Meeting - Unaudited Financial Results for Q2 ended September 30, 2026", _make_table(1420.8, 1340.5, 1268.0, 168.4, 155.2, 142.1, 88.5, 79.4, 71.2), None),
    ("b10", "ABB", 55, "Board approves acquisition of 80% stake in SmartGrid Automation India for Rs 420 crore", "Acquiring control of electrical automation firm to strengthen transmission portfolio.", None),
    ("b11", "SOBHA", 68, "Appointment of Ms. Ritu Singhal as Chief Legal Officer", "Ms. Ritu Singhal joins as Chief Legal Officer to head regulatory and land titles.", "Ritu Singhal"),
    ("b12", "VOLTAS", 80, "Commercial cooling: Rs 550 crore manufacturing unit commissioning in Chennai", "Commercial facility commences commercial dispatch ahead of summer peak.", None),
    ("b13", "ZEEL", 110, "Strategic partnership agreement signed for regional OTT co-production", "Long term syndication pact for regional streaming slate.", None),
    ("b14", "TRIDENT", 130, "Receipt of patent grant for energy-saving recycled textile processing", "Patent grant received from Indian Patent Office.", None),
    ("b15", "GICRE", 150, "Outcome of Board Meeting - Financial Results for the period ended September 30, 2026", _make_table(9450.2, 9120.0, 8430.5, 1210.4, 1140.2, 985.0, 845.2, 790.1, 680.5), None),
]

# Provide fundamentals for portfolio & research names
import copy as _copy
_research_source = next(iter(FUNDAMENTALS.values()))
FUNDAMENTALS = {
    ticker: dict(_copy.deepcopy(_research_source), name=name)
    for ticker, name in {
        "TITAN": "Titan Company",
        "MOTHERSON": "Samvardhana Motherson",
        "INDHOTEL": "Indian Hotels Company",
        "DABUR": "Dabur India",
        "BHARATFORG": "Bharat Forge",
        "SUZLON": "Suzlon Energy",
        "ULTRACEMCO": "UltraTech Cement",
        "BLUEDART": "Blue Dart Express",
        "CONCOR": "Container Corporation of India",
        "BHEL": "Bharat Heavy Electricals",
        "ABB": "ABB India",
        "VOLTAS": "Voltas",
        "STARHEALTH": "Star Health Insurance",
        "PIIND": "PI Industries",
    }.items()
}
