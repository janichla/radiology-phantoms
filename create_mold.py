"""
NIfTI Segmentation Mask → 3D-printable Mold (STL).

Workflow:
1. Load binary organ mask from NIfTI
2. Dilate mask by wall thickness to create outer boundary
3. Subtract organ from outer boundary → hollow mold
4. Split into two halves (top/bottom) for filling and removal
5. Export each half as STL for 3D printing
"""

import os
import sys
import numpy as np
import nibabel as nib
from scipy import ndimage
from skimage import measure
import trimesh

###################
#  CONFIGURATION  #
###################

# input directory with segmentation files
SEGMENTATION_DIR = r"C:\Users\Laura\Desktop\El_Phantom\data\organ segmentations (nifti)"

# output directory 
OUTPUT_DIR = r"C:\Users\Laura\Desktop\El_Phantom\data\3d objects (stl)"

# thickness of wall in mm
WALL_THICKNESS_MM = 2.50 

# target spacing in mm after upsamling (smaller/more voxel/smoother surface)
UPSAMPLE_SPACING = (0.75, 0.75, 0.75)

# pin dimensions in mm
PIN_RADIUS = 2.5       # pin radius
PIN_HEIGHT = 5.0       # how deep the pin goes
PIN_CLEARANCE = 0.3    # gap between pin and socket for easy fit

# axis vessel tunnels run along; holes filled per-slice to keep cavity hollow (0=x, 1=y, 2=z)
TUNNEL_FILL_AXIS = 1

def load_mask(nifti_path):
    """Loads a NIfTI file and returns the binary mask and voxel spacing."""
    # load reads the header (lazy loading)
    img = nib.load(nifti_path)
    # loads voxel data
    data = img.get_fdata().astype(np.uint8)
    spacing = np.array(img.header.get_zooms()[:3])
    print(f"Dimensions: {data.shape}")
    print(f"Spacing: {spacing[0]:.2f} x {spacing[1]:.2f} x {spacing[2]:.2f} mm")

    # fill vessel tunnels per-slice so the mold cavity stays fully hollow (no column)
    before = int(data.sum())
    for i in range(data.shape[TUNNEL_FILL_AXIS]):
        sl = [slice(None)] * 3
        sl[TUNNEL_FILL_AXIS] = i
        data[tuple(sl)] = ndimage.binary_fill_holes(data[tuple(sl)])
    print(f"  Filled {int(data.sum()) - before} tunnel voxel(s)")

    # # upsample to finer resolution for smoother surface
    # target = np.array(UPSAMPLE_SPACING)
    # zoom_factors = spacing / target
    # data = ndimage.zoom(data, zoom_factors, order=1)
    # spacing = target
    # print(f"  Upsampled to: {data.shape}, spacing: {spacing[0]:.2f} x {spacing[1]:.2f} x {spacing[2]:.2f} mm")

    # # light smoothing to remove staircase artifacts without losing shape
    # sigma = [1.0 / sp for sp in spacing]  # ~1mm smoothing
    # mask = ndimage.gaussian_filter(mask, sigma=sigma)
    # mask = (mask > 0.4).astype(np.uint8)  # threshold back to binary

    # print(f"  Non-zero voxels (after smoothing): {np.sum(data)}")
    return data, tuple(spacing)


def create_mold_volume(mask, spacing, wall_mm):
    """Creates a mold volume by dilating the mask and subtracting the original."""
    # create inverted mask for distance transform function
    inverted_mask = (mask == 0)
    # calculate euclidean distance from each empty voxel to nearest organ voxel
    distance = ndimage.distance_transform_edt(inverted_mask, sampling=spacing)
    # everything within wall thickness becomes the outer boundary
    dilated = (distance <= wall_mm).astype(np.uint8)

    # crate mold as dilated outer shell minus the organ cavity
    mold = dilated - mask
    # prevent uint8 underflow from substraction
    mold = np.clip(mold, 0, 1).astype(np.uint8)

    print(f"Mold voxels: {np.sum(mold)}")
    return mold


def detect_shortest_axis(mask, spacing):
    """Finds the shortest axis of the mask in mm and returns its index."""
    # get all organ voxels (nonzero voxels)
    nonzero = np.argwhere(mask > 0)
    # find shortest axis (get highest and lowest value for each koordinate and calculate)
    extent_mm = (nonzero.max(axis=0) - nonzero.min(axis=0)) * np.array(spacing)
    # get index of shortest axis
    return int(np.argmin(extent_mm))


