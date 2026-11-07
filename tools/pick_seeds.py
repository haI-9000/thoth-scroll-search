"""pick_seeds.py Z_L0 OUT.json [--rays 8] : seeds for GrowPatch on PHerc0175A from the organisers' m7 surface prediction.
Reads ONE level-3 (8x) xy slice of the prediction from the open-data bucket (anonymous HTTP, chunk by chunk), takes the
centroid of predicted-sheet pixels as an approximate scroll axis, casts rays from it and records every sheet crossing
(centre of each run of predicted pixels) as a level-0 seed (x*8+4, y*8+4, z). Writes seeds + per-ray winding counts."""
import sys, json, math, urllib.request
import numpy as np, numcodecs
U = ("https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/PHerc0175A/representations/predictions/surfaces/"
     "20250521115057-surface-20260413222639-surface-m7-L0-th0.2.zarr/3")
ZL0 = int(sys.argv[1]); OUT = sys.argv[2]; RAYS = int(sys.argv[sys.argv.index('--rays') + 1]) if '--rays' in sys.argv else 8
meta = json.load(urllib.request.urlopen(U + "/.zarray")); Zs, Ys, Xs = meta['shape']; C = meta['chunks'][0]
codec = numcodecs.get_codec(meta['compressor']); z3 = ZL0 // 8; cz, oz = divmod(z3, C)
sl = np.zeros((Ys, Xs), np.uint8); nbytes = 0
for cy in range(math.ceil(Ys / C)):
    for cx in range(math.ceil(Xs / C)):
        try: raw = urllib.request.urlopen(f"{U}/{cz}/{cy}/{cx}", timeout=60).read()
        except Exception: continue                                   # missing chunk = fill value 0
        nbytes += len(raw); a = np.frombuffer(codec.decode(raw), np.uint8).reshape(C, C, C)
        h, w = min(C, Ys - cy * C), min(C, Xs - cx * C); sl[cy * C:cy * C + h, cx * C:cx * C + w] = a[oz, :h, :w]
m = sl > 0; yy, xx = np.nonzero(m)
cy0, cx0 = float(yy.mean()), float(xx.mean())
seeds, rays = [], []
for k in range(RAYS):
    th = 2 * math.pi * k / RAYS; r = np.arange(0, max(Ys, Xs))
    py = np.round(cy0 + r * math.sin(th)).astype(int); px = np.round(cx0 + r * math.cos(th)).astype(int)
    ok = (py >= 0) & (py < Ys) & (px >= 0) & (px < Xs); py, px, r = py[ok], px[ok], r[ok]
    v = m[py, px].astype(np.int8); d = np.diff(np.r_[0, v, 0]); s, e = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
    cr = [(int(r[(a + b - 1) // 2]), int(px[(a + b - 1) // 2]) * 8 + 4, int(py[(a + b - 1) // 2]) * 8 + 4) for a, b in zip(s, e)]
    rays.append(dict(ray=k, theta_deg=round(math.degrees(th), 1), crossings=len(cr)))
    for i, (rr, x, y) in enumerate(cr): seeds.append(dict(ray=k, idx=i, radius_l3=rr, seed=[x, y, ZL0]))
json.dump(dict(z_l0=ZL0, level=3, slice_z_l3=z3, centroid_l0=[cx0 * 8 + 4, cy0 * 8 + 4], pred_px=int(m.sum()),
               bytes_fetched=nbytes, rays=rays, seeds=seeds), open(OUT, 'w'), indent=1)
print('bytes', nbytes, 'pred_px', int(m.sum()), 'centroid_l0', round(cx0 * 8), round(cy0 * 8), 'crossings per ray', [r['crossings'] for r in rays])
