import hashlib
from datetime import datetime
from django.shortcuts import render
from web3 import Web3
from .utils.pinata import upload_to_pinata

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# Contract setup
contract_address = "0xFc85E2d9Ce4e97f3B424084A8a33AeE52D8Fa54e"
contract_abi =[
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "hash",
				"type": "string"
			}
		],
		"name": "registerDocument",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"name": "documentHashes",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "hash",
				"type": "string"
			}
		],
		"name": "verifyDocument",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Global variables for reupload context
last_reupload_hash = None
last_reupload_cid = None

def index(request):
    global last_reupload_hash, last_reupload_cid
    context = {
        "message": "",
        "ipfs_url": None,
        "result": None,
        "active_tab": "upload",
        "document_details": None
    }

    action = request.POST.get("action")

    # Upload new document
    if action == "upload" and request.FILES.get("document"):
        doc = request.FILES["document"]
        doc_bytes = doc.read()
        doc_hash = hashlib.sha256(doc_bytes).hexdigest()

        existing_address = contract.functions.verifyDocument(doc_hash).call()
        if int(existing_address, 16) != 0:
            context["message"] = "❗ Duplicate document detected - already registered"
        else:
            sender_address = w3.eth.accounts[0]
            tx_hash = contract.functions.registerDocument(doc_hash).transact({'from': sender_address})
            w3.eth.wait_for_transaction_receipt(tx_hash)

            try:
                doc.seek(0)
                ipfs_url = upload_to_pinata(doc)
                context["message"] = "✅ Document registered successfully"
                context["ipfs_url"] = ipfs_url
            except Exception as e:
                context["message"] = f"⚠️ Registered on blockchain, but IPFS upload failed: {str(e)}"

        context["document_details"] = {
            "status": context["message"],
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": doc.name,
            "size": f"{doc.size} bytes",
            "hash": doc_hash,
            "ipfs_cid": context["ipfs_url"].split("/")[-1] if context["ipfs_url"] else "N/A"
        }
        context["active_tab"] = "upload"

    # Verify document authenticity
    elif action == "verify" and request.FILES.get("verify_document"):
        uploaded_file = request.FILES["verify_document"]
        file_bytes = uploaded_file.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        registered_address = contract.functions.verifyDocument(file_hash).call()

        if int(registered_address, 16) != 0:
            context["result"] = "✅ Valid document. No tampering detected"
        else:
            context["result"] = "❌ Document not found on the blockchain."

        context["document_details"] = {
            "status": context["result"],
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": uploaded_file.name,
            "size": f"{uploaded_file.size} bytes",
            "hash": file_hash,
            "ipfs_cid": "N/A"
        }
        context["active_tab"] = "verify"

    # Reupload document for comparison
    elif action == "reupload" and request.FILES.get("reupload_document"):
        doc = request.FILES["reupload_document"]
        doc_bytes = doc.read()
        doc_hash = hashlib.sha256(doc_bytes).hexdigest()

        existing_address = contract.functions.verifyDocument(doc_hash).call()
        if int(existing_address, 16) == 0:
            context["message"] = "❌ Document is not yet registered on blockchain!"
        else:
            try:
                doc.seek(0)
                ipfs_url = upload_to_pinata(doc)
                last_reupload_hash = doc_hash
                last_reupload_cid = ipfs_url
                context["message"] = "🔁 Document reuploaded. Compare hash and CID"
                context["ipfs_url"] = ipfs_url
            except Exception as e:
                context["message"] = f"⚠️ Reupload failed: {str(e)}"

        context["document_details"] = {
            "status": context["message"],
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": doc.name,
            "size": f"{doc.size} bytes",
            "hash": doc_hash,
            "ipfs_cid": context["ipfs_url"].split("/")[-1] if context["ipfs_url"] else "N/A"
        }
        context["active_tab"] = "reupload"

    return render(request, "authsystem/index.html", context)
