import requests
import json

def get_ensembl_data(variant_id):
    server = "https://rest.ensembl.org"
    ext = f"/vep/human/id/{variant_id}"
    try:
        response = requests.get(server + ext, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"API Error: {e}")
        return None
