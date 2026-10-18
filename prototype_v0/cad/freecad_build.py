"""
freecad_build.py - import the prototype v0 chassis into FreeCAD and verify it.

This is the FreeCAD half of the check. build123d (build_v0_frame.py) is the
source of truth; this script re-reads the STEP it wrote and verifies it with a
different kernel path:

  1. explode the imported compound into individual solids
  2. match every solid to v0_parts.json by centroid, and check its size
     (catches a part silently missing, duplicated, or moved)
  3. interference check on all pairs - any pair sharing more than a sliver of
     VOLUME is a real clash (butting faces give zero volume and are fine)
  4. recompute the steel mass from FreeCAD's own volumes
  5. name, colour and group the parts, then save prototype_v0.FCStd

Run inside FreeCAD (GUI thread):
  exec(open('C:/Users/malliath/Desktop/matlab/prototype_v0/cad/freecad_build.py').read())
"""
import json
import os

import FreeCAD as App
import Part

CAD_DIR = r"C:/Users/malliath/Desktop/matlab/prototype_v0/cad"
STEP_FAB = os.path.join(CAD_DIR, "v0_frame.step").replace("\\", "/")
STEP_ASM = os.path.join(CAD_DIR, "v0_layout.step").replace("\\", "/")
MANIFEST = os.path.join(CAD_DIR, "v0_parts.json").replace("\\", "/")
OUT_FCSTD = os.path.join(CAD_DIR, "prototype_v0.FCStd").replace("\\", "/")

MATCH_TOL_MM = 0.20      # bbox-centre match tolerance
SIZE_TOL_MM = 0.05       # size agreement tolerance
CLASH_MIN_MM3 = 1.0      # above this a pair is a real interference
STEEL_KG_M3 = 7850.0

# Joints that are MEANT to share volume: welds, press fits, through-bores.
# Everything else sharing volume is a design clash and fails the check.
# Key = frozenset of the two part names, value = why.
#
# MfD pass (option B): this dictionary is now EMPTY, and that is the result we
# want. The old front axle was the only part on the machine that shared volume
# with anything - a O20 x 420 rod notched 320 mm through the front cross
# member's bottom wall. Replacing it with two short stubs in the corner
# brackets (and welding the guard tabs to the band's rim) means NOTHING is
# buried inside anything else any more: every joint is a butt, lap or flush fit
# that the check sees as zero volume. If a future edit reintroduces a buried
# part, this check now fails loudly instead of being waved through.
INTENDED_JOINTS: dict = {}

_fails = []


def gate(name, ok, detail=""):
    if not ok:
        _fails.append(name)
    tail = f"  {detail}" if detail else ""
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{tail}")


def info(name, detail):
    print(f"  [info] {name}  {detail}")


def shape_metrics(shape):
    """bbox centre, size and volume of a solid, in mm / mm3.

    Uses the bbox centre, NOT CenterOfMass: a part with an off-centre hole
    (the deck's wiring grommet) has a centroid that shifts away from the
    manifest bbox centre and would never match.
    """
    bb = shape.BoundBox
    return (((bb.XMin + bb.XMax) / 2.0,
             (bb.YMin + bb.YMax) / 2.0,
             (bb.ZMin + bb.ZMax) / 2.0),
            (bb.XLength, bb.YLength, bb.ZLength),
            shape.Volume)


print("=" * 68)
print(" PROTOTYPE V0 - FREECAD VERIFICATION")
print("=" * 68)
print(f"FreeCAD {App.Version()[0]}.{App.Version()[1]}.{App.Version()[2]}  |  "
      f"CAD dir {CAD_DIR}")

# ---------------------------------------------------------------- manifest
with open(MANIFEST) as fh:
    manifest = json.load(fh)
parts_meta = manifest["parts"]
print(f"\nmanifest: {manifest['n_parts']} parts "
      f"({sum(1 for p in parts_meta if p['group'] == 'fabricated')} fabricated, "
      f"{sum(1 for p in parts_meta if p['group'] == 'bought')} bought)")

# expected centroids from the manifest bboxes
for p in parts_meta:
    lo, hi = p["bbox_min"], p["bbox_max"]
    p["_centroid"] = tuple((lo[i] + hi[i]) / 2.0 for i in range(3))
    p["_size"] = tuple(hi[i] - lo[i] for i in range(3))

# ------------------------------------------------------------------ import
for name in ("prototype_v0",):
    if name in [d.Name for d in App.listDocuments().values()]:
        App.closeDocument(name)
doc = App.newDocument("prototype_v0")
doc.Label = "prototype v0 - 775/nylon-line cart"

asm_shape = Part.Shape()
asm_shape.read(STEP_ASM)
fab_shape = Part.Shape()
fab_shape.read(STEP_FAB)

solids = list(asm_shape.Solids)
print(f"\nimported v0_layout.step : {len(solids)} solids, "
      f"{asm_shape.Volume / 1000.0:.1f} cm3 bounding "
      f"{asm_shape.BoundBox.XLength:.0f} x {asm_shape.BoundBox.YLength:.0f} x "
      f"{asm_shape.BoundBox.ZLength:.0f} mm")
print(f"imported v0_frame.step  : {len(fab_shape.Solids)} solids, "
      f"{fab_shape.Volume / 1000.0:.1f} cm3")

# ------------------------------------------------- match solids to manifest
print("\nPART MATCH (centroid within %.2f mm, size within %.2f mm)"
      % (MATCH_TOL_MM, SIZE_TOL_MM))
