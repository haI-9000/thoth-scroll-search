# thoth-scroll-search

Parallel, free surface growing for the Vesuvius Challenge on GitHub Actions.

Each run builds VC3D from [ScrollPrize/villa](https://github.com/ScrollPrize/villa) at commit `a4979b99004934955784ea19b30da66cfe5f9ead` (the VC3D used for the PHerc. 0306B First Letters claim), then grows one surface per seed in parallel with that team's published GrowPatch recipe (step 20, minimum 0.5 cm², generations capped at 70). It runs on the organisers' public m7 surface predictions and normal grids, read directly from the Vesuvius Challenge open-data bucket, so nothing is bulk-downloaded.

| Path | What it is |
|---|---|
| `.github/workflows/pherc0175a-parallel-grow.yml` | build job + 16-seed grow matrix (PHerc. 0175A, z 6144) |
| `seeds/seeds_z6144.json` | sheet-crossing proposals from one level-3 slice of the PHerc. 0175A m7 prediction (8 rays from the predicted-sheet centroid). These are proposals, not certified windings. |
| `seeds/batch1_seeds.json` | the 16 batch seeds: every 5th crossing on ray 0, snapped to a level-0 predicted-sheet voxel |
| `tools/pick_seeds.py`, `tools/snap_seed.py` | how those seed files were made (anonymous HTTP reads of the public prediction) |
| `tools/face_orientation_check.py` | which way a tifxyz mesh's render normal points relative to the scroll axis (the reading-face rule of the 0306B release) |

Each grow job uploads its mesh and log as an artifact. Status: exploratory. No text has been found or claimed.
