def get_all_keys(json_obj, keys_set=None):
    if keys_set is None:
        keys_set = set()
    
    if isinstance(json_obj, dict):
        # Add all keys from current dictionary
        for key, value in json_obj.items():
            keys_set.add(key)
            # Recursively process nested objects
            get_all_keys(value, keys_set)
            
    elif isinstance(json_obj, list):
        # Process each item in the list
        for item in json_obj:
            get_all_keys(item, keys_set)
            
    return keys_set

def extract_keys_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the file line by line for large files
            keys_set = set()
            for line in file:
                try:
                    json_data = json.loads(line.strip())
                    get_all_keys(json_data, keys_set)
                except json.JSONDecodeError:
                    continue
            return keys_set
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
    except Exception as e:
        print(f"Error: {str(e)}")
    return set()

# Example usage
import json

keys = extract_keys_from_file('data/raw/deleted_listings_sale.json')
print("All keys:", sorted(keys))