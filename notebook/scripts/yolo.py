import os
from collections import defaultdict
import cv2
import numpy as np
import random
import shutil
import matplotlib.pyplot as plt
import yaml

def split_dataset(image_folder, mask_folder, output_folder, train_ratio=0.8):
    if not os.path.exists(image_folder):
        raise ValueError(f"Image folder '{image_folder}' does not exist")
    if not os.path.exists(mask_folder):
        raise ValueError(f"Mask folder '{mask_folder}' does not exist")
    if not 0 < train_ratio < 1:
        raise ValueError(f"train_ratio must be between 0 and 1, got {train_ratio}")

    train_dir = os.path.join(output_folder, 'train')
    val_dir = os.path.join(output_folder, 'val')
    train_images_dir = os.path.join(train_dir, 'images')
    train_masks_dir = os.path.join(train_dir, 'masks')
    val_images_dir = os.path.join(val_dir, 'images')
    val_masks_dir = os.path.join(val_dir, 'masks')

    for dir_path in [train_images_dir, train_masks_dir, val_images_dir, val_masks_dir]:
        os.makedirs(dir_path, exist_ok=True)

    image_files = []
    fragment_counts = defaultdict(list)

    for f in os.listdir(image_folder):
        if f.endswith('.jpg'):
            mask_file = f.replace('.jpg', '.png')
            mask_path = os.path.join(mask_folder, mask_file)
            if os.path.exists(mask_path):
                mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
                if mask is None:
                    print(f"Warning: Could not load mask {mask_file}, skipping {f}")
                    continue
                
                unique_values = np.unique(mask)
                unique_values = unique_values[unique_values > 0]
                num_fragments = len(unique_values)

                image_files.append(f)
                fragment_counts[num_fragments].append(f)
            else:
                print(f"Warning: Skipping {f} - mask file {mask_file} not found in mask folder")

    if not image_files:
        raise ValueError("No valid image-mask pairs found")

    train_files = []
    val_files = []

    for num_fragments, files in fragment_counts.items():
        random.shuffle(files)
        train_count = int(len(files) * train_ratio)
        train_files.extend(files[:train_count])
        val_files.extend(files[train_count:])

    random.shuffle(train_files)
    random.shuffle(val_files)

    def copy_file_pair(img_file, src_img_dir, src_mask_dir, dst_img_dir, dst_mask_dir):
        mask_file = img_file.replace('.jpg', '.png')
        src_img = os.path.join(src_img_dir, img_file)
        src_mask = os.path.join(src_mask_dir, mask_file)
        dst_img = os.path.join(dst_img_dir, img_file)
        dst_mask = os.path.join(dst_mask_dir, mask_file)
        try:
            shutil.copy2(src_img, dst_img)
            shutil.copy2(src_mask, dst_mask)
            return True
        except Exception as e:
            print(f"Error copying {img_file} or {mask_file}: {str(e)}")
            return False

    train_success = 0
    for img_file in train_files:
        if copy_file_pair(img_file, image_folder, mask_folder, train_images_dir, train_masks_dir):
            train_success += 1
            print(f"Copied {img_file} and its mask to training set")

    val_success = 0
    for img_file in val_files:
        if copy_file_pair(img_file, image_folder, mask_folder, val_images_dir, val_masks_dir):
            val_success += 1
            print(f"Copied {img_file} and its mask to validation set")

    print(f"\nDataset split complete (stratified by fragment distribution):")
    print(f"Total valid image-mask pairs found: {len(image_files)}")
    print(f"Training set: {train_success} pairs ({train_success/len(image_files)*100:.1f}%)")
    print(f"Validation set: {val_success} pairs ({val_success/len(image_files)*100:.1f}%)")

    train_frag_dist = defaultdict(int)
    val_frag_dist = defaultdict(int)
    for f in train_files:
        mask_file = f.replace('.jpg', '.png')
        mask = cv2.imread(os.path.join(mask_folder, mask_file), cv2.IMREAD_GRAYSCALE)
        num_fragments = len(np.unique(mask)[np.unique(mask) > 0])
        train_frag_dist[num_fragments] += 1
    for f in val_files:
        mask_file = f.replace('.jpg', '.png')
        mask = cv2.imread(os.path.join(mask_folder, mask_file), cv2.IMREAD_GRAYSCALE)
        num_fragments = len(np.unique(mask)[np.unique(mask) > 0])
        val_frag_dist[num_fragments] += 1

    print("\nFragment distribution:")
    print("Training set:", dict(train_frag_dist))
    print("Validation set:", dict(val_frag_dist))

