import os
import cv2
import json
import numpy as np
import random
from pycocotools.coco import COCO
import torch
import torchvision.transforms.functional as F
import matplotlib.pyplot as plt
from torchvision.utils import draw_segmentation_masks
from PIL import Image

def convert_dataset_to_coco(train_images_dir, train_masks_dir, output_json):
    image_id = 1
    annotation_id = 1
    coco_data = {
        "images": [],
        "annotations": [],
        "categories": [{"id": 1, "name": "fragment", "supercategory": "rock"}],
    }

    image_files = sorted(os.listdir(train_images_dir))

    for image_file in image_files:
        image_path = os.path.join(train_images_dir, image_file)
        mask_path = os.path.join(train_masks_dir, image_file.replace('.jpg', '.png'))  

        if not os.path.exists(mask_path):
            print(f"Warning: Mask not found for {image_file}")
            continue

        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        image = cv2.imread(image_path)
        height, width = mask.shape

        coco_data["images"].append({
            "id": image_id,
            "file_name": image_file,
            "height": height,
            "width": width
        })
        unique_ids = np.unique(mask)
        unique_ids = unique_ids[unique_ids != 0]

        for obj_id in unique_ids:
            obj_mask = (mask == obj_id).astype(np.uint8) * 255
            contours, _ = cv2.findContours(obj_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if len(contour) < 3:
                    continue

                segmentation = contour.flatten().tolist()
                x, y, w, h = cv2.boundingRect(contour)
                coco_data["annotations"].append({
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": 1,
                    "segmentation": [segmentation],
                    "area": w * h,
                    "bbox": [x, y, w, h],
                    "iscrowd": 0
                })
                annotation_id += 1
        image_id += 1

    with open(output_json, "w") as f:
        json.dump(coco_data, f, indent=4)
    print(f"COCO dataset saved to {output_json}")

def split_annotations_file(coco_file, train_ratio = 0.8):
    with open(coco_file, 'r') as f:
        data = json.load(f)
    
    images = data['images']
    annotations = data['annotations']
    categories = data['categories']
    
    
    num_images = len(images)
    num_train = int(num_images * train_ratio)
    
    random.shuffle(images)
    train_images = images[:num_train]
    val_images = images[num_train:]
    
    train_image_ids = {img['id'] for img in train_images}
    val_image_ids = {img['id'] for img in val_images}
    
    train_annotations = [ann for ann in annotations if ann['image_id'] in train_image_ids]
    val_annotations = [ann for ann in annotations if ann['image_id'] in val_image_ids]
    
    train_data = {
        'images': train_images,
        'annotations': train_annotations,
        'categories': categories
    }
    

    val_data = {
        'images': val_images,
        'annotations': val_annotations,
        'categories': categories
    }
    
    with open('train.json', 'w') as f:
        json.dump(train_data, f, indent=4)
    with open('val.json', 'w') as f:
        json.dump(val_data, f, indent=4)
    
    print(f"Training set: {len(train_images)} images, {len(train_annotations)} annotations")
    print(f"Validation set: {len(val_images)} images, {len(val_annotations)} annotations")

def random_image_display(image_folder_path, annotation_file):
    coco = COCO(annotation_file)
    image_ids = coco.getImgIds()

    if not image_ids:
        print(f"No images found in the dataset at {image_folder_path}")
        return
    chosen_image_id = random.choice(image_ids)
    img_info = coco.loadImgs(chosen_image_id)[0]
    image_path = os.path.join(image_folder_path, img_info['file_name'])
    image = Image.open(image_path).convert("RGB")
    annotation_ids = coco.getAnnIds(imgIds=chosen_image_id)
    annotations = coco.loadAnns(annotation_ids)
    mask = torch.zeros((len(annotations), image.height, image.width), dtype=torch.uint8)
    colors = []
    for i, ann in enumerate(annotations):
        if 'segmentation' in ann:
            rle_mask = coco.annToMask(ann) 
            mask[i] = torch.tensor(rle_mask, dtype=torch.uint8)
            colors.append(tuple(random.randint(0, 255) for _ in range(3))) 
    
    image_tensor = F.to_tensor(image) * 255
    image_tensor = image_tensor.to(torch.uint8)
    output_image = draw_segmentation_masks(image_tensor, masks=mask.bool(), alpha=0.5, colors=colors)

    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.title(f"Original Image {chosen_image_id}")
    plt.imshow(image)

    plt.subplot(1, 2, 2)
    plt.title(f"Segmentation Mask {chosen_image_id}")
    plt.imshow(output_image.permute(1, 2, 0))

    plt.show()