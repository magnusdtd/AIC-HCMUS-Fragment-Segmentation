import os, base64
from ultralytics import YOLO
from huggingface_hub import hf_hub_download
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from random import randint

class Model:
    def __init__(
        self,
        repo_id: str = "magnusdtd/aic-hcmus-2025-yolo11m-seg",
        model_filename: str = "yolov11m_finetuned.pt",
    ):
        # Download the model file from Hugging Face Hub
        self.yolo_path = hf_hub_download(
            repo_id=repo_id,
            filename=model_filename,
            cache_dir=os.path.expanduser("~/.cache/huggingface/yolo"),
            force_filename=model_filename
        )

        # Load the YOLO model
        self.model = YOLO(self.yolo_path)
        self.model.info()
        self.model.to("cpu")

    def preprocess(self, img):
        pass

    def postprocess(self, model_result):
        pass

    def get_overlaid_mask(self, image: Image, binary_masks: np.ndarray):
        image_array = np.array(image)
        if image_array.shape[-1] == 4:  # Handle RGBA images
            image_array = image_array[:, :, :3]

        # Resize binary masks to match the image dimensions
        resized_masks = [
            np.array(Image.fromarray(mask.astype(np.uint8)).resize(image.size, Image.NEAREST), dtype=bool)
            for mask in binary_masks
        ]

        # Generate random colors for each mask
        num_masks = len(resized_masks)
        colors = [tuple(randint(0, 255) for _ in range(3)) for _ in range(num_masks)]

        # Overlay masks on the image
        overlaid_image = image_array.copy()
        for mask, color in zip(resized_masks, colors):
            overlaid_image[mask] = np.array(color, dtype=np.uint8) * 0.5 + overlaid_image[mask] * 0.5

        # Convert the overlaid image to base64
        buffer = BytesIO()
        Image.fromarray(overlaid_image.astype(np.uint8)).save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
  
    def _detect_calibration_object(self, img_rgb):
        """
        Detect calibration object (usually a red ball) in the image
        
        Parameters:
            img_rgb: Input image in RGB format
            
        Returns:
            has_calibration: Boolean indicating if calibration object was found
            calibration_obj: Tuple (x, y, radius) of the calibration object
        """
        try:
            # Convert to HSV color space for easier red color detection
            hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
            
            # Define red color range (red is at the beginning and end of HSV color range)
            lower_red1 = np.array([0, 120, 70])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 120, 70])
            upper_red2 = np.array([180, 255, 255])
            
            # Create mask for red regions
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = mask1 | mask2
            
            # Morphological operations to clean up the mask
            kernel = np.ones((5, 5), np.uint8)
            red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
            red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours in the mask
            contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by shape (close to circular)
            calibration_balls = []
            for contour in contours:
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                
                if area < 100 or perimeter == 0:
                    continue
                    
                # Calculate circularity of the contour
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # If circular enough, add to the list
                if circularity > 0.7:
                    (x, y), radius = cv2.minEnclosingCircle(contour)
                    calibration_balls.append((int(x), int(y), int(radius)))
            
            if calibration_balls:
                # Sort by radius in descending order and take the largest ball
                calibration_balls.sort(key=lambda x: x[2], reverse=True)
                return True, calibration_balls[0]
                
            return False, None
            
        except Exception as e:
            print(f"Error detecting calibration object: {e}")
            return False, None

    def get_volume(self, img, binary_masks):
        volumes = []
        if isinstance(binary_masks, np.ndarray) and binary_masks.ndim > 2:
            masks_list = [mask.astype(np.uint8) for mask in binary_masks]
        elif isinstance(binary_masks, list):
            masks_list = [mask.astype(np.uint8) for mask in binary_masks]
        else:
            masks_list = [binary_masks.astype(np.uint8)]
        
        for mask in masks_list:
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                volumes.append(0)
                continue
            contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            M = cv2.moments(contour)
            if M["m00"] == 0:
                volumes.append(0)
                continue
            try:
                (x, y), (major_axis, minor_axis), angle = cv2.fitEllipse(contour)
                aspect_ratio = major_axis / minor_axis if minor_axis > 0 else 1 
                circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                equivalent_diameter = np.sqrt(4 * area / np.pi)
                
                sphere_volume = (4/3) * np.pi * (equivalent_diameter/2)**3
                
                ellipsoid_volume = (4/3) * np.pi * (major_axis/2) * (minor_axis/2) * (minor_axis/2)
                
                empirical_volume = area**1.5 * (0.8 + 0.4 * circularity)
                
                if circularity > 0.8:  
                    final_volume = 0.6 * sphere_volume + 0.2 * ellipsoid_volume + 0.2 * empirical_volume
                elif circularity > 0.5:  
                    final_volume = 0.3 * sphere_volume + 0.4 * ellipsoid_volume + 0.3 * empirical_volume
                else: 
                    final_volume = 0.1 * sphere_volume + 0.5 * ellipsoid_volume + 0.4 * empirical_volume   
                volumes.append(float(final_volume))
            except Exception as e:
                volumes.append(float(area**1.5 * 0.8))
        
        return volumes

    async def predict(self, img: Image, conf: float=0.5, iou: float=0.5, save: bool=False):
        print("Model trying to inference...")
        try:
            results = self.model.predict(source=img, conf=conf, iou=iou, save=save)
            if results[0].masks is None:
                print("No masks were generated by the model.")
                return None
            masks = results[0].masks.data.cpu().numpy()

            print("Mask shape: ", masks.shape)
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None
        
        volumes = self.get_volume(img, masks)
        is_calibrated = False
        overlaid_img = self.get_overlaid_mask(img, masks)
        print("Model inference successfully")
        return (masks, overlaid_img, volumes, is_calibrated)

model = Model()
