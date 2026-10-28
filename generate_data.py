#!/usr/bin/env python3
"""Generate 100 Sea Point properties with the full data model."""
import json, random, datetime

random.seed(42)

# Streets with approximate base coordinates (lat, lng) in Sea Point
STREETS = [
    ("Beach Road",      -33.9210, 18.3830, 0.0008, 0.0008),  # coastal bend
    ("Main Road",       -33.9205, 18.3885, 0.0012, 0.0006),
    ("High Level Road", -33.9210, 18.3920, 0.0013, 0.0005),
    ("Regent Road",     -33.9210, 18.3845, 0.0010, 0.0006),
    ("Queens Road",     -33.9225, 18.3800, 0.0009, 0.0007),
    ("Kloof Road",      -33.9240, 18.3835, 0.0008, 0.0006),
    ("St John's Road",  -33.9220, 18.3815, 0.0008, 0.0006),
    ("Surrey Road",     -33.9200, 18.3855, 0.0009, 0.0006),
    ("Milton Road",     -33.9245, 18.3820, 0.0007, 0.0006),
    ("Arthur's Road",   -33.9185, 18.3870, 0.0009, 0.0005),
    ("Rose Street",     -33.9180, 18.3860, 0.0008, 0.0005),
    ("Victoria Road",   -33.9260, 18.3805, 0.0010, 0.0008),
    ("Bay View Avenue", -33.9165, 18.3895, 0.0008, 0.0005),
    ("Neptune Street",  -33.9195, 18.3880, 0.0007, 0.0005),
    ("Geneva Road",     -33.9175, 18.3885, 0.0007, 0.0005),
    ("Penzance Road",   -33.9155, 18.3895, 0.0008, 0.0005),
    ("Gladstone Street",-33.9230, 18.3865, 0.0008, 0.0005),
    ("Trinity Road",    -33.9240, 18.3875, 0.0007, 0.0005),
    ("Camp Street",     -33.9190, 18.3840, 0.0008, 0.0005),
    ("Beresford Road",  -33.9250, 18.3840, 0.0007, 0.0005),
]

PROPERTY_TYPES = ["Apartment", "House", "Vacant Land"]
WEIGHTS = [0.53, 0.37, 0.10]
OCCUPANTS = ["Owner", "Renter", "Vacant"]
OCC_WEIGHTS = [0.46, 0.40, 0.14]
MARKETING = ["For Sale", "To Rent", "Not on Market"]
MKT_WEIGHTS = [0.30, 0.20, 0.50]
CONTACT = ["Email only", "Mobile only", "Email and Mobile", "None"]
CONTACT_WEIGHTS = [0.25, 0.22, 0.33, 0.20]
AGENTS = ["Harcourts", "Pam Golding", "Seeff", "Remax", "Lew Geffen Sotheby's",
          "Jawitz", "Keller Williams", "Chas Everitt", "Fine & Country",
          "Engel & Völkers", "Camps Bay & Sea Point Properties", "Just Property"]

def agent(): return random.choice(AGENTS)

def last_sale_date():
    years_ago = random.choices([0.4, 1.8, 3.8, 7.0, 13.0], weights=[18, 20, 22, 22, 18])[0]
    d = datetime.date(2026, 10, 1) - datetime.timedelta(days=int(years_ago * 365.25))
    return d.isoformat()

def sale_price(p_type):
    if p_type == "Vacant Land":
        return round(random.uniform(0.8e6, 12e6), -4)
    if p_type == "Apartment":
        return round(random.uniform(1.4e6, 9e6), -4)
    return round(random.uniform(4e6, 28e6), -4)

def valuation(p, p_type):
    year_factor = 1.0 + random.uniform(-0.04, 0.10)
    if p_type == "Vacant Land": return round(p * year_factor * 1.12, -4)
    if p_type == "Apartment": return round(p * year_factor * 1.15, -4)
    return round(p * year_factor * 1.20, -4)

def time_on_market(mkt):
    if mkt != "For Sale":
        return None
    return random.choices(
        ["< 1 month", "2-3 months", "3-6 months", "6-12 months", "> 12 months"],
        weights=[18, 22, 26, 20, 14])[0]

def propensity(o, mkt, tom, tags):
    s = 0
    if mkt == "For Sale": s = 100
    elif mkt == "To Rent":
        s = random.choices([8, 15, 25, 40], [40, 35, 20, 5])[0]
        if o == "Vacant": s += 10
    else:  # not on market
        s = random.choices([0, 5, 12, 22, 35], [35, 30, 20, 10, 5])[0]
        if "potential seller" in tags: s = max(s, 55)
        if "downsizers" in tags: s = max(s, 60)
        if "absentee owner" in tags: s = max(s, 50)
        if "long-term owners" in tags: s = min(s, 15)
        if "heritage" in tags: s = min(s, 20)
    if tom in ("> 12 months", "6-12 months"): s = min(100, s + 5)
    return s

