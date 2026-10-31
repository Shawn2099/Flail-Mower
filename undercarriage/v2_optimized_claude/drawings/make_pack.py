#!/usr/bin/env python3
"""make_pack.py - merge the cover + approved sheets into one bookmarked PDF.

P-008 and P-009 are intentionally excluded from this client/final pack;
they remain shop-only sheets in the review folder.
"""
import pathlib
from pypdf import PdfWriter

ROOT = pathlib.Path(__file__).resolve().parent
SHEETS = [
    ("ga_isometric", "Cover - isometric"),
    ("UCV2-GA-001", "GA-001 Side elevation"),
    ("UCV2-P-011", "P-011 Reading key / definitions"),
    ("UCV2-GA-002", "GA-002 Plan & end view"),
    ("UCV2-GA-005", "GA-005 Top view - side plates"),
    ("UCV2-GA-004", "GA-004 Drive station"),
    ("UCV2-P-002", "P-002 Roller drum"),
    ("UCV2-P-003", "P-003 Idler drum"),
    ("UCV2-P-004", "P-004 Shaft & axle"),
    ("UCV2-P-005", "P-005 Sprocket & hub"),
    ("UCV2-P-006", "P-006 Chain drive"),
    ("UCV2-P-007", "P-007 Frame & flanges"),
    ("UCV2-P-001", "P-001 Side plate"),
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
                "/Author": "OpenCode",
                "/Subject": "A3 general arrangement + part drawings"})
out = ROOT / "UCV2_DRAWING_PACK.pdf"
with open(out, "wb") as fh:
    w.write(fh)
print("wrote", out)
