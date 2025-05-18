# Fragment Segmentation Model

## Overview

The AIC-HCMUS Fragment Segmentation Model is designed to identify and segment rock fragments in images. It leverages a YOLOv11-based architecture to detect individual fragments, create precise segmentation masks, and estimate fragment volumes.

## Model Architecture

- **Base Model**: YOLOv11m with segmentation capabilities
- **Source**: Hosted on Hugging Face Hub (`magnusdtd/aic-hcmus-2025-yolo11m-seg`)
- **File**: `yolov11m_finetuned.pt`

## Key Features

- **Fragment Detection**: Precisely identifies individual rock fragments in images
- **Instance Segmentation**: Creates accurate pixel masks for each detected fragment
- **Volume Estimation**: Calculates approximate volume based on fragment geometry
- **Visualization**: Generates overlay images with colored masks for visual inspection

## Mathematical Approach

### Shape Analysis
For each detected fragment, the model calculates several geometric properties:

- **Circularity**: $C = \frac{4\pi A}{P^2}$
    - Where $A$ is the contour area and $P$ is the perimeter
    - Perfect circles have $C = 1$
    - Complex, irregular shapes have $C \ll 1$

- **Aspect Ratio**: $AR = \frac{a}{b}$
    - Where $a$ and $b$ are the major and minor axes of the fitted ellipse

- **Equivalent Diameter**: $D_{eq} = \sqrt{\frac{4A}{\pi}}$
    - Diameter of a circle with the same area as the fragment

### Volume Estimation
Volume estimation uses a weighted combination of three methods:

- **Spherical Approximation**: $V_{sphere} = \frac{4}{3}\pi\left(\frac{D_{eq}}{2}\right)^3$

- **Ellipsoidal Approximation**: $V_{ellipsoid} = \frac{4}{3}\pi\left(\frac{a}{2}\right)\left(\frac{b}{2}\right)^2$
    - Assumes the third axis equals the minor axis

- **Empirical Formula**: $V_{empirical} = A^{1.5} \times (0.8 + 0.4C)$
    - Derived from experimental correlations

The final volume is a weighted average based on circularity:

$$V_{final} = \begin{cases}
0.6V_{sphere} + 0.2V_{ellipsoid} + 0.2V_{empirical} & \text{if } C > 0.8 \\
0.3V_{sphere} + 0.4V_{ellipsoid} + 0.3V_{empirical} & \text{if } C > 0.5 \\
0.1V_{sphere} + 0.5V_{ellipsoid} + 0.4V_{empirical} & \text{otherwise}
\end{cases}$$

This adaptive approach provides more accurate estimates across various fragment shapes.

### Calibration Detection
For calibration objects (typically red spheres), the model analyzes contours using:

$$C = \frac{4\pi A}{P^2} > 0.7$$

Where calibration objects must have high circularity to be considered valid reference objects.

## Performance Notes
- Default execution on CPU
- Processing time depends on image resolution and fragment count
- Optimal results with clear, well-separated fragments
- Recommended image resolution: 640×640 pixels

## Limitations
- Volume estimates are approximations based on 2D projections
- Performance may decrease with crowded or overlapping fragments
- Best results achieved with good lighting and contrast