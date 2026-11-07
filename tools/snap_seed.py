"""snap_seed.py X Y Z [R=24] : move a seed onto the nearest predicted-sheet voxel of the PHerc0175A m7 prediction at level 0,
searching the z-slice within R voxels in-plane (the role of 306B sqm_grow.py's xsec snap; reimplemented, bounded reads only:
the one or few 192^3 level-0 chunks covering the window). Prints 'X Y Z dist' or 'NONE'."""
import sys, json, math, urllib.request
import numpy as np, numcodecs
U = ("https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/PHerc0175A/representations/predictions/surfaces/"
     "20250521115057-surface-20260413222639-surface-m7-L0-th0.2.zarr/0")
x, y, z = map(int, sys.argv[1:4]); R = int(sys.argv[4]) if len(sys.argv) > 4 else 24
meta = json.load(urllib.request.urlopen(U + "/.zarray")); C = meta['chunks'][0]; codec = numcodecs.get_codec(meta['compressor'])
cz, oz = divmod(z, C); win = np.zeros((2 * R + 1, 2 * R + 1), np.uint8)
for cy in range((y - R) // C, (y + R) // C + 1):
    for cx in range((x - R) // C, (x + R) // C + 1):
        try: raw = urllib.request.urlopen(f"{U}/{cz}/{cy}/{cx}", timeout=60).read()
        except Exception: continue
        a = np.frombuffer(codec.decode(raw), np.uint8).reshape(C, C, C)[oz]
        for j in range(max(y - R, cy * C), min(y + R + 1, cy * C + C)):
            for i in range(max(x - R, cx * C), min(x + R + 1, cx * C + C)):
                win[j - (y - R), i - (x - R)] = a[j - cy * C, i - cx * C]
yy, xx = np.nonzero(win > 0)
if not len(yy): print("NONE"); sys.exit(0)
d = np.hypot(yy - R, xx - R); k = int(np.argmin(d))
print(int(xx[k] + x - R), int(yy[k] + y - R), z, round(float(d[k]), 2))
