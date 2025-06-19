import cv2
import pytesseract

def capture_image_from_camera(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    while True:    
        ret, frame = cap.read()
        if not ret:
            return None
        
        cv2.imshow("Captured Image", frame)

        cap.release()
        cv2.destroyAllWindows()
        
    if not ret:
        print("Error: Could not read frame from camera.")
        return None
    
    return frame


def image_to_text(image):
    if image is None:
        return "No image to process."
    
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    try:
        import pytesseract
        text = pytesseract.image_to_string(gray_image)
        return text.strip()
        return "01A127AB"
    except ImportError:
        return "pytesseract is not installed. Please install it to use OCR functionality."


def main():
    camera_index = "http://66.27.116.187/mjpg/video.mjpg"
    image = capture_image_from_camera(camera_index)
    
    if image is not None:
        text = image_to_text(image)
        print("Extracted Text:", text)
    else:
        print("Failed to capture image from camera.")

