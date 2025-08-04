import requests
import base64


class YHXBB:
    def __init__(self, area_id):
        self.url = "http://172.249.35.50:9293/api/v1/jm-car/car-io"
        self.area_id = area_id

    def _encode_image_to_base64(self, image_file):
        image_content = image_file.read()
        encoded = base64.b64encode(image_content).decode("utf-8")
        return encoded

    def _send(self, plate_number, car_photo, io_type):
        payload = {
            "area_id": self.area_id,
            "io_type": io_type,
            "car_drb_number": plate_number,
            "car_photo": car_photo
        }
        try:
            response = requests.post(url=self.url, json=payload, timeout=5)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error while sending to YHXBB API: {e}")
            return False


    def car_entry(self, plate_number, image_file):
        return self._send(plate_number=plate_number, car_photo=self._encode_image_to_base64(image_file), io_type=1)


    def car_exit(self, plate_number, image_file):
        return self._send(plate_number=plate_number, car_photo=self._encode_image_to_base64(image_file), io_type=2)

