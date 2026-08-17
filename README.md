# radiology-phantoms

## What This Project Does

Three Python scripts that turn a CT DICOM series into 3D-printable organ molds:

1. **`dicom_to_nifti.py`** - Converts a DICOM folder to a resampled NIfTI file
2. **`segment_organs.py`** - Interactive menu to select and segment organs with TotalSegmentator
3. **`create_mold.py`** - Builds a hollow two-part mold (with pin/socket alignment) from each organ mask and exports it as STL

## Workflow

```
DICOM folder
    |
    v
[dicom_to_nifti.py]  -->  *_resampled.nii.gz  (1x1x1.5mm spacing)
    |
    v
[segment_organs.py]  -->  segmentations/*.nii.gz  (organ masks)
    |
    v
[create_mold.py]     -->  molds/*_mold_{top,bottom,full}.stl
    |
    v
Slice STLs in PrusaSlicer / Cura / Bambu Studio and 3D-print
```

Load the NIfTI/masks in 3D Slicer to inspect results.

## Setup

```bash
python -m venv venv
.\venv\Scripts\activate        # every new terminal
pip install -r requirements.txt
```

For GPU-accelerated segmentation (recommended), install PyTorch with CUDA separately:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
python -c "import torch; print(torch.cuda.is_available())"   # should print True
```

## Running

There are no CLI arguments — edit the `CONFIGURATION` constants near the top of each
script (input/output paths, spacing, wall thickness, pin sizes) before running.

```bash
python dicom_to_nifti.py       # step 1
python segment_organs.py       # step 2 (interactive menu)
python create_mold.py          # step 3 (processes every mask in the segmentation dir)
```
