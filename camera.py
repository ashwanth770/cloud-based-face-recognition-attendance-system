import cv2
import requests
import time

# Your EC2 Flask endpoint
UPLOAD_URL = "http://13.126.21.207:5000/upload"  
def capture_and_upload():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    print("Camera started. Press 'q' to quit...")
    last_sent = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Live Face Attendance", frame)

        # If a face is detected and at least 3 seconds passed since last upload
        if len(faces) > 0 and (time.time() - last_sent) > 3:
            x, y, w, h = faces[0]
            face_roi = frame[y:y+h, x:x+w]

            _, img_encoded = cv2.imencode('.jpg', face_roi)
            files = {'file': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}

            print("Face detected, sending to server...")
            try:
                response = requests.post(UPLOAD_URL, files=files, timeout=10)
                if response.status_code == 200:
                    print("Attendance logged:", response.json())
                else:
                    print("No match:", response.text)
            except Exception as e:
                print("Error sending frame:", e)

            last_sent = time.time()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_upload()