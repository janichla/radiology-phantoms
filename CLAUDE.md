# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

Three standalone Python scripts that turn a CT DICOM series into 3D-printable organ molds:

1. **`dicom_to_nifti.py`** — reads a DICOM series (SimpleITK), resamples it to a fixed voxel spacing, writes `*_resampled.nii.gz`.
2. **`segment_organs.py`** — interactive terminal menu (category → organ) that runs TotalSegmentator on the resampled NIfTI and writes one binary mask per selected organ to `segmentations/`.
3. **`create_mold.py`** — for every mask in `segmentations/`, builds a hollow mold shell (dilate by wall thickness, subtract organ), splits it into two halves along the organ's shortest axis, adds a pin/socket alignment system at the split plane, and exports each half (plus the unsplit mold) as STL for 3D printing.

Pipeline: `DICOM folder → dicom_to_nifti.py → segment_organs.py → create_mold.py → STL halves → slice/print`. Load masks in 3D Slicer to inspect; slice STLs in PrusaSlicer/Cura to print. Prints are two-part negative molds: the halves separate at the pinned split plane to extract the cast shape.

## Running the scripts

There are no CLI arguments, config files, tests, or build steps — each script is run directly with `python <script>.py`, and all inputs/outputs are set via a `CONFIGURATION` block of constants near the top of the file (`DICOM_DIR`, `SEGMENTATION_DIR`, `OUTPUT_DIR`, `WALL_THICKNESS_MM`, pin dimensions, etc.). **Edit these constants in the script before running** — there's no other way to point them at different data.

```bash
.\venv\Scripts\activate        # every new terminal; venv lives in the project folder
python dicom_to_nifti.py       # step 1
python segment_organs.py       # step 2 (interactive menu)
python create_mold.py          # step 3, processes every .nii.gz in SEGMENTATION_DIR
```

The scripts hardcode a `C:\Users\Laura\Desktop\El_Phantom\data\...` path layout from the machine they were developed on — expect to update these per-machine/per-dataset. `dicom_to_nifti.py` and `segment_organs.py` derive their NIfTI/output paths from `DICOM_DIR`, so only that one constant needs editing there; `create_mold.py` has independent `SEGMENTATION_DIR`/`OUTPUT_DIR` constants.

`data/` (raw DICOM, NIfTI, segmentations, molds) is gitignored — it holds real scan data and generated artifacts. Never commit it.

## Environment

A Python venv with GPU-enabled PyTorch is required for practical TotalSegmentator runtimes (CPU: ~10-30 min/segmentation vs GPU: ~1-2 min). `requirements.txt` only lists `SimpleITK` and `TotalSegmentator`; `create_mold.py` additionally needs `numpy`, `nibabel`, `scipy`, `scikit-image`, and `trimesh`, which are not currently captured there. Verify GPU is picked up with:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

If `False`, reinstall the CUDA build: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121`.

## Architecture notes specific to `create_mold.py`

- Mold generation works entirely in **voxel space** (numpy arrays), not mesh space: dilation via `scipy.ndimage.distance_transform_edt`, splitting via array slicing, and pin/socket cylinders rasterized directly into the two half-volumes (`add_pins_and_sockets_voxel`). Meshing (`skimage.measure.marching_cubes` → `trimesh`) happens last, only to produce the STL.
- The split axis is chosen automatically as the organ's **shortest bounding-box dimension in mm** (`detect_shortest_axis`), not a fixed anatomical axis — so which axis is "top/bottom" varies per organ.
- Pins are placed by finding wall voxels on the split plane, computing their angle around the centroid, and picking the wall voxel closest to each of N evenly-spaced target angles (`find_pin_voxel_positions`) — an angular nearest-voxel search, not a geometric constructor.

## Notes

- `segment_organs.py` menu labels are in German (organ categories/names); the mapping to TotalSegmentator IDs is in `ORGAN_CATEGORIES`.
- `NOTES.md` and `progress_documentation.md` are working notes in German. `progress_documentation.md` logs a first-layer print-defect investigation whose conclusion was that print-quality issues (bed adhesion, contact area, curved resting surfaces) are printer/slicer concerns, not mesh-generation bugs — worked around in the slicer (reorient part, add raft/skirt), not in this code.
