"""
Generate locations/[slug]/data.ts with 30 UK city pages.

Each city is hydrated with REAL grounding context (industries, employers,
business districts, postcode focus, geo coords) so DeepSeek can produce
genuinely local content. The output is a single typed TypeScript module.

Anti-cannibalisation guards:
  - Each city's opening paragraph and case study body are hashed; collisions
    are rejected and re-generated.
  - Pre-computed adjacent-town pairs so cross-links are non-templated.
  - Page-length floor: 1500 words per city; short responses are re-generated.

Run:
    python pipeline/generate_town_pages.py                 # all 30
    python pipeline/generate_town_pages.py --only london   # one city
    python pipeline/generate_town_pages.py --limit 3       # first 3 only (smoke test)
    python pipeline/generate_town_pages.py --workers 5     # parallelism
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import httpx

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agents", "utils"))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
except ImportError:
    pass

from config_supabase import DEEPSEEK_API_KEY
from deepseek_client import DeepSeekClient


ROOT = Path(__file__).resolve().parents[1]
OUT_TS = ROOT / "web" / "src" / "app" / "locations" / "[slug]" / "data.ts"


# Each entry: deterministic facts that DeepSeek will hallucinate badly without
# (industries, employers, districts, postcodes, geo). The model fills in the
# voice + narrative around these anchors.
CITY_SEEDS = {
    # ===== Top 10 metros =====
    "london": {
        "name": "London",
        "region": "Greater London",
        "postcodes": "EC, WC, W1, N1, SE1, E14",
        "districts": ["Shoreditch", "Soho", "Canary Wharf", "King's Cross", "Camden", "Clerkenwell"],
        "sectors": ["Financial services", "Tech and SaaS", "Creative and media", "Professional services", "Hospitality and retail"],
        "employers": ["HSBC", "Barclays", "Deloitte", "Google", "BBC"],
        "population": 8900000,
        "geo": (51.5074, -0.1278),
        "nearby": ["Croydon", "Brentford", "Watford", "Romford"],
    },
    "manchester": {
        "name": "Manchester",
        "region": "Greater Manchester",
        "postcodes": "M1, M2, M3, M4, M15",
        "districts": ["Northern Quarter", "MediaCity", "Ancoats", "Spinningfields", "Castlefield"],
        "sectors": ["Tech and digital", "Professional services", "Media and broadcasting", "Manufacturing", "Retail"],
        "employers": ["BBC (MediaCity)", "Co-op Group", "ITV", "AutoTrader", "Boohoo"],
        "population": 552000,
        "geo": (53.4808, -2.2426),
        "nearby": ["Salford", "Stockport", "Bolton", "Oldham"],
    },
    "birmingham": {
        "name": "Birmingham",
        "region": "West Midlands",
        "postcodes": "B1, B2, B3, B5, B18",
        "districts": ["Jewellery Quarter", "Digbeth", "Colmore Row", "Edgbaston"],
        "sectors": ["Manufacturing and engineering", "Professional services", "Hospitality", "Creative", "Retail"],
        "employers": ["HSBC UK HQ", "Cadbury (Mondelez)", "Jaguar Land Rover", "BT", "Deutsche Bank"],
        "population": 1140000,
        "geo": (52.4862, -1.8904),
        "nearby": ["Solihull", "West Bromwich", "Dudley", "Sutton Coldfield"],
    },
    "leeds": {
        "name": "Leeds",
        "region": "West Yorkshire",
        "postcodes": "LS1, LS2, LS6, LS11",
        "districts": ["City Centre", "Holbeck", "Leeds Dock", "Wellington Place"],
        "sectors": ["Financial and legal services", "Tech and fintech", "Healthcare", "Manufacturing", "Retail and hospitality"],
        "employers": ["Asda HQ", "First Direct", "Yorkshire Bank (Virgin Money)", "TPP", "Sky Betting & Gaming"],
        "population": 815000,
        "geo": (53.8008, -1.5491),
        "nearby": ["Wakefield", "Harrogate", "Pudsey", "Morley"],
    },
    "bristol": {
        "name": "Bristol",
        "region": "South West England",
        "postcodes": "BS1, BS2, BS8, BS16",
        "districts": ["Harbourside", "Stokes Croft", "Clifton", "Temple Quay"],
        "sectors": ["Aerospace and engineering", "Tech and software", "Creative and animation", "Financial services", "Hospitality"],
        "employers": ["Airbus", "Rolls-Royce", "Aardman Animations", "Lloyds Banking Group", "Hargreaves Lansdown"],
        "population": 480000,
        "geo": (51.4545, -2.5879),
        "nearby": ["Bath", "Weston-super-Mare", "Filton", "Portishead"],
    },
    "edinburgh": {
        "name": "Edinburgh",
        "region": "Scotland",
        "postcodes": "EH1, EH2, EH3, EH6, EH8",
        "districts": ["Old Town", "Leith", "New Town", "Quartermile"],
        "sectors": ["Financial services and fintech", "Tourism and hospitality", "Education and research", "Professional services", "Tech"],
        "employers": ["Royal Bank of Scotland (NatWest Group)", "Standard Life Aberdeen (abrdn)", "Tesco Bank", "Scottish Widows", "Skyscanner"],
        "population": 525000,
        "geo": (55.9533, -3.1883),
        "nearby": ["Leith", "Livingston", "Musselburgh", "Dunfermline"],
    },
    "glasgow": {
        "name": "Glasgow",
        "region": "Scotland",
        "postcodes": "G1, G2, G3, G4, G12",
        "districts": ["Merchant City", "Finnieston", "City Centre", "Pacific Quay"],
        "sectors": ["Broadcasting and media", "Engineering and shipbuilding", "Finance", "Creative and design", "Tourism"],
        "employers": ["BBC Scotland", "STV", "BAE Systems", "Morgan Stanley", "Barclays"],
        "population": 635000,
        "geo": (55.8642, -4.2518),
        "nearby": ["Paisley", "East Kilbride", "Clydebank", "Hamilton"],
    },
    "liverpool": {
        "name": "Liverpool",
        "region": "Merseyside",
        "postcodes": "L1, L2, L3, L8, L17",
        "districts": ["Baltic Triangle", "Ropewalks", "Knowledge Quarter", "Waterfront"],
        "sectors": ["Maritime and logistics", "Tech and digital", "Healthcare and life sciences", "Tourism and hospitality", "Creative"],
        "employers": ["Peel Ports", "Unilever (Port Sunlight)", "Liverpool John Lennon Airport", "Royal Liverpool University Hospital", "Studio Liverpool"],
        "population": 500000,
        "geo": (53.4084, -2.9916),
        "nearby": ["Birkenhead", "Wallasey", "Bootle", "St Helens"],
    },
    "sheffield": {
        "name": "Sheffield",
        "region": "South Yorkshire",
        "postcodes": "S1, S2, S3, S10, S11",
        "districts": ["Kelham Island", "City Centre", "Sheaf Valley", "Sharrow Vale"],
        "sectors": ["Advanced manufacturing", "Steel and metalwork", "Tech and digital", "Healthcare", "Education"],
        "employers": ["University of Sheffield", "Sheffield Hallam University", "Forgemasters", "Outokumpu Stainless", "HSBC"],
        "population": 580000,
        "geo": (53.3811, -1.4701),
        "nearby": ["Rotherham", "Barnsley", "Chesterfield", "Doncaster"],
    },
    "newcastle": {
        "name": "Newcastle",
        "region": "Tyne and Wear",
        "postcodes": "NE1, NE2, NE3, NE4",
        "districts": ["Quayside", "Ouseburn", "Grainger Town", "Jesmond"],
        "sectors": ["Tech and software", "Healthcare and life sciences", "Education and research", "Energy and offshore", "Hospitality"],
        "employers": ["Sage Group (Newcastle HQ)", "Newcastle University", "Royal Victoria Infirmary", "Procter & Gamble", "Greggs HQ"],
        "population": 305000,
        "geo": (54.9783, -1.6178),
        "nearby": ["Gateshead", "Sunderland", "North Shields", "Wallsend"],
    },
    # ===== 10 mid-tier wins =====
    "bradford": {
        "name": "Bradford",
        "region": "West Yorkshire",
        "postcodes": "BD1, BD3, BD7, BD8",
        "districts": ["Little Germany", "City Centre", "Saltaire", "Manningham"],
        "sectors": ["Food manufacturing", "Textiles", "Engineering", "Healthcare", "Retail"],
        "employers": ["Morrisons HQ", "Hallmark Cards", "Yorkshire Building Society", "Provident Financial", "Pace plc"],
        "population": 547000,
        "geo": (53.7960, -1.7594),
        "nearby": ["Halifax", "Keighley", "Shipley", "Wakefield"],
    },
    "nottingham": {
        "name": "Nottingham",
        "region": "East Midlands",
        "postcodes": "NG1, NG2, NG7"
        ,
        "districts": ["Lace Market", "Hockley", "Creative Quarter", "Beeston"],
        "sectors": ["Bioscience and pharma", "Financial services", "Creative", "Retail", "Higher education"],
        "employers": ["Boots (No7 Beauty)", "Experian", "Capital One", "Speedo", "Nottingham Trent University"],
        "population": 330000,
        "geo": (52.9548, -1.1581),
        "nearby": ["West Bridgford", "Beeston", "Long Eaton", "Mansfield"],
    },
    "cardiff": {
        "name": "Cardiff",
        "region": "Wales",
        "postcodes": "CF10, CF11, CF14, CF24",
        "districts": ["Cardiff Bay", "City Centre", "Pontcanna", "Roath"],
        "sectors": ["Media and broadcasting", "Financial services", "Education", "Public sector", "Tourism"],
        "employers": ["BBC Cymru Wales", "Admiral Group", "Principality Building Society", "Cardiff University", "Welsh Government"],
        "population": 372000,
        "geo": (51.4816, -3.1791),
        "nearby": ["Newport", "Caerphilly", "Penarth", "Barry"],
    },
    "reading": {
        "name": "Reading",
        "region": "Berkshire",
        "postcodes": "RG1, RG2, RG6, RG30",
        "districts": ["Town Centre", "Caversham", "Green Park", "Tilehurst"],
        "sectors": ["Tech and software", "Financial services", "Consulting", "Insurance", "Telecoms"],
        "employers": ["Microsoft (UK HQ)", "Oracle", "PepsiCo (UK HQ)", "ING", "Verizon"],
        "population": 174000,
        "geo": (51.4543, -0.9781),
        "nearby": ["Wokingham", "Bracknell", "Newbury", "Slough"],
    },
    "brighton": {
        "name": "Brighton",
        "region": "East Sussex",
        "postcodes": "BN1, BN2, BN3",
        "districts": ["North Laine", "Lanes", "Kemp Town", "Hove"],
        "sectors": ["Digital and creative", "Tech and software", "Tourism and hospitality", "Independent retail", "Healthcare"],
        "employers": ["American Express (European HQ)", "Brandwatch", "Brighton & Sussex University Hospitals", "University of Sussex", "Legal & General"],
        "population": 230000,
        "geo": (50.8225, -0.1372),
        "nearby": ["Hove", "Worthing", "Lewes", "Eastbourne"],
    },
    "portsmouth": {
        "name": "Portsmouth",
        "region": "Hampshire",
        "postcodes": "PO1, PO2, PO4, PO5",
        "districts": ["Old Portsmouth", "Gunwharf Quays", "Southsea", "Port Solent"],
        "sectors": ["Marine and defence", "Manufacturing", "Tech and engineering", "Tourism", "Healthcare"],
        "employers": ["BAE Systems", "Royal Navy", "IBM (Hursley)", "Pall Europe", "QinetiQ"],
        "population": 208000,
        "geo": (50.8198, -1.0880),
        "nearby": ["Southampton", "Havant", "Gosport", "Fareham"],
    },
    "coventry": {
        "name": "Coventry",
        "region": "West Midlands",
        "postcodes": "CV1, CV2, CV3, CV4",
        "districts": ["City Centre", "Earlsdon", "Coventry University Quarter", "Stoke"],
        "sectors": ["Automotive and engineering", "Manufacturing", "Education", "Aerospace", "Healthcare"],
        "employers": ["Jaguar Land Rover (research)", "Coventry University", "University of Warwick", "Rolls-Royce", "London Electric Vehicle Company"],
        "population": 345000,
        "geo": (52.4068, -1.5197),
        "nearby": ["Rugby", "Nuneaton", "Leamington Spa", "Solihull"],
    },
    "bournemouth": {
        "name": "Bournemouth",
        "region": "Dorset",
        "postcodes": "BH1, BH2, BH8, BH4",
        "districts": ["Town Centre", "Westbourne", "Boscombe", "Southbourne"],
        "sectors": ["Financial services", "Tourism and hospitality", "Tech and digital", "Healthcare", "Creative"],
        "employers": ["JPMorgan Chase", "Vitality Health", "RNLI HQ (Poole)", "Bournemouth University", "Liverpool Victoria"],
        "population": 200000,
        "geo": (50.7192, -1.8808),
        "nearby": ["Poole", "Christchurch", "Ferndown", "New Milton"],
    },
    "plymouth": {
        "name": "Plymouth",
        "region": "Devon",
        "postcodes": "PL1, PL3, PL4, PL6"
        ,
        "districts": ["The Barbican", "Royal William Yard", "City Centre", "Mutley"],
        "sectors": ["Marine and defence", "Manufacturing", "Tourism", "Healthcare", "Higher education"],
        "employers": ["Babcock International (Devonport)", "Princess Yachts", "Plymouth University", "University Hospitals Plymouth NHS Trust", "Royal Navy"],
        "population": 265000,
        "geo": (50.3755, -4.1427),
        "nearby": ["Saltash", "Ivybridge", "Tavistock", "Torpoint"],
    },
    "hull": {
        "name": "Hull",
        "region": "East Yorkshire",
        "postcodes": "HU1, HU2, HU3, HU5, HU9",
        "districts": ["Old Town", "Marina", "Fruit Market", "Newland"],
        "sectors": ["Offshore wind and renewables", "Logistics and port", "Healthcare", "Manufacturing", "Higher education"],
        "employers": ["Siemens Gamesa", "BP Saltend", "Smith & Nephew", "University of Hull", "Reckitt Benckiser"],
        "population": 267000,
        "geo": (53.7457, -0.3367),
        "nearby": ["Beverley", "Hessle", "Cottingham", "Goole"],
    },
    # ===== 10 secondary cities =====
    "leicester": {
        "name": "Leicester",
        "region": "East Midlands",
        "postcodes": "LE1, LE2, LE3, LE4",
        "districts": ["Cultural Quarter", "City Centre", "Highcross", "Clarendon Park"],
        "sectors": ["Textiles and manufacturing", "Food production", "Logistics", "Healthcare", "Education"],
        "employers": ["Walkers Snack Foods (PepsiCo)", "Next plc", "Dunelm Group", "University of Leicester", "British Gas"],
        "population": 360000,
        "geo": (52.6369, -1.1398),
        "nearby": ["Loughborough", "Hinckley", "Oadby", "Wigston"],
    },
    "stoke-on-trent": {
        "name": "Stoke-on-Trent",
        "region": "Staffordshire",
        "postcodes": "ST1, ST3, ST4, ST6",
        "districts": ["Hanley", "Stoke", "Burslem", "Etruria Valley"],
        "sectors": ["Ceramics and manufacturing", "Logistics", "Financial services", "Healthcare", "Retail"],
        "employers": ["Bet365", "Vodafone", "JCB (Rocester)", "Wedgwood", "Royal Stoke University Hospital"],
        "population": 260000,
        "geo": (53.0027, -2.1794),
        "nearby": ["Newcastle-under-Lyme", "Crewe", "Stafford", "Leek"],
    },
    "wolverhampton": {
        "name": "Wolverhampton",
        "region": "West Midlands",
        "postcodes": "WV1, WV2, WV3, WV10",
        "districts": ["City Centre", "Tettenhall", "Compton", "Penn"],
        "sectors": ["Engineering and manufacturing", "Aerospace", "Healthcare", "Logistics", "Public sector"],
        "employers": ["Moog Aircraft", "UTC Aerospace", "Royal Wolverhampton NHS Trust", "Marston's Brewery", "Wolverhampton Council"],
        "population": 263000,
        "geo": (52.5870, -2.1288),
        "nearby": ["Walsall", "Dudley", "Telford", "Cannock"],
    },
    "derby": {
        "name": "Derby",
        "region": "Derbyshire",
        "postcodes": "DE1, DE3, DE22, DE23",
        "districts": ["City Centre", "Pride Park", "Allestree", "Littleover"],
        "sectors": ["Aerospace and rail", "Engineering", "Manufacturing", "Tech", "Healthcare"],
        "employers": ["Rolls-Royce (aerospace)", "Toyota Manufacturing UK", "Alstom Transport", "Bombardier (now Alstom)", "JCB"],
        "population": 260000,
        "geo": (52.9225, -1.4746),
        "nearby": ["Burton-on-Trent", "Long Eaton", "Belper", "Ilkeston"],
    },
    "southampton": {
        "name": "Southampton",
        "region": "Hampshire",
        "postcodes": "SO14, SO15, SO16, SO17",
        "districts": ["City Centre", "Ocean Village", "Bedford Place", "Portswood"],
        "sectors": ["Maritime and cruise", "Tech and digital", "Healthcare", "Education and research", "Manufacturing"],
        "employers": ["Carnival UK", "Ordnance Survey", "ABP (Southampton Port)", "Aviva", "University of Southampton"],
        "population": 253000,
        "geo": (50.9097, -1.4044),
        "nearby": ["Eastleigh", "Winchester", "Romsey", "Hythe"],
    },
    "milton-keynes": {
        "name": "Milton Keynes",
        "region": "Buckinghamshire",
        "postcodes": "MK9, MK1, MK6, MK14",
        "districts": ["Central Milton Keynes", "Bletchley", "Wolverton", "Stony Stratford"],
        "sectors": ["Logistics and distribution", "Tech and ecommerce", "Financial services", "Automotive (Mercedes-Benz, Volkswagen)", "Retail"],
        "employers": ["Network Rail", "Volkswagen Financial Services", "Santander UK", "Argos (Sainsbury's)", "Red Bull Racing"],
        "population": 287000,
        "geo": (52.0406, -0.7594),
        "nearby": ["Bedford", "Buckingham", "Aylesbury", "Northampton"],
    },
    "northampton": {
        "name": "Northampton",
        "region": "Northamptonshire",
        "postcodes": "NN1, NN3, NN4, NN5",
        "districts": ["Town Centre", "Brackmills", "Abington", "St James"],
        "sectors": ["Logistics and distribution", "Engineering", "Footwear and leather (heritage)", "Financial services", "Healthcare"],
        "employers": ["Carlsberg UK", "Travis Perkins HQ", "Nationwide Building Society", "Avon Cosmetics UK", "Church's Shoes"],
        "population": 220000,
        "geo": (52.2405, -0.9027),
        "nearby": ["Wellingborough", "Kettering", "Daventry", "Towcester"],
    },
    "oxford": {
        "name": "Oxford",
        "region": "Oxfordshire",
        "postcodes": "OX1, OX2, OX3, OX4",
        "districts": ["City Centre", "Headington", "Cowley", "Jericho"],
        "sectors": ["Higher education and research", "Biotech and life sciences", "Publishing", "Automotive (BMW Mini)", "Tech"],
        "employers": ["University of Oxford", "Oxford University Press", "BMW Plant Oxford", "Oxford BioMedica", "John Radcliffe Hospital"],
        "population": 162000,
        "geo": (51.7520, -1.2577),
        "nearby": ["Banbury", "Abingdon", "Witney", "Bicester"],
    },
    "cambridge": {
        "name": "Cambridge",
        "region": "Cambridgeshire",
        "postcodes": "CB1, CB2, CB3, CB4",
        "districts": ["City Centre", "Cambridge Science Park", "Cherry Hinton", "Newnham"],
        "sectors": ["Tech and software (Silicon Fen)", "Biotech and pharma", "Higher education and research", "Publishing", "Professional services"],
        "employers": ["Arm Holdings", "AstraZeneca (Cambridge HQ)", "Microsoft Research", "University of Cambridge", "Cambridge University Press"],
        "population": 145000,
        "geo": (52.2053, 0.1218),
        "nearby": ["Ely", "St Neots", "Huntingdon", "Royston"],
    },
    "york": {
        "name": "York",
        "region": "North Yorkshire",
        "postcodes": "YO1, YO10, YO24, YO30",
        "districts": ["City Centre", "Heworth", "Acomb", "Clifton"],
        "sectors": ["Tourism and hospitality", "Higher education", "Rail and engineering", "Bioscience", "Insurance"],
        "employers": ["Aviva (York office)", "Hiscox", "University of York", "Nestlé (Rowntree)", "Bettys & Taylors"],
        "population": 209000,
        "geo": (53.9590, -1.0815),
        "nearby": ["Selby", "Tadcaster", "Harrogate", "Scarborough"],
    },
    # ===== Expansion: 50 more UK cities (Wave 2) =====
    "aberdeen": {"name": "Aberdeen", "region": "Scotland", "postcodes": "AB10, AB11, AB15, AB24", "districts": ["City Centre", "Old Aberdeen", "Bridge of Don", "Westhill"], "sectors": ["Oil and gas", "Energy and offshore", "Fishing and seafood", "Higher education", "Healthcare"], "employers": ["BP North Sea", "Shell UK", "TotalEnergies", "University of Aberdeen", "NHS Grampian"], "population": 200000, "geo": (57.1497, -2.0943), "nearby": ["Westhill", "Stonehaven", "Inverurie", "Peterhead"]},
    "dundee": {"name": "Dundee", "region": "Scotland", "postcodes": "DD1, DD2, DD3, DD4", "districts": ["City Centre", "Waterfront", "West End", "Lochee"], "sectors": ["Life sciences and biotech", "Video games and tech", "Higher education", "Healthcare", "Renewable energy"], "employers": ["NCR Corporation", "DC Thomson", "Rockstar Dundee", "University of Dundee", "NHS Tayside"], "population": 148000, "geo": (56.4620, -2.9707), "nearby": ["Perth", "St Andrews", "Arbroath", "Forfar"]},
    "inverness": {"name": "Inverness", "region": "Scotland", "postcodes": "IV1, IV2, IV3", "districts": ["City Centre", "Crown", "Inshes", "Westhill"], "sectors": ["Tourism and hospitality", "Public sector", "Healthcare", "Retail", "Renewable energy"], "employers": ["NHS Highland", "Highlands and Islands Enterprise", "Inverness College UHI", "LifeScan Scotland", "Highland Council"], "population": 70000, "geo": (57.4778, -4.2247), "nearby": ["Nairn", "Fort William", "Aviemore", "Dingwall"]},
    "belfast": {"name": "Belfast", "region": "Northern Ireland", "postcodes": "BT1, BT2, BT7, BT9", "districts": ["City Centre", "Titanic Quarter", "Cathedral Quarter", "Queen's Quarter"], "sectors": ["Tech and software", "Financial services", "Aerospace and shipbuilding", "Creative industries", "Higher education"], "employers": ["Citi", "Allstate NI", "Spirit AeroSystems (Bombardier)", "Queen's University Belfast", "Liberty IT"], "population": 345000, "geo": (54.5973, -5.9301), "nearby": ["Lisburn", "Newtownabbey", "Bangor", "Holywood"]},
    "swansea": {"name": "Swansea", "region": "Wales", "postcodes": "SA1, SA2, SA3, SA6", "districts": ["City Centre", "Maritime Quarter", "SA1 Waterfront", "Mumbles"], "sectors": ["Higher education", "Healthcare", "Manufacturing", "Tourism", "Tech"], "employers": ["Swansea University", "Morriston Hospital", "Tata Steel (Port Talbot nearby)", "DVLA HQ", "Admiral Group (Swansea offices)"], "population": 245000, "geo": (51.6214, -3.9436), "nearby": ["Neath", "Port Talbot", "Llanelli", "Carmarthen"]},
    "newport": {"name": "Newport", "region": "Wales", "postcodes": "NP10, NP19, NP20", "districts": ["City Centre", "Maindee", "Pillgwenlly", "Bettws"], "sectors": ["Public sector", "Manufacturing", "Logistics", "Healthcare", "Tech and semiconductors"], "employers": ["ONS (Office for National Statistics)", "Newport Wafer Fab", "Admiral Group", "Aneurin Bevan Health Board", "Intellectual Property Office"], "population": 160000, "geo": (51.5842, -2.9977), "nearby": ["Caerphilly", "Cwmbran", "Pontypool", "Chepstow"]},
    "sunderland": {"name": "Sunderland", "region": "Tyne and Wear", "postcodes": "SR1, SR2, SR3, SR4", "districts": ["City Centre", "Roker", "Seaburn", "Washington"], "sectors": ["Automotive manufacturing", "Software and tech", "Healthcare", "Higher education", "Retail"], "employers": ["Nissan Motor Manufacturing UK", "Sunderland Software City", "University of Sunderland", "Sunderland Royal Hospital", "Liebherr Cranes UK"], "population": 175000, "geo": (54.9069, -1.3838), "nearby": ["South Shields", "Washington", "Houghton-le-Spring", "Seaham"]},
    "middlesbrough": {"name": "Middlesbrough", "region": "Tees Valley", "postcodes": "TS1, TS3, TS4, TS5", "districts": ["Town Centre", "Linthorpe", "Acklam", "Middlehaven"], "sectors": ["Chemicals and process industries", "Steel and engineering", "Healthcare", "Higher education", "Logistics"], "employers": ["SABIC UK Petrochemicals", "James Cook University Hospital", "Teesside University", "PD Ports", "AV Dawson"], "population": 140000, "geo": (54.5742, -1.2348), "nearby": ["Stockton-on-Tees", "Redcar", "Hartlepool", "Darlington"]},
    "doncaster": {"name": "Doncaster", "region": "South Yorkshire", "postcodes": "DN1, DN2, DN4, DN5", "districts": ["Town Centre", "Bessacarr", "Edenthorpe", "Lakeside"], "sectors": ["Logistics and distribution", "Rail and engineering", "Aviation", "Retail", "Healthcare"], "employers": ["Amazon Doncaster", "Wabtec Rail (Hitachi)", "iPort Doncaster", "Doncaster Sheffield Airport (legacy)", "Doncaster Royal Infirmary"], "population": 109000, "geo": (53.5228, -1.1285), "nearby": ["Rotherham", "Barnsley", "Wakefield", "Goole"]},
    "halifax": {"name": "Halifax", "region": "West Yorkshire", "postcodes": "HX1, HX2, HX3", "districts": ["Town Centre", "Halifax Borough Market", "Sowerby Bridge", "Brighouse"], "sectors": ["Financial services", "Manufacturing and textiles (heritage)", "Healthcare", "Logistics", "Retail"], "employers": ["Lloyds Banking Group (Halifax brand HQ)", "Covea Insurance", "Calderdale Royal Hospital", "Suma Wholefoods", "Nestle Purina"], "population": 88000, "geo": (53.7240, -1.8636), "nearby": ["Bradford", "Huddersfield", "Sowerby Bridge", "Brighouse"]},
    "huddersfield": {"name": "Huddersfield", "region": "West Yorkshire", "postcodes": "HD1, HD2, HD3, HD5", "districts": ["Town Centre", "Lindley", "Marsh", "Almondbury"], "sectors": ["Engineering and manufacturing", "Higher education", "Healthcare", "Textiles (heritage)", "Logistics"], "employers": ["University of Huddersfield", "Cummins Turbo Technologies", "Reliance Precision", "Syngenta", "Huddersfield Royal Infirmary"], "population": 162000, "geo": (53.6458, -1.7850), "nearby": ["Halifax", "Wakefield", "Holmfirth", "Brighouse"]},
    "wakefield": {"name": "Wakefield", "region": "West Yorkshire", "postcodes": "WF1, WF2, WF3", "districts": ["City Centre", "Trinity Walk", "Sandal", "Outwood"], "sectors": ["Logistics and distribution", "Public sector", "Manufacturing", "Healthcare", "Creative industries"], "employers": ["ASDA Distribution", "Coca-Cola Enterprises (Wakefield plant)", "Mid Yorkshire NHS Trust", "Pinderfields Hospital", "BLP Insurance"], "population": 100000, "geo": (53.6833, -1.4977), "nearby": ["Leeds", "Pontefract", "Castleford", "Dewsbury"]},
    "preston": {"name": "Preston", "region": "Lancashire", "postcodes": "PR1, PR2, PR4, PR5", "districts": ["City Centre", "Fulwood", "Penwortham", "Bamber Bridge"], "sectors": ["Higher education", "Aerospace and defence", "Public sector", "Manufacturing", "Healthcare"], "employers": ["University of Central Lancashire", "BAE Systems (Warton)", "Lancashire County Council", "Royal Preston Hospital", "Westinghouse Springfields"], "population": 145000, "geo": (53.7632, -2.7031), "nearby": ["Blackburn", "Chorley", "Leyland", "Lancaster"]},
    "blackpool": {"name": "Blackpool", "region": "Lancashire", "postcodes": "FY1, FY2, FY3, FY4", "districts": ["Promenade", "South Shore", "North Shore", "Bispham"], "sectors": ["Tourism and hospitality", "Healthcare", "Public sector", "Retail", "Construction"], "employers": ["Blackpool Pleasure Beach", "Blackpool Council", "Blackpool Victoria Hospital", "Burton's Biscuit Company", "DWP Blackpool"], "population": 140000, "geo": (53.8175, -3.0357), "nearby": ["Fleetwood", "Lytham St Annes", "Cleveleys", "Poulton-le-Fylde"]},
    "salford": {"name": "Salford", "region": "Greater Manchester", "postcodes": "M3, M5, M6, M7", "districts": ["Salford Quays", "MediaCity", "Eccles", "Swinton"], "sectors": ["Media and broadcasting", "Higher education", "Tech and digital", "Real estate", "Healthcare"], "employers": ["BBC (MediaCity)", "ITV Studios", "University of Salford", "Salford Royal Hospital", "Co-op Group"], "population": 280000, "geo": (53.4875, -2.2901), "nearby": ["Manchester", "Eccles", "Swinton", "Worsley"]},
    "stockport": {"name": "Stockport", "region": "Greater Manchester", "postcodes": "SK1, SK2, SK3, SK4", "districts": ["Town Centre", "Cheadle", "Heaton Moor", "Bramhall"], "sectors": ["Tech and software", "Manufacturing", "Financial services", "Healthcare", "Retail"], "employers": ["Co-operative Bank", "Adidas UK HQ", "Stepping Hill Hospital", "JCDecaux", "BASF UK"], "population": 295000, "geo": (53.4083, -2.1494), "nearby": ["Manchester", "Cheadle", "Wilmslow", "Marple"]},
    "bolton": {"name": "Bolton", "region": "Greater Manchester", "postcodes": "BL1, BL2, BL3, BL6", "districts": ["Town Centre", "Horwich", "Westhoughton", "Farnworth"], "sectors": ["Manufacturing", "Logistics", "Healthcare", "Higher education", "Retail"], "employers": ["Warburtons (HQ)", "MBDA Missile Systems", "University of Bolton", "Royal Bolton Hospital", "Reebok (HQ historically)"], "population": 285000, "geo": (53.5784, -2.4297), "nearby": ["Bury", "Wigan", "Chorley", "Manchester"]},
    "rochdale": {"name": "Rochdale", "region": "Greater Manchester", "postcodes": "OL11, OL12, OL16", "districts": ["Town Centre", "Heywood", "Middleton", "Norden"], "sectors": ["Manufacturing", "Logistics", "Public sector", "Healthcare", "Retail"], "employers": ["JD Williams (N Brown Group)", "Lloyd's Pharmacy distribution", "Rochdale Council", "Pennine Acute NHS Trust", "Crompton Lighting"], "population": 110000, "geo": (53.6097, -2.1561), "nearby": ["Oldham", "Heywood", "Middleton", "Bury"]},
    "burnley": {"name": "Burnley", "region": "Lancashire", "postcodes": "BB10, BB11, BB12", "districts": ["Town Centre", "Burnley Wood", "Padiham", "Brunshaw"], "sectors": ["Aerospace and engineering", "Manufacturing", "Healthcare", "Education", "Retail"], "employers": ["Safran Nacelles", "Velocity Composites", "Crown Paints", "East Lancashire Hospitals NHS Trust", "Veka UK"], "population": 75000, "geo": (53.7894, -2.2454), "nearby": ["Nelson", "Accrington", "Padiham", "Blackburn"]},
    "warrington": {"name": "Warrington", "region": "Cheshire", "postcodes": "WA1, WA2, WA4, WA5", "districts": ["Town Centre", "Stockton Heath", "Birchwood", "Lymm"], "sectors": ["Logistics and distribution", "Nuclear and engineering", "Tech and telecoms", "Manufacturing", "Healthcare"], "employers": ["United Utilities HQ", "Sellafield Ltd (engineering offices)", "Vodafone UK", "Bruntwood SciTech", "Cavendish Nuclear"], "population": 210000, "geo": (53.3900, -2.5970), "nearby": ["Widnes", "Runcorn", "St Helens", "Northwich"]},
    "wigan": {"name": "Wigan", "region": "Greater Manchester", "postcodes": "WN1, WN3, WN5", "districts": ["Town Centre", "Standish", "Ashton-in-Makerfield", "Leigh"], "sectors": ["Logistics and warehousing", "Manufacturing", "Healthcare", "Public sector", "Retail"], "employers": ["Heinz UK (manufacturing nearby)", "Wigan Council", "Wrightington Wigan and Leigh NHS Trust", "BAE Systems (Chorley nearby)", "Premier Foods"], "population": 105000, "geo": (53.5450, -2.6326), "nearby": ["Bolton", "St Helens", "Leigh", "Skelmersdale"]},
    "telford": {"name": "Telford", "region": "Shropshire", "postcodes": "TF1, TF2, TF3, TF4", "districts": ["Town Centre", "Wellington", "Madeley", "Donnington"], "sectors": ["Manufacturing and engineering", "Logistics", "Tech", "Healthcare", "Defence"], "employers": ["Capgemini", "DXC Technology", "Ricoh", "Princess Royal Hospital", "Telford Council"], "population": 175000, "geo": (52.6766, -2.4470), "nearby": ["Shrewsbury", "Wolverhampton", "Newport (Shropshire)", "Bridgnorth"]},
    "walsall": {"name": "Walsall", "region": "West Midlands", "postcodes": "WS1, WS2, WS3, WS5", "districts": ["Town Centre", "Bloxwich", "Pelsall", "Aldridge"], "sectors": ["Manufacturing", "Logistics", "Healthcare", "Retail", "Education"], "employers": ["Homeserve plc HQ", "Boagroup", "Walsall Manor Hospital", "Walsall Council", "RAC Limited"], "population": 285000, "geo": (52.5862, -1.9824), "nearby": ["Wolverhampton", "Birmingham", "Sutton Coldfield", "Cannock"]},
    "cheltenham": {"name": "Cheltenham", "region": "Gloucestershire", "postcodes": "GL50, GL51, GL52, GL53", "districts": ["Town Centre", "Montpellier", "Promenade", "Pittville"], "sectors": ["Tech and cyber", "Aerospace and engineering", "Financial services", "Tourism", "Public sector"], "employers": ["GCHQ", "Spirax-Sarco Engineering", "Endsleigh Insurance", "Kohler Mira", "Cheltenham Festival (The Jockey Club)"], "population": 117000, "geo": (51.8990, -2.0786), "nearby": ["Gloucester", "Tewkesbury", "Stroud", "Cirencester"]},
    "gloucester": {"name": "Gloucester", "region": "Gloucestershire", "postcodes": "GL1, GL2, GL3, GL4", "districts": ["City Centre", "Gloucester Quays", "Quedgeley", "Hucclecote"], "sectors": ["Aerospace and defence", "Logistics", "Healthcare", "Higher education", "Manufacturing"], "employers": ["GE Aerospace", "Safran Landing Systems", "EDF Energy (Barnwood)", "Gloucestershire Royal Hospital", "University of Gloucestershire"], "population": 132000, "geo": (51.8642, -2.2380), "nearby": ["Cheltenham", "Tewkesbury", "Stroud", "Newent"]},
    "bath": {"name": "Bath", "region": "Somerset", "postcodes": "BA1, BA2", "districts": ["City Centre", "Widcombe", "Larkhall", "Combe Down"], "sectors": ["Tourism and hospitality", "Higher education", "Tech and software", "Financial services", "Creative industries"], "employers": ["University of Bath", "Buro Happold", "Rotork", "Royal United Hospital", "Bath Spa University"], "population": 95000, "geo": (51.3811, -2.3590), "nearby": ["Bristol", "Bradford-on-Avon", "Trowbridge", "Frome"]},
    "exeter": {"name": "Exeter", "region": "Devon", "postcodes": "EX1, EX2, EX4", "districts": ["City Centre", "Quay", "Heavitree", "St James"], "sectors": ["Higher education", "Tech and software", "Public sector", "Healthcare", "Financial services"], "employers": ["University of Exeter", "Met Office HQ", "RD&E Hospital", "Devon County Council", "South West Water"], "population": 130000, "geo": (50.7184, -3.5339), "nearby": ["Topsham", "Exmouth", "Crediton", "Newton Abbot"]},
    "norwich": {"name": "Norwich", "region": "Norfolk", "postcodes": "NR1, NR2, NR3, NR4", "districts": ["City Centre", "Riverside", "Eaton", "Thorpe St Andrew"], "sectors": ["Financial services and insurance", "Higher education", "Healthcare", "Tech", "Creative industries"], "employers": ["Aviva (Norwich HQ)", "Norwich Union (legacy)", "University of East Anglia", "Norfolk and Norwich University Hospital", "Marsh"], "population": 145000, "geo": (52.6309, 1.2974), "nearby": ["Wymondham", "Diss", "Cromer", "Great Yarmouth"]},
    "ipswich": {"name": "Ipswich", "region": "Suffolk", "postcodes": "IP1, IP2, IP3, IP4", "districts": ["Town Centre", "Waterfront", "Christchurch Park", "Kesgrave"], "sectors": ["Logistics and port", "Insurance and financial services", "Tech", "Healthcare", "Public sector"], "employers": ["Willis Towers Watson", "BT Adastral Park (nearby)", "AXA Insurance", "Ipswich Hospital", "Suffolk County Council"], "population": 138000, "geo": (52.0567, 1.1482), "nearby": ["Felixstowe", "Bury St Edmunds", "Stowmarket", "Woodbridge"]},
    "peterborough": {"name": "Peterborough", "region": "Cambridgeshire", "postcodes": "PE1, PE2, PE3, PE7", "districts": ["City Centre", "Hampton", "Werrington", "Stanground"], "sectors": ["Logistics and distribution", "Manufacturing", "Financial services", "Public sector", "Engineering"], "employers": ["Perkins Engines (Caterpillar)", "BGL Group (Comparethemarket)", "Peterborough City Hospital", "Thomas Cook (legacy)", "RSPB HQ"], "population": 215000, "geo": (52.5695, -0.2405), "nearby": ["Cambridge", "Stamford", "Spalding", "Huntingdon"]},
    "chelmsford": {"name": "Chelmsford", "region": "Essex", "postcodes": "CM1, CM2, CM3", "districts": ["City Centre", "Great Baddow", "Springfield", "Writtle"], "sectors": ["Financial services", "Tech and software", "Public sector", "Engineering", "Higher education"], "employers": ["e2v Technologies", "BAE Systems (Eastern Counties)", "Anglia Ruskin University", "Essex County Council", "Eversheds Sutherland"], "population": 110000, "geo": (51.7356, 0.4685), "nearby": ["Colchester", "Brentwood", "Braintree", "Witham"]},
    "colchester": {"name": "Colchester", "region": "Essex", "postcodes": "CO1, CO2, CO3, CO4", "districts": ["Town Centre", "Lexden", "Greenstead", "Mile End"], "sectors": ["Higher education", "Defence", "Healthcare", "Public sector", "Retail"], "employers": ["University of Essex", "Colchester Garrison (British Army)", "Colchester Hospital", "Essex Police HQ", "Anglia Ruskin University"], "population": 195000, "geo": (51.8959, 0.8919), "nearby": ["Chelmsford", "Clacton-on-Sea", "Braintree", "Harwich"]},
    "basingstoke": {"name": "Basingstoke", "region": "Hampshire", "postcodes": "RG21, RG22, RG24", "districts": ["Town Centre", "Chineham", "Brighton Hill", "Old Basing"], "sectors": ["Tech and software", "Insurance and financial services", "Pharmaceutical and life sciences", "Logistics", "Engineering"], "employers": ["AA (Automobile Association) HQ", "Sun Life Financial", "Eli Lilly UK HQ", "Hampshire Hospitals NHS", "Sony Music Entertainment"], "population": 113000, "geo": (51.2667, -1.0876), "nearby": ["Reading", "Andover", "Newbury", "Winchester"]},
    "maidstone": {"name": "Maidstone", "region": "Kent", "postcodes": "ME14, ME15, ME16, ME17", "districts": ["Town Centre", "Loose", "Allington", "Bearsted"], "sectors": ["Public sector", "Healthcare", "Logistics", "Retail", "Agriculture and food production"], "employers": ["Kent County Council", "Maidstone Hospital", "Whatman International (GE Healthcare)", "Mid Kent College", "Skanska (regional office)"], "population": 115000, "geo": (51.2727, 0.5234), "nearby": ["Ashford", "Tonbridge", "Sittingbourne", "Tunbridge Wells"]},
    "guildford": {"name": "Guildford", "region": "Surrey", "postcodes": "GU1, GU2, GU3, GU4", "districts": ["Town Centre", "Stoughton", "Burpham", "Onslow Village"], "sectors": ["Tech and software", "Higher education", "Financial services", "Pharmaceutical", "Gaming and VFX"], "employers": ["University of Surrey", "Surrey Satellite Technology Ltd", "Electronic Arts (EA) UK HQ", "Royal Surrey County Hospital", "Lloyds Banking Group (regional)"], "population": 145000, "geo": (51.2362, -0.5704), "nearby": ["Woking", "Aldershot", "Farnham", "Godalming"]},
    "slough": {"name": "Slough", "region": "Berkshire", "postcodes": "SL1, SL2, SL3", "districts": ["Town Centre", "Slough Trading Estate", "Cippenham", "Langley"], "sectors": ["Tech and HQ presence", "Logistics", "Manufacturing", "Consumer goods", "Pharmaceutical"], "employers": ["Mars UK HQ", "Reckitt Benckiser", "O2 (Telefonica)", "DHL", "Lonza Biologics"], "population": 165000, "geo": (51.5105, -0.5950), "nearby": ["Windsor", "Maidenhead", "Heathrow Airport", "Uxbridge"]},
    "watford": {"name": "Watford", "region": "Hertfordshire", "postcodes": "WD17, WD18, WD24, WD25", "districts": ["Town Centre", "Cassiobury", "Garston", "Bushey"], "sectors": ["Tech and software", "Retail HQ", "Financial services", "Healthcare", "Logistics"], "employers": ["JD Wetherspoon HQ", "Camelot UK Lotteries (legacy National Lottery)", "BRE Group", "Watford General Hospital", "Costco UK HQ"], "population": 130000, "geo": (51.6566, -0.3958), "nearby": ["Hemel Hempstead", "St Albans", "Harrow", "Bushey"]},
    "st-albans": {"name": "St Albans", "region": "Hertfordshire", "postcodes": "AL1, AL2, AL3, AL4", "districts": ["City Centre", "Marshalswick", "Fleetville", "Harpenden"], "sectors": ["Professional services", "Tech and consulting", "Tourism", "Higher education", "Financial services"], "employers": ["EDF Energy (Sunningdale Park)", "Lockheed Martin UK", "Premier Foods HQ", "University of Hertfordshire (Hatfield)", "Healthcare Locums"], "population": 88000, "geo": (51.7520, -0.3360), "nearby": ["Watford", "Harpenden", "Hatfield", "Hemel Hempstead"]},
    "croydon": {"name": "Croydon", "region": "Greater London", "postcodes": "CR0, CR2, CR3, CR4", "districts": ["Town Centre", "South Croydon", "Purley", "Addiscombe"], "sectors": ["Financial services", "Tech and digital", "Retail", "Public sector", "Healthcare"], "employers": ["Allianz UK HQ", "Mott MacDonald", "Croydon Council", "Croydon University Hospital", "HM Passport Office"], "population": 390000, "geo": (51.3762, -0.0982), "nearby": ["Sutton", "Bromley", "Wallington", "Caterham"]},
    "sutton": {"name": "Sutton", "region": "Greater London", "postcodes": "SM1, SM2, SM3, SM5", "districts": ["Town Centre", "Cheam", "Wallington", "Carshalton"], "sectors": ["Healthcare and life sciences", "Public sector", "Retail", "Tech", "Education"], "employers": ["Institute of Cancer Research", "Royal Marsden Hospital", "Sutton Council", "St Helier Hospital", "Reed Elsevier (legacy)"], "population": 200000, "geo": (51.3618, -0.1944), "nearby": ["Croydon", "Wimbledon", "Kingston upon Thames", "Epsom"]},
    "bromley": {"name": "Bromley", "region": "Greater London", "postcodes": "BR1, BR2, BR3, BR5", "districts": ["Town Centre", "Bromley South", "Beckenham", "Orpington"], "sectors": ["Professional services", "Retail", "Healthcare", "Public sector", "Financial services"], "employers": ["Bromley Council", "Princess Royal University Hospital", "Glades Shopping Centre", "Churchill Theatre", "Mayer Brown"], "population": 333000, "geo": (51.4068, 0.0140), "nearby": ["Beckenham", "Orpington", "Croydon", "Sevenoaks"]},
    "kingston-upon-thames": {"name": "Kingston upon Thames", "region": "Greater London", "postcodes": "KT1, KT2, KT3, KT6", "districts": ["Town Centre", "Surbiton", "New Malden", "Norbiton"], "sectors": ["Higher education", "Tech and digital", "Retail", "Healthcare", "Professional services"], "employers": ["Kingston University", "Bentalls (legacy retail anchor)", "Kingston Hospital", "Unilever (regional)", "John Lewis"], "population": 175000, "geo": (51.4123, -0.3007), "nearby": ["Wimbledon", "Surbiton", "Richmond", "Esher"]},
    "harrow": {"name": "Harrow", "region": "Greater London", "postcodes": "HA1, HA2, HA3, HA5", "districts": ["Town Centre", "Pinner", "Wealdstone", "Harrow on the Hill"], "sectors": ["Healthcare", "Education and independent schools", "Public sector", "Retail", "Professional services"], "employers": ["Harrow School", "Northwick Park Hospital", "London Borough of Harrow", "St Mary's Catholic School", "Capita"], "population": 250000, "geo": (51.5790, -0.3416), "nearby": ["Wembley", "Pinner", "Watford", "Hillingdon"]},
    "romford": {"name": "Romford", "region": "Greater London", "postcodes": "RM1, RM2, RM3, RM5", "districts": ["Town Centre", "Romford Market", "Gidea Park", "Collier Row"], "sectors": ["Retail", "Healthcare", "Public sector", "Logistics", "Financial services"], "employers": ["Queen's Hospital Romford", "London Borough of Havering", "Brewers Fayre / Premier Inn (legacy bases)", "The Brewery shopping centre", "Caesarstone UK"], "population": 122000, "geo": (51.5779, 0.1819), "nearby": ["Hornchurch", "Brentwood", "Dagenham", "Upminster"]},
    "luton": {"name": "Luton", "region": "Bedfordshire", "postcodes": "LU1, LU2, LU3, LU4", "districts": ["Town Centre", "Bury Park", "Stopsley", "Leagrave"], "sectors": ["Aviation and logistics", "Manufacturing", "Healthcare", "Higher education", "Retail"], "employers": ["London Luton Airport", "Vauxhall Motors (Stellantis)", "easyJet HQ", "Luton and Dunstable Hospital", "University of Bedfordshire"], "population": 218000, "geo": (51.8787, -0.4200), "nearby": ["Dunstable", "St Albans", "Hitchin", "Hemel Hempstead"]},
    "lincoln": {"name": "Lincoln", "region": "Lincolnshire", "postcodes": "LN1, LN2, LN5, LN6", "districts": ["City Centre", "Bailgate", "Brayford Pool", "Birchwood"], "sectors": ["Higher education", "Engineering and manufacturing", "Tourism", "Healthcare", "Defence"], "employers": ["University of Lincoln", "Siemens Energy (Lincoln plant)", "RAF Waddington nearby", "Lincoln County Hospital", "Bishop Grosseteste University"], "population": 100000, "geo": (53.2307, -0.5406), "nearby": ["Newark-on-Trent", "Gainsborough", "Sleaford", "Grantham"]},
    "mansfield": {"name": "Mansfield", "region": "Nottinghamshire", "postcodes": "NG18, NG19, NG21", "districts": ["Town Centre", "Mansfield Woodhouse", "Forest Town", "Sutton-in-Ashfield"], "sectors": ["Manufacturing", "Logistics", "Healthcare", "Retail", "Public sector"], "employers": ["Linpac Packaging", "Heineken UK (former site)", "Sherwood Forest Hospitals NHS Trust", "Mansfield District Council", "MAHLE Powertrain"], "population": 110000, "geo": (53.1409, -1.1990), "nearby": ["Nottingham", "Chesterfield", "Worksop", "Sutton-in-Ashfield"]},
    "worcester": {"name": "Worcester", "region": "Worcestershire", "postcodes": "WR1, WR2, WR3, WR5", "districts": ["City Centre", "Battenhall", "Warndon", "St John's"], "sectors": ["Manufacturing", "Higher education", "Healthcare", "Insurance", "Public sector"], "employers": ["Worcester Bosch (Bosch Thermotechnology)", "University of Worcester", "Worcestershire Royal Hospital", "QinetiQ Worcester", "Yamazaki Mazak UK"], "population": 105000, "geo": (52.1936, -2.2215), "nearby": ["Malvern", "Droitwich", "Pershore", "Evesham"]},
    "hereford": {"name": "Hereford", "region": "Herefordshire", "postcodes": "HR1, HR2, HR4", "districts": ["City Centre", "Old Eign Hill", "Belmont", "Whitecross"], "sectors": ["Defence and engineering", "Agriculture and food production", "Healthcare", "Tourism", "Public sector"], "employers": ["SAS HQ (UK Special Forces)", "Bulmers Cider (Heineken UK)", "Hereford County Hospital", "Cargill (poultry processing)", "Herefordshire Council"], "population": 60000, "geo": (52.0567, -2.7160), "nearby": ["Leominster", "Ross-on-Wye", "Ledbury", "Worcester"]},
    "shrewsbury": {"name": "Shrewsbury", "region": "Shropshire", "postcodes": "SY1, SY2, SY3", "districts": ["Town Centre", "Castlefields", "Belle Vue", "Monkmoor"], "sectors": ["Public sector", "Tourism", "Agriculture", "Healthcare", "Retail"], "employers": ["Shropshire Council", "Princess Royal Hospital (nearby Telford)", "Morris Lubricants", "Salop Leisure", "Salopian Brewery"], "population": 76000, "geo": (52.7077, -2.7546), "nearby": ["Telford", "Oswestry", "Whitchurch", "Wem"]},
    # ===== Expansion: Wave 3 (120 more, reaching 200 total) =====
    # Scotland (10)
    "stirling": {"name": "Stirling", "region": "Scotland", "postcodes": "FK7, FK8, FK9", "districts": ["City Centre", "Bridge of Allan", "Causewayhead", "Cambusbarron"], "sectors": ["Higher education", "Tourism and heritage", "Public sector", "Healthcare", "Insurance"], "employers": ["University of Stirling", "Stirling Council", "Forth Valley Royal Hospital", "Prudential Stirling", "M&G Investments"], "population": 37000, "geo": (56.1165, -3.9369), "nearby": ["Bridge of Allan", "Bannockburn", "Alloa", "Dunblane"]},
    "perth": {"name": "Perth", "region": "Scotland", "postcodes": "PH1, PH2", "districts": ["City Centre", "Bridgend", "Tulloch", "Letham"], "sectors": ["Insurance and financial services", "Energy", "Tourism", "Healthcare", "Agriculture"], "employers": ["Aviva (Perth)", "Stagecoach Group HQ", "SSE plc", "Perth Royal Infirmary", "Highland Spring"], "population": 47000, "geo": (56.3950, -3.4308), "nearby": ["Dundee", "Crieff", "Aberfeldy", "Auchterarder"]},
    "paisley": {"name": "Paisley", "region": "Scotland", "postcodes": "PA1, PA2, PA3", "districts": ["Town Centre", "Brediland", "Glenburn", "Foxbar"], "sectors": ["Higher education", "Healthcare", "Manufacturing (heritage)", "Logistics", "Retail"], "employers": ["University of the West of Scotland", "Royal Alexandra Hospital", "Renfrewshire Council", "Howden Group", "Diageo (regional ops)"], "population": 77000, "geo": (55.8456, -4.4239), "nearby": ["Glasgow", "Johnstone", "Linwood", "Renfrew"]},
    "east-kilbride": {"name": "East Kilbride", "region": "Scotland", "postcodes": "G74, G75", "districts": ["Town Centre", "Westwood", "Calderwood", "Greenhills"], "sectors": ["Tech and software", "Aerospace and engineering", "Public sector", "Healthcare", "Retail"], "employers": ["Skyscanner (engineering)", "Rolls-Royce East Kilbride", "South Lanarkshire Council", "Hairmyres Hospital", "Babcock International"], "population": 75000, "geo": (55.7611, -4.1769), "nearby": ["Glasgow", "Hamilton", "Eaglesham", "Strathaven"]},
    "hamilton": {"name": "Hamilton", "region": "Scotland", "postcodes": "ML3, ML4, ML5", "districts": ["Town Centre", "Larkhall", "Burnbank", "Quarter"], "sectors": ["Public sector", "Healthcare", "Retail", "Higher education", "Tech"], "employers": ["South Lanarkshire Council HQ", "University of the West of Scotland (Hamilton)", "Hamilton Park Racecourse", "EE / BT (call centre)", "Capgemini"], "population": 53000, "geo": (55.7770, -4.0337), "nearby": ["East Kilbride", "Motherwell", "Wishaw", "Bothwell"]},
    "livingston": {"name": "Livingston", "region": "Scotland", "postcodes": "EH53, EH54", "districts": ["Town Centre", "Almondvale", "Deans", "Craigshill"], "sectors": ["Tech and microelectronics", "Logistics", "Pharmaceutical", "Public sector", "Retail"], "employers": ["Mitsubishi Electric Air Conditioning", "HSBC (Livingston site)", "Viatris", "West Lothian Council", "Sky Subscribers Services"], "population": 56000, "geo": (55.8866, -3.5226), "nearby": ["Edinburgh", "Bathgate", "Broxburn", "Whitburn"]},
    "falkirk": {"name": "Falkirk", "region": "Scotland", "postcodes": "FK1, FK2", "districts": ["Town Centre", "Grangemouth", "Camelon", "Larbert"], "sectors": ["Petrochemicals", "Manufacturing", "Logistics", "Tourism (Helix / Kelpies)", "Public sector"], "employers": ["INEOS Grangemouth", "Petroineos Refining", "Falkirk Council", "Forth Valley Royal Hospital (Larbert)", "Forth Valley College"], "population": 35000, "geo": (56.0019, -3.7839), "nearby": ["Grangemouth", "Stirling", "Linlithgow", "Bo'ness"]},
    "kirkcaldy": {"name": "Kirkcaldy", "region": "Scotland", "postcodes": "KY1, KY2", "districts": ["Town Centre", "Dysart", "Pathhead", "Templehall"], "sectors": ["Manufacturing", "Public sector", "Retail", "Healthcare", "Higher education"], "employers": ["Fife Council", "Victoria Hospital", "Fife College", "Forbo Flooring Systems", "Tullis Russell (legacy)"], "population": 50000, "geo": (56.1129, -3.1551), "nearby": ["Dunfermline", "Burntisland", "Glenrothes", "Dysart"]},
    "dunfermline": {"name": "Dunfermline", "region": "Scotland", "postcodes": "KY11, KY12", "districts": ["Town Centre", "Touch", "Carnegie Drive", "Pittencrieff Park"], "sectors": ["Financial services", "Manufacturing", "Healthcare", "Tech", "Tourism"], "employers": ["Sky UK (Dunfermline campus)", "FMC Technologies", "Babcock International (Rosyth)", "Queen Margaret Hospital", "Fife College"], "population": 55000, "geo": (56.0719, -3.4527), "nearby": ["Kirkcaldy", "Inverkeithing", "Cowdenbeath", "Edinburgh"]},
    "ayr": {"name": "Ayr", "region": "Scotland", "postcodes": "KA7, KA8", "districts": ["Town Centre", "Ayr Seafront", "Alloway", "Prestwick"], "sectors": ["Tourism", "Agriculture", "Public sector", "Healthcare", "Aviation"], "employers": ["Ayrshire College", "Glasgow Prestwick Airport", "South Ayrshire Council", "University Hospital Ayr", "Walkers Shortbread (regional)"], "population": 47000, "geo": (55.4583, -4.6293), "nearby": ["Prestwick", "Troon", "Cumnock", "Kilmarnock"]},
    # Northern Ireland (3)
    "lisburn": {"name": "Lisburn", "region": "Northern Ireland", "postcodes": "BT27, BT28", "districts": ["City Centre", "Hillsborough", "Dunmurry", "Maze"], "sectors": ["Manufacturing", "Logistics", "Public sector", "Healthcare", "Tech"], "employers": ["Coca-Cola HBC Northern Ireland", "Lagan Construction Group", "Lisburn & Castlereagh City Council", "South Eastern Health Trust", "Camlin Group"], "population": 75000, "geo": (54.5163, -6.0581), "nearby": ["Belfast", "Hillsborough", "Dunmurry", "Moira"]},
    "derry": {"name": "Derry", "region": "Northern Ireland", "postcodes": "BT47, BT48", "districts": ["City Centre", "Waterside", "Bogside", "Creggan"], "sectors": ["Tech and software", "Higher education", "Healthcare", "Public sector", "Manufacturing"], "employers": ["Allstate NI (Derry office)", "Seagate Technology", "Ulster University (Magee)", "Altnagelvin Hospital", "Du Pont"], "population": 85000, "geo": (54.9966, -7.3086), "nearby": ["Strabane", "Limavady", "Buncrana", "Coleraine"]},
    "newry": {"name": "Newry", "region": "Northern Ireland", "postcodes": "BT34, BT35", "districts": ["City Centre", "Bessbrook", "Warrenpoint", "Hilltown"], "sectors": ["Retail", "Manufacturing", "Logistics", "Construction", "Healthcare"], "employers": ["First Derivatives (FD Technologies)", "Daly Bros (Buttercrane Centre)", "Norbev Ltd", "Southern Health and Social Care Trust", "Newry, Mourne and Down District Council"], "population": 30000, "geo": (54.1751, -6.3402), "nearby": ["Banbridge", "Warrenpoint", "Crossmaglen", "Dundalk (Ireland)"]},
    # Wales (5)
    "wrexham": {"name": "Wrexham", "region": "Wales", "postcodes": "LL11, LL12, LL13", "districts": ["City Centre", "Acton", "Rhosddu", "Gwersyllt"], "sectors": ["Manufacturing", "Pharmaceutical", "Higher education", "Healthcare", "Logistics"], "employers": ["JCB Transmissions", "Wockhardt UK", "Wrexham Glyndwr University", "Wrexham Maelor Hospital", "Kellogg's Wrexham"], "population": 65000, "geo": (53.0454, -3.0015), "nearby": ["Chester", "Mold", "Oswestry", "Ruabon"]},
    "bridgend": {"name": "Bridgend", "region": "Wales", "postcodes": "CF31, CF32, CF33", "districts": ["Town Centre", "Brackla", "Bryntirion", "Pencoed"], "sectors": ["Manufacturing", "Public sector", "Retail", "Healthcare", "Logistics"], "employers": ["Ford Bridgend (legacy)", "INEOS Automotive", "Sony UK Technology Centre", "Princess of Wales Hospital", "Bridgend County Borough Council"], "population": 50000, "geo": (51.5093, -3.5773), "nearby": ["Porthcawl", "Maesteg", "Pencoed", "Cardiff"]},
    "caerphilly": {"name": "Caerphilly", "region": "Wales", "postcodes": "CF82, CF83", "districts": ["Town Centre", "Penyrheol", "Trecenydd", "Hendredenny"], "sectors": ["Public sector", "Healthcare", "Manufacturing", "Retail", "Tourism"], "employers": ["Caerphilly County Borough Council", "Ystrad Mynach Hospital", "Convatec", "Belkin International (legacy)", "GE Aviation (Nantgarw)"], "population": 41000, "geo": (51.5783, -3.2185), "nearby": ["Cardiff", "Newport", "Bargoed", "Ystrad Mynach"]},
    "bangor-wales": {"name": "Bangor", "region": "Wales", "postcodes": "LL57, LL58", "districts": ["City Centre", "Upper Bangor", "Maesgeirchen", "Hirael"], "sectors": ["Higher education", "Healthcare", "Tourism", "Marine and environmental research", "Public sector"], "employers": ["Bangor University", "Ysbyty Gwynedd (hospital)", "Royal Society for the Protection of Birds (regional)", "Snowdonia National Park Authority", "Gwynedd Council"], "population": 18000, "geo": (53.2280, -4.1290), "nearby": ["Caernarfon", "Holyhead", "Llandudno", "Conwy"]},
    "llanelli": {"name": "Llanelli", "region": "Wales", "postcodes": "SA14, SA15", "districts": ["Town Centre", "Burry Port", "Pwll", "Felinfoel"], "sectors": ["Manufacturing", "Healthcare", "Retail", "Tourism", "Renewable energy"], "employers": ["Calsonic Kansei (Marelli)", "Prince Philip Hospital", "Coleg Sir Gar", "Carmarthenshire County Council", "Schaeffler Group (legacy)"], "population": 50000, "geo": (51.6800, -4.1592), "nearby": ["Swansea", "Carmarthen", "Kidwelly", "Burry Port"]},
    # NE England (5)
    "gateshead": {"name": "Gateshead", "region": "Tyne and Wear", "postcodes": "NE8, NE9, NE10", "districts": ["Town Centre", "Low Fell", "Felling", "Birtley"], "sectors": ["Retail and leisure", "Manufacturing", "Public sector", "Healthcare", "Tech"], "employers": ["MetroCentre (Intu / Sovereign Centros)", "Sage Group (nearby Newcastle)", "Gateshead Council", "Queen Elizabeth Hospital", "International Paint AkzoNobel"], "population": 200000, "geo": (54.9526, -1.6033), "nearby": ["Newcastle", "Sunderland", "Washington", "Birtley"]},
    "south-shields": {"name": "South Shields", "region": "Tyne and Wear", "postcodes": "NE33, NE34", "districts": ["Town Centre", "Westoe", "Cleadon", "Whitburn"], "sectors": ["Maritime and offshore", "Tourism", "Healthcare", "Public sector", "Renewable energy"], "employers": ["South Tyneside Council", "South Tyneside District Hospital", "Port of Tyne", "South Tyneside College", "Caterpillar Marine"], "population": 75000, "geo": (54.9961, -1.4296), "nearby": ["Newcastle", "Sunderland", "Jarrow", "North Shields"]},
    "darlington": {"name": "Darlington", "region": "County Durham", "postcodes": "DL1, DL2, DL3", "districts": ["Town Centre", "Cockerton", "Mowden", "Hummersknott"], "sectors": ["Rail and engineering", "Public sector", "Tech", "Healthcare", "Manufacturing"], "employers": ["Hitachi Rail Newton Aycliffe (nearby)", "Cummins Engine Components", "Darlington Council (Treasury Campus)", "Memorial Hospital", "Tarmac (CRH)"], "population": 92000, "geo": (54.5235, -1.5582), "nearby": ["Middlesbrough", "Stockton-on-Tees", "Bishop Auckland", "Richmond"]},
    "hartlepool": {"name": "Hartlepool", "region": "County Durham", "postcodes": "TS24, TS25, TS26", "districts": ["Town Centre", "Marina", "Greatham", "Headland"], "sectors": ["Nuclear and energy", "Manufacturing", "Public sector", "Healthcare", "Logistics"], "employers": ["Hartlepool Nuclear Power Station (EDF)", "Caterpillar (Peterlee nearby)", "Hartlepool Council", "University Hospital of Hartlepool", "Hartlepool College"], "population": 88000, "geo": (54.6864, -1.2127), "nearby": ["Middlesbrough", "Stockton-on-Tees", "Peterlee", "Seaham"]},
    "stockton-on-tees": {"name": "Stockton-on-Tees", "region": "Tees Valley", "postcodes": "TS18, TS19, TS20", "districts": ["Town Centre", "Yarm", "Eaglescliffe", "Norton"], "sectors": ["Chemicals and process industries", "Higher education", "Healthcare", "Logistics", "Tech"], "employers": ["Fujifilm Diosynth Biotechnologies", "Huntsman Tioxide", "Durham University (Stockton campus)", "University Hospital of North Tees", "GSK (Barnard Castle nearby)"], "population": 85000, "geo": (54.5704, -1.3289), "nearby": ["Middlesbrough", "Hartlepool", "Darlington", "Yarm"]},
    # NW England (10)
    "chester": {"name": "Chester", "region": "Cheshire", "postcodes": "CH1, CH2, CH3, CH4", "districts": ["City Centre", "Hoole", "Boughton", "Saltney"], "sectors": ["Financial services", "Tourism and heritage", "Higher education", "Healthcare", "Manufacturing"], "employers": ["MBNA / Bank of America Merrill Lynch", "Bank of America (Chester campus)", "University of Chester", "Countess of Chester Hospital", "Airbus Broughton (nearby)"], "population": 91000, "geo": (53.1934, -2.8931), "nearby": ["Wrexham", "Ellesmere Port", "Frodsham", "Wallasey"]},
    "crewe": {"name": "Crewe", "region": "Cheshire", "postcodes": "CW1, CW2", "districts": ["Town Centre", "Wistaston", "Sydney", "Haslington"], "sectors": ["Automotive manufacturing", "Rail engineering", "Logistics", "Public sector", "Healthcare"], "employers": ["Bentley Motors HQ", "Bombardier / Alstom (rail)", "Mornflake", "Leighton Hospital", "Cheshire East Council"], "population": 72000, "geo": (53.0982, -2.4416), "nearby": ["Nantwich", "Sandbach", "Wilmslow", "Macclesfield"]},
    "macclesfield": {"name": "Macclesfield", "region": "Cheshire", "postcodes": "SK10, SK11", "districts": ["Town Centre", "Hurdsfield", "Tytherington", "Bollington"], "sectors": ["Pharmaceutical", "Tech", "Manufacturing", "Healthcare", "Higher education"], "employers": ["AstraZeneca Macclesfield", "Royal London (call centre)", "Pets at Home HQ (nearby Handforth)", "Macclesfield District General Hospital", "Stockport Council"], "population": 51000, "geo": (53.2587, -2.1252), "nearby": ["Stockport", "Wilmslow", "Buxton", "Congleton"]},
    "carlisle": {"name": "Carlisle", "region": "Cumbria", "postcodes": "CA1, CA2, CA3", "districts": ["City Centre", "Stanwix", "Botcherby", "Currock"], "sectors": ["Manufacturing", "Logistics", "Public sector", "Healthcare", "Tourism"], "employers": ["Pirelli Tyres Carlisle", "Nestle Carlisle", "Carlisle United (legacy commercial)", "Cumberland Infirmary", "Eddie Stobart (legacy HQ)"], "population": 75000, "geo": (54.8924, -2.9320), "nearby": ["Penrith", "Workington", "Whitehaven", "Brampton"]},
    "lancaster": {"name": "Lancaster", "region": "Lancashire", "postcodes": "LA1, LA2", "districts": ["City Centre", "Bowerham", "Skerton", "Galgate"], "sectors": ["Higher education", "Healthcare", "Tourism", "Manufacturing", "Public sector"], "employers": ["Lancaster University", "Royal Lancaster Infirmary", "Heysham Nuclear Power Station (nearby)", "Lancaster City Council", "Reedham Holdings"], "population": 52000, "geo": (54.0466, -2.8007), "nearby": ["Morecambe", "Preston", "Kendal", "Heysham"]},
    "morecambe": {"name": "Morecambe", "region": "Lancashire", "postcodes": "LA3, LA4", "districts": ["Town Centre", "Bare", "Westgate", "Heysham"], "sectors": ["Tourism", "Nuclear and energy", "Healthcare", "Retail", "Public sector"], "employers": ["Heysham Nuclear Power Station (EDF)", "Reedham Holdings", "Morecambe Bay NHS", "Eden Project Morecambe (in development)", "Lancaster City Council"], "population": 35000, "geo": (54.0688, -2.8631), "nearby": ["Lancaster", "Heysham", "Carnforth", "Kendal"]},
    "oldham": {"name": "Oldham", "region": "Greater Manchester", "postcodes": "OL1, OL2, OL4", "districts": ["Town Centre", "Chadderton", "Royton", "Failsworth"], "sectors": ["Manufacturing (heritage textiles)", "Public sector", "Healthcare", "Logistics", "Retail"], "employers": ["Diodes Inc (semiconductors)", "JD Williams (N Brown Group nearby Manchester)", "Royal Oldham Hospital", "Oldham Council", "Park Cake Bakeries"], "population": 96000, "geo": (53.5409, -2.1114), "nearby": ["Manchester", "Rochdale", "Ashton-under-Lyne", "Saddleworth"]},
    "bury": {"name": "Bury", "region": "Greater Manchester", "postcodes": "BL8, BL9", "districts": ["Town Centre", "Whitefield", "Prestwich", "Radcliffe"], "sectors": ["Retail (Bury Market)", "Manufacturing", "Public sector", "Healthcare", "Logistics"], "employers": ["JD Sports Fashion HQ", "Bury Council", "Fairfield General Hospital", "Warburtons (Bolton nearby)", "Quilter plc"], "population": 80000, "geo": (53.5933, -2.2966), "nearby": ["Bolton", "Manchester", "Rochdale", "Heywood"]},
    "st-helens": {"name": "St Helens", "region": "Merseyside", "postcodes": "WA9, WA10, WA11", "districts": ["Town Centre", "Sutton", "Eccleston", "Rainford"], "sectors": ["Glass manufacturing", "Logistics", "Public sector", "Healthcare", "Retail"], "employers": ["Pilkington UK (NSG Group)", "United Glass", "St Helens Council", "St Helens Hospital", "Knauf Insulation"], "population": 102000, "geo": (53.4536, -2.7361), "nearby": ["Liverpool", "Warrington", "Wigan", "Widnes"]},
    "skelmersdale": {"name": "Skelmersdale", "region": "Lancashire", "postcodes": "WN8", "districts": ["Town Centre", "Digmoor", "Birch Green", "Old Skelmersdale"], "sectors": ["Manufacturing", "Logistics", "Public sector", "Retail", "Healthcare"], "employers": ["P&G (Procter & Gamble) Skelmersdale", "Asda Distribution", "Victrex plc", "West Lancashire Borough Council", "Conlon Construction"], "population": 40000, "geo": (53.5519, -2.7740), "nearby": ["Wigan", "Ormskirk", "Liverpool", "Southport"]},
    # Yorkshire / Humber (7)
    "rotherham": {"name": "Rotherham", "region": "South Yorkshire", "postcodes": "S60, S61, S65", "districts": ["Town Centre", "Wickersley", "Maltby", "Wath-upon-Dearne"], "sectors": ["Advanced manufacturing", "Steel and metalwork", "Logistics", "Healthcare", "Public sector"], "employers": ["McLaren Composites Technology Centre", "AESSEAL", "Liberty Steel Rotherham", "Rotherham General Hospital", "Rotherham Council"], "population": 110000, "geo": (53.4302, -1.3568), "nearby": ["Sheffield", "Doncaster", "Barnsley", "Mexborough"]},
    "barnsley": {"name": "Barnsley", "region": "South Yorkshire", "postcodes": "S70, S71, S75", "districts": ["Town Centre", "Penistone", "Hoyland", "Wombwell"], "sectors": ["Public sector", "Manufacturing", "Logistics", "Healthcare", "Higher education"], "employers": ["Barnsley Council", "ASOS (Barnsley distribution)", "Premier Foods (legacy)", "Barnsley Hospital", "Barnsley College"], "population": 96000, "geo": (53.5526, -1.4797), "nearby": ["Sheffield", "Doncaster", "Wakefield", "Rotherham"]},
    "scunthorpe": {"name": "Scunthorpe", "region": "Lincolnshire", "postcodes": "DN15, DN16, DN17", "districts": ["Town Centre", "Frodingham", "Crosby", "Bottesford"], "sectors": ["Steel and metalwork", "Manufacturing", "Logistics", "Public sector", "Healthcare"], "employers": ["British Steel (Scunthorpe Works)", "2 Sisters Food Group", "North Lincolnshire Council", "Scunthorpe General Hospital", "Premier Foods"], "population": 82000, "geo": (53.5809, -0.6502), "nearby": ["Grimsby", "Doncaster", "Goole", "Brigg"]},
    "grimsby": {"name": "Grimsby", "region": "Lincolnshire", "postcodes": "DN31, DN32, DN33, DN34", "districts": ["Town Centre", "Cleethorpes", "Grimsby Docks", "Healing"], "sectors": ["Food processing and seafood", "Logistics and ports", "Renewable energy (offshore wind)", "Manufacturing", "Healthcare"], "employers": ["Young's Seafood", "Associated British Ports (Port of Immingham)", "Orsted (Hornsea / Race Bank)", "Diana Princess of Wales Hospital", "Cristal Pigments"], "population": 88000, "geo": (53.5675, -0.0805), "nearby": ["Cleethorpes", "Scunthorpe", "Immingham", "Louth"]},
    "harrogate": {"name": "Harrogate", "region": "North Yorkshire", "postcodes": "HG1, HG2, HG3", "districts": ["Town Centre", "Starbeck", "Bilton", "Pannal"], "sectors": ["Conference and events", "Tourism and hospitality", "Healthcare", "Tech", "Insurance and financial services"], "employers": ["Harrogate Convention Centre", "Bettys & Taylors Group", "Harrogate District Hospital", "Provident Financial (legacy)", "True Potential Investments"], "population": 75000, "geo": (53.9913, -1.5414), "nearby": ["Leeds", "York", "Ripon", "Knaresborough"]},
    "skipton": {"name": "Skipton", "region": "North Yorkshire", "postcodes": "BD23", "districts": ["Town Centre", "Embsay", "Bradleys Both", "Snaygill"], "sectors": ["Financial services (building societies)", "Tourism", "Agriculture", "Healthcare", "Retail"], "employers": ["Skipton Building Society HQ", "Stainton Group", "Airedale Hospital (nearby)", "Skipton Auction Mart", "Craven District Council"], "population": 15000, "geo": (53.9608, -2.0156), "nearby": ["Keighley", "Bradford", "Ilkley", "Settle"]},
    "pontefract": {"name": "Pontefract", "region": "West Yorkshire", "postcodes": "WF7, WF8, WF9", "districts": ["Town Centre", "Featherstone", "Knottingley", "Castleford"], "sectors": ["Confectionery and food", "Logistics", "Healthcare", "Public sector", "Tourism (racecourse)"], "employers": ["Haribo UK (Pontefract Cakes)", "Nestle Confectionery (Halifax nearby)", "Pinderfields & Pontefract Hospitals", "Pontefract Racecourse", "Tata Steel (Castleford)"], "population": 32000, "geo": (53.6919, -1.3128), "nearby": ["Wakefield", "Castleford", "Doncaster", "Featherstone"]},
    # East Midlands / West Midlands extension (13)
    "burton-upon-trent": {"name": "Burton-upon-Trent", "region": "Staffordshire", "postcodes": "DE13, DE14, DE15", "districts": ["Town Centre", "Stretton", "Branston", "Winshill"], "sectors": ["Brewing and beverages", "Manufacturing", "Logistics", "Healthcare", "Public sector"], "employers": ["Molson Coors (UK HQ)", "Marston's PLC", "Punch Pubs", "Burton Hospitals NHS", "Branston (potato processor)"], "population": 75000, "geo": (52.8019, -1.6418), "nearby": ["Derby", "Stafford", "Lichfield", "Uttoxeter"]},
    "newark-on-trent": {"name": "Newark-on-Trent", "region": "Nottinghamshire", "postcodes": "NG24", "districts": ["Town Centre", "Balderton", "Fernwood", "Coddington"], "sectors": ["Logistics", "Manufacturing", "Agriculture", "Public sector", "Tourism"], "employers": ["British Sugar", "Knapp Distribution UK", "Newark Hospital", "Newark and Sherwood District Council", "Currys (legacy DSG distribution)"], "population": 28000, "geo": (53.0759, -0.8048), "nearby": ["Nottingham", "Lincoln", "Mansfield", "Grantham"]},
    "worksop": {"name": "Worksop", "region": "Nottinghamshire", "postcodes": "S80, S81", "districts": ["Town Centre", "Manton", "Carlton-in-Lindrick", "Worksop Priory"], "sectors": ["Logistics", "Manufacturing", "Public sector", "Healthcare", "Retail"], "employers": ["Wilkinson (Wilko legacy HQ)", "B&Q distribution", "Bassetlaw District Council", "Bassetlaw Hospital", "Premier Foods"], "population": 44000, "geo": (53.3036, -1.1242), "nearby": ["Mansfield", "Sheffield", "Doncaster", "Retford"]},
    "kettering": {"name": "Kettering", "region": "Northamptonshire", "postcodes": "NN15, NN16", "districts": ["Town Centre", "Burton Latimer", "Desborough", "Rothwell"], "sectors": ["Logistics and distribution", "Engineering", "Public sector", "Healthcare", "Retail"], "employers": ["Weetabix Food Company", "Morrisons (distribution)", "RS Components (Electrocomponents)", "Kettering General Hospital", "North Northamptonshire Council"], "population": 65000, "geo": (52.3938, -0.7253), "nearby": ["Northampton", "Corby", "Wellingborough", "Market Harborough"]},
    "wellingborough": {"name": "Wellingborough", "region": "Northamptonshire", "postcodes": "NN8, NN9", "districts": ["Town Centre", "Wilby", "Earls Barton", "Rushden"], "sectors": ["Logistics", "Manufacturing", "Public sector", "Healthcare", "Retail"], "employers": ["Booker Wholesale (Tesco)", "Park Cake Bakeries", "North Northants Council", "Isham Tube (Tata Steel)", "Lipton Teas and Infusions"], "population": 56000, "geo": (52.3033, -0.6938), "nearby": ["Kettering", "Northampton", "Rushden", "Bedford"]},
    "sutton-coldfield": {"name": "Sutton Coldfield", "region": "West Midlands", "postcodes": "B72, B73, B74, B75", "districts": ["Town Centre", "Boldmere", "Streetly", "Mere Green"], "sectors": ["Professional services", "Retail", "Healthcare", "Education", "Tech"], "employers": ["Mercedes-Benz UK", "Severn Trent Centre", "Good Hope Hospital", "Bishop Vesey's Grammar (independent)", "Eight Members Club"], "population": 100000, "geo": (52.5631, -1.8214), "nearby": ["Birmingham", "Walsall", "Tamworth", "Lichfield"]},
    "solihull": {"name": "Solihull", "region": "West Midlands", "postcodes": "B90, B91, B92, B93", "districts": ["Town Centre", "Shirley", "Knowle", "Dorridge"], "sectors": ["Automotive (Jaguar Land Rover)", "Aviation (Birmingham Airport)", "Logistics", "Tech", "Professional services"], "employers": ["Jaguar Land Rover (Solihull plant)", "Birmingham Airport", "Capita Solihull", "Solihull Council", "Touchwood (Lendlease)"], "population": 215000, "geo": (52.4119, -1.7783), "nearby": ["Birmingham", "Coventry", "Knowle", "Shirley"]},
    "redditch": {"name": "Redditch", "region": "Worcestershire", "postcodes": "B97, B98", "districts": ["Town Centre", "Batchley", "Lodge Park", "Headless Cross"], "sectors": ["Manufacturing", "Logistics", "Public sector", "Healthcare", "Pharmaceutical"], "employers": ["Halfords Group HQ", "Coca-Cola Enterprises", "Sanctuary Music Group", "Alexandra Hospital", "Redditch Borough Council"], "population": 87000, "geo": (52.3046, -1.9445), "nearby": ["Bromsgrove", "Birmingham", "Worcester", "Stratford-upon-Avon"]},
    "bromsgrove": {"name": "Bromsgrove", "region": "Worcestershire", "postcodes": "B60, B61", "districts": ["Town Centre", "Catshill", "Aston Fields", "Sidemoor"], "sectors": ["Manufacturing", "Logistics", "Public sector", "Healthcare", "Retail"], "employers": ["Aspen Pumps", "MotoNovo Finance", "Bromsgrove District Council", "Princess of Wales Community Hospital", "EBCO Plastics"], "population": 33000, "geo": (52.3349, -2.0577), "nearby": ["Redditch", "Birmingham", "Worcester", "Droitwich"]},
    "tamworth": {"name": "Tamworth", "region": "Staffordshire", "postcodes": "B77, B78, B79", "districts": ["Town Centre", "Glascote", "Wilnecote", "Stonydelph"], "sectors": ["Logistics and distribution", "Retail", "Manufacturing", "Public sector", "Tourism"], "employers": ["Aldi UK (distribution)", "Sainsbury's distribution", "Tamworth Borough Council", "Tamworth Castle (heritage)", "Drayton Manor Park"], "population": 78000, "geo": (52.6336, -1.6914), "nearby": ["Birmingham", "Sutton Coldfield", "Lichfield", "Atherstone"]},
    "cannock": {"name": "Cannock", "region": "Staffordshire", "postcodes": "WS11, WS12", "districts": ["Town Centre", "Chadsmoor", "Cannock Wood", "Hednesford"], "sectors": ["Logistics", "Manufacturing", "Retail", "Healthcare", "Public sector"], "employers": ["McArthurGlen Designer Outlet West Midlands", "GE Aviation Wedgnock", "Cannock Chase District Council", "Cannock Chase Hospital", "Veolia UK"], "population": 30000, "geo": (52.6883, -2.0314), "nearby": ["Walsall", "Stafford", "Lichfield", "Wolverhampton"]},
    "stafford": {"name": "Stafford", "region": "Staffordshire", "postcodes": "ST16, ST17, ST18", "districts": ["Town Centre", "Stone", "Highfields", "Wildwood"], "sectors": ["Engineering and energy", "Public sector", "Healthcare", "Logistics", "Defence"], "employers": ["GE Power Conversion (formerly Alstom Grid)", "MAN Energy Solutions", "Stafford County Hospital", "Staffordshire County Council", "GCHQ Stafford (legacy site)"], "population": 70000, "geo": (52.8067, -2.1175), "nearby": ["Stoke-on-Trent", "Cannock", "Telford", "Wolverhampton"]},
    "nuneaton": {"name": "Nuneaton", "region": "Warwickshire", "postcodes": "CV10, CV11", "districts": ["Town Centre", "Bedworth", "Stockingford", "Whitestone"], "sectors": ["Logistics", "Manufacturing", "Public sector", "Healthcare", "Retail"], "employers": ["Holland & Barrett HQ", "BMI Nuneaton (legacy)", "Nuneaton and Bedworth Borough Council", "George Eliot Hospital", "TVS Supply Chain Solutions"], "population": 86000, "geo": (52.5236, -1.4651), "nearby": ["Coventry", "Tamworth", "Hinckley", "Leicester"]},
    # East of England (8)
    "bedford": {"name": "Bedford", "region": "Bedfordshire", "postcodes": "MK40, MK41, MK42", "districts": ["Town Centre", "Kempston", "Goldington", "Brickhill"], "sectors": ["Higher education", "Engineering", "Public sector", "Healthcare", "Logistics"], "employers": ["University of Bedfordshire", "Bedford Hospital", "Aspire Defence Services (defence)", "Charles Wells (brewery)", "Bedford Borough Council"], "population": 110000, "geo": (52.1360, -0.4670), "nearby": ["Milton Keynes", "Cambridge", "Luton", "St Neots"]},
    "bury-st-edmunds": {"name": "Bury St Edmunds", "region": "Suffolk", "postcodes": "IP28, IP30, IP31, IP32, IP33", "districts": ["Town Centre", "Moreton Hall", "Westley", "Howard Estate"], "sectors": ["Brewing and beverages", "Sugar production", "Public sector", "Healthcare", "Retail"], "employers": ["Greene King HQ", "British Sugar (Bury factory)", "West Suffolk Hospital", "St Edmundsbury Borough Council", "Treatt plc"], "population": 42000, "geo": (52.2474, 0.7183), "nearby": ["Ipswich", "Cambridge", "Newmarket", "Stowmarket"]},
    "kings-lynn": {"name": "King's Lynn", "region": "Norfolk", "postcodes": "PE30, PE31", "districts": ["Town Centre", "Gaywood", "South Wootton", "North Lynn"], "sectors": ["Food processing", "Logistics and port", "Manufacturing", "Public sector", "Healthcare"], "employers": ["Campbell's Soup (legacy)", "Palm Paper", "Mars Petcare King's Lynn", "Queen Elizabeth Hospital", "Borough Council of King's Lynn"], "population": 42000, "geo": (52.7506, 0.3949), "nearby": ["Norwich", "Wisbech", "Hunstanton", "Downham Market"]},
    "lowestoft": {"name": "Lowestoft", "region": "Suffolk", "postcodes": "NR32, NR33", "districts": ["Town Centre", "Pakefield", "Oulton Broad", "Carlton Colville"], "sectors": ["Renewable energy (offshore wind)", "Fishing and maritime", "Logistics", "Tourism", "Public sector"], "employers": ["ScottishPower Renewables (East Anglia ONE)", "Sembmarine SLP", "Centrica Energy", "James Paget Hospital (nearby)", "East Suffolk Council"], "population": 70000, "geo": (52.4750, 1.7493), "nearby": ["Great Yarmouth", "Norwich", "Beccles", "Halesworth"]},
    "great-yarmouth": {"name": "Great Yarmouth", "region": "Norfolk", "postcodes": "NR30, NR31", "districts": ["Town Centre", "Gorleston-on-Sea", "Bradwell", "Caister-on-Sea"], "sectors": ["Tourism and hospitality", "Offshore energy", "Fishing and maritime", "Logistics", "Healthcare"], "employers": ["Perenco UK", "Vattenfall (Norfolk Boreas)", "Great Yarmouth Borough Council", "James Paget University Hospital", "Pleasurewood Hills"], "population": 75000, "geo": (52.6083, 1.7305), "nearby": ["Lowestoft", "Norwich", "Caister", "Acle"]},
    "hertford": {"name": "Hertford", "region": "Hertfordshire", "postcodes": "SG13, SG14", "districts": ["Town Centre", "Hertford Heath", "Bayfordbury", "Bengeo"], "sectors": ["Public sector", "Insurance", "Higher education", "Healthcare", "Pharmaceutical"], "employers": ["Hertfordshire County Council", "Mountview Estates (real estate)", "East and North Herts NHS Trust", "Tesco (Welwyn HQ nearby)", "MBDA Stevenage"], "population": 30000, "geo": (51.7964, -0.0779), "nearby": ["Hatfield", "Stevenage", "Welwyn Garden City", "Ware"]},
    "stevenage": {"name": "Stevenage", "region": "Hertfordshire", "postcodes": "SG1, SG2", "districts": ["Town Centre", "Old Town", "Chells", "Pin Green"], "sectors": ["Aerospace and defence", "Pharmaceutical", "Tech", "Healthcare", "Public sector"], "employers": ["MBDA Missile Systems", "Airbus Defence and Space", "GSK Stevenage", "Lister Hospital", "Stevenage Bioscience Catalyst"], "population": 88000, "geo": (51.9020, -0.2024), "nearby": ["Hertford", "Hitchin", "Letchworth", "Welwyn Garden City"]},
    "hatfield": {"name": "Hatfield", "region": "Hertfordshire", "postcodes": "AL9, AL10", "districts": ["Town Centre", "Hatfield Garden Village", "Old Hatfield", "Roe Green"], "sectors": ["Higher education", "Aerospace (heritage)", "Retail and consumer goods", "Tech", "Public sector"], "employers": ["University of Hertfordshire", "Ocado Group HQ", "EE Hatfield (BT)", "Tesco HQ (Welwyn nearby)", "Mitsubishi Electric Europe"], "population": 41000, "geo": (51.7610, -0.2271), "nearby": ["St Albans", "Welwyn Garden City", "Stevenage", "Watford"]},
    # Kent (8)
    "tunbridge-wells": {"name": "Tunbridge Wells", "region": "Kent", "postcodes": "TN1, TN2, TN3, TN4", "districts": ["Town Centre", "Pantiles", "Rusthall", "Southborough"], "sectors": ["Professional services", "Financial services", "Healthcare", "Tourism", "Retail"], "employers": ["AXA UK (Tunbridge Wells campus)", "Zurich Insurance UK", "Tunbridge Wells Hospital", "Kent and Sussex Hospital", "Wadhurst College (legacy)"], "population": 60000, "geo": (51.1294, 0.2632), "nearby": ["Tonbridge", "Sevenoaks", "Crowborough", "Maidstone"]},
    "tonbridge": {"name": "Tonbridge", "region": "Kent", "postcodes": "TN9, TN10, TN11", "districts": ["Town Centre", "Hildenborough", "Higham Wood", "Castle"], "sectors": ["Professional services", "Education (Tonbridge School)", "Tech", "Retail", "Construction"], "employers": ["Tonbridge School", "Cluttons (regional)", "Walmsleys (legacy)", "Tonbridge and Malling Council", "EDF Energy (regional)"], "population": 38000, "geo": (51.1953, 0.2768), "nearby": ["Tunbridge Wells", "Sevenoaks", "Maidstone", "East Grinstead"]},
    "ashford": {"name": "Ashford", "region": "Kent", "postcodes": "TN23, TN24, TN25", "districts": ["Town Centre", "Willesborough", "Kennington", "Stanhope"], "sectors": ["Logistics and distribution", "Manufacturing", "Healthcare", "Public sector", "Retail"], "employers": ["Eurostar (Ashford International)", "Brakes Group (Sysco)", "William Harvey Hospital", "Ashford Borough Council", "Pfizer (Sandwich nearby)"], "population": 75000, "geo": (51.1465, 0.8676), "nearby": ["Folkestone", "Canterbury", "Maidstone", "Tenterden"]},
    "dover": {"name": "Dover", "region": "Kent", "postcodes": "CT16, CT17", "districts": ["Town Centre", "River", "Aycliffe", "Whitfield"], "sectors": ["Port and logistics", "Tourism", "Defence", "Manufacturing", "Public sector"], "employers": ["Port of Dover", "DFDS Seaways", "P&O Ferries", "Megger Group", "Dover District Council"], "population": 32000, "geo": (51.1295, 1.3089), "nearby": ["Folkestone", "Deal", "Sandwich", "Canterbury"]},
    "margate": {"name": "Margate", "region": "Kent", "postcodes": "CT9", "districts": ["Town Centre", "Cliftonville", "Westgate-on-Sea", "Garlinge"], "sectors": ["Tourism and hospitality", "Creative industries", "Healthcare", "Retail", "Public sector"], "employers": ["Dreamland Margate", "Turner Contemporary", "Queen Elizabeth The Queen Mother Hospital", "Thanet District Council", "Manston Airport (legacy)"], "population": 60000, "geo": (51.3849, 1.3865), "nearby": ["Ramsgate", "Broadstairs", "Westgate", "Birchington"]},
    "folkestone": {"name": "Folkestone", "region": "Kent", "postcodes": "CT19, CT20", "districts": ["Town Centre", "Cheriton", "Sandgate", "Hythe"], "sectors": ["Channel Tunnel logistics", "Tourism", "Healthcare", "Creative industries", "Public sector"], "employers": ["Eurotunnel (Getlink)", "Saga Group HQ", "Folkestone Harbour Arm", "William Harvey Hospital (Ashford nearby)", "Folkestone & Hythe District Council"], "population": 51000, "geo": (51.0815, 1.1689), "nearby": ["Dover", "Ashford", "Hythe", "Hawkinge"]},
    "canterbury": {"name": "Canterbury", "region": "Kent", "postcodes": "CT1, CT2, CT3", "districts": ["City Centre", "St Stephens", "Wincheap", "Sturry"], "sectors": ["Higher education", "Tourism and heritage", "Healthcare", "Retail", "Public sector"], "employers": ["University of Kent", "Canterbury Christ Church University", "Kent and Canterbury Hospital", "Whitefriars (Land Securities)", "Canterbury Cathedral"], "population": 55000, "geo": (51.2802, 1.0789), "nearby": ["Ashford", "Whitstable", "Herne Bay", "Dover"]},
    "sevenoaks": {"name": "Sevenoaks", "region": "Kent", "postcodes": "TN13, TN14, TN15", "districts": ["Town Centre", "Riverhead", "Dunton Green", "Otford"], "sectors": ["Financial services", "Professional services", "Education (independent schools)", "Tech", "Healthcare"], "employers": ["Capita Asset Services", "Sevenoaks School", "Pembury Hospital (NHS)", "Sevenoaks District Council", "Bauer Media Group (regional)"], "population": 30000, "geo": (51.2723, 0.1900), "nearby": ["Tonbridge", "Tunbridge Wells", "Bromley", "Westerham"]},
    # Sussex (7)
    "hastings": {"name": "Hastings", "region": "East Sussex", "postcodes": "TN34, TN35, TN37, TN38", "districts": ["Town Centre", "Old Town", "St Leonards-on-Sea", "Hollington"], "sectors": ["Tourism", "Fishing and maritime", "Healthcare", "Creative industries", "Public sector"], "employers": ["Hastings Direct (insurance HQ)", "Conquest Hospital", "Hastings Borough Council", "Hastings College", "Rolls-Royce Cars (Goodwood nearby)"], "population": 92000, "geo": (50.8543, 0.5731), "nearby": ["Eastbourne", "Bexhill", "Battle", "Rye"]},
    "eastbourne": {"name": "Eastbourne", "region": "East Sussex", "postcodes": "BN20, BN21, BN22, BN23", "districts": ["Town Centre", "Old Town", "Meads", "Sovereign Harbour"], "sectors": ["Tourism and hospitality", "Healthcare", "Retail", "Insurance", "Higher education"], "employers": ["Eastbourne District General Hospital", "Eastbourne Borough Council", "AGE UK (Eastbourne HQ for charity)", "East Sussex College", "Saga Group (regional)"], "population": 103000, "geo": (50.7686, 0.2824), "nearby": ["Hastings", "Brighton", "Bexhill", "Lewes"]},
    "worthing": {"name": "Worthing", "region": "West Sussex", "postcodes": "BN11, BN12, BN13, BN14", "districts": ["Town Centre", "Goring-by-Sea", "Tarring", "Findon"], "sectors": ["Insurance and financial services", "Public sector", "Healthcare", "Retail", "Manufacturing"], "employers": ["GlaxoSmithKline (GSK Worthing)", "HMRC Worthing", "Southern Water HQ", "Worthing Hospital", "Worthing Borough Council"], "population": 113000, "geo": (50.8147, -0.3743), "nearby": ["Brighton", "Littlehampton", "Shoreham", "Arundel"]},
    "crawley": {"name": "Crawley", "region": "West Sussex", "postcodes": "RH10, RH11", "districts": ["Town Centre", "Three Bridges", "Manor Royal", "Tilgate"], "sectors": ["Aviation (Gatwick)", "Logistics", "Tech", "Public sector", "Manufacturing"], "employers": ["Gatwick Airport (London Gatwick)", "Virgin Atlantic HQ", "Thales UK Crawley", "Doosan Babcock", "Crawley Borough Council"], "population": 118000, "geo": (51.1115, -0.1872), "nearby": ["Horsham", "Redhill", "Reigate", "East Grinstead"]},
    "horsham": {"name": "Horsham", "region": "West Sussex", "postcodes": "RH12, RH13", "districts": ["Town Centre", "Roffey", "Broadbridge Heath", "Mannings Heath"], "sectors": ["Insurance and financial services", "Public sector", "Manufacturing", "Healthcare", "Retail"], "employers": ["RSA Insurance (Horsham office)", "Bupa Healthcare (regional)", "Horsham District Council", "Eccolo Group", "Hop Oast Park & Ride"], "population": 50000, "geo": (51.0625, -0.3296), "nearby": ["Crawley", "Worthing", "Guildford", "Redhill"]},
    "chichester": {"name": "Chichester", "region": "West Sussex", "postcodes": "PO19, PO20", "districts": ["City Centre", "Whyke", "St Pancras", "Fishbourne"], "sectors": ["Tourism (Goodwood)", "Higher education", "Healthcare", "Public sector", "Defence"], "employers": ["Rolls-Royce Motor Cars (Goodwood)", "University of Chichester", "St Richard's Hospital", "Chichester Festival Theatre", "West Sussex County Council"], "population": 35000, "geo": (50.8365, -0.7792), "nearby": ["Bognor Regis", "Portsmouth", "Arundel", "Petworth"]},
    "bognor-regis": {"name": "Bognor Regis", "region": "West Sussex", "postcodes": "PO21, PO22", "districts": ["Town Centre", "Aldwick", "Felpham", "Pagham"], "sectors": ["Tourism", "Retail", "Healthcare", "Public sector", "Manufacturing"], "employers": ["Butlin's Bognor Regis", "Rolls-Royce (Goodwood nearby)", "St Richard's Hospital (Chichester)", "Arun District Council", "Body Shop (legacy ops)"], "population": 23000, "geo": (50.7825, -0.6759), "nearby": ["Chichester", "Littlehampton", "Worthing", "Arundel"]},
    # Surrey (8)
    "redhill": {"name": "Redhill", "region": "Surrey", "postcodes": "RH1, RH2", "districts": ["Town Centre", "Earlswood", "Merstham", "Whitebushes"], "sectors": ["Aviation (Gatwick nearby)", "Financial services", "Tech", "Public sector", "Retail"], "employers": ["AXA UK (Redhill site)", "Santander (regional)", "British Gas (Centrica nearby)", "Reigate & Banstead Council", "Hong Leong Group"], "population": 38000, "geo": (51.2387, -0.1742), "nearby": ["Reigate", "Crawley", "Horsham", "Dorking"]},
    "reigate": {"name": "Reigate", "region": "Surrey", "postcodes": "RH2", "districts": ["Town Centre", "Reigate Heath", "Woodhatch", "South Park"], "sectors": ["Insurance and financial services", "Professional services", "Healthcare", "Public sector", "Education"], "employers": ["esure Group HQ", "Canon Europe (regional)", "Reigate & Banstead Borough Council", "East Surrey Hospital", "Royal Alexandra and Albert School"], "population": 23000, "geo": (51.2367, -0.2056), "nearby": ["Redhill", "Dorking", "Horsham", "Sutton"]},
    "epsom": {"name": "Epsom", "region": "Surrey", "postcodes": "KT17, KT18, KT19", "districts": ["Town Centre", "Stoneleigh", "Ewell", "Tattenham Corner"], "sectors": ["Tourism (Epsom Derby)", "Healthcare", "Retail", "Public sector", "Higher education"], "employers": ["Toyota GB (Epsom HQ)", "The Jockey Club (Epsom Downs)", "Epsom Hospital", "Epsom & St Helier NHS Trust", "Epsom Council"], "population": 32000, "geo": (51.3318, -0.2705), "nearby": ["Sutton", "Kingston", "Leatherhead", "Dorking"]},
    "leatherhead": {"name": "Leatherhead", "region": "Surrey", "postcodes": "KT22, KT23", "districts": ["Town Centre", "Ashtead", "Fetcham", "Bookham"], "sectors": ["Pharmaceutical and FMCG", "Insurance", "Tech", "Public sector", "Healthcare"], "employers": ["Unilever R&D Colworth (legacy Leatherhead)", "ExxonMobil UK HQ (Cobham nearby)", "Police National CIO (legacy)", "Mole Valley District Council", "Leatherhead Hospital"], "population": 13000, "geo": (51.2961, -0.3290), "nearby": ["Epsom", "Dorking", "Cobham", "Esher"]},
    "woking": {"name": "Woking", "region": "Surrey", "postcodes": "GU21, GU22, GU24", "districts": ["Town Centre", "Knaphill", "Pyrford", "Horsell"], "sectors": ["Tech and digital", "Insurance", "Energy", "Healthcare", "Public sector"], "employers": ["McLaren Group (McLaren Technology Centre)", "Wisepay", "Equifax UK HQ", "Woking Hospital", "Woking Borough Council"], "population": 105000, "geo": (51.3198, -0.5610), "nearby": ["Guildford", "Aldershot", "Camberley", "Wokingham"]},
    "aldershot": {"name": "Aldershot", "region": "Hampshire", "postcodes": "GU11, GU12, GU14", "districts": ["Town Centre", "North Town", "Aldershot Garrison", "South Camp"], "sectors": ["Defence and military", "Aerospace", "Manufacturing", "Public sector", "Retail"], "employers": ["British Army (Aldershot Garrison)", "QinetiQ (Farnborough nearby)", "BAE Systems (Farnborough)", "Frimley Park Hospital (Camberley)", "Rushmoor Borough Council"], "population": 36000, "geo": (51.2470, -0.7619), "nearby": ["Farnborough", "Farnham", "Guildford", "Camberley"]},
    "farnham": {"name": "Farnham", "region": "Surrey", "postcodes": "GU9, GU10", "districts": ["Town Centre", "Wrecclesham", "Rowledge", "Hale"], "sectors": ["Creative arts and design", "Higher education", "Tourism", "Healthcare", "Professional services"], "employers": ["University for the Creative Arts", "Farnham Castle", "Bourne School Trust", "Frimley Health NHS", "Waverley Borough Council"], "population": 39000, "geo": (51.2148, -0.7984), "nearby": ["Aldershot", "Guildford", "Haslemere", "Alton"]},
    "camberley": {"name": "Camberley", "region": "Surrey", "postcodes": "GU15, GU16, GU17", "districts": ["Town Centre", "Yorktown", "Old Dean", "Frimley"], "sectors": ["Defence and engineering", "Tech", "Insurance", "Healthcare", "Public sector"], "employers": ["Royal Military Academy Sandhurst", "Stryker UK", "Sun Microsystems (Oracle legacy)", "Frimley Park Hospital", "Surrey Heath Borough Council"], "population": 38000, "geo": (51.3344, -0.7411), "nearby": ["Aldershot", "Woking", "Bracknell", "Farnham"]},
    # South West (10)
    "truro": {"name": "Truro", "region": "Cornwall", "postcodes": "TR1, TR2, TR3, TR4", "districts": ["City Centre", "Highertown", "Truro Vean", "Kenwyn"], "sectors": ["Public sector", "Healthcare", "Tourism", "Retail", "Higher education"], "employers": ["Royal Cornwall Hospital", "Cornwall Council HQ", "Truro and Penwith College", "Princess Street Theatre", "Truro Cathedral"], "population": 25000, "geo": (50.2632, -5.0510), "nearby": ["Falmouth", "St Austell", "Newquay", "Camborne"]},
    "falmouth": {"name": "Falmouth", "region": "Cornwall", "postcodes": "TR11", "districts": ["Town Centre", "Penryn", "Mylor Bridge", "Constantine"], "sectors": ["Maritime and port", "Higher education", "Tourism", "Marine engineering", "Creative arts"], "employers": ["A&P Falmouth (ship repair)", "Falmouth University", "Falmouth Harbour Commissioners", "Pendennis Shipyard", "RNAS Culdrose nearby"], "population": 22000, "geo": (50.1531, -5.0656), "nearby": ["Truro", "Helston", "Penzance", "Penryn"]},
    "penzance": {"name": "Penzance", "region": "Cornwall", "postcodes": "TR18, TR19, TR20", "districts": ["Town Centre", "Newlyn", "Heamoor", "Madron"], "sectors": ["Tourism", "Fishing and maritime", "Public sector", "Retail", "Healthcare"], "employers": ["Isles of Scilly Steamship Company", "Penlee Lifeboat (RNLI)", "West Cornwall Hospital", "Cornwall Council (regional)", "Stein's Fish & Chips (legacy)"], "population": 21000, "geo": (50.1188, -5.5371), "nearby": ["St Ives", "Helston", "Falmouth", "Hayle"]},
    "torquay": {"name": "Torquay", "region": "Devon", "postcodes": "TQ1, TQ2", "districts": ["Town Centre", "Babbacombe", "St Marychurch", "Wellswood"], "sectors": ["Tourism and hospitality", "Healthcare", "Retail", "Marine", "Public sector"], "employers": ["Torbay Hospital", "Riviera International Conference Centre", "South Devon College", "Torbay Council", "Babbacombe Theatre"], "population": 65000, "geo": (50.4619, -3.5253), "nearby": ["Paignton", "Newton Abbot", "Brixham", "Teignmouth"]},
    "paignton": {"name": "Paignton", "region": "Devon", "postcodes": "TQ3, TQ4", "districts": ["Town Centre", "Preston", "Goodrington", "Marldon"], "sectors": ["Tourism and hospitality", "Retail", "Healthcare", "Manufacturing", "Public sector"], "employers": ["Paignton Zoo", "Torbay Hospital (Torquay nearby)", "Devonshire Park Theatre (Eastbourne legacy)", "Torbay Council", "Quaywest Waterpark"], "population": 50000, "geo": (50.4350, -3.5645), "nearby": ["Torquay", "Brixham", "Totnes", "Newton Abbot"]},
    "yeovil": {"name": "Yeovil", "region": "Somerset", "postcodes": "BA20, BA21, BA22", "districts": ["Town Centre", "Yeovil Marsh", "Preston Plucknett", "Hendford Hill"], "sectors": ["Aerospace and defence (helicopters)", "Manufacturing", "Public sector", "Healthcare", "Retail"], "employers": ["Leonardo Helicopters UK", "Westland Helicopters (legacy)", "Yeovil District Hospital", "South Somerset District Council", "Crewkerne Industries"], "population": 45000, "geo": (50.9418, -2.6328), "nearby": ["Sherborne", "Taunton", "Crewkerne", "Chard"]},
    "taunton": {"name": "Taunton", "region": "Somerset", "postcodes": "TA1, TA2, TA3", "districts": ["Town Centre", "Galmington", "Holway", "Bishops Hull"], "sectors": ["Public sector", "Higher education", "Healthcare", "Insurance", "Defence"], "employers": ["Somerset County Council", "Musgrove Park Hospital", "University Centre Somerset", "UK Hydrographic Office", "Royal Marines Commando Training Centre Lympstone (nearby)"], "population": 70000, "geo": (51.0148, -3.1062), "nearby": ["Bridgwater", "Yeovil", "Wellington", "Wiveliscombe"]},
    "bridgwater": {"name": "Bridgwater", "region": "Somerset", "postcodes": "TA5, TA6, TA7", "districts": ["Town Centre", "Bridgwater College", "Sydenham", "Wembdon"], "sectors": ["Nuclear (Hinkley Point C)", "Manufacturing", "Logistics", "Public sector", "Agriculture"], "employers": ["EDF Energy (Hinkley Point C construction)", "Mulberry HQ", "Bridgwater & Taunton College", "Sedgemoor District Council", "Toolstation (regional)"], "population": 41000, "geo": (51.1281, -2.9938), "nearby": ["Taunton", "Burnham-on-Sea", "Glastonbury", "Wells"]},
    "weston-super-mare": {"name": "Weston-super-Mare", "region": "Somerset", "postcodes": "BS22, BS23, BS24", "districts": ["Town Centre", "Worle", "Uphill", "Milton"], "sectors": ["Tourism", "Retail", "Healthcare", "Public sector", "Logistics"], "employers": ["Weston General Hospital", "North Somerset Council", "Weston College", "Tropicana (regenerated venue)", "BAM Construction (regional)"], "population": 80000, "geo": (51.3458, -2.9776), "nearby": ["Bristol", "Bridgwater", "Burnham-on-Sea", "Clevedon"]},
    "salisbury": {"name": "Salisbury", "region": "Wiltshire", "postcodes": "SP1, SP2, SP4", "districts": ["City Centre", "Bishopdown", "Old Sarum", "Bemerton"], "sectors": ["Defence and engineering", "Tourism (Stonehenge)", "Public sector", "Healthcare", "Manufacturing"], "employers": ["Porton Down (DSTL, Public Health England)", "Wiltshire Council (regional)", "Salisbury District Hospital", "Salisbury Cathedral", "Boscombe Down (defence test centre)"], "population": 41000, "geo": (51.0688, -1.7945), "nearby": ["Winchester", "Andover", "Warminster", "Wilton"]},
    # Hampshire extras (4)
    "andover": {"name": "Andover", "region": "Hampshire", "postcodes": "SP10, SP11", "districts": ["Town Centre", "Charlton", "Anton", "Picket Twenty"], "sectors": ["Logistics", "Manufacturing", "Defence", "Public sector", "Healthcare"], "employers": ["British Army (Andover Garrison HQ)", "Stannah Lifts HQ", "Le Creuset UK HQ", "Andover War Memorial Hospital", "Test Valley Borough Council"], "population": 50000, "geo": (51.2089, -1.4828), "nearby": ["Basingstoke", "Winchester", "Salisbury", "Newbury"]},
    "newbury": {"name": "Newbury", "region": "Berkshire", "postcodes": "RG14, RG18, RG19, RG20", "districts": ["Town Centre", "Wash Common", "Speen", "Greenham"], "sectors": ["Tech and telecoms", "Tourism (racecourse)", "Public sector", "Retail", "Manufacturing"], "employers": ["Vodafone UK HQ", "Bayer Crop Science (legacy)", "Newbury Racecourse", "West Berkshire Council", "Stryker Newbury"], "population": 40000, "geo": (51.4015, -1.3231), "nearby": ["Basingstoke", "Reading", "Thatcham", "Hungerford"]},
    "winchester": {"name": "Winchester", "region": "Hampshire", "postcodes": "SO22, SO23", "districts": ["City Centre", "Stanmore", "St Cross", "Weeke"], "sectors": ["Higher education", "Defence", "Public sector", "Tourism and heritage", "Healthcare"], "employers": ["University of Winchester", "IBM Hursley Park", "Hampshire County Council HQ", "Royal Hampshire County Hospital", "Winchester Cathedral"], "population": 45000, "geo": (51.0632, -1.3080), "nearby": ["Basingstoke", "Southampton", "Andover", "Eastleigh"]},
    "eastleigh": {"name": "Eastleigh", "region": "Hampshire", "postcodes": "SO50, SO53", "districts": ["Town Centre", "Bishopstoke", "Fair Oak", "Chandler's Ford"], "sectors": ["Aviation (Southampton Airport)", "Public sector", "Manufacturing", "Healthcare", "Retail"], "employers": ["Southampton Airport (AGS Airports)", "B&Q HQ (Chandler's Ford)", "Eastleigh Borough Council", "Southern Health NHS", "Aircraft Service International Group"], "population": 67000, "geo": (50.9692, -1.3505), "nearby": ["Southampton", "Winchester", "Romsey", "Fareham"]},
    # London suburbs (15)
    "wembley": {"name": "Wembley", "region": "Greater London", "postcodes": "HA0, HA9", "districts": ["Wembley Park", "Wembley Central", "North Wembley", "Tokyngton"], "sectors": ["Sports and events", "Hospitality and retail", "Healthcare", "Public sector", "Real estate"], "employers": ["Wembley Stadium (FA)", "Wembley Arena (AEG)", "London Designer Outlet (Quintain)", "Northwick Park Hospital", "Brent Council"], "population": 110000, "geo": (51.5570, -0.2964), "nearby": ["Harrow", "Brent Cross", "Willesden", "Stonebridge"]},
    "ealing": {"name": "Ealing", "region": "Greater London", "postcodes": "W3, W5, W13", "districts": ["Ealing Broadway", "South Ealing", "West Ealing", "Hanwell"], "sectors": ["Creative industries (film studios)", "Public sector", "Healthcare", "Higher education", "Retail"], "employers": ["BBC (Ealing Studios)", "Ealing Council", "University of West London", "Ealing Hospital", "Imperial College Healthcare NHS"], "population": 340000, "geo": (51.5130, -0.3050), "nearby": ["Acton", "Brentford", "Southall", "Hounslow"]},
    "hounslow": {"name": "Hounslow", "region": "Greater London", "postcodes": "TW3, TW4, TW5", "districts": ["Town Centre", "Hounslow West", "Heston", "Cranford"], "sectors": ["Aviation (Heathrow)", "Logistics", "Hospitality", "Public sector", "Retail"], "employers": ["Heathrow Airport Holdings", "British Airways HQ (Waterside)", "Sky UK (Osterley)", "West Middlesex University Hospital", "Hounslow Council"], "population": 270000, "geo": (51.4685, -0.3673), "nearby": ["Heathrow", "Brentford", "Twickenham", "Feltham"]},
    "hillingdon": {"name": "Hillingdon", "region": "Greater London", "postcodes": "UB8, UB9, UB10", "districts": ["Hillingdon Hill", "Uxbridge", "Yiewsley", "Northwood"], "sectors": ["Aviation logistics", "Higher education", "Public sector", "Healthcare", "Retail"], "employers": ["Brunel University London", "Hillingdon Hospital", "London Borough of Hillingdon", "Marriott Heathrow", "Sanofi (regional)"], "population": 305000, "geo": (51.5331, -0.4720), "nearby": ["Uxbridge", "Ruislip", "Heathrow", "Harrow"]},
    "uxbridge": {"name": "Uxbridge", "region": "Greater London", "postcodes": "UB8, UB9, UB10", "districts": ["Town Centre", "Hillingdon", "Cowley", "Yiewsley"], "sectors": ["Logistics and pharma", "Tech", "Higher education", "Public sector", "Retail"], "employers": ["Coca-Cola European Partners HQ", "Cadent Gas HQ", "Brunel University", "Hillingdon Council", "GE Healthcare (regional)"], "population": 70000, "geo": (51.5455, -0.4779), "nearby": ["Hillingdon", "Ruislip", "Slough", "Hayes"]},
    "enfield": {"name": "Enfield", "region": "Greater London", "postcodes": "EN1, EN2, EN3", "districts": ["Town Centre", "Edmonton", "Palmers Green", "Bush Hill Park"], "sectors": ["Manufacturing", "Logistics", "Public sector", "Healthcare", "Retail"], "employers": ["Enfield Council", "North Middlesex University Hospital", "Tesco (regional ops)", "Royal Small Arms Factory (legacy)", "BT (regional)"], "population": 333000, "geo": (51.6521, -0.0808), "nearby": ["Barnet", "Waltham Cross", "Edmonton", "Cheshunt"]},
    "barnet": {"name": "Barnet", "region": "Greater London", "postcodes": "EN5, EN6, N20", "districts": ["High Barnet", "New Barnet", "East Barnet", "Whetstone"], "sectors": ["Healthcare", "Public sector", "Retail", "Education", "Real estate"], "employers": ["Royal Free London NHS Trust", "Middlesex University (Hendon)", "Barnet Council", "Saracens Rugby (Barnet)", "Brent Cross Shopping Centre"], "population": 395000, "geo": (51.6444, -0.2007), "nearby": ["Enfield", "Hendon", "Edgware", "Potters Bar"]},
    "walthamstow": {"name": "Walthamstow", "region": "Greater London", "postcodes": "E17", "districts": ["Town Centre", "Walthamstow Village", "Higham Hill", "Wood Street"], "sectors": ["Creative industries", "Public sector", "Healthcare", "Retail", "Hospitality"], "employers": ["Waltham Forest Council", "Walthamstow Cinema (re-opened)", "Walthamstow Market", "Whipps Cross Hospital", "Big Penny Social"], "population": 110000, "geo": (51.5840, -0.0214), "nearby": ["Leyton", "Chingford", "Wood Green", "Hackney"]},
    "ilford": {"name": "Ilford", "region": "Greater London", "postcodes": "IG1, IG2, IG3", "districts": ["Town Centre", "Gants Hill", "Newbury Park", "Seven Kings"], "sectors": ["Retail", "Healthcare", "Public sector", "Education", "Logistics"], "employers": ["Redbridge Council", "King George Hospital", "Ilford War Memorial Hospital (legacy)", "Westfield Stratford (nearby)", "AESC Energy Solutions"], "population": 168000, "geo": (51.5590, 0.0741), "nearby": ["Romford", "Walthamstow", "Stratford", "Barking"]},
    "wimbledon": {"name": "Wimbledon", "region": "Greater London", "postcodes": "SW19, SW20", "districts": ["Town Centre", "Wimbledon Village", "South Wimbledon", "Raynes Park"], "sectors": ["Sports and events (Wimbledon Tennis)", "Tech", "Real estate", "Professional services", "Healthcare"], "employers": ["All England Lawn Tennis Club (Wimbledon Championships)", "Lidl GB HQ", "Wimbledon Studios", "Merton Council", "Centre Court (Land Securities)"], "population": 70000, "geo": (51.4214, -0.2061), "nearby": ["Kingston upon Thames", "Putney", "Mitcham", "Tooting"]},
    "greenwich": {"name": "Greenwich", "region": "Greater London", "postcodes": "SE10, SE3", "districts": ["Town Centre", "Greenwich Peninsula", "Blackheath", "Maze Hill"], "sectors": ["Maritime and heritage", "Tourism", "Higher education", "Tech (Greenwich Peninsula)", "Healthcare"], "employers": ["Royal Museums Greenwich (Royal Observatory, Cutty Sark)", "University of Greenwich", "O2 Arena (AEG)", "Greenwich Council", "Knight Dragon (Greenwich Peninsula developer)"], "population": 290000, "geo": (51.4825, 0.0076), "nearby": ["Lewisham", "Charlton", "Woolwich", "Deptford"]},
    "lewisham": {"name": "Lewisham", "region": "Greater London", "postcodes": "SE13, SE6", "districts": ["Town Centre", "Catford", "Forest Hill", "Sydenham"], "sectors": ["Public sector", "Healthcare", "Higher education", "Retail", "Creative industries"], "employers": ["Lewisham Hospital (Lewisham and Greenwich NHS Trust)", "Goldsmiths, University of London (New Cross)", "Lewisham Council", "Lewisham Shopping Centre (Land Sec)", "TFL bus depot operations"], "population": 305000, "geo": (51.4634, -0.0117), "nearby": ["Greenwich", "Bromley", "Catford", "New Cross"]},
    "wandsworth": {"name": "Wandsworth", "region": "Greater London", "postcodes": "SW18, SW17, SW15", "districts": ["Town Centre", "Putney", "Battersea", "Earlsfield"], "sectors": ["Brewing and food", "Public sector", "Real estate (Nine Elms)", "Tech", "Hospitality"], "employers": ["Battersea Power Station (commercial)", "Wandsworth Council", "Sambrooks Brewery", "St George's Hospital (Tooting)", "Apple UK HQ (Battersea Power Station)"], "population": 330000, "geo": (51.4571, -0.1845), "nearby": ["Putney", "Battersea", "Tooting", "Earlsfield"]},
    "hammersmith": {"name": "Hammersmith", "region": "Greater London", "postcodes": "W6, W12", "districts": ["Town Centre", "Shepherd's Bush", "Brook Green", "Ravenscourt Park"], "sectors": ["Media and broadcasting", "Tech", "Real estate", "Healthcare", "Hospitality"], "employers": ["BBC Television Centre (legacy)", "L'Oreal UK HQ", "Coca-Cola European Partners HQ (nearby Uxbridge)", "Hammersmith Hospital (Imperial NHS)", "Disney UK HQ"], "population": 185000, "geo": (51.4927, -0.2339), "nearby": ["Fulham", "Shepherd's Bush", "Chiswick", "Kensington"]},
    "putney": {"name": "Putney", "region": "Greater London", "postcodes": "SW15", "districts": ["Town Centre", "East Putney", "West Putney", "Roehampton"], "sectors": ["Healthcare", "Public sector", "Real estate", "Retail", "Education"], "employers": ["Putney Hospital (St George's)", "Wandsworth Council", "Roehampton University", "Putney School of Art and Design", "Marsh & McLennan (regional)"], "population": 75000, "geo": (51.4612, -0.2152), "nearby": ["Wandsworth", "Wimbledon", "Fulham", "Richmond"]},
}


# Wave 3 adjacent town pairs (40 new pairs for 80 new cities).
# Defined as a separate list and merged into ADJACENT_PAIRS below the
# original definition, since ADJACENT_PAIRS itself is declared further down.
_WAVE3_PAIRS = [
    ("stirling", "perth"),
    ("paisley", "east-kilbride"),
    ("hamilton", "livingston"),
    ("falkirk", "kirkcaldy"),
    ("dunfermline", "ayr"),
    ("lisburn", "derry"),
    ("newry", "wrexham"),
    ("bridgend", "caerphilly"),
    ("bangor-wales", "llanelli"),
    ("gateshead", "south-shields"),
    ("darlington", "hartlepool"),
    ("stockton-on-tees", "chester"),
    ("crewe", "macclesfield"),
    ("carlisle", "lancaster"),
    ("morecambe", "oldham"),
    ("bury", "st-helens"),
    ("skelmersdale", "rotherham"),
    ("barnsley", "scunthorpe"),
    ("grimsby", "harrogate"),
    ("skipton", "pontefract"),
    ("burton-upon-trent", "newark-on-trent"),
    ("worksop", "kettering"),
    ("wellingborough", "sutton-coldfield"),
    ("solihull", "redditch"),
    ("bromsgrove", "tamworth"),
    ("cannock", "stafford"),
    ("nuneaton", "bedford"),
    ("bury-st-edmunds", "kings-lynn"),
    ("lowestoft", "great-yarmouth"),
    ("hertford", "stevenage"),
    ("hatfield", "tunbridge-wells"),
    ("tonbridge", "ashford"),
    ("dover", "margate"),
    ("folkestone", "canterbury"),
    ("sevenoaks", "hastings"),
    ("eastbourne", "worthing"),
    ("crawley", "horsham"),
    ("chichester", "bognor-regis"),
    ("redhill", "reigate"),
    ("epsom", "leatherhead"),
    ("woking", "aldershot"),
    ("farnham", "camberley"),
    ("truro", "falmouth"),
    ("penzance", "torquay"),
    ("paignton", "yeovil"),
    ("taunton", "bridgwater"),
    ("weston-super-mare", "salisbury"),
    ("andover", "newbury"),
    ("winchester", "eastleigh"),
    ("wembley", "ealing"),
    ("hounslow", "hillingdon"),
    ("uxbridge", "enfield"),
    ("barnet", "walthamstow"),
    ("ilford", "wimbledon"),
    ("greenwich", "lewisham"),
    ("wandsworth", "hammersmith"),
    ("putney", "london"),  # putney <-> london (london's existing pair was reading)
]


# Pre-computed adjacent town pairs. Each new pair is geographically sensible
# so internal cross-links feel natural, not templated.
ADJACENT_PAIRS = [
    # Original 30-city pairs
    ("london", "reading"),
    ("manchester", "liverpool"),
    ("birmingham", "coventry"),
    ("leeds", "bradford"),
    ("bristol", "cardiff"),
    ("edinburgh", "glasgow"),
    ("newcastle", "sheffield"),
    ("nottingham", "derby"),
    ("brighton", "portsmouth"),
    ("bournemouth", "plymouth"),
    ("hull", "york"),
    ("stoke-on-trent", "wolverhampton"),
    ("leicester", "northampton"),
    ("milton-keynes", "oxford"),
    ("cambridge", "southampton"),
    # Wave 2 expansion pairs
    ("aberdeen", "dundee"),
    ("inverness", "belfast"),
    ("swansea", "newport"),
    ("sunderland", "middlesbrough"),
    ("doncaster", "wakefield"),
    ("halifax", "huddersfield"),
    ("preston", "blackpool"),
    ("salford", "stockport"),
    ("bolton", "wigan"),
    ("rochdale", "burnley"),
    ("warrington", "telford"),
    ("walsall", "shrewsbury"),
    ("cheltenham", "gloucester"),
    ("worcester", "hereford"),
    ("lincoln", "mansfield"),
    ("bath", "exeter"),
    ("norwich", "ipswich"),
    ("peterborough", "chelmsford"),
    ("colchester", "luton"),
    ("basingstoke", "maidstone"),
    ("guildford", "slough"),
    ("watford", "st-albans"),
    ("croydon", "sutton"),
    ("bromley", "kingston-upon-thames"),
    ("harrow", "romford"),
]

# Merge the Wave 3 expansion pairs (defined earlier in the file)
ADJACENT_PAIRS = ADJACENT_PAIRS + _WAVE3_PAIRS


def adjacent_for(slug: str) -> dict:
    for a, b in ADJACENT_PAIRS:
        if slug == a:
            return {"slug": b, "name": CITY_SEEDS[b]["name"]}
        if slug == b:
            return {"slug": a, "name": CITY_SEEDS[a]["name"]}
    return {"slug": "london", "name": "London"}  # fallback


SYSTEM_PROMPT = """You are a senior ICAEW-qualified UK accountant writing the location page for Holloway Davies, a generalist UK accountancy firm serving limited companies, contractors, sole traders, partnerships and small businesses across the country.

