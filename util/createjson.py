import json
import os
import re
import datetime

def extract_and_compare_date(filename):
    """Extracts the date part from a filename, reformats it, and compares it to today's date.

    Args:
        filename (str): The filename to extract the date from.

    Returns:
        bool: True if the extracted date matches today's date, False otherwise.
    """
    # Use regular expression to match date format (assuming consistent format)
    pattern = r"detection_data_(\d{2}-\d{2}-\d{4})\.json"
    match = re.search(pattern, filename)

    if match:
        # Extract the matched date string 
        date_str = match.group(1)

        # Reformat the date string (assuming desired format is YYYY-MM-DD)
        date_obj = datetime.datetime.strptime(date_str, "%d-%m-%Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")

        # Get today's date
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        # Compare the formatted date with today's date
        return formatted_date == today
    else:
        # Handle case where filename doesn't match the expected format (optional)
        print(f"Error: Filename '{filename}' does not match expected format.")
        return False

def save_into_json_file(accumulate:list, all_fly_data:dict, filename:str):
    """Save the given information into a JSON file.
    
    Args:
        filename (str): The name of the output file.    
        accumulate (list): The information to be saved. It should have a list of dict of keys as  
            "fly_id", "date_time", "confidence" and values corresponding to their respective  
            attributes. For example:
            
            data = [
                {   
                "fly_id": 1,
                "date_time": "16-04-24_17-02-07",
                "confidence": "85.09"
                },
                {
                "fly_id": 2,
                "date_time": "16-04-24_17-02-07",
                "confidence": "89.99"
                },
                {
                "fly_id": 3,
                "date_time": "16-04-24_17-02-08",
                "confidence": "86.68"
                }
            ]
        all_fly_data (dict): The information to be saved. It should have data list (accumulate)
                
                { "data": [
                    {   
                    "fly_id": 1,
                    "date_time": "16-04-24_17-02-07",
                    "confidence": "85.09"
                    },
                    {
                    "fly_id": 2,
                    "date_time": "16-04-24_17-02-07",
                    "confidence": "89.99"
                    },
                    {
                    "fly_id": 3,
                    "date_time": "16-04-24_17-02-08",
                    "confidence": "86.68"
                    }
                ]}
                
    Returns:
        all_fly_data dictionary with the new data added to it.
        
    Raises:
        TypeError: If `filename` is not a string or if `fly_info` is not a dict.
    """ 
    
    # all_fly_data = {accumulate} # Dictionary that will contain "data" as key and empty list as value
    # accumulate  = [] # List of dictionaries that will contain fly_info per frame
    
    # Check if file is open and filename is == date.now()
    assert type(filename)==str,"Error! Filename must be a string."
    
    # Check if file is  open and filename == date.now()
    if extract_and_compare_date(filename): 
        
        # Loop through each element of accumulate list and add them to data
        for dict in accumulate:
            all_fly_data.append(dict)   
    
        # Dump data to JSON file
        json.dump(all_fly_data, filename, indent=4)
    return all_fly_data

# print(all_fly_data)

data = [
    {'fly_id': 1, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.38},
    {'fly_id': 2, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.61}, 
    {'fly_id': 3, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.37}, 
    {'fly_id': 4, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.09}, 
    {'fly_id': 5, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.22}, 
    {'fly_id': 6, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.65}, 
    {'fly_id': 7, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.83}, 
    {'fly_id': 8, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.37}, 
    {'fly_id': 9, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.02}, 
    {'fly_id': 10, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.92}
    ]

# Example filename (assuming today's date is 2024-04-17)
filename = "detection_data_17-04-2024.json"

# Call the function (optional path argument can be omitted)
all_fly_data = save_into_json_file(data, {}, filename)

print(all_fly_data)

{'data': [
    {'fly_id': 1, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.38},
    {'fly_id': 2, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.61}, 
    {'fly_id': 3, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.37}, 
    {'fly_id': 4, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.09}, 
    {'fly_id': 5, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.22}, 
    {'fly_id': 6, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.65}, 
    {'fly_id': 7, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.83}, 
    {'fly_id': 8, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.37}, 
    {'fly_id': 9, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.02}, 
    {'fly_id': 10, 'date_time': '2024-04-16 11:51:06', 'confidence': 0.92}
    ]
}

# 
# # Function to generate random confidence value
# def generate_random_number():
#     return random.randint(0, 99) / 100
# 
# # Example usage
# filename = "detection_data_17-04-2024.json"
# if extract_and_compare_date(filename):
#   print("Extracted date matches today's date.")
# else:
#   print("Extracted date does not match today's date.")