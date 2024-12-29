import flask
from flask import request, send_file
from PIL import Image
import numpy as np
from io import BytesIO
import cv2
import torch
import traceback
from concurrent.futures import ThreadPoolExecutor
from motion_magnification import motion_magnification

# Initialize Flask app and thread pool
app = flask.Flask(__name__)
executor = ThreadPoolExecutor(max_workers=2)

@app.route('/process-frame', methods=['POST'])
def process_frame():
    try:
        # Get image data
        img_bytes = request.get_data()
        if not img_bytes:
            print("No image data received")
            return "No image data received", 400
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            print("Failed to decode image")
            return "Failed to decode image", 400

        print(f"Received image shape: {image.shape}")  # Debug info
        
        # Process image directly without threading for now
        try:
            processed_image = motion_magnification(
                image,
                phase_mag=5.0,
                freq_lo=0.2,
                freq_hi=0.25,
                colorspace='luma3',
                sigma=2.0,
                attenuate=False
            )
        except Exception as e:
            print(f"Motion magnification error: {str(e)}")
            print(traceback.format_exc())
            return f"Motion magnification error: {str(e)}", 500
        
        # Encode processed image
        try:
            _, img_encoded = cv2.imencode('.jpg', processed_image, [cv2.IMWRITE_JPEG_QUALITY, 75])
            if img_encoded is None:
                print("Failed to encode processed image")
                return "Failed to encode processed image", 500
            
            return send_file(
                BytesIO(img_encoded.tobytes()),
                mimetype='image/jpeg'
            )
        except Exception as e:
            print(f"Image encoding error: {str(e)}")
            print(traceback.format_exc())
            return f"Image encoding error: {str(e)}", 500
            
    except Exception as e:
        print(f"General error: {str(e)}")
        print(traceback.format_exc())
        return f"General error: {str(e)}", 500

if __name__ == '__main__':
    print("Starting Flask server...")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"Device being used: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
    app.run(host='0.0.0.0', port=5000, debug=True)
