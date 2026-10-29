#!/usr/bin/env python3
"""build_v3_simple.py - simple pipe + backplate + welded bearing seat + loose spacer.

No Loctite, no ring stacks.
  drum = pipe + inner backplate + welded 65/52 bearing seat (bearing at tread centre)
  two identical drums at +-62 on a Ø25 shaft
  loose 42.4/35.5 spacer between the bearing inner races
  open outer pipe end (debris cap optional)

Outputs: v3_roller.step, v3_idler.step, section PNGs, masses.
"""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from build123d import (Align, Axis, Compound, Cylinder, Location,
                       export_step, export_stl)

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "drawings"
RHO = 7850e-9  # kg/mm3

DRUM_W = 40.0
BACK_T = 6.0
SEAT_OD, SEAT_ID = 65.0, 52.0
SEAT_L = 22.0
BRG_OD, BRG_ID, BRG_W = 52.0, 25.0, 15.0
SP_OD, SP_ID = 42.4, 35.5
SP_L = 109.0
SHAFT_D, SHAFT_L = 25.0, 260.0
DRUM_C = 62.0


def tube(od, id_, h):
    return (Cylinder(od / 2, h, align=(Align.CENTER, Align.CENTER, Align.CENTER)) -
            Cylinder(id_ / 2, h, align=(Align.CENTER, Align.CENTER, Align.CENTER)))


def drum_solid(od, id_):
    pipe = tube(od, id_, DRUM_W).moved(Location((0, 0, DRUM_W / 2)))
    back = tube(id_, SEAT_OD, BACK_T).moved(Location((0, 0, BACK_T / 2)))
    seat = tube(SEAT_OD, SEAT_ID, SEAT_L).moved(
        Location((0, 0, BACK_T + SEAT_L / 2)))
    return pipe + back + seat


def make_drum(od, id_, y_inner, sign):
    drum = drum_solid(od, id_)
    drum = drum.rotate(Axis.X, 90 if sign < 0 else -90)
    return drum.moved(Location((0, y_inner, 0)))


def make_bearing(yc):
    outer = tube(BRG_OD, 40.0, BRG_W)
    inner = tube(32.0, BRG_ID, BRG_W)
    return (outer + inner).rotate(Axis.X, 90).moved(Location((0, yc, 0)))


def build(od, id_, tag):
    parts = {
        "right drum": make_drum(od, id_, -42.0, -1),
        "left drum": make_drum(od, id_, +42.0, +1),
        "bearing R": make_bearing(-DRUM_C),
        "bearing L": make_bearing(+DRUM_C),
        "spacer": tube(SP_OD, SP_ID, SP_L).rotate(Axis.X, 90),
        "shaft": Cylinder(SHAFT_D / 2, SHAFT_L,
                          align=(Align.CENTER, Align.CENTER, Align.CENTER)
                          ).rotate(Axis.X, 90),
    }
    for k, p in parts.items():
        export_stl(p, str(ROOT / f"v3_{tag}_{k.replace(' ', '_')}.stl"),
                   tolerance=0.2, angular_tolerance=0.2)
    export_step(Compound(children=list(parts.values())),
                str(ROOT / f"v3_{tag}.step"))
    mass = {k: round(p.volume * RHO, 3) for k, p in parts.items()}
    return parts, mass


