"""
TotalSegmentator Organ Segmentation with interactive menu.

Workflow:
1. User selects a category (organs, lung & heart, bones, vessels, muscels)
2. User selects specific organ(s) or all in category
3. TotalSegmentator runs with --roi_subset for selected organs
4. Output masks saved to segmentations folder
"""

import os
import sys
import time
from totalsegmentator.python_api import totalsegmentator

# ============================================================
# Configuration:
# ============================================================

# input path of DICOM directory
DICOM_DIR = r"C:\Users\Laura\Desktop\El_Phantom\data\ProtocolModel_Mono_70keV_Qr40f(3)_0.4_(0.4)_[A,1]_0"

# input path of NIfTI file
INPUT_FILE = os.path.join(os.path.dirname(DICOM_DIR), os.path.basename(DICOM_DIR) + "_resampled.nii.gz")

# output path of segmentation mask file
OUTPUT_DIR = os.path.join(os.path.dirname(DICOM_DIR), "segmentations")

# Available organs grouped by category
# Format: "Display Name": "totalsegmentator_id"
ORGAN_CATEGORIES = {
    "Organe": {
        "Leber": "liver",
        "Milz": "spleen",
        "Niere rechts": "kidney_right",
        "Niere links": "kidney_left",
        "Magen": "stomach",
        "Gallenblase": "gallbladder",
        "Bauchspeicheldrüse": "pancreas",
        "Nebenniere rechts": "adrenal_gland_right",
        "Nebenniere links": "adrenal_gland_left",
        "Blase": "urinary_bladder",
        "Speiseröhre": "esophagus",
        "Luftröhre": "trachea",
        "Dünndarm": "small_bowel",
        "Dickdarm": "colon",
        "Zwölffingerdarm": "duodenum",
    },
    "Lunge & Herz": {
        "Lunge Oberlappen links": "lung_upper_lobe_left",
        "Lunge Unterlappen links": "lung_lower_lobe_left",
        "Lunge Oberlappen rechts": "lung_upper_lobe_right",
        "Lunge Mittellappen rechts": "lung_middle_lobe_right",
        "Lunge Unterlappen rechts": "lung_lower_lobe_right",
        "Herz (Myokard)": "heart_myocardium",
        "Herz (Vorhof links)": "heart_atrium_left",
        "Herz (Vorhof rechts)": "heart_atrium_right",
        "Herz (Ventrikel links)": "heart_ventricle_left",
        "Herz (Ventrikel rechts)": "heart_ventricle_right",
    },
    "Knochen": {
        "Wirbel C1-C7 (HWS)": ["vertebrae_C1", "vertebrae_C2", "vertebrae_C3", "vertebrae_C4", "vertebrae_C5", "vertebrae_C6", "vertebrae_C7"],
        "Wirbel T1-T12 (BWS)": ["vertebrae_T1", "vertebrae_T2", "vertebrae_T3", "vertebrae_T4", "vertebrae_T5", "vertebrae_T6", "vertebrae_T7", "vertebrae_T8", "vertebrae_T9", "vertebrae_T10", "vertebrae_T11", "vertebrae_T12"],
        "Wirbel L1-L5 (LWS)": ["vertebrae_L1", "vertebrae_L2", "vertebrae_L3", "vertebrae_L4", "vertebrae_L5"],
        "Rippen": ["rib_left_1", "rib_left_2", "rib_left_3", "rib_left_4", "rib_left_5", "rib_left_6", "rib_left_7", "rib_left_8", "rib_left_9", "rib_left_10", "rib_left_11", "rib_left_12", "rib_right_1", "rib_right_2", "rib_right_3", "rib_right_4", "rib_right_5", "rib_right_6", "rib_right_7", "rib_right_8", "rib_right_9", "rib_right_10", "rib_right_11", "rib_right_12"],
        "Hüftknochen links": "hip_left",
        "Hüftknochen rechts": "hip_right",
        "Kreuzbein": "sacrum",
        "Oberschenkelknochen links": "femur_left",
        "Oberschenkelknochen rechts": "femur_right",
        "Schulterblatt links": "scapula_left",
        "Schulterblatt rechts": "scapula_right",
        "Schlüsselbein links": "clavicula_left",
        "Schlüsselbein rechts": "clavicula_right",
        "Oberarmknochen links": "humerus_left",
        "Oberarmknochen rechts": "humerus_right",
    },
    "Gefäße": {
        "Aorta": "aorta",
        "Vena cava inferior": "inferior_vena_cava",
        "Portalvene + Milzvene": "portal_vein_and_splenic_vein",
        "A. iliaca communis links": "iliac_artery_left",
        "A. iliaca communis rechts": "iliac_artery_right",
        "V. iliaca communis links": "iliac_vena_left",
        "V. iliaca communis rechts": "iliac_vena_right",
        "Pulmonalarterie": "pulmonary_artery",
    },
    "Muskeln": {
        "Autochthone Rückenmuskulatur": "autochthon_left,autochthon_right",
        "Iliopsoas links": "iliopsoas_left",
        "Iliopsoas rechts": "iliopsoas_right",
        "Gluteus maximus links": "gluteus_maximus_left",
        "Gluteus maximus rechts": "gluteus_maximus_right",
        "Gluteus medius links": "gluteus_medius_left",
        "Gluteus medius rechts": "gluteus_medius_right",
        "Gluteus minimus links": "gluteus_minimus_left",
        "Gluteus minimus rechts": "gluteus_minimus_right",
    },
}

