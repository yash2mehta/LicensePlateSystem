# License Plate Recognition System User Guide

## 1. Overview

The License Plate Recognition System is a Python-based application that utilizes the Plate Recognizer API to detect and recognize license plates from images. The system can:
- Process single or multiple images
- Extract license plate numbers, vehicle make, and model information
- Save results in both Excel and JSON formats
- Handle retries for failed recognition attempts
- Process random subsets of images for testing

## 2. Installation & Setup

### Prerequisites

- Python Version: Python 3.x
- Required Python packages:
  - requests
  - opencv-python (cv2)
  - pandas
  - IPython (optional, for notebook support)

### Directory Structure

```
Project Root:
├── selected_images/     # Directory for input images
├── output/             # Directory for processed results
├── test_results/       # Directory for test outputs
├── evaluation/         # Directory for evaluation results
├── PlateRecognizer.py  # Main Python script
└── PlateRecognizer.ipynb # Jupyter notebook version
```

### Setup Steps

1. Install Python 3.x from [python.org](https://www.python.org/downloads/)
2. Install required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```
3. Create the following directories in your project root:
   - `selected_images/` (for input images)
   - `output/`
   - `test_results/`
   - `evaluation/`
4. Place your license plate images in the `selected_images/` directory
5. Ensure you have a valid PlateRecognizer API token (You would require a paid subscription as the normal subscription only provides license plate and not make and model)

## 3. Running the System

### Running the Python Script

1. Open a terminal/command prompt
2. Navigate to your project directory
3. Run the script:
   ```bash
   python PlateRecognizer.py
   ```

## 4. Available Functions

### 1. Process All Images
- Processes all images in the `selected_images/` directory
- Excel & JSON results are saved in the `All_results/` directory, if not specified
- Usage: `process_all_images()`

### 2. Process Random Images
- Processes a specified number of random images (through num_images)
- Results are saved in the `Subset_results/` directory
- Usage: `process_random_images()`

### 3. Process Single Image
- Processes a single image with retry mechanism
- Usage: `process_single_image()`

### 4. Test Single Image
- Tests license plate recognition on a single image
- Results are saved in the `test_results/` directory
- Usage: `test_single_image()`

## 5. Possible Errors & Troubleshooting

### Common Issues and Solutions

#### 1. API Connection Errors
- Error: "Error: [status_code] [error message]"
- Solution:
  - Check your internet connection
  - Verify the API token is valid
  - Ensure the API endpoint is accessible

#### 2. Image Processing Errors
- Error: "No plate detected"
- Solution:
  - Ensure images are clear and well-lit
  - Check if the license plate is visible and not obstructed
  - Verify image format (supports .jpg, .jpeg, .png)

#### 3. File System Errors
- Error: "Directory not found" or "File not found"
- Solution:
  - Verify all required directories exist
  - Check file permissions
  - Ensure correct file paths are used

#### 4. Memory Errors
- Error: "Directory not found" or "File not found"
- Solution:
  - Verify all required directories exist
  - Check file permissions
  - Ensure correct file paths are used

### Best Practices
- Keep images in the supported formats (.jpg, .jpeg, .png)
- Ensure images are of good quality and well-lit
- Process images in batches if dealing with large numbers
- Regularly backup your results
- Monitor API usage to avoid rate limits

## Support

This guide provides a comprehensive overview of the License Plate Recognition System. For additional support or specific issues, please contact the development team or refer to the Plate Recognizer API documentation. 