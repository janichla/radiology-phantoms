# El Phantom - Notes for HiWi

## What This Project Does

Two Python scripts that convert DICOM CT data to NIfTI and then segment organs using TotalSegmentator:

1. **`dicom_to_nifti.py`** - Converts DICOM folder to a resampled NIfTI file
2. **`segment_organs.py`** - Interactive menu to select and segment organs with TotalSegmentator

## What Went Wrong Initially

The first version used a **custom DICOM-to-NIfTI converter** built with `pydicom` and `nibabel`. This read each DICOM slice individually, built the 3D volume manually, and computed the affine matrix from scratch. The segmentation results were completely wrong - organs were detected in wrong locations or not at all.

### The two main problems:

**1. Orientation / Affine Matrix**
The custom converter computed the 4x4 affine matrix (which maps voxel coordinates to patient coordinates) manually from DICOM headers. This is error-prone because DICOM orientation handling has many edge cases. The resulting NIfTI file had incorrect spatial information, so TotalSegmentator looked for organs in the wrong places.

**2. Resampling Mismatch**
When downsampling to reduce file size, both the CT volume AND the segmentation masks must be in the same voxel spacing. The initial approach (dropping every n-th slice) changed the effective spacing without properly updating the affine matrix.

### What we also tried that didn't work:
- **dcm2niix** (external exe) - Worked for conversion but produced a flipped/reversed orientation compared to what TotalSegmentator expected. Also required downloading a separate `.exe` file since `pip install dcm2niix` failed (needs a C compiler).
- **Fast mode** in TotalSegmentator (`fast=True`) - Uses 3mm resolution instead of 1.5mm, which was too coarse for accurate organ boundaries.

## The Fix: SimpleITK

We replaced everything with **SimpleITK**, a standard medical imaging library that:
- Reads DICOM series correctly (orientation, HU values, metadata - all handled internally)
- Resamples with proper interpolation and affine matrix updates
- No external executables needed

The key insight: **don't write custom DICOM handling code**. Use established libraries that have been tested on thousands of datasets.

## Virtual Environment (venv)

We use a Python **virtual environment** (venv). This is an isolated Python installation inside the project folder that has its own packages, separate from the system Python.

### Why use a venv?
- **Isolation**: Packages installed here don't affect other projects on the machine
- **Reproducibility**: Everyone working on the project has the same package versions
- **GPU PyTorch**: We need a specific PyTorch version with CUDA support. Installing this globally could break other projects

### How to use it:

```bash
# Activate the venv (do this every time you open a new terminal)
cd C:\Users\radstudie\Desktop\El_Phantom
.\venv\Scripts\activate

# You should see (venv) at the start of your terminal prompt
# Now run the scripts:
python dicom_to_nifti.py
python segment_organs.py

# Deactivate when done:
deactivate
```

### What's installed in the venv:
- `torch` + `torchvision` with **CUDA support** (GPU acceleration)
- `TotalSegmentator` (organ segmentation)
- `SimpleITK` (DICOM reading and image resampling)
- `nibabel`, `scipy`, `numpy` (NIfTI handling and numerics)

### GPU vs CPU
TotalSegmentator uses a neural network (nnU-Net) that benefits massively from GPU acceleration:
- **CPU**: ~10-30 minutes per segmentation
- **GPU (CUDA)**: ~1-2 minutes per segmentation

The venv has PyTorch installed with CUDA support. If you see "No GPU detected" when running, check:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```
This should print `True`. If it prints `False`, reinstall PyTorch:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## Workflow

```
DICOM folder
    |
    v
[dicom_to_nifti.py]  -->  *_resampled.nii.gz  (1x1x1.5mm spacing)
    |
    v
[segment_organs.py]   -->  segmentations/*.nii.gz  (organ masks)
    |
    v
Load both in 3D Slicer to inspect results
```

## Important Notes

- Always make sure the **venv is activated** before running the scripts.
- The segmentation masks and the CT volume must have **matching spacing** to overlay correctly in 3D Slicer.
