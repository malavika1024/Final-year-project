import requests
from io import BytesIO

PINATA_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiI3ZWIzNTg3ZS03NTIzLTRmMGItYTZjZC1jNTk0OTBlOTU5NDYiLCJlbWFpbCI6ImFiaXNoZWtqb2VsLjAyQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaW5fcG9saWN5Ijp7InJlZ2lvbnMiOlt7ImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxLCJpZCI6IkZSQTEifSx7ImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxLCJpZCI6Ik5ZQzEifV0sInZlcnNpb24iOjF9LCJtZmFfZW5hYmxlZCI6ZmFsc2UsInN0YXR1cyI6IkFDVElWRSJ9LCJhdXRoZW50aWNhdGlvblR5cGUiOiJzY29wZWRLZXkiLCJzY29wZWRLZXlLZXkiOiI1YzY3YzE1ODQ3MmY4NTcyNDA3MSIsInNjb3BlZEtleVNlY3JldCI6IjE1Y2EyNWI0ZGVlYjcwZGMyZDczZjJiODNmYjU3ODg5NDhhZTQxMjZjZjhmMTAxMjYzMDlmNDA0YWQ5ZTk4ZmYiLCJleHAiOjE3NzYyNTgxNjF9.jiteihPycc0mZgjnTYgWwEbS7Q_6I4Z4Alv1YMr04Ls"

def upload_to_pinata(file):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}"
    }

    file_bytes = BytesIO(file.read())
    file.seek(0)

    files = {
        'file': (file.name, file_bytes)
    }

    response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        cid = response.json()['IpfsHash']
        return f"https://gateway.pinata.cloud/ipfs/{cid}"  # ⬅️ Gateway changed here
    else:
        raise Exception(f"Failed to upload to Pinata: {response.text}")
