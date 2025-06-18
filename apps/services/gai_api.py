import requests

def check_with_gai(plate_number):
    # Bu joyni real API bo‘lsa moslashtirasiz
    try:
        response = requests.get(f"http://192.168.0.10/api/check/{plate_number}")
        data = response.json()
        return data.get("is_fined", False), data.get("is_paid", False)
    except Exception:
        return False, False
