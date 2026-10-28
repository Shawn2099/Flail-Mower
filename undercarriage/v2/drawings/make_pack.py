#!/usr/bin/env python3
"""make_pack.py - merge the 14 A3 sheets into one bookmarked PDF."""
import pathlib
from pypdf import PdfWriter, PdfReader

ROOT = pathlib.Path(__file__).resolve().parent
SHEETS = [
    ("UCV2-GA-001", "GA-001 Side elevation"),
    ("UCV2-GA-002", "GA-002 Plan & end view"),
    ("UCV2-GA-003", "GA-003 Section A-A roller station"),
    ("UCV2-GA-004", "GA-004 Section B-B drive station"),
    ("UCV2-P-001", "P-001 Side plate"),
    ("UCV2-P-002", "P-002 Roller drum"),
    ("UCV2-P-003", "P-003 Idler disc"),
    ("UCV2-P-004", "P-004 Shaft & axle"),
    ("UCV2-P-005", "P-005 Sprocket & hub"),
    ("UCV2-P-006", "P-006 Chain drive & guard"),
    ("UCV2-P-007", "P-007 Frame & flanges"),
    ("UCV2-P-008", "P-008 Deck interface & lugs"),
    ("UCV2-P-009", "P-009 Tensioner & small parts"),
    ("UCV2-P-010", "P-010 Parts list / BOM"),
]
w = PdfWriter()
for stem, title in SHEETS:
    f = ROOT / (stem + ".pdf")
    if not f.exists():
        raise SystemExit("missing " + str(f))
    start = len(w.pages)
    w.append(str(f))
    w.add_outline_item(title, start)
w.add_metadata({"/Title": "UC-V2 undercarriage drawing pack",
                "/Author": "OpenCode", "/Subject": "A3 general arrangement + part drawings"})
out = ROOT / "UCV2_DRAWING_PACK.pdf"
with open(out, "wb") as fh:
    w.write(fh)
print("wrote", out, len(w.pages), "pages")
