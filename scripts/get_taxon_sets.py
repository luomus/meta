"""Fetch taxa of taxonSets from FinBIF API using Bearer token authentication."""

import requests

ACCESS_TOKEN = "TOKEN-HERE"
BASE_URL = "https://laji.fi/api/taxa"


def fetch_taxa(taxon_set, lang="fi", selected_fields="id,scientificName,vernacularName", page_size=1000):
    """Fetch taxa for one taxon set from FinBIF API. Uses Authorization: Bearer header."""
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    all_results = []
    page = 1

    while True:
        params = {
            "taxonSets": taxon_set,
            "lang": lang,
            "selectedFields": selected_fields,
            "sortOrder": "taxonomic",
            "pageSize": page_size,
            "page": page,
        }
        response = requests.get(BASE_URL, params=params, headers=headers)
        print(f"API URL: {response.url}")
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            results = data
            total = len(data)
        else:
            results = data.get("results", [])
            total = data.get("totalResults", len(all_results) + len(results))
        all_results.extend(results)

        if len(all_results) >= total or not results:
            break
        page += 1

    return all_results


def write_taxa_md(taxa, taxon_set_name, path):
    """Write taxa to a markdown file: # taxon set name, then vernacularName, scientificName per line."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {taxon_set_name}\n")
        for t in taxa:
            vernacular = t.get("vernacularName") or ""
            scientific = t.get("scientificName") or ""
            f.write(f"{vernacular}, {scientific}\n")


if __name__ == "__main__":
    taxon_sets = ["MX.taxonSetWaterbirdAmphibia", "MX.taxonSetWaterbirdGulls", "MX.taxonSetWaterbirdPasserines", "MX.taxonSetWaterbirdWaders", "MX.taxonSetWaterbirdWaterbirds"]
    with open("taxa.md", "w", encoding="utf-8") as f:
        for taxon_set in taxon_sets:
            taxa = fetch_taxa(taxon_set)
            f.write(f"# {taxon_set}\n")
            for t in taxa:
                vernacular = t.get("vernacularName") or ""
                scientific = t.get("scientificName") or ""
                f.write(f"{vernacular}, {scientific}\n")
            f.write("\n")
    print("Wrote taxa to taxa.md")