def section(ax, leg, od, id_, title, mass, horn_z=None, horn_txt=""):
    hw, iw = od / 2, id_ / 2
    for s in (-1, 1):
        xa, xb = sorted((s * 42, s * 82))
        for z0, h in ((iw, hw - iw), (-hw, hw - iw)):
            ax.add_patch(Rectangle((xa, z0), 40, h, facecolor="none",
                                   edgecolor="k", hatch="////", lw=0.8))
        xa, xb = sorted((s * 42, s * 48))
        for z0, h in ((32.5, iw - 32.5), (-iw, iw - 32.5)):
            ax.add_patch(Rectangle((xa, z0), 6, h, facecolor="none",
                                   edgecolor="k", hatch="\\\\\\\\", lw=0.8))
        xa, xb = sorted((s * 48, s * 70))
        for z0, h in ((26, 6.5), (-32.5, 6.5)):
            ax.add_patch(Rectangle((xa, z0), 22, h, facecolor="none",
                                   edgecolor="k", hatch="xxxx", lw=0.8))
        xa, xb = sorted((s * 54.5, s * 69.5))
        for z0, h in ((12.5, 13.5), (-26, 13.5)):
            ax.add_patch(Rectangle((xa, z0), 15, h, facecolor="0.86",
                                   edgecolor="k", lw=0.8))
    for z0, h in ((17.75, 3.45), (-21.2, 3.45)):
        ax.add_patch(Rectangle((-54.5, z0), 109, h, facecolor="none",
                               edgecolor="k", hatch="....", lw=0.8))
    ax.add_patch(Rectangle((-130, -12.5), 260, 25, facecolor="0.65",
                           edgecolor="k", lw=0.8))
    ax.plot([-135, 135], [0, 0], "k-.", lw=0.6)
    if horn_z is not None:
        ax.plot([-42, 42], [horn_z, horn_z], "r--", lw=0.9)
        ax.text(0, horn_z - 4, horn_txt, color="r", ha="center", va="top",
                fontsize=7.5)
    ax.annotate("", xy=(-82, hw + 12), xytext=(82, hw + 12),
                arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(0, hw + 14, "164 overall", ha="center", fontsize=8)
    ax.annotate("", xy=(-62, hw + 26), xytext=(62, hw + 26),
                arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(0, hw + 28, "124 drum centres", ha="center", fontsize=8)
    ax.annotate("", xy=(-82, -hw - 12), xytext=(-42, -hw - 12),
                arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(-62, -hw - 16, "40", ha="center", fontsize=8)
    ax.annotate("", xy=(-48, -hw - 26), xytext=(-42, -hw - 26),
                arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(-45, -hw - 30, "6", ha="center", fontsize=8)
    ax.annotate("", xy=(-70, -hw - 40), xytext=(-48, -hw - 40),
                arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(-59, -hw - 44, "22 seat", ha="center", fontsize=8)
    ax.annotate("", xy=(-54.5, hw + 40), xytext=(54.5, hw + 40),
                arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(0, hw + 42, "109 spacer", ha="center", fontsize=8)

    def lead(x, z, px, pz, n):
        ax.annotate("", xy=(px, pz), xytext=(x, z),
                    arrowprops=dict(arrowstyle="->", lw=0.7, shrinkA=5))
        ax.add_patch(Circle((x, z), 4.6, fc="white", ec="k", lw=0.9, zorder=10))
        ax.text(x, z, str(n), fontsize=9, weight="bold", ha="center",
                va="center", zorder=11)

    lead(-145, hw - 6, -70, hw - 2, 1)
    lead(-145, 42, -45, 42, 2)
    lead(-145, 30, -59, 29, 3)
    lead(-145, 18, -62, 19, 4)
    lead(145, 19, 0, 19.5, 5)
    lead(145, 0, 0, 6, 6)
    lead(145, hw - 6, 82, hw - 2, 7)
    ax.set_aspect("equal")
    ax.set_xlim(-165, 165)
    ax.set_ylim(-hw - 55, hw + 55)
    ax.axis("off")
    ax.set_title(title, fontsize=11, weight="bold")

    leg.axis("off")
    leg.set_xlim(0, 1)
    leg.set_ylim(0, 1)
    leg.text(0.02, 0.98, title.split("  ")[0], fontsize=10, weight="bold",
             va="top")
    entries = [
        ("1", "PIPE Ø%.1f × %.1f wall × 40" % (od, (od - id_) / 2)),
        ("2", "BACKPLATE 6, welded inside pipe"),
        ("3", "BEARING SEAT 65/52 × 22,\n     welded to backplate, 52H7"),
        ("4", "6205-2RS (25 × 52 × 15), press fit"),
        ("5", "SPACER 42.4/35.5 × 109, loose,\n     between bearing inner races"),
        ("6", "SHAFT Ø25 × 260, press fit\n     (no Loctite)"),
        ("7", "OPEN OUTER END (cap optional)"),
    ]
    y = 0.88
    for n, txt in entries:
        leg.text(0.02, y, n, fontsize=9, weight="bold", va="top")
        leg.text(0.10, y, txt, fontsize=7.6, va="top")
        y -= 0.105
    leg.text(0.02, 0.14, "Two identical drums at ±62.\nMass %.2f kg/station.\n"
             "No Loctite. No ring stack." % mass, fontsize=8, va="top")


def figure(od, id_, title, mass, fname, horn_z=None, horn_txt=""):
    fig = plt.figure(figsize=(16, 8))
    gs = fig.add_gridspec(1, 2, width_ratios=[3.25, 1.0], wspace=0.02)
    section(fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]),
            od, id_, title, mass, horn_z, horn_txt)
    fig.savefig(OUT / fname, dpi=180, bbox_inches="tight")
    plt.close(fig)


export_step(drum_solid(114.3, 105.3), str(ROOT / "v3_roller_drum.step"))
export_step(drum_solid(200.0, 190.0), str(ROOT / "v3_idler_drum.step"))
export_step(tube(SP_OD, SP_ID, SP_L), str(ROOT / "v3_spacer.step"))

mass_r, mr = build(114.3, 105.3, "roller")
mass_i, mi = build(200.0, 190.0, "idler")
print("roller masses", mr, "total", round(sum(mr.values()), 2))
print("idler masses", mi, "total", round(sum(mi.values()), 2))

figure(114.3, 105.3, "ROLLER  Ø114.3 × 40 — one station, two identical drums",
       round(sum(mr.values()), 2), "v3_roller_section.png",
       horn_z=62.5 - 91.2, horn_txt="track horn tip\n7.5 mm below spacer")
figure(200.0, 190.0, "IDLER  Ø200 × 40 — one station, two identical drums",
       round(sum(mi.values()), 2), "v3_idler_section.png",
       horn_z=62.5 - 133.3, horn_txt="track horn tip\n49.6 mm below spacer")

(ROOT / "v3_mass.json").write_text(json.dumps({"roller": mr, "idler": mi}, indent=2))
print("wrote v3_roller_section.png / v3_idler_section.png")
