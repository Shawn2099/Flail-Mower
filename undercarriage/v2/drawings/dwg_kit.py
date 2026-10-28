#!/usr/bin/env python3
"""dwg_kit.py - minimal A3 engineering-drawing kit on matplotlib.

Units are millimetres on the sheet: A3 = 420 x 297.  Views are placed with a
scale and draw in model mm, so a dimension reads the true model value.
"""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Rectangle
import ezdxf

plt.rcParams["hatch.linewidth"] = 0.35
plt.rcParams["font.family"] = "DejaVu Sans"

W, H = 420.0, 297.0
LW = {"out": 1.5, "thin": 0.7, "hid": 0.7, "dim": 0.55, "cen": 0.55}
FS = 8.0


def _unit(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


class View:
    def __init__(self, sheet, scale, ox, oy, label=None, label_at=None):
        self.sheet, self.s, self.ox, self.oy = sheet, scale, ox, oy
        self.ax = sheet.ax
        if label:
            x, y = label_at if label_at else (ox, oy - 12)
            self.ax.text(x, y, label, fontsize=FS + 1, weight="bold",
                         ha="left", va="top")

    def P(self, x, y):
        return self.ox + x * self.s, self.oy + y * self.s

    def line(self, x1, y1, x2, y2, style="out", color="k", z=2):
        p, q = self.P(x1, y1), self.P(x2, y2)
        self.ax.plot([p[0], q[0]], [p[1], q[1]], color=color,
                     lw=LW[style], solid_capstyle="round", zorder=z)

    def poly(self, pts, close=False, style="out", color="k", z=2, fill=None,
             hatch=None):
        xy = [self.P(x, y) for x, y in pts]
        if close:
            xy = xy + [xy[0]]
        if fill is not None or hatch:
            self.ax.add_patch(Polygon(xy, closed=close, facecolor=fill or "none",
                                      edgecolor=color, lw=LW[style], hatch=hatch,
                                      zorder=z))
        else:
            xs, ys = zip(*xy)
            self.ax.plot(xs, ys, color=color, lw=LW[style], zorder=z)

    def circle(self, cx, cy, r, style="out", color="k", z=2, fill=None):
        c = self.P(cx, cy)
        self.ax.add_patch(Circle(c, r * self.s, facecolor=fill or "none",
                                 edgecolor=color, lw=LW[style], zorder=z))

    def rect(self, x, y, w, h, style="out", color="k", z=2, hatch=None,
             fill=None):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                  close=True, style=style, color=color, z=z, hatch=hatch,
                  fill=fill)

    def text(self, x, y, s, size=FS, ha="center", va="center", color="k",
             rot=0, weight="normal"):
        X, Y = self.P(x, y)
        self.ax.text(X, Y, s, fontsize=size, ha=ha, va=va, color=color,
                     rotation=rot, weight=weight, zorder=6)

    def center(self, x, y, r, style="cen"):
        self.circle(x, y, r, style=style)
        self.line(x - r * 1.15, y, x + r * 1.15, y, style)
        self.line(x, y - r * 1.15, x, y + r * 1.15, style)

    def centerline_pts(self, pts, style="cen"):
        for i in range(0, len(pts) - 1, 2):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], style)

    # ---------- arrows / dimensions ----------
    def _arrow(self, tip, direction, size=3.0):
        dx, dy = direction
        n = math.hypot(dx, dy) or 1.0
        dx, dy = dx / n, dy / n
        px, py = -dy, dx
        a = (tip[0] - dx * size, tip[1] - dy * size)
        b = (tip[0] - dx * size * 0.55 + px * size * 0.28,
             tip[1] - dy * size * 0.55 + py * size * 0.28)
        c = (tip[0] - dx * size * 0.55 - px * size * 0.28,
             tip[1] - dy * size * 0.55 - py * size * 0.28)
        self.ax.add_patch(Polygon([tip, b, c], closed=True, fc="k", ec="k",
                                  lw=0, zorder=7))

    def dim_h(self, x1, x2, y, text=None, off=7, color="k"):
        off = off / self.s
        y0 = y + off
        self.line(x1, y + 1, x1, y0 + 2, "dim", color)
        self.line(x2, y + 1, x2, y0 + 2, "dim", color)
        self.line(x1, y0, x2, y0, "dim", color)
        self._arrow(self.P(x2, y0), (-1, 0))
        self._arrow(self.P(x1, y0), (1, 0))
        s = text if text is not None else f"{abs(x2 - x1):.1f}"
        X, Y = self.P((x1 + x2) / 2, y0)
        self.ax.text(X, Y + 1.2, s, fontsize=FS, ha="center", va="bottom",
                     bbox=dict(fc="white", ec="none", pad=0.4), zorder=8)

    def dim_v(self, x, y1, y2, text=None, off=7, color="k"):
        off = off / self.s
        x0 = x + off
        self.line(x + 1, y1, x0 + 2, y1, "dim", color)
        self.line(x + 1, y2, x0 + 2, y2, "dim", color)
        self.line(x0, y1, x0, y2, "dim", color)
        self._arrow(self.P(x0, y2), (0, -1))
        self._arrow(self.P(x0, y1), (0, 1))
        s = text if text is not None else f"{abs(y2 - y1):.1f}"
        X, Y = self.P(x0, (y1 + y2) / 2)
        self.ax.text(X - 1.5, Y, s, fontsize=FS, ha="right", va="center",
                     rotation=90, bbox=dict(fc="white", ec="none", pad=0.4),
                     zorder=8)

    def dim(self, p1, p2, text, off=7, side=1):
        """Aligned dimension between two model points, offset normal by off mm."""
        off = off / self.s
        dx, dy = _unit(p1, p2)
        nx, ny = -dy * side, dx * side
        q1 = (p1[0] + nx * off, p1[1] + ny * off)
        q2 = (p2[0] + nx * off, p2[1] + ny * off)
        self.line(p1[0], p1[1], q1[0] + nx * 2, q1[1] + ny * 2, "dim")
        self.line(p2[0], p2[1], q2[0] + nx * 2, q2[1] + ny * 2, "dim")
        self.line(q1[0], q1[1], q2[0], q2[1], "dim")
        self._arrow(self.P(*q2), (-dx, -dy))
        self._arrow(self.P(*q1), (dx, dy))
        mx, my = (q1[0] + q2[0]) / 2, (q1[1] + q2[1]) / 2
        X, Y = self.P(mx, my)
        ang = math.degrees(math.atan2(dy, dx))
        if ang > 90 or ang < -90:
            ang += 180
        self.ax.text(X + nx * 1.2, Y + ny * 1.2, text, fontsize=FS,
                     ha="center", va="center", rotation=ang,
                     bbox=dict(fc="white", ec="none", pad=0.4), zorder=8)

    def leader(self, px, py, tx, ty, text, ha="left", arrow=True):
        self.line(px, py, tx, ty, "dim")
        if arrow:
            self._arrow(self.P(px, py), _unit((tx, ty), (px, py)))
        X, Y = self.P(tx, ty)
        self.ax.text(X, Y, text, fontsize=FS, ha=ha, va="center", zorder=8)

    def dia(self, cx, cy, r, text, ang=45, ext=8):
        ext = ext / self.s
        a = math.radians(ang)
        p = (cx + r * math.cos(a), cy + r * math.sin(a))
        q = (cx + (r + ext) * math.cos(a), cy + (r + ext) * math.sin(a))
        self.line(p[0], p[1], q[0], q[1], "dim")
        self._arrow(self.P(*p), (math.cos(a), math.sin(a)))
        X, Y = self.P(*q)
        self.ax.text(X, Y, text, fontsize=FS, ha="left" if math.cos(a) >= 0 else "right",
                     va="center", zorder=8)

    def balloon(self, px, py, tx, ty, num):
        self.line(px, py, tx, ty, "dim")
        self._arrow(self.P(px, py), _unit((tx, ty), (px, py)))
        X, Y = self.P(tx, ty)
        self.ax.add_patch(Circle((X, Y), 4.2, fc="white", ec="k", lw=0.8, zorder=8))
        self.ax.text(X, Y, str(num), fontsize=FS, ha="center", va="center",
                     weight="bold", zorder=9)

    def hatch_rect(self, x, y, w, h, angle="///"):
        self.rect(x, y, w, h, style="thin", hatch=angle)

    def hatch_poly(self, pts, angle="///"):
        self.poly(pts, close=True, style="thin", hatch=angle)

    # ---------- DXF ----------
    def dxf(self, path, dx=0.0, dy=0.0, style="out", scale=1.0):
        doc = ezdxf.readfile(path)
        for e in doc.modelspace():
            t = e.dxftype()
            if t == "LINE":
                a, b = e.dxf.start, e.dxf.end
                self.line(dx + a.x * scale, dy + a.y * scale,
                          dx + b.x * scale, dy + b.y * scale, style)
            elif t == "CIRCLE":
                c, r = e.dxf.center, e.dxf.radius
                self.circle(dx + c.x * scale, dy + c.y * scale, r * scale, style)
            elif t == "ARC":
                c, r = e.dxf.center, e.dxf.radius
                a0, a1 = e.dxf.start_angle, e.dxf.end_angle
                if a1 <= a0:
                    a1 += 360
                n = max(8, int((a1 - a0) / 4) + 1)
                pts = [(dx + c.x * scale + r * scale * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                        dy + c.y * scale + r * scale * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
                       for i in range(n + 1)]
                self.poly(pts, close=False, style=style)
            elif t == "LWPOLYLINE":
                pts = [(dx + p[0] * scale, dy + p[1] * scale) for p in e.get_points("xy")]
                self.poly(pts, close=e.closed, style=style)


class Sheet:
    def __init__(self, no, title, sheet_idx, sheet_total, scale="1:5",
                 material="-", qty="-", mass="-", rev="A", notes=None,
                 subtitle=""):
        self.no, self.title = no, title
        self.fig = plt.figure(figsize=(W / 25.4, H / 25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(0, H)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.border()
        self.title_block(sheet_idx, sheet_total, scale, material, qty, mass,
                         rev, subtitle)
        self.notes = notes or []
        self.notes_block()
        self.drawn = []

    # ---------- frame / blocks ----------
    def border(self):
        a = self.ax
        a.add_patch(Rectangle((10, 10), 400, 277, fill=False, ec="k", lw=1.6))
        a.add_patch(Rectangle((10, 10), 400, 277, fill=False, ec="k", lw=0.5,
                              ls=(0, (12, 3, 2, 3))))
        # zones
        for i, x in enumerate(range(10, 411, 50)):
            a.text(x + 25, 289, str(i + 1), fontsize=6, ha="center", va="center")
        for i, y in enumerate(range(10, 288, 50)):
            a.text(5, y + 25, chr(65 + i), fontsize=6, ha="center", va="center")

    def title_block(self, idx, total, scale, material, qty, mass, rev, subtitle):
        a = self.ax
        x0, y0, w, h = 220, 10, 190, 48
        a.add_patch(Rectangle((x0, y0), w, h, fill=False, ec="k", lw=1.2))
        a.plot([x0, x0 + w], [y0 + 30, y0 + 30], color="k", lw=0.8)
        a.plot([x0, x0 + w], [y0 + 16, y0 + 16], color="k", lw=0.8)
        a.plot([x0 + 115, x0 + 115], [y0 + 16, y0 + 48], color="k", lw=0.8)
        a.plot([x0 + 60, x0 + 60], [y0, y0 + 16], color="k", lw=0.8)
        a.plot([x0 + 140, x0 + 140], [y0, y0 + 16], color="k", lw=0.8)
        a.text(x0 + 3, y0 + 43, "FLAIL MOWER 500  /  UC-V2", fontsize=7,
               weight="bold", va="center")
        a.text(x0 + 3, y0 + 36, self.title, fontsize=10, weight="bold", va="center")
        if subtitle:
            a.text(x0 + 3, y0 + 32.5, subtitle, fontsize=6.2, va="center")
        a.text(x0 + 118, y0 + 43, "DWG No.", fontsize=5.5, va="center")
        a.text(x0 + 118, y0 + 38, self.no, fontsize=11, weight="bold", va="center")
        a.text(x0 + 118, y0 + 33, f"REV {rev}", fontsize=6.5, va="center")
        # row 2
        a.text(x0 + 3, y0 + 24, "MATERIAL", fontsize=5, va="center")
        a.text(x0 + 3, y0 + 19.5, material, fontsize=7, va="center")
        a.text(x0 + 63, y0 + 24, "QTY / MASS", fontsize=5, va="center")
        a.text(x0 + 63, y0 + 19.5, f"{qty}   /   {mass}", fontsize=7, va="center")
        # row 3
        a.text(x0 + 3, y0 + 10, "SCALE", fontsize=5, va="center")
        a.text(x0 + 3, y0 + 5, scale, fontsize=7, va="center")
        a.text(x0 + 63, y0 + 10, "SIZE", fontsize=5, va="center")
        a.text(x0 + 63, y0 + 5, "A3", fontsize=7, va="center")
        a.text(x0 + 78, y0 + 10, "SHEET", fontsize=5, va="center")
        a.text(x0 + 78, y0 + 5, f"{idx} / {total}", fontsize=7, va="center")
        a.text(x0 + 143, y0 + 10, "DATE", fontsize=5, va="center")
        a.text(x0 + 143, y0 + 5, "2026-10-29", fontsize=7, va="center")
        a.text(x0 + 170, y0 + 10, "DRAWN", fontsize=5, va="center")
        a.text(x0 + 170, y0 + 5, "OC", fontsize=7, va="center")
        # projection symbol (first angle)
        cx, cy = x0 + 178, y0 + 40
        a.add_patch(Circle((cx, cy), 3.2, fill=False, ec="k", lw=0.6))
        a.plot([cx - 6, cx + 6], [cy - 1.2, cy - 1.2], color="k", lw=0.6)
        a.plot([cx - 2, cx + 6], [cy, cy], color="k", lw=0.6)
        a.plot([cx - 6, cx + 6], [cy + 1.2, cy + 1.2], color="k", lw=0.6)

    def notes_block(self):
        if not self.notes:
            return
        a = self.ax
        x0, y0, w = 12, 10, 204
        n = len(self.notes)
        h = 8 + 4.3 * n
        a.add_patch(Rectangle((x0, y0), w, h, fill=False, ec="k", lw=0.8))
        a.text(x0 + 2, y0 + h - 5, "NOTES", fontsize=6, weight="bold", va="center")
        for i, s in enumerate(self.notes):
            a.text(x0 + 2, y0 + h - 10 - 4.3 * i, s, fontsize=6.4, va="center")

    def section_line(self, p1, p2, label, view_dir=1):
        """Section cut line with arrows; p1/p2 model points."""
        self.ax.plot(*zip(self._P(p1), self._P(p2)), color="k", lw=0.9,
                     ls=(0, (10, 2, 2, 2)))
        dx, dy = _unit(p1, p2)
        for p, s in ((p1, -1), (p2, 1)):
            tip = self._P(p)
            n = (-dy * view_dir, dx * view_dir)
            self.ax.annotate("", xy=(tip[0] + n[0] * 7, tip[1] + n[1] * 7),
                             xytext=tip, arrowprops=dict(arrowstyle="-|>", lw=0.9))
            self.ax.text(tip[0] + n[0] * 9, tip[1] + n[1] * 9, label,
                         fontsize=10, weight="bold", ha="center", va="center")

    def _P(self, p):
        return p if len(p) == 2 and p[0] > 10 else p

    def save(self, path_base):
        path_base = str(path_base)
        self.fig.savefig(path_base + ".pdf", format="pdf")
        self.fig.savefig(path_base + ".png", dpi=110)
        plt.close(self.fig)
