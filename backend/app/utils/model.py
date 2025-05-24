import os, base64
import numpy as np
from PIL import Image
from random import randint
from io import BytesIO
import matplotlib.pyplot as plt
import cv2
class Model:
    def __init__(
        self,
        repo_id: str = "magnusdtd/aic-hcmus-2025-yolo11m-seg",
        model_filename: str = "yolov11m_finetuned.pt",
    ):
        from ultralytics import YOLO
        from huggingface_hub import hf_hub_download
        
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

    @staticmethod
    def get_overlaid_mask(image: Image, masks: np.ndarray):  
        image_array = np.array(image)
        if image_array.shape[-1] == 4: 
            image_array = image_array[:, :, :3]

        resized_masks = [
            np.array(Image.fromarray(mask.astype(np.uint8)).resize(image.size, Image.NEAREST), dtype=bool)
            for mask in masks
        ]
        num_masks = len(resized_masks)
        colors = [tuple(randint(0, 255) for _ in range(3)) for _ in range(num_masks)]

        overlaid_image = image_array.copy()
        for mask, color in zip(resized_masks, colors):
            overlaid_image[mask] = np.array(color, dtype=np.uint8) * 0.5 + overlaid_image[mask] * 0.5

        return overlaid_image

    def get_diameter(self, masks):
        diameters = []
        for mask in masks:
            area = np.sum(mask) 
            if area > 0:  
                diameter = np.sqrt(4 * area / np.pi)
                diameters.append(diameter)

        diameters = np.array(diameters)
        diameters_sorted = np.sort(diameters)
        return diameters_sorted
    
    @staticmethod
    def draw_cdf_chart(diameters: np.ndarray, is_calibrated: bool = False, unit: str = 'pixels'):
        """Draw the CDF chart of the diameters"""  
        if not is_calibrated:
            unit = "pixels"
            
        D10 = np.percentile(diameters, 10)
        D50 = np.percentile(diameters, 50)
        D90 = np.percentile(diameters, 90)
        Dmin = diameters.min()
        Dmax = diameters.max()
        Davg = diameters.mean()

        cdf = np.arange(1, len(diameters) + 1) / len(diameters) * 100
        plt.figure(figsize=(12, 8))
        plt.plot(diameters, cdf, marker='.', linestyle='-', label='CDF', color='blue')

        # Add vertical lines for D10, D50, D90
        plt.axvline(D10, color='deepskyblue', linestyle='--', label=f'D10 = {D10:.2f} {unit}')
        plt.axvline(D50, color='purple', linestyle='--', label=f'D50 = {D50:.2f} {unit}')
        plt.axvline(D90, color='blue', linestyle='--', label=f'D90 = {D90:.2f} {unit}')
        plt.axvline(Dmin, color='green', linestyle='--', label=f'Dmin = {Dmin:.2f} {unit}')
        plt.axvline(Dmax, color='red', linestyle='--', label=f'Dmax = {Dmax:.2f} {unit}')
        plt.axvline(Davg, color='orange', linestyle='--', label=f'Davg = {Davg:.2f} {unit}')

        # Add horizontal lines for 10%, 50%, 90%
        plt.axhline(10, color='deepskyblue', linestyle='--', alpha=0.3)
        plt.axhline(50, color='purple', linestyle='--', alpha=0.3)
        plt.axhline(90, color='blue', linestyle='--', alpha=0.3)

        max_x = diameters.max()  
        plt.text(max_x * 1.01, 10, '10%', color='deepskyblue', verticalalignment='bottom', fontsize=10)
        plt.text(max_x * 1.01, 50, '50%', color='purple', verticalalignment='bottom', fontsize=10)
        plt.text(max_x * 1.01, 90, '90%', color='blue', verticalalignment='bottom', fontsize=10)

        # Add calibration status text
        calibration_text = "Calibrated" if is_calibrated else "Not Calibrated"
        plt.text(0.98, 0.02, f"{calibration_text}", fontsize=12, color='black',
                 ha='right', va='bottom', transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))

        # Customize the plot
        plt.xlabel(f'Equivalent Diameter (D) [{unit}]')
        plt.ylabel(f'Cumulative Percentage (%)')
        plt.title(f'Cumulative Distribution Function (CDF) of Equivalent Diameter of Fragments\nTotal Fragments: {len(diameters)}')
        plt.grid(True)
        plt.legend()

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        return Image.open(buf)
    
    def _detect_calibration_object(self, img):
        """Detect calibration object (a red ball) in the image"""
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 | mask2

        kernel = np.ones((5, 5), np.uint8)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        calibration_balls = []
        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)

            if area < 100 or perimeter == 0:
                continue

            circularity = 4 * np.pi * area / (perimeter * perimeter)

            if circularity > 0.7:
                (x, y), radius = cv2.minEnclosingCircle(contour)
                calibration_balls.append((int(x), int(y), int(radius)))

        if calibration_balls:
            calibration_balls.sort(key=lambda x: x[2], reverse=True)
            return True, calibration_balls[0]

        return False, None

    def calibrate(self, img: Image, diameters: np.ndarray, centre: tuple[float, float], real_radius: float, pixel_radius: float):
        """Calibrate the diameters using the red ball"""
        if pixel_radius == 0:
            print("Pixel radius is zero, cannot calibrate.")
            return diameters
        pixel_circle_area = np.pi * (pixel_radius ** 2)
        real_circle_area = np.pi * (real_radius ** 2)
        scaling_factor = real_circle_area / pixel_circle_area

        return np.array([d * scaling_factor for d in diameters])

    async def predict(self, img: Image, real_radius: float = None, unit: str = 'pixels', conf: float=0.5, iou: float=0.5, save: bool=False):
        print("Model trying to inference...")
        try:
            results = self.model.predict(source=img, conf=conf, iou=iou, save=save)
            if results[0].masks is None:
                print("No masks were generated by the model.")
                return None
            masks = results[0].masks.data.cpu().numpy()
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None

        is_calibrated, red_ball = self._detect_calibration_object(np.array(img))

        diameters = self.get_diameter(masks)
        overlaid_img = self.get_overlaid_mask(img, masks)
        if real_radius is not None and red_ball is not None:
            (x, y, pixel_radius) = red_ball
            centre = (x, y)
            is_calibrated = True
            diameters = self.calibrate(img, diameters, centre, real_radius, pixel_radius)
        else:
            is_calibrated = False

        cdf_chart = self.draw_cdf_chart(diameters, is_calibrated, unit)

        print("Model inference successfully")
        return (masks, overlaid_img, diameters, cdf_chart, is_calibrated)

