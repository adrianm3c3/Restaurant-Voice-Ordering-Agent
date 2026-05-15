import requests

def debug_output_local(text):
    print("[DEBUG] Transcribed text:")
    print(text)

def debug_output_http(text, url="http://127.0.0.1:5000/debug"):
    try:
        response = requests.post(url, json={"transcript": text}, timeout=5)
        print(f"[DEBUG] Sent to {url} | Status: {response.status_code}")
        print(f"[DEBUG] Response: {response.text}")
    except Exception as e:
        print(f"[DEBUG] Failed to send transcript: {e}")