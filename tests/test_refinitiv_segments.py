#!/usr/bin/env python3
"""
Test Refinitiv Segment Data Entitlement
"""

import json
import logging
import os
import sys
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Load env
PROJECT_ROOT = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv
    if (PROJECT_ROOT / ".env.local").exists():
        load_dotenv(PROJECT_ROOT / ".env.local", override=True)
    if (PROJECT_ROOT / ".env").exists():
        load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

class SegmentTester:
    BASE_URL = "https://api.refinitiv.com"
    AUTH_URL = "https://api.refinitiv.com/auth/oauth2/v1/token"

    def __init__(self):
        self.client_id = os.getenv("REFINITIV_CLIENT_ID")
        self.username = os.getenv("REFINITIV_USERNAME")
        self.password = os.getenv("REFINITIV_PASSWORD")
        self.access_token = None

    def authenticate(self):
        if not all([self.client_id, self.username, self.password]):
            logger.error("Missing credentials")
            return False

        logger.info("Authenticating...")
        resp = requests.post(
            self.AUTH_URL,
            data={
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "client_id": self.client_id,
                "scope": "trapi",
                "takeExclusiveSignOnControl": "true",
            }
        )
        if resp.status_code == 200:
            self.access_token = resp.json()["access_token"]
            return True
        logger.error(f"Auth failed: {resp.text}")
        return False

    def test_segments(self):
        if not self.authenticate():
            return

        endpoint = "/data/datagrid/beta1/"
        url = f"{self.BASE_URL}{endpoint}"

        # Test fields from rdp_client.py
        fields = [
            "TR.BGS.BusSegmentName",
            "TR.BGS.BusSegmentRevenue",
            "TR.BGS.BusSegmentRevenuePct",
            "TR.BGS.BusSegmentOperatingIncome"
        ]

        payload = {
            "universe": ["AAPL.O"],
            "fields": fields
        }

        logger.info(f"Testing Segment Fields: {fields}")

        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            json=payload
        )

        if resp.status_code == 200:
            data = resp.json()
            if "error" in data:
                logger.error(f"❌ API Error: {json.dumps(data['error'], indent=2)}")
            else:
                logger.info("✅ SUCCESS! Segment data received:")
                print(json.dumps(data, indent=2))
        else:
            logger.error(f"❌ HTTP Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    SegmentTester().test_segments()
