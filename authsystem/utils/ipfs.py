# docauth/utils/ipfs.py

import requests

def upload_to_ipfs(file_obj):
    url = "http://127.0.0.1:5001/api/v0/add"
    files = {'file': file_obj}
    response = requests.post(url, files=files)

    if response.status_code == 200:
        ipfs_hash = response.json()['Hash']
        return f"https://ipfs.io/ipfs/{ipfs_hash}"
    else:
        raise Exception("Failed to upload to IPFS")
