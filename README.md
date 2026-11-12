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
Open STLs in Bambu Studio and 3D-print
```

## Setup

```bash
python -m venv venv
.\venv\Scripts\activate        
pip install -r requirements.txt
```

## Running

There are no CLI arguments — edit the `CONFIGURATION` constants near the top of each
script (input/output paths, spacing, wall thickness, pin sizes) before running.

```bash
python dicom_to_nifti.py       # step 1
python segment_organs.py       # step 2 (interactive menu)
python create_mold.py          # step 3 (processes every mask in the segmentation dir)
```

## Printing (Using a Bambu Lab X1E)

1. Install Bambu Studio: https://bambulab.com/de-de/download/studio. Open the Bambu Studio Project file and select the printer.
2. Connect the PC with the printer using a LAN adapter. Go to "Gerät" in Bambu Studio and add a new printer via "mit Zugangscode binden". Enter the IP address of the wired network, the access code and the serial number.
3. Insert a SD card at the printer.
4. Import the .stl files (Top & Bottom) of the organs you want to print and arrange them so that they rest on the plate with their cut surface facing down. Click "Druckplatte slicen" to build the support structures.
5. Start printing.

1. Install Bambu Studio: https://bambulab.com/de-de/download/studio. Then open the project file `<name>.3mf` from the `<folder>` directory and select the X1E as the printer.
2. Connect the PC and the printer with an Ethernet cable (LAN). In Bambu Studio, go to "Gerät" (Device) and add the printer via "Mit Zugangscode binden" (Bind with Access Code). You need three values:
   - the **IP address of the printer** (wired)
   - the **access code**
   - the **serial number**
3. Insert an SD card into the printer. 

### For each print

4. Import the `.stl` files (top and bottom) of the organs you want to print. Arrange them so that each part rests on the plate with its cut surface facing down. Make sure supports are enabled in the print settings, then click "Druckplatte slicen" (Slice plate) to generate the print paths and support structures.
5. Click "Drucken" (Print) and start the print.