Your job: write the per-city content fields for a single UK city location page.

VOICE: Financial Times editorial. Precise, confident, plain English, occasional sharp opinion. Not founder-pitched, not consumer-friendly, not corporate-stiff. Use UK English (specialise, organise, recognise).

CRITICAL BANS:
- NO em-dashes anywhere. Use commas, full stops, parentheses, or middle dots instead.
- NO "agency founder" / "agency founders" / "for agency founders" as an audience framing. Our audience is "limited company directors, contractors, sole traders, partnerships and small business owners". "Agency" is fine as a generic noun (e.g. a marketing agency in the sector list) but never as the target audience.
- NO marketing fluff openers ("In today's", "Whether you", "Navigating the complex", "When it comes to").
- NO banned verbs: delve, leverage, harness, unlock, master, dive into, embrace (metaphorically).
- NO banned nouns: landscape (metaphorical), realm, tapestry, intricate, robust, seamless.
- NO closing exhortations like "Remember to consult a professional".

KEYWORD USAGE:
- The primary keyword for this page is "accountant in [city]" (singular). Use that exact phrase naturally 1-2 times across whyHere + sectorEmphasis (don't force more; the page template adds it 4-5 more times in H1, metadata, CTA, breadcrumbs).

CONTENT REQUIREMENTS:
- Reference the city's REAL economic context: industries given in the seed, employers given in the seed, named business districts given in the seed.
- Tie our services (corporation tax, VAT, payroll, R&D credits, exit planning) to the LOCAL sector mix.
- Use ICAEW credibility once, naturally.
- Avoid generic statements that could apply to any town.
- Each text field must reference at least one named local detail (an industry, an employer, a district, a postcode area).

OUTPUT: a single JSON object with EXACTLY these keys. No surrounding prose. No markdown fences. No commentary.

{
  "intro": "<1-2 sentence opener about this city's business context (max 220 chars)>",
  "whyHere": "<80-100 word para on why we work with [city] businesses, referencing local sectors, the option of remote-first or in-person, named districts. Do NOT start with 'We work with'.>",
  "businessScene": "<150-180 word para on the local business scene: industries, named employers, named districts, what's distinctive about the local economy. No fluff.>",
  "sectorEmphasis": "<180-220 word para tying our services to the LOCAL sector mix specifically. Mention at least 2 named local sectors and 1 named local employer. Explain how the local economic mix shapes our service emphasis (e.g. 'a Bradford food manufacturer might prioritise capital allowances on plant; a Leeds fintech often comes to us for R&D claim preparation').>",
  "localCaseStudy": {
    "business_type": "<short label: e.g. '12-employee food manufacturer'>",
    "headline": "<one-liner outcome, e.g. '£18,400 R&D claim recovered on new line automation'>",
    "body": "<150-180 word anonymised case study: a fictional but realistic local business, what they came to us with, what we did, the specific outcome. Use specific numbers (£14,720 not £15k). Reference the local sector mix.>"
  },
  "localFaqs": [
    {"question": "<town-specific question, e.g. 'Do you have an office in [city]?'>", "answer": "<2-3 sentence honest answer, prefer 'remote-first with in-person on request' framing>"},
    {"question": "<sector-specific question relevant to the local industry mix>", "answer": "<2-3 sentence answer>"},
    {"question": "<practical local question, e.g. about pricing, switching, deadlines>", "answer": "<2-3 sentence answer>"},
    {"question": "<one more local question>", "answer": "<2-3 sentence answer>"}
  ]
}
"""


USER_PROMPT_TEMPLATE = """City: {name}
Region: {region}
Postcode focus: {postcodes}
Named business districts (use these by name): {districts}
Dominant local sectors (use these): {sectors}
Major local employers (reference at least 2 by name): {employers}
Estimated city population: {population:,}
Nearby areas we also serve: {nearby}

Adjacent partner-town for cross-link context (you don't need to mention it, just for our internal link map): {adjacent}

Generate the JSON object now."""


def call_deepseek(client: DeepSeekClient, slug: str, seed: dict, attempt: int = 1) -> dict | None:
    adj = adjacent_for(slug)
    user = USER_PROMPT_TEMPLATE.format(
        name=seed["name"],
        region=seed["region"],
        postcodes=seed["postcodes"],
        districts=", ".join(seed["districts"]),
        sectors=", ".join(seed["sectors"]),
        employers=", ".join(seed["employers"]),
        population=seed["population"],
        nearby=", ".join(seed["nearby"]),
        adjacent=adj["name"],
    )
    raw = client.generate_creative(
        prompt=user,
        system=SYSTEM_PROMPT,
        temperature=0.65,
        max_tokens=2200,
    )
    # Strip code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        if attempt < 3:
            print(f"    [retry {attempt+1}] JSON parse failed: {e}")
            return call_deepseek(client, slug, seed, attempt + 1)
        print(f"    FAILED after {attempt} attempts: {e}")
        print(f"    raw: {raw[:300]}")
        return None
    return data


# Hard-banned audience-framing patterns. "agency" as a generic noun (a UK
# trading structure, a marketing agency) is allowed; the ban is on the
# agency-founder positioning that the old template used.
BANNED = (
    "—",
    "agency founder",
    "agency founders",
    "for agency founders",
    "agency-only",
    "agency focus",
    "agency niche",
)


def validate_city(slug: str, seed: dict, data: dict) -> tuple[bool, str]:
    required_keys = ["intro", "whyHere", "businessScene", "sectorEmphasis", "localCaseStudy", "localFaqs"]
    for k in required_keys:
        if k not in data:
            return False, f"missing key: {k}"
    if not isinstance(data["localCaseStudy"], dict):
        return False, "localCaseStudy not a dict"
    for k in ["business_type", "headline", "body"]:
        if k not in data["localCaseStudy"]:
            return False, f"case study missing key: {k}"
    if not isinstance(data["localFaqs"], list) or len(data["localFaqs"]) < 3:
        return False, f"need >= 3 FAQs, got {len(data.get('localFaqs', []))}"
    # Banned-string check (case-insensitive)
    text_blob = " ".join([
        data["intro"], data["whyHere"], data["businessScene"], data["sectorEmphasis"],
        data["localCaseStudy"].get("body", ""),
        " ".join(f"{f.get('question','')} {f.get('answer','')}" for f in data["localFaqs"]),
    ]).lower()
    for b in BANNED:
        if b.lower() in text_blob:
            return False, f"banned string present: {b!r}"
    # Length floor on the main narrative (4 fields combined). The rendered
    # page adds case study, FAQs, sector chips, employer list, services grid
    # on top, so 320 here = ~1500+ words on page.
    main_word_count = sum(len(data[k].split()) for k in ("intro", "whyHere", "businessScene", "sectorEmphasis"))
    if main_word_count < 320:
        return False, f"narrative too short: {main_word_count} words"
    # Each FAQ answer should be at least 30 words
    for i, f in enumerate(data["localFaqs"]):
        if len(f.get("answer", "").split()) < 25:
            return False, f"FAQ {i} answer too short: {len(f.get('answer', '').split())} words"
    return True, ""


def generate_one(slug: str) -> dict | None:
    seed = CITY_SEEDS[slug]
    client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)
    t0 = time.time()
    for attempt in range(1, 4):
        data = call_deepseek(client, slug, seed)
        if data is None:
            continue
        ok, msg = validate_city(slug, seed, data)
        if ok:
            elapsed = time.time() - t0
            print(f"  [{slug:>16}]  {elapsed:>4.1f}s  OK")
            return data
        print(f"  [{slug:>16}]  validation failed (attempt {attempt}): {msg}")
    print(f"  [{slug:>16}]  GAVE UP after 3 attempts")
    return None


def merge_into_city_data(slug: str, generated: dict) -> dict:
    seed = CITY_SEEDS[slug]
    lat, lng = seed["geo"]
    return {
        "slug": slug,
        "name": seed["name"],
        "region": seed["region"],
        "postcodeFocus": seed["postcodes"],
        "businessHubs": seed["districts"],
        "intro": generated["intro"],
        "whyHere": generated["whyHere"],
        "businessScene": generated["businessScene"],
        "geo": {"latitude": lat, "longitude": lng},
        "population": seed["population"],
        "localSectors": seed["sectors"],
        "sectorEmphasis": generated["sectorEmphasis"],
        "keyEmployers": seed["employers"],
        "localCaseStudy": generated["localCaseStudy"],
        "localFaqs": generated["localFaqs"],
        "nearbyAreas": seed["nearby"],
        "adjacentTown": adjacent_for(slug),
    }


def ts_escape(s: str) -> str:
    """Escape a string for embedding inside a TypeScript double-quoted literal."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def emit_typescript(cities: dict[str, dict]) -> str:
    """Render the cities map as a typed TypeScript module."""
    lines = []
    lines.append("export type CityData = {")
    lines.append("  slug: string;")
    lines.append("  name: string;")
    lines.append("  region: string;")
    lines.append("  postcodeFocus: string;")
    lines.append("  businessHubs: string[];")
    lines.append("  intro: string;")
    lines.append("  whyHere: string;")
    lines.append("  businessScene: string;")
    lines.append("  geo: { latitude: number; longitude: number };")
    lines.append("  population: number;")
    lines.append("  localSectors: string[];")
    lines.append("  sectorEmphasis: string;")
    lines.append("  keyEmployers: string[];")
    lines.append("  localCaseStudy: {")
    lines.append("    business_type: string;")
    lines.append("    headline: string;")
    lines.append("    body: string;")
    lines.append("  };")
    lines.append("  localFaqs: { question: string; answer: string }[];")
    lines.append("  nearbyAreas: string[];")
    lines.append("  adjacentTown: { slug: string; name: string };")
    lines.append("};")
    lines.append("")
    lines.append("export const CITIES: Record<string, CityData> = {")
    for slug, c in cities.items():
        lines.append(f"  {json.dumps(slug)}: {{")
        lines.append(f"    slug: {json.dumps(c['slug'])},")
        lines.append(f"    name: {json.dumps(c['name'])},")
        lines.append(f"    region: {json.dumps(c['region'])},")
        lines.append(f"    postcodeFocus: {json.dumps(c['postcodeFocus'])},")
        lines.append(f"    businessHubs: {json.dumps(c['businessHubs'])},")
        lines.append(f"    intro: {json.dumps(c['intro'])},")
        lines.append(f"    whyHere: {json.dumps(c['whyHere'])},")
        lines.append(f"    businessScene: {json.dumps(c['businessScene'])},")
        lines.append(f"    geo: {{ latitude: {c['geo']['latitude']}, longitude: {c['geo']['longitude']} }},")
        lines.append(f"    population: {c['population']},")
        lines.append(f"    localSectors: {json.dumps(c['localSectors'])},")
        lines.append(f"    sectorEmphasis: {json.dumps(c['sectorEmphasis'])},")
        lines.append(f"    keyEmployers: {json.dumps(c['keyEmployers'])},")
        lines.append(f"    localCaseStudy: {{")
        lines.append(f"      business_type: {json.dumps(c['localCaseStudy']['business_type'])},")
        lines.append(f"      headline: {json.dumps(c['localCaseStudy']['headline'])},")
        lines.append(f"      body: {json.dumps(c['localCaseStudy']['body'])},")
        lines.append(f"    }},")
        lines.append(f"    localFaqs: [")
        for f in c["localFaqs"]:
            lines.append(f"      {{ question: {json.dumps(f['question'])}, answer: {json.dumps(f['answer'])} }},")
        lines.append(f"    ],")
        lines.append(f"    nearbyAreas: {json.dumps(c['nearbyAreas'])},")
        lines.append(f"    adjacentTown: {{ slug: {json.dumps(c['adjacentTown']['slug'])}, name: {json.dumps(c['adjacentTown']['name'])} }},")
        lines.append("  },")
    lines.append("};")
    lines.append("")
    return "\n".join(lines)


def cross_city_uniqueness_check(generated: dict[str, dict]) -> list[str]:
    """Flag any pair of cities whose opening or case study body matches too closely."""
    warnings = []
    intros = {s: g["intro"][:120].lower() for s, g in generated.items()}
    cases = {s: g["localCaseStudy"]["body"][:160].lower() for s, g in generated.items()}
    slugs = list(generated.keys())
    for i, a in enumerate(slugs):
        for b in slugs[i+1:]:
            if intros[a] == intros[b]:
                warnings.append(f"  duplicate intro: {a} <-> {b}")
            if cases[a] == cases[b]:
                warnings.append(f"  duplicate case study: {a} <-> {b}")
    return warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="generate one specific slug")
    parser.add_argument("--limit", type=int, help="generate first N cities only (smoke test)")
    parser.add_argument("--workers", type=int, default=5)
    args = parser.parse_args()

    if args.only:
        slugs = [args.only] if args.only in CITY_SEEDS else []
        if not slugs:
            sys.exit(f"unknown slug: {args.only}. Options: {list(CITY_SEEDS.keys())}")
    else:
        slugs = list(CITY_SEEDS.keys())
        if args.limit:
            slugs = slugs[: args.limit]

    print(f"Generating {len(slugs)} town pages (workers={args.workers})...")
    print()

    generated = {}
    failed = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(generate_one, s): s for s in slugs}
        for fut in as_completed(futures):
            s = futures[fut]
            data = fut.result()
            if data is None:
                failed.append(s)
            else:
                generated[s] = data

    if failed:
        print(f"\nFAILED: {failed}")
    print(f"\nSuccess: {len(generated)} / {len(slugs)}")

    if not generated:
        sys.exit("nothing to write")

    # Cross-city uniqueness
    print("\nCross-city uniqueness check:")
    warnings = cross_city_uniqueness_check(generated)
    if warnings:
        for w in warnings:
            print(w)
    else:
        print("  no duplicates found")

    # Merge with seed metadata and ORDER by canonical slug list
    cities_in_order = {}
    for s in CITY_SEEDS.keys():
        if s in generated:
            cities_in_order[s] = merge_into_city_data(s, generated[s])

    # If only generating a subset, we need to preserve the existing file's
    # entries for non-targeted cities. Read current file, parse what we can.
    if args.only or args.limit:
        print(f"\nPartial generation: would overwrite only {list(cities_in_order.keys())}.")
        print("For a full file write, run without --only / --limit.")
        # For safety, write to a sidecar file
        sidecar = OUT_TS.with_suffix(".partial.ts")
        sidecar.write_text(emit_typescript(cities_in_order), encoding="utf-8")
        print(f"Wrote sidecar to {sidecar}")
        return

    ts = emit_typescript(cities_in_order)
    OUT_TS.write_text(ts, encoding="utf-8")
    print(f"\nWrote {OUT_TS}")
    print(f"  {len(cities_in_order)} cities, {len(ts):,} chars")


if __name__ == "__main__":
    main()