TAG_POOL = {
    "Apartment": ["beachfront", "sea view", "renovated", "airbnb", "investment", "potential seller",
                  "first-time buyer", "young professional", "long-term owners", "new owner",
                  "absorber", "body corporate issues", "short-term rental", "fully furnished"],
    "House": ["family", "pool", "corner plot", "heritage", "premium", "high value", "potential seller",
              "downsizers", "empty nesters", "renovating", "extended", "double garage",
              "large garden", "security estate", "remote worker"],
    "Vacant Land": ["development potential", "subdivisible", "plot", "investment", "by architect",
                    "regime complex", "potential seller", "land bank"],
}

NOTES = {
    "potential seller": "Owner mentioned they may sell within 6-12 months.",
    "downsizers": "Empty nesters considering downsizing to a smaller apartment.",
    "renovating": "Currently renovating — kitchen/bathroom upgrade in progress.",
    "absentee owner": "Owner lives abroad and rarely visits. Managed remotely.",
    "long-term owners": "Original owners — in the building 25+ years.",
    "airbnb": "Running as a short-term Airbnb. Strong nightly returns.",
    "body corporate issues": "Owner unhappy with rising body corporate levies.",
    "inherited": "Property inherited from parents. Unsure about selling.",
    "new owner": "Recently purchased. Settling into the area.",
}

def build():
    props = []
    for i in range(1, 101):
        p_type = random.choices(PROPERTY_TYPES, weights=WEIGHTS)[0]
        street, blat, blng, jlat, jlng = random.choice(STREETS)
        num = random.choice([random.randint(1, 220), random.choice(['2A','4B','7C','12A','15B','19A','22B','3B','5A','8B'])])
        p = {
            "id": f"SP{i:03d}",
            "address": f"{num} {street}",
            "type": p_type,
            "lastSaleDate": last_sale_date(),
            "lastSalePrice": 0,
            "currentValuation": 0,
            "valuationDate": "2026-10-01",
            "occupantType": random.choices(OCCUPANTS, weights=OCC_WEIGHTS)[0],
            "marketingStatus": random.choices(MARKETING, weights=MKT_WEIGHTS)[0],
            "contactDetails": random.choices(CONTACT, weights=CONTACT_WEIGHTS)[0],
            "lastSellingAgent": agent(),
            "timeOnMarket": None,
            "propensityScore": 0,
            "lat": round(blat + random.uniform(-jlat, jlat), 6),
            "lng": round(blng + random.uniform(-jlng, jlng), 6),
        }
        if p_type == "Vacant Land":
            p["beds"] = 0; p["baths"] = 0
            p["size"] = random.choice([250, 320, 420, 510, 620, 740, 880, 1000])
            p["tags"] = random.sample(TAG_POOL["Vacant Land"], k=random.randint(2, 4))
        elif p_type == "Apartment":
            p["beds"] = random.choices([1, 2, 3, 4], weights=[20, 45, 28, 7])[0]
            p["baths"] = min(p["beds"], 3) if random.random() < 0.8 else p["beds"] + 1
            p["size"] = round(random.uniform(38, 260))
            p["tags"] = random.sample(TAG_POOL["Apartment"], k=random.randint(2, 4))
        else:  # House
            p["beds"] = random.choices([2, 3, 4, 5, 6], weights=[8, 25, 35, 22, 10])[0]
            p["baths"] = min(p["beds"] - 1, 4) if p["beds"] > 2 else p["beds"]
            p["size"] = round(random.uniform(150, 520))
            p["tags"] = random.sample(TAG_POOL["House"], k=random.randint(2, 4))

        p["lastSalePrice"] = sale_price(p_type)
        p["currentValuation"] = valuation(p["lastSalePrice"], p_type)
        p["timeOnMarket"] = time_on_market(p["marketingStatus"])
        p["propensityScore"] = propensity(p["occupantType"], p["marketingStatus"], p["timeOnMarket"], p["tags"])

        # Notes from interesting tags
        interesting = [t for t in p["tags"] if t in NOTES]
        if interesting:
            p["notes"] = " ".join(NOTES[t] for t in interesting[:2])
        else:
            p["notes"] = ""

        props.append(p)

    return props

if __name__ == "__main__":
    props = build()
    with open("/opt/data/property-library/data.json", "w") as f:
        json.dump(props, f, indent=2)
    # Quick distribution report
    from collections import Counter
    print(f"Total: {len(props)}")
    print("Type:", dict(Counter(p['type'] for p in props)))
    print("Occupant:", dict(Counter(p['occupantType'] for p in props)))
    print("Marketing:", dict(Counter(p['marketingStatus'] for p in props)))
    print("Contact:", dict(Counter(p['contactDetails'] for p in props)))
    print("Propensity 0-39:", sum(1 for p in props if p['propensityScore'] < 40),
          "40-79:", sum(1 for p in props if 40 <= p['propensityScore'] < 80),
          "80-100:", sum(1 for p in props if p['propensityScore'] >= 80))
    print("With coords:", sum(1 for p in props if 'lat' in p and 'lng' in p))