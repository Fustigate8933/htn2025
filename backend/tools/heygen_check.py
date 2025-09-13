from dotenv import load_dotenv; load_dotenv()
import os, requests

key = os.getenv("HEYGEN_API_KEY")

r = requests.get(
    "https://api.heygen.com/v2/avatars",
    headers={"X-Api-Key": key}, 
    timeout=15
)
r.raise_for_status()
data = r.json()

avatars = data.get("avatars") or data.get("data") or []
print("HeyGen OK, avatars =", len(avatars))