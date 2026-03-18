#!/usr/bin/env python3
"""
Initialize the remote tracker with ENJOB25012424 spool data.
Run this once after deployment to load all 192 spools.

Usage:
    python3 init_424.py https://enerxon-china-tracker.onrender.com
"""

import sys
import json
import requests

# All 424 project spools (extracted from matrix)
# Run locally first to generate this, or use the API

def load_spools_from_matrix(matrix_path):
    """Load spools from local Excel file."""
    sys.path.insert(0, '/Users/danny/Library/CloudStorage/Dropbox/ENERXON/Agents Claude/Charlie-Production-Agent')
    from charlie_parse_spools import parse_matrix
    spools = parse_matrix(matrix_path, project='ENJOB25012424')
    return [s.to_dict() for s in spools]


def push_to_remote(base_url, spools):
    """Push spool data to the remote tracker API."""
    url = f"{base_url.rstrip('/')}/api/import"
    print(f"Pushing {len(spools)} spools to {url}...")

    # Send in batches of 50
    for i in range(0, len(spools), 50):
        batch = spools[i:i+50]
        resp = requests.post(url, json=batch, timeout=30)
        if resp.status_code == 200:
            print(f"  Batch {i//50 + 1}: {resp.json()}")
        else:
            print(f"  ERROR: {resp.status_code} - {resp.text}")

    print("Done!")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 init_424.py <tracker_url>")
        print("Example: python3 init_424.py https://enerxon-china-tracker.onrender.com")
        sys.exit(1)

    base_url = sys.argv[1]
    matrix = '/Users/danny/Library/CloudStorage/Dropbox/ENERXON/Operational process/QC/MTC/Customers/424/Manufacturing/Production/spool_summary and cutting.xlsx'

    spools = load_spools_from_matrix(matrix)
    push_to_remote(base_url, spools)
