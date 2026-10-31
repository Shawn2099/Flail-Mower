#!/usr/bin/env python3
"""make_client_pack.py - non-technical client presentation pack.

This intentionally excludes the P-series fabrication sheets, including P-008
and P-009, and the BOM.  It is the pack to send to a client for a walk-through.
"""
import pathlib
from pypdf import PdfWriter

ROOT = pathlib.Path(__file__).resolve().parent
SHEETS = [
    ("ga_isometric", "Cover - isometric"),
    ("UCV2-GA-001", "GA-001 Side elevation"),
    ("UCV2-P-011", "P-011 Reading key"),
    ("UCV2-GA-002", "GA-002 Plan & end view"),
    ("UCV2-GA-005", "GA-005 Top view - side plates"),
    ("UCV2-GA-004", "GA-004 Drive station"),
]
w = PdfWriter()
for stem, title in SHEETS:
    f = ROOT / (stem + ".pdf")
    if not f.exists():
        raise SystemExit("missing " + str(f))
    start = len(w.pages)
    w.append(str(f))
    w.add_outline_item(title, start)
w.add_metadata({"/Title": "UC-V2 client presentation pack",
                "/Author": "OpenCode",
                "/Subject": "Whole-machine presentation sheets"})
out = ROOT / "UCV2_CLIENT_PACK.pdf"
with open(out, "wb") as fh:
    w.write(fh)
print("wrote", out)