def convert_mask_to_yolo(mask_path, output_label_path, image_shape, class_id=1):
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    # Add morphological operation to separate overlapping regions
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    if mask is None:
        raise ValueError(f"Could not load mask at {mask_path}")

    if mask.shape != image_shape:
        mask = cv2.resize(mask, (image_shape[1], image_shape[0]), interpolation=cv2.INTER_NEAREST)

    unique_values = np.unique(mask)
    unique_values = unique_values[unique_values > 0]

    if len(unique_values) == 0:
        return None

    height, width = image_shape
    with open(output_label_path, 'w') as f:
        for value in unique_values:
            instance_mask = (mask == value).astype(np.uint8) * 255
            
            contours, _ = cv2.findContours(instance_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                continue

            for contour in contours:
                contour = contour.reshape(-1, 2)
                points = contour / [width, height]
                points_str = " ".join(map(str, points.flatten()))
                f.write(f"{class_id} {points_str}\n")

    if os.stat(output_label_path).st_size == 0:
        os.remove(output_label_path)

def process_dataset(image_dir, mask_dir, label_dir):
    os.makedirs(label_dir, exist_ok=True)
    
    for img_file in os.listdir(image_dir):
        if img_file.endswith('.jpg'):
            img_path = os.path.join(image_dir, img_file)
            mask_file = img_file.replace('.jpg', '.png')
            mask_path = os.path.join(mask_dir, mask_file)
            label_path = os.path.join(label_dir, img_file.replace('.jpg', '.txt'))
            
            if os.path.exists(mask_path):
                img = cv2.imread(img_path)
                if img is not None:
                    convert_mask_to_yolo(mask_path, label_path, img.shape[:2])

def visualize_yolo_segmentation(image_path, label_path, output_image_path=None):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image at {image_path}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = image.shape[:2]

    contours = []
    try:
        with open(label_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split()
                if len(parts) < 3: 
                    continue
                class_id = int(parts[0]) 
                coords = np.array(parts[1:], dtype=np.float32).reshape(-1, 2) 
                coords[:, 0] *= width 
                coords[:, 1] *= height
                contours.append(coords.astype(np.int32))
    except FileNotFoundError:
        raise ValueError(f"Could not find label file at {label_path}")

    if not contours:
        print("No valid contours found in the label file.")
        return

    overlay_image = image.copy()
    cv2.polylines(overlay_image, contours, isClosed=True, color=(255, 0, 0), thickness=2)
    plt.figure(figsize=(8, 6))
    plt.title("Image with YOLO Segmentation Overlay")
    plt.imshow(overlay_image)
    plt.axis('off')
    plt.show()
    if output_image_path:
        cv2.imwrite(output_image_path, cv2.cvtColor(overlay_image, cv2.COLOR_RGB2BGR))
        print(f"Overlay image saved at: {output_image_path}")

def random_visualize_yolo_segmentation(image_dir, label_dir, output_image_path=None):
    if not os.path.exists(image_dir):
        raise ValueError(f"Image directory '{image_dir}' does not exist")
    if not os.path.exists(label_dir):
        raise ValueError(f"Label directory '{label_dir}' does not exist")

    image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
    if not image_files:
        raise ValueError(f"No .jpg images found in {image_dir}")

    random_image_file = random.choice(image_files)
    image_path = os.path.join(image_dir, random_image_file)
    label_file = random_image_file.replace('.jpg', '.txt')
    label_path = os.path.join(label_dir, label_file)

    if not os.path.exists(label_path):
        raise FileNotFoundError(f"Label file '{label_file}' not found for image '{random_image_file}'")

    visualize_yolo_segmentation(image_path, label_path, output_image_path)

    print(f"Displayed: {random_image_file} with annotations from {label_file}")

def create_yolo_yaml(
    data_dir, train_images_path, val_images_path, output_yaml_path, num_classes, class_names):

    if not os.path.exists(train_images_path):
        raise FileNotFoundError(f"Training images directory not found: {train_images_path}")
    if not os.path.exists(val_images_path):
        raise FileNotFoundError(f"Validation images directory not found: {val_images_path}")
    yaml_data = {
        "path": data_dir,              
        "train": train_images_path, 
        "val": val_images_path,  
        "nc": num_classes,      
        "names": class_names  
    }
    with open(output_yaml_path, "w") as f:
        yaml.dump(yaml_data, f, default_flow_style=False)

    print(f"YAML file created at: {output_yaml_path}")