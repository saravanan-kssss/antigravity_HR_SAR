import cv2
import os
import subprocess

def crop_video_to_face(input_path: str, output_path: str):
    """
    Detects face in the first few seconds of the video and crops the whole video 
    to a square/portrait ratio centered on the face.
    Uses OpenCV for detection and FFmpeg for cropping.
    """
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return

    # 1. Detect face in the middle of the video (or start)
    cap = cv2.VideoCapture(input_path)
    
    # Read a frame from 1 second in
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0: fps = 30
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps * 1))
    
    ret, frame = cap.read()
    if not ret:
        # Try first frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
    
    cap.release()
    
    if not ret:
        print("Could not read video frame for detection.")
        return

    # Face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) == 0:
        print("No face detected for cropping. Keeping original.")
        # Just copy or symlink? For now, we might just skip cropping or copy.
        # subprocess.run(["cp", input_path, output_path]) 
        return

    # Pick the largest face
    x, y, w, h = max(faces, key=lambda b: b[2] * b[3])
    
    # Calculate crop window (add some padding)
    height, width = frame.shape[:2]
    
    # Desired aspect ratio (e.g., 9:16 or 1:1). Let's do 1:1 for the dashboard thumbnail
    # or keep it simple: crop to the face with 50% padding
    
    pad_w = int(w * 0.5)
    pad_h = int(h * 0.5)
    
    crop_x = max(0, x - pad_w)
    crop_y = max(0, y - pad_h)
    crop_w = min(width - crop_x, w + 2*pad_w)
    crop_h = min(height - crop_y, h + 2*pad_h)
    
    # FFmpeg command to crop
    # ffmpeg -i input.mp4 -filter:v "crop=w:h:x:y" output.mp4
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y}",
        "-c:a", "copy",
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Cropped video saved to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed: {e}")
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg.")