matched, unmatched = {}, []
for i, sol in enumerate(solids):
    cen, size, vol = shape_metrics(sol)
    best, best_d = None, 1e9
    for p in parts_meta:
        d = sum((cen[k] - p["_centroid"][k]) ** 2 for k in range(3)) ** 0.5
        if d < best_d:
            best, best_d = p, d
    if best is None or best_d > MATCH_TOL_MM or best["name"] in matched:
        unmatched.append((i, cen, size))
        continue
    matched[best["name"]] = (sol, size, vol, best_d)

missing = [p["name"] for p in parts_meta if p["name"] not in matched]
size_bad = []
for p in parts_meta:
    if p["name"] not in matched:
        continue
    _, size, _, _ = matched[p["name"]]
    worst = max(abs(size[k] - p["_size"][k]) for k in range(3))
    if worst > SIZE_TOL_MM:
        size_bad.append((p["name"], p["_size"], size, worst))

gate(f"every imported solid matched a manifest part",
     not unmatched, f"{len(unmatched)} unmatched" if unmatched else "")
gate(f"every manifest part found in the STEP", not missing,
     f"missing: {missing}" if missing else "")
gate("every part size agrees with the manifest", not size_bad,
     "; ".join(f"{n} {e} vs {g}" for n, e, g, _ in size_bad) if size_bad else "")

worst_d = max((m[3] for m in matched.values()), default=0.0)
info("worst centroid match", f"{worst_d:.3f} mm")

# -------------------------------------------------------------- interference
print("\nINTERFERENCE (pairs sharing measurable volume)")
names = sorted(matched.keys())
clashes, joints, touching, pairs = [], [], 0, 0
for a in range(len(names)):
    for b in range(a + 1, len(names)):
        bb_a = matched[names[a]][0].BoundBox
        bb_b = matched[names[b]][0].BoundBox
        if not bb_a.intersect(bb_b):       # bbox prune
            continue
        pairs += 1
        common = matched[names[a]][0].common(matched[names[b]][0])
        v = common.Volume if common is not None else 0.0
        if v <= 1e-6:
            continue
        why = INTENDED_JOINTS.get(frozenset((names[a], names[b])))
        if why and v > CLASH_MIN_MM3:
            joints.append((names[a], names[b], v, why))
        elif v > CLASH_MIN_MM3:
            clashes.append((names[a], names[b], v))
        else:
            touching += 1
for a, b, v, why in joints:
    info(f"intended joint {a} <-> {b}", f"{v:.0f} mm3 - {why}")
gate("no UNINTENDED volume interference between any two parts", not clashes,
     "" if not clashes else "; ".join(f"{a}<->{b} {v:.1f} mm3" for a, b, v in clashes))
info("bbox-overlapping pairs tested", f"{pairs}")
info("intended joints (whitelisted)", f"{len(joints)}")
info("pairs touching, zero volume (butt/flush fits)", f"{touching}")

# --------------------------------------------------------------------- mass
steel_vol = sum(m[2] for n, m in matched.items()
                if next(p for p in parts_meta if p["name"] == n)["group"] == "fabricated")
m_steel = steel_vol * STEEL_KG_M3 * 1e-9
manifest_steel = sum(p["volume_mm3"] for p in parts_meta
                     if p["group"] == "fabricated") * STEEL_KG_M3 * 1e-9
gate("FreeCAD steel mass agrees with the manifest",
     abs(m_steel - manifest_steel) < 0.02,
     f"FreeCAD {m_steel:.2f} kg vs manifest {manifest_steel:.2f} kg")

# --------------------------------------------------- build the FreeCAD doc
grp = {g: doc.addObject("App::DocumentObjectGroup", g)
       for g in ("fabricated", "bought")}
grp["fabricated"].Label = "fabricated (steel)"
grp["bought"].Label = "bought (wheels, 775, hub)"

COLOR = {"fabricated": (0.62, 0.63, 0.66),
         "wheel": (0.16, 0.17, 0.19),
         "motor_775": (0.78, 0.60, 0.18),
         "hub_D50": (0.85, 0.45, 0.10)}
TRANSPARENT = {"deck": 55}

for name in names:
    meta = next(p for p in parts_meta if p["name"] == name)
    obj = doc.addObject("Part::Feature", name)
    obj.Label = name
    obj.Shape = matched[name][0]
    grp[meta["group"]].addObject(obj)
    vo = getattr(obj, "ViewObject", None)      # absent when run headless
    if vo is not None:
        if meta["group"] == "fabricated":
            vo.ShapeColor = COLOR["fabricated"]
        elif "wheel" in name:
            vo.ShapeColor = COLOR["wheel"]
        else:
            vo.ShapeColor = COLOR.get(name, (0.5, 0.5, 0.5))
        if name in TRANSPARENT:
            vo.Transparency = TRANSPARENT[name]

doc.recompute()
doc.saveAs(OUT_FCSTD)
info("document objects", f"{len(doc.Objects)} (inc. 2 groups)")
info("saved", OUT_FCSTD)

print("\n" + "=" * 68)
print(f" FREECAD VERIFY RESULT: "
      f"{'all checks PASS' if not _fails else str(len(_fails)) + ' FAILED: ' + ', '.join(_fails)}")
print("=" * 68)
if not _fails:
    print(" STEP matches the design: no missing, moved or clashing parts.")
