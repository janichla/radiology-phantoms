# radiology-phantoms

## What This Project Does

Two Python scripts that convert DICOM CT data to NIfTI and then segment organs using TotalSegmentator:

1. **`dicom_to_nifti.py`** - Converts DICOM folder to a resampled NIfTI file
2. **`segment_organs.py`** - Interactive menu to select and segment organs with TotalSegmentator

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