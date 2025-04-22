import requests
from pprint import pprint
from IPython.display import JSON
import json
import cv2
import os
import random
import pandas as pd
import time
from datetime import timedelta

# API Configuration
TOKEN = ""
CURRENT_DIRECTORY = "selected_images"

def recognize_license_plate(image_path, token, regions=["sg"], strict_region=True, mmc=True):
    """
    Recognize license plate from an image using PlateRecognizer API.
    
    Args:
        image_path (str): Path to the image file
        token (str): API token
        regions (list): List of regions to consider
        strict_region (bool): Whether to use strict region detection
        mmc (bool): Whether to use make/model classification
        
    Returns:
        dict: API response containing plate recognition results
    """
    start_time = time.time()
    url = "https://api.platerecognizer.com/v1/plate-reader/"
    headers = {"Authorization": f"Token {token}"}
    
    with open(image_path, "rb") as fp:
        data = {
            "regions": regions,       
            "mmc": str(mmc).lower()  
        }
        if strict_region:
            data["config"] = json.dumps({"region": "strict"})

        response = requests.post(url, headers=headers, files={"upload": fp}, data=data)
        
        if response.status_code in [200, 201]:
            end_time = time.time()
            print(f"API call completed in {timedelta(seconds=end_time - start_time)}")
            return response.json()
        else:
            print("Error:", response.status_code, response.text)
            return None

def process_single_image(image_path, image_name, max_retries=3):
    """
    Process a single image with retry mechanism.
    
    Args:
        image_path (str): Path to the image file
        image_name (str): Name of the image file
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        tuple: (result_dict, full_response)
    """
    start_time = time.time()

    # Initialize variables
    plate = None
    make = None
    model = None
    response = None
    
    for attempt in range(max_retries):
        print(f"\nProcessing: {image_name} (Attempt {attempt + 1})")
        response = recognize_license_plate(image_path, TOKEN)
        
        if response and response.get("results"):
            result = response["results"][0]
            plate = result.get("plate", None)
            
            if "model_make" in result and result["model_make"]:
                make = result["model_make"][0].get("make", None)
                model = result["model_make"][0].get("model", None)
            else:
                make = model = None
            
            should_retry = False
            
            # Retry if plate is not detected
            if not plate:
                should_retry = True
                print("Retrying: No plate detected")
            
            # Retry if make or model is empty when model_make exists
            elif "model_make" in result and result["model_make"] and (not make or not model):
                should_retry = True
                print("Retrying: Make or model information is missing")
            
            # If we don't need to retry, return the results
            if not should_retry:
                end_time = time.time()
                print(f"Image processing completed in {timedelta(seconds=end_time - start_time)}")
                return {
                    "Image Number (Filename)": image_name,
                    "License Plate": plate.upper(),
                    "Make": make.title() if make else None,
                    "Model": model.title() if model else None
                }, response
            
            # If we need to retry and this isn't the last attempt
            if attempt < max_retries - 1:
                print(f"Retrying {image_name}...")
                time.sleep(2) 
            
        else:
            # Retry if the API call failed
            if attempt < max_retries - 1:
                print(f"Retrying {image_name} due to API failure...")
                time.sleep(2)
    
    end_time = time.time()
    print(f"Image processing completed in {timedelta(seconds=end_time - start_time)}")
    
    # Return whatever we have, after all retries
    return {
        "Image Number (Filename)": image_name,
        "License Plate": plate.upper() if plate else None,
        "Make": make.title() if make else None,
        "Model": model.title() if model else None
    }, response

def save_results(results, full_responses, excel_dir=".", json_dir="."):
    """
    Save results to Excel and JSON files in specified directories.
    
    Args:
        results (list): List of recognition results
        full_responses (list): List of full API responses
        excel_dir (str): Directory to save Excel file
        json_dir (str): Directory to save JSON files
    """
    # Create directories if they don't exist
    os.makedirs(excel_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)
    
    # Save full responses
    full_responses_path = os.path.join(json_dir, "full_responses.json")
    with open(full_responses_path, "w") as f:
        json.dump(full_responses, f, indent=2)
    
    # Save results
    df = pd.DataFrame(results)
    excel_path = os.path.join(excel_dir, "recognized_plates.xlsx")
    json_path = os.path.join(json_dir, "recognized_plates.json")
    
    df.to_excel(excel_path, index=False)
    df.to_json(json_path, orient="records", indent=2)
    
    print(f"\n✅ Results saved to {excel_path}")
    print(f"✅ Results saved to {json_path}")
    print(f"✅ Full responses saved to {full_responses_path}")

