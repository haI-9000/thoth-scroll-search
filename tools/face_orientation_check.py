"""Read-only: sign of render normal n = dP/dcol x dP/drow relative to the radial direction from the umbilicus.
Same arithmetic as 306B ink_lane.reading_face (central differences) plus np.gradient variant (render_segment.py)."""
import sys, json, numpy as np, tifffile
mesh, umb = sys.argv[1], sys.argv[2]
win = [int(v) for v in sys.argv[3].split(',')] if len(sys.argv) > 3 else None   # node r0,r1,c0,c1
P = np.stack([tifffile.imread(f'{mesh}/{c}.tif') for c in 'xyz'], -1).astype(np.float64)
bad = (P[..., 0] == -1) | ~np.isfinite(P).all(-1) | (P[..., 2] <= 0)
P[bad] = np.nan
d = json.load(open(umb)); cp = d['control_points'] if isinstance(d, dict) and 'control_points' in d else d
if isinstance(cp[0], dict): pts = sorted((p['z'], p['x'], p['y']) for p in cp)
else: pts = sorted((p[2], p[0], p[1]) for p in cp)
uz, ux, uy = (np.array(v, float) for v in zip(*pts))
n = np.cross(P[1:-1, 2:] - P[1:-1, :-2], P[2:, 1:-1] - P[:-2, 1:-1]); q = P[1:-1, 1:-1]
if win:
    r0, r1, c0, c1 = win; n = n[r0-1:r1-1, c0-1:c1-1]; q = q[r0-1:r1-1, c0-1:c1-1]
rad = np.stack([q[..., 0] - np.interp(q[..., 2], uz, ux), q[..., 1] - np.interp(q[..., 2], uz, uy), np.zeros(q.shape[:2])], -1)
s = np.sign((n * rad).sum(-1)); s = s[np.isfinite(s) & (s != 0)]
out = float((s > 0).mean())
print(json.dumps(dict(mesh=mesh, umb=umb, window_nodes=win, grid_shape=list(P.shape[:2]), n_vertices=int(s.size),
  frac_normal_points_AWAY_from_umbilicus=round(out, 4), umb_z_range=[float(uz.min()), float(uz.max())],
  mesh_z_range=[float(np.nanmin(q[..., 2])), float(np.nanmax(q[..., 2]))])))
