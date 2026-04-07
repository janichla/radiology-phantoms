# El Phantom - Notes for HiWi

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
