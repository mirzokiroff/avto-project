import requests

def open_barrier(device_id):
    try:
        response = requests.post(f"http://192.168.0.20/api/open/{device_id}")
        return response.status_code == 200
    except:
        return False
