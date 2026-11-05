"""
DICOM to NIfTI Converter.

Workflow:
1. Use SimpleITK to convert DICOM to NIfTI (preserves orientation correctly)
2. Resample the volume to 1x1x1.5mm spacing
3. Save as compressed NIfTI (.nii.gz)
"""

import os
import sys
import SimpleITK as sitk

###################
#  CONFIGURATION  #
###################

# input path of DICOM files
DICOM_DIR = r"C:\Users\Laura\Desktop\El_Phantom\data\original data (dicom)\ProtocolModel_Mono_70keV_Qr40f(3)_0.4_(0.4)_[A,1]_0"

# target voxel spacing in mm in columns/rows/slices
TARGET_SPACING = (1.0, 1.0, 1.5)

# output path of NIfTI file
OUTPUT_DIR = os.path.dirname(DICOM_DIR)

######################
#  HELPER FUNCTIONS  #
######################

def read_dicom_series(dicom_dir):
    """Reads a DICOM series using SimpleITK. Returns a SimpleITK image."""
    
    # create Reader
    reader = sitk.ImageSeriesReader()

    # ensure files are ordered in spatial order
    dicom_names = reader.GetGDCMSeriesFileNames(dicom_dir)
    if not dicom_names:
        print("ERROR: No DICOM files found!")
        sys.exit(1)

    # pass ordered file paths to reader
    reader.SetFileNames(dicom_names)

    # build and return SimpleITK image object
    image = reader.Execute()
    return image


def resample_image(image, target_spacing):
    """Resamples a SimpleITK image to the target spacing using linear interpolation."""

    # get spacing (voxel size in mm) and size (number of voxels) for each dimension 
    original_spacing = image.GetSpacing()
    original_size = image.GetSize()

    print(f"  Current spacing: {original_spacing[0]:.3f} x {original_spacing[1]:.3f} x {original_spacing[2]:.3f} mm")
    print(f"  Current size:    {original_size[0]} x {original_size[1]} x {original_size[2]}")
    print(f"  Target spacing:  {target_spacing[0]:.1f} x {target_spacing[1]:.1f} x {target_spacing[2]:.1f} mm")

    # calculate new size: (original size * original spacing) / target spacing = new number of voxels per dimension, rounded to int
    new_size = [int(round(osz * ospc / tspc)) for osz, ospc, tspc in zip(original_size, original_spacing, target_spacing)]

    print(f"  New size:        {new_size[0]} x {new_size[1]} x {new_size[2]}")

    # create Resampler
    resampler = sitk.ResampleImageFilter()

    # set output parameters and linear interpolator
    resampler.SetOutputSpacing(target_spacing)
    resampler.SetSize(new_size)
    resampler.SetOutputDirection(image.GetDirection())
    resampler.SetOutputOrigin(image.GetOrigin())
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(-1000)  # air for out-of-bounds

    # build and return resampled SimpleITK image
    resampled = resampler.Execute(image)
    return resampled


##############
#  WORKFLOW  #
##############

def main():
    print("=" * 60)
    print("DICOM to NIfTI Converter")
    print("=" * 60)

    # Step 1: Read DICOM series
    print(f"\n[1/3] Reading DICOM series from: {DICOM_DIR}")
    image = read_dicom_series(DICOM_DIR)
    print(f"  Found {image.GetSize()[2]} slices")

    # Step 2: Resample to target spacing
    print(f"\n[2/3] Resampling to {TARGET_SPACING[0]}x{TARGET_SPACING[1]}x{TARGET_SPACING[2]}mm...")
    resampled = resample_image(image, TARGET_SPACING)

    # Step 3: Save as NIfTI
    output_path = os.path.join(OUTPUT_DIR, os.path.basename(DICOM_DIR) + "_resampled.nii.gz")
    print(f"\n[3/3] Saving NIfTI file...")
    sitk.WriteImage(resampled, output_path)
    print(f"  Saved: {output_path}")

    print(f"\n{'=' * 60}")
    print("Finished! Use this file with segment_organs.py:")
    print(f"  {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
