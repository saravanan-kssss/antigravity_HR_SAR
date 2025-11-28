import cv2
import numpy as np
import base64

class ProctorEngine:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def analyze_frame(self, frame_path: str):
        """
        Analyzes a saved frame for proctoring events.
        Returns a list of detected events.
        """
        img = cv2.imread(frame_path)
        if img is None:
            return []

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        events = []
        
        # 1. No Face
        if len(faces) == 0:
            events.append({
                "type": "no_face",
                "confidence": 1.0,
                "notes": "No face detected in frame"
            })
        
        # 2. Multiple Faces
        elif len(faces) > 1:
            events.append({
                "type": "multi_face",
                "confidence": 0.9,
                "notes": f"Detected {len(faces)} faces"
            })
            
        # 3. Eyes (if face detected)
        # This is a bit rough for static frames without calibration, but we can try
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) == 0:
                # Could be looking away or closed
                events.append({
                    "type": "eyes_off",
                    "confidence": 0.6,
                    "notes": "Eyes not clearly visible"
                })
                
        # 4. Low Light (Brightness)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        brightness = hsv[..., 2].mean()
        if brightness < 50:
            events.append({
                "type": "low_light",
                "confidence": 0.9,
                "notes": f"Low brightness detected ({int(brightness)})"
            })

        return events

    def analyze_base64_frame(self, base64_str: str):
        # Decode
        try:
            if "," in base64_str:
                base64_str = base64_str.split(",")[1]
            nparr = np.frombuffer(base64.b64decode(base64_str), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Reuse logic (save to temp or refactor)
            # Refactoring analyze_frame to take image object would be better
            # For now, let's just do the checks directly here to avoid IO
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            events = []
            if len(faces) == 0:
                events.append({"type": "no_face", "confidence": 1.0, "notes": "No face"})
            elif len(faces) > 1:
                events.append({"type": "multi_face", "confidence": 0.9, "notes": "Multiple faces"})
                
            return events
            
        except Exception as e:
            print(f"Error analyzing frame: {e}")
            return []
