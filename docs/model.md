# Fragment Segmentation Model

## Overview

The AIC-HCMUS Fragment Segmentation Model is designed to identify and segment rock fragments in images. It leverages a YOLOv11-based architecture to detect individual fragments, create precise segmentation masks, and estimate fragment equivalent diameters.

## Model Architecture

- **Base Model**: YOLOv11m with segmentation capabilities
- **Source**: Hosted on Hugging Face Hub (`magnusdtd/aic-hcmus-2025-yolo11m-seg`)
- **File**: `yolov11m_finetuned.pt`

## Key Features

- **Fragment Detection**: Precisely identifies individual rock fragments in images
- **Instance Segmentation**: Creates accurate pixel masks for each detected fragment
- **Equivalent Diameter Estimation**: Calculates the equivalent diameter based on fragment geometry
- **Visualization**: Generates overlay images with colored masks for visual inspection

## Mathematical Approach

### Shape Analysis
For each detected fragment, the model calculates several geometric properties:

- **Circularity**: $C = \frac{4\pi A}{P^2}$
    - Where $A$ is the contour area and $P$ is the perimeter
    - Perfect circles have $C = 1$
    - Complex, irregular shapes have $C \ll 1$

- **Equivalent Diameter**: $D_{eq} = \sqrt{\frac{4A}{\pi}}$
    - Diameter of a circle with the same area as the fragment

The equivalent diameter provides a standardized measure of fragment size, allowing for consistent comparison between fragments of varying shapes.

### Calibration Detection
For calibration objects (typically red ball), the model analyzes contours using:

$$C = \frac{4\pi A}{P^2} > 0.7$$

Where calibration objects must have high circularity to be considered valid reference objects.

## Performance Notes
- Default execution on CPU
- Processing time depends on image resolution and fragment count
- Optimal results with clear, well-separated fragments
- Recommended image resolution: 512x512 pixels

## Limitations
- Equivalent diameter estimates are based on 2D projections
- Performance may decrease with crowded or overlapping fragments
- Best results achieved with good lighting and contrast
