import csv
import sys
from collections import OrderedDict
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

# Base of every URL on the results site; all other pages are relative to it.
BASE_URL = "https://volby.gov.cz/pls/ps2017nss/"

# Top-level page listing every kraj (region) and, within each, every okres
# (district) together with a link to that district's list of municipalities.
DISTRICTS_URL = urljoin(BASE_URL, "ps3?xjazyk=CZ")

# Table cell "headers" ids on a municipality results page (ps311) that hold
# the summary numbers we care about. These ids are fixed by the site markup.
HEADER_REGISTERED = "sa2"  # Volici v seznamu (registered voters)
HEADER_ENVELOPES = "sa3"   # Vydane obalky (envelopes issued)
HEADER_VALID = "sa6"       # Platne hlasy (valid votes)

def fetch_soup(url):
    """Download a page and return it parsed as a BeautifulSoup object."""
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def find_district(district_name):
    """Resolve a district name to its (xkraj, xnumnuts) URL parameters."""
    soup = fetch_soup(DISTRICTS_URL)

    for row in soup.find_all("tr"):
        link = row.find("a", href=lambda href: href and "ps32?" in href)
        if link is None:
            continue

        cells = row.find_all("td")
        name = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        if name != district_name:
            continue

        query = parse_qs(urlparse(link["href"]).query)
        # Bezpečné vytažení hodnot bez použití hranatých závorek s indexy
        kraj_kod = next(iter(query.get("xkraj", [])))
        nuts_kod = next(iter(query.get("xnumnuts", [])))
        return kraj_kod, nuts_kod

    print(f"District '{district_name}' was not found on {DISTRICTS_URL}.")
    print("Check the spelling and diacritics match the site exactly.")
    sys.exit(1)

def get_municipalities(xkraj, xnumnuts):
    """Return a list of (code, name, results_url) for every municipality."""
    list_url = urljoin(
        BASE_URL, f"ps32?xjazyk=CZ&xkraj={xkraj}&xnumnuts={xnumnuts}"
    )
    soup = fetch_soup(list_url)

    municipalities = []
    for link in soup.find_all("a", href=lambda href: href and "ps311?" in href):
        code = link.get_text(strip=True)
        if not code.isdigit():
            continue
        row = link.find_parent("tr")
        cells = row.find_all("td")
        name_cell = next(iter(cells[1:]))
        name = name_cell.get_text(strip=True)
        results_url = urljoin(BASE_URL, link["href"])
        municipalities.append((code, name, results_url))

    return municipalities

def _parse_int(text):
    """Convert a site number like '13\xa0104' into 1304."""
    return int(text.replace("\xa0", "").replace(" ", ""))

def get_municipality_results(url):
    """Scrape one municipality's results page."""
    soup = fetch_soup(url)

    summary = soup.find("table", id="ps311_t1")
    registered = _parse_int(
        summary.find("td", headers=lambda h: h and HEADER_REGISTERED in h.split())
        .get_text(strip=True)
    )
    envelopes = _parse_int(
        summary.find("td", headers=lambda h: h and HEADER_ENVELOPES in h.split())
        .get_text(strip=True)
    )
    valid = _parse_int(
        summary.find("td", headers=lambda h: h and HEADER_VALID in h.split())
        .get_text(strip=True)
    )

    parties = OrderedDict()
    for name_cell in soup.find_all("td", class_="overflow_name"):
        party_name = name_cell.get_text(strip=True)
        votes_cell = name_cell.find_next_sibling("td", class_="cislo")
        parties[party_name] = _parse_int(votes_cell.get_text(strip=True))

    return {
        "registered": registered,
        "envelopes": envelopes,
        "valid": valid,
        "parties": parties,
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <district name> <output file.csv>")
        print('Example: python main.py "Benešov" benesov.csv')
        sys.exit(1)

    district_name, output_file = sys.argv[1], sys.argv[2]

    xkraj, xnumnuts = find_district(district_name)

    municipalities = get_municipalities(xkraj, xnumnuts)
    if not municipalities:
        print(f"No municipalities found for district '{district_name}'.")
        sys.exit(1)

    rows = []
    party_names = None
    for code, name, url in municipalities:
        print(f"Scraping {name} ...")
        results = get_municipality_results(url)

        if party_names is None:
            party_names = list(results["parties"].keys())

        row = [code, name, results["registered"], results["envelopes"], results["valid"]]
        row.extend(results["parties"].get(party, 0) for party in party_names)
        rows.append(row)

    header = ["kod", "obec", "volici_v_seznamu", "vydane_obalky", "platne_hlasy"]
    header.extend(party_names)

    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"Done. Wrote {len(rows)} rows to {output_file}.")

if __name__ == "__main__":
    main()