def process_all_images(directory=CURRENT_DIRECTORY, excel_dir="All_results", json_dir="All_results"):
    """
    Process all images in the specified directory.
    
    Args:
        directory (str): Directory containing images to process
        excel_dir (str): Directory to save Excel file
        json_dir (str): Directory to save JSON files
        
    Returns:
        tuple: (results_df, full_responses)
    """
    start_time = time.time()
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    results = []
    full_responses = []

    for image in image_files:
        image_path = os.path.join(directory, image)
        result, response = process_single_image(image_path, image)
        
        results.append(result)
        if response:
            full_responses.append({
                "Image Number (Filename)": image,
                "Full Response": response
            })

    # Sort results by image number
    results = sorted(results, key=lambda x: int(x["Image Number (Filename)"].split('.')[0]))
    full_responses = sorted(full_responses, key=lambda x: int(x["Image Number (Filename)"].split('.')[0]))

    # Save results
    save_results(results, full_responses, excel_dir, json_dir)
    
    end_time = time.time()
    print(f"\nTotal processing time for all images: {timedelta(seconds=end_time - start_time)}")
    return pd.DataFrame(results), full_responses

def process_random_images(num_images=2, directory=CURRENT_DIRECTORY, excel_dir="Subset_results", json_dir="Subset_results"):
    """
    Process a random selection of images from the directory.
    
    Args:
        num_images (int): Number of random images to process
        directory (str): Directory containing images to process
        excel_dir (str): Directory to save Excel file
        json_dir (str): Directory to save JSON files
        
    Returns:
        tuple: (results_df, full_responses)
    """
    start_time = time.time()
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    random_images = random.sample(image_files, min(num_images, len(image_files)))
    
    results = []
    full_responses = []

    for image in random_images:
        image_path = os.path.join(directory, image)
        result, response = process_single_image(image_path, image)
        
        results.append(result)
        if response:
            full_responses.append({
                "Image Number (Filename)": image,
                "Full Response": response
            })

    # Sort results by image number
    results = sorted(results, key=lambda x: int(x["Image Number (Filename)"].split('.')[0]))
    full_responses = sorted(full_responses, key=lambda x: int(x["Image Number (Filename)"].split('.')[0]))

    # Save results
    save_results(results, full_responses, excel_dir, json_dir)
    
    end_time = time.time()
    print(f"\nTotal processing time for random images: {timedelta(seconds=end_time - start_time)}")
    return pd.DataFrame(results), full_responses

def test_single_image(image_path, directory = "test_results"):
    """
    Test the license plate recognition on a single image.
    
    Args:
        image_path (str): Path to the image file to test
        directory (str): Directory to save test results
        
    Returns:
        tuple: (result_dict, full_response)
    """
    start_time = time.time()
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None, None
        
    print(f"\nTesting image: {os.path.basename(image_path)}")
    result, response = process_single_image(image_path, os.path.basename(image_path))
    
    if result:
        print("\nResults:")
        print(f"License Plate: {result['License Plate']}")
        print(f"Make: {result['Make']}")
        print(f"Model: {result['Model']}")
        
        # Save results to a test directory
        os.makedirs(directory, exist_ok=True)
        
        # Save to Excel
        df = pd.DataFrame([result])
        excel_path = os.path.join(directory, "test_result.xlsx")
        df.to_excel(excel_path, index=False)
        
        # Save full response to JSON
        if response:
            json_path = os.path.join(directory, "test_response.json")
            with open(json_path, "w") as f:
                json.dump(response, f, indent=2)
            
            print(f"\n✅ Results saved to {excel_path}")
            print(f"✅ Full response saved to {json_path}")
    
    end_time = time.time()
    print(f"\nTotal test time: {timedelta(seconds=end_time - start_time)}")
    return result, response

if __name__ == "__main__":
    # Example usage with custom output directories
    excel_output_dir = "output/excel" # Modify this to the directory you want to save the excel file to
    json_output_dir = "output/json" # Modify this to the directory you want to save the json file to
    CURRENT_DIRECTORY = "selected_images" # Modify this to the directory containing the images you want to process
    
    # Example of processing all images
    print("Processing all images...")
    all_results_df, all_responses = process_all_images(excel_dir=excel_output_dir, json_dir=json_output_dir)
    
    # Process random images
    # print("\nProcessing random images...")
    # random_results_df, random_responses = process_random_images(
    #     num_images=3,
    #     directory = CURRENT_DIRECTORY,
    #     excel_dir=excel_output_dir,
    #     json_dir=json_output_dir
    # )


    # Example of testing a single image
    # test_image_path = "selected_images/21.jpg"
    # test_dir = "test_results"
    # print("Testing single image...")
    # test_single_image(test_image_path, directory = test_dir)