def split_mold(mold_volume, axis=2):
    """Splits the mold into top and bottom halves along the given axis."""
    # get indices with value 1 of shortest
    nonzero_indices = np.nonzero(mold_volume)[axis]
    # calculate mid of organ
    mid = int((nonzero_indices.min() + nonzero_indices.max()) // 2)
    print(f"  Splitting at slice {mid} (of {mold_volume.shape[axis]}) — center of organ")

    bottom = mold_volume.copy()
    top = mold_volume.copy()

    # Zero out the other half
    if axis == 2:
        bottom[:, :, mid:] = 0
        top[:, :, :mid] = 0
    elif axis == 1:
        bottom[:, mid:, :] = 0
        top[:, :mid, :] = 0
    else:
        bottom[mid:, :, :] = 0
        top[:mid, :, :] = 0

    return bottom, top, mid


def volume_to_mesh(volume, spacing):
    """Converts a binary volume to a triangle mesh using marching cubes."""
    # Pad volume so marching cubes can close the surface at boundaries
    padded = np.pad(volume, pad_width=1, mode='constant', constant_values=0)

    verts, faces, normals, _ = measure.marching_cubes(padded, level=0.5, spacing=spacing)

    # Offset vertices to account for padding
    verts -= np.array(spacing)

    # Center mesh at origin (0,0,0)
    center = (verts.max(axis=0) + verts.min(axis=0)) / 2
    verts -= center

    mesh = trimesh.Trimesh(vertices=verts, faces=faces, vertex_normals=normals)
    return mesh


def find_pin_voxel_positions(mold_volume, spacing, axis, mid, num_pins=4):
    """Finds voxel positions for pins along the split plane, evenly spaced on the mold wall."""
    slicing = [slice(None)] * 3
    slicing[axis] = mid
    split_slice = mold_volume[tuple(slicing)]

    wall_coords = np.argwhere(split_slice > 0)
    if len(wall_coords) < num_pins:
        return []

    plane_axes = [i for i in range(3) if i != axis]

    center = wall_coords.mean(axis=0)
    angles = np.arctan2(wall_coords[:, 1] - center[1], wall_coords[:, 0] - center[0])

    pin_positions = []
    for i in range(num_pins):
        target_angle = -np.pi + i * (2 * np.pi / num_pins)
        angle_diff = np.abs(angles - target_angle)
        angle_diff = np.minimum(angle_diff, 2 * np.pi - angle_diff)
        best_idx = np.argmin(angle_diff)
        voxel = wall_coords[best_idx]

        # Return as full 3D voxel index
        pos = [0, 0, 0]
        pos[plane_axes[0]] = int(voxel[0])
        pos[plane_axes[1]] = int(voxel[1])
        pos[axis] = mid
        pin_positions.append(pos)

    return pin_positions


def add_pins_and_sockets_voxel(bottom, top, spacing, axis, pin_positions):
    """Adds pins to bottom and sockets to top directly in the voxel volumes."""
    pin_r_voxels = [max(1, int(round(PIN_RADIUS / sp))) for sp in spacing]
    pin_h_voxels = max(1, int(round(PIN_HEIGHT / spacing[axis])))
    socket_r_voxels = [max(1, int(round((PIN_RADIUS + PIN_CLEARANCE) / sp))) for sp in spacing]
    socket_h_voxels = max(1, int(round((PIN_HEIGHT + 1.0) / spacing[axis])))

    plane_axes = [i for i in range(3) if i != axis]

    for pos in pin_positions:
        # Draw a cylinder in voxel space
        for vol, r_vox, h_vox, is_pin in [
            (bottom, pin_r_voxels, pin_h_voxels, True),
            (top, socket_r_voxels, socket_h_voxels, False),
        ]:
            # Range along split axis
            # Both pin and socket go in the same direction (from split plane into top half)
            # Pin sticks out of bottom, socket is a hole in top
            a_start = pos[axis]
            a_end = min(vol.shape[axis], pos[axis] + h_vox)

            # Range along the two plane axes
            r0 = r_vox[plane_axes[0]]
            r1 = r_vox[plane_axes[1]]
            c0 = pos[plane_axes[0]]
            c1 = pos[plane_axes[1]]

            for da in range(a_start, a_end):
                for d0 in range(max(0, c0 - r0), min(vol.shape[plane_axes[0]], c0 + r0 + 1)):
                    for d1 in range(max(0, c1 - r1), min(vol.shape[plane_axes[1]], c1 + r1 + 1)):
                        # Check if within ellipse (accounts for anisotropic spacing)
                        if ((d0 - c0) / r0) ** 2 + ((d1 - c1) / r1) ** 2 <= 1.0:
                            idx = [0, 0, 0]
                            idx[axis] = da
                            idx[plane_axes[0]] = d0
                            idx[plane_axes[1]] = d1
                            if is_pin:
                                vol[tuple(idx)] = 1  # add material
                            else:
                                vol[tuple(idx)] = 0  # remove material

    return bottom, top



def process_organ(nifti_path, output_dir, wall_mm):
    """Full pipeline for one organ: load → mold → split → STL"""
    organ_name = os.path.splitext(os.path.splitext(os.path.basename(nifti_path))[0])[0]

    print(f"\n{'=' * 60}")
    print(f"Processing: {organ_name}")
    print(f"{'=' * 60}")

    # Step 1: Load mask
    print(f"\n[1/4] Loading mask...")
    mask, spacing = load_mask(nifti_path)

    # Step 2: Create mold volume
    print(f"\n[2/4] Creating mold (wall thickness: {wall_mm}mm)...")
    mold = create_mold_volume(mask, spacing, wall_mm)

    # Step 3: Split into halves
    axis = detect_shortest_axis(mask, spacing)
    axis_names = {0: "x (links/rechts)", 1: "y (vorne/hinten)", 2: "z (oben/unten)"}
    print(f"\n[3/5] Splitting along {axis_names[axis]}...")
    bottom, top, mid = split_mold(mold, axis=axis)

    # Step 4: Add pin & socket locking system into voxel volumes
    has_both = np.sum(bottom) > 0 and np.sum(top) > 0
    if has_both:
        print(f"\n[4/5] Adding pin & socket locking system...")
        pin_positions = find_pin_voxel_positions(mold, spacing, axis, mid, num_pins=4)
        print(f"  Placing {len(pin_positions)} pins on split plane")
        bottom, top = add_pins_and_sockets_voxel(bottom, top, spacing, axis, pin_positions)
    else:
        print(f"\n[4/5] Skipping pins (need both halves).")

    # Step 5: Convert to mesh and save STL
    print(f"\n[5/5] Generating STL files...")
    os.makedirs(output_dir, exist_ok=True)

    for part_name, part_volume in [("bottom", bottom), ("top", top)]:
        if np.sum(part_volume) == 0:
            print(f"  WARNING: {part_name} half is empty, skipping.")
            continue
        mesh = volume_to_mesh(part_volume, spacing)
        stl_path = os.path.join(output_dir, f"{organ_name}_mold_{part_name}.stl")
        mesh.export(stl_path)
        size_mb = os.path.getsize(stl_path) / (1024 * 1024)
        print(f"  Saved: {stl_path} ({size_mb:.1f} MB)")

    # Also save the complete (unsplit) mold
    full_mesh = volume_to_mesh(mold, spacing)
    full_path = os.path.join(output_dir, f"{organ_name}_mold_full.stl")
    full_mesh.export(full_path)
    size_mb = os.path.getsize(full_path) / (1024 * 1024)
    print(f"  Saved: {full_path} ({size_mb:.1f} MB)")


def main():
    print("=" * 60)
    print("Convert NIfTI Mask to 3D-printable STL-File of Mold)")
    print(f"Wall thickness: {WALL_THICKNESS_MM} mm")
    print("=" * 60)

    # Find all .nii.gz files in segmentation dir
    nifti_files = sorted([
        f for f in os.listdir(SEGMENTATION_DIR)
        if f.endswith(".nii.gz")
    ])

    if not nifti_files:
        print(f"ERROR: No .nii.gz files found in {SEGMENTATION_DIR}")
        sys.exit(1)

    print(f"\nFound {len(nifti_files)} segmentation(s): {', '.join(nifti_files)}")

    for fname in nifti_files:
        nifti_path = os.path.join(SEGMENTATION_DIR, fname)
        process_organ(nifti_path, OUTPUT_DIR, WALL_THICKNESS_MM)

    print(f"\n{'=' * 60}")
    print("Done! All molds saved to:")
    print(f"  {OUTPUT_DIR}")
    print(f"\nOpen the STL files in a slicer (e.g. PrusaSlicer, Cura) for 3D printing.")
    print("=" * 60)


if __name__ == "__main__":
    main()