# get flat list of totalsegmentator IDs
def get_roi_ids(value):
    """Converts organ value(s) to a flat list of TotalSegmentator IDs."""
    if isinstance(value, list):
        return value
    return [v.strip() for v in value.split(",")]

# print list of all categories with their structure count
def show_categories():
    """Shows numbered list of categories."""
    print("\nAvailable categories:")
    print("-" * 40)
    categories = list(ORGAN_CATEGORIES.keys())
    for i, cat in enumerate(categories, 1):
        count = len(ORGAN_CATEGORIES[cat])
        print(f"  [{i}] {cat} ({count} structures)")
    return categories

# print list of organs in a category, with option [0] to select all
def show_organs(category_name):
    """Shows numbered list of organs in a category."""
    organs = ORGAN_CATEGORIES[category_name]
    print(f"\n{category_name}:")
    print("-" * 40)
    print(f"  [0] --- All in this category ---")
    organ_names = list(organs.keys())
    for i, name in enumerate(organ_names, 1):
        print(f"  [{i}] {name}")
    return organ_names

# get numeric input from user
def select_from_menu(prompt, max_val, allow_multi=True):
    """Gets user selection (single number or comma-separated)."""
    while True:
        try:
            raw = input(f"\n{prompt}: ").strip()
            if allow_multi and "," in raw:
                nums = [int(x.strip()) for x in raw.split(",")]
            else:
                nums = [int(raw)]
            if all(0 <= n <= max_val for n in nums):
                return nums
            print(f"  Please enter numbers between 0 and {max_val}.")
        except ValueError:
            print("  Invalid input. Enter a number.")
        except KeyboardInterrupt:
            print("\nAborted.")
            sys.exit(0)


def run_totalsegmentator(roi_subset):
    """Runs TotalSegmentator with the selected organs using the Python API."""
    
    # create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"Running TotalSegmentator...")
    print(f"  Input:  {INPUT_FILE}")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Organs: {', '.join(roi_subset)}")
    print(f"  Count:  {len(roi_subset)} structure(s)")
    print(f"{'=' * 60}\n")

    # start time 
    start_time = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] Loading model...")

    try:
        # execute totalsegmentator
        totalsegmentator(input=INPUT_FILE, output=OUTPUT_DIR, roi_subset=roi_subset)

        # calculate segmentation time
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        print(f"\n[{time.strftime('%H:%M:%S')}] Done!")
        print(f"\n{'=' * 60}")
        print("Segmentation complete!")
        print(f"  Results saved to: {OUTPUT_DIR}")
        print(f"  Duration: {minutes}m {seconds}s")
        print(f"\nOpen in 3D Slicer to view the results.")
        print(f"{'=' * 60}")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n[{time.strftime('%H:%M:%S')}] Failed after {int(elapsed)}s")
        print(f"\nERROR: TotalSegmentator failed: {e}")
        sys.exit(1)


def main():
    print("=" * 60)
    print("TotalSegmentator - Organ Segmentation")
    print("=" * 60)

    # Check if input file exists
    if not os.path.isfile(INPUT_FILE):
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        print("Run dicom_to_nifti.py first to create the NIfTI file.")
        sys.exit(1)

    # Step 1: Select category
    categories = show_categories()
    selection = select_from_menu("Select category (number)", len(categories))
    cat_idx = selection[0]
    if cat_idx < 1 or cat_idx > len(categories):
        print("Invalid category.")
        sys.exit(1)
    selected_category = categories[cat_idx - 1]

    # Step 2: Select organ(s)
    organ_names = show_organs(selected_category)
    selection = select_from_menu("Select organ (number, or comma-separated for multiple, 0 for all)", len(organ_names), allow_multi=True)

    # Build list of TotalSegmentator IDs
    organs = ORGAN_CATEGORIES[selected_category]
    roi_subset = []

    if 0 in selection:
        for value in organs.values():
            roi_subset.extend(get_roi_ids(value))
        print(f"\n  Selected: All in '{selected_category}' ({len(roi_subset)} structures)")
    else:
        for idx in selection:
            name = organ_names[idx - 1]
            value = organs[name]
            roi_subset.extend(get_roi_ids(value))
            print(f"  Selected: {name}")

    # Step 3: Run TotalSegmentator
    run_totalsegmentator(roi_subset)


if __name__ == "__main__":
    main()
