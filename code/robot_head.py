from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import cv2
import threading
import time
from collections import deque
import RPi.GPIO as GPIO
import urllib.parse
import sys

import ArducamDepthCamera as ac
import numpy as np


MAX_DISTANCE = 4

# Set up GPIO
LED_PIN = 17
LED_PIN2 = 26
SERVO_PIN_HORIZONTAL = 27
SERVO_PIN_VERTICAL = 18

GPIO.setmode(GPIO.BCM)
# GPIO.cleanup(LED_PIN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(LED_PIN2, GPIO.OUT)
GPIO.setup(SERVO_PIN_HORIZONTAL, GPIO.OUT)
GPIO.setup(SERVO_PIN_VERTICAL, GPIO.OUT)

GPIO.output(LED_PIN, GPIO.LOW)
GPIO.output(LED_PIN2, GPIO.LOW)

# Set up PWM for servo control
servo_horizontal = GPIO.PWM(SERVO_PIN_HORIZONTAL, 50)  # 50Hz PWM frequency
servo_vertical = GPIO.PWM(SERVO_PIN_VERTICAL, 50)      # 50Hz PWM frequency
servo_horizontal.start(0)
servo_vertical.start(0)
import subprocess

# cam = ac.ArducamCamera()
# if cam.open(ac.TOFConnect.CSI,0) != 0 :
#     print("initialization failed")
# if cam.start(ac.TOFOutput.DEPTH) != 0 :
#     print("Failed to start camera")
# cam.setControl(ac.TOFControl.RANG,MAX_DISTANCE)
# frame_tmp = cam.requestFrame(200)
# depth_buf = frame_tmp.getDepthData()
# amplitude_buf = frame_tmp.getAmplitudeData()
# cam.releaseFrame(frame_tmp)
# amplitude_buf*=(255/1024)
# amplitude_buf = np.clip(amplitude_buf, 0, 255)
# result_image = process_frame(depth_buf,amplitude_buf)
# cv2.imshow("preview",result_image)

# key = cv2.waitKey(1)
# if key == ord("q"):
#     exit_ = True
#     cam.stop()
#     cam.close()
    
def process_frame(depth_buf: np.ndarray, amplitude_buf: np.ndarray) -> np.ndarray:
        
    depth_buf = np.nan_to_num(depth_buf)

    amplitude_buf[amplitude_buf<=7] = 0
    amplitude_buf[amplitude_buf>7] = 255

    depth_buf =(1 - (depth_buf/MAX_DISTANCE)) * 255
    depth_buf = np.clip(depth_buf, 0, 255)
    result_frame = depth_buf.astype(np.uint8)  & amplitude_buf.astype(np.uint8)
    return result_frame 
class ArduCamCam(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        cam = ac.ArducamCamera()
        camIDx = int(find_webcam_index("unicam"))
        if cam.open(ac.TOFConnect.CSI,camIDx) != 0 :
            print("initialization failed")
        if cam.start(ac.TOFOutput.DEPTH) != 0 :
            print("Failed to start camera")
        cam.setControl(ac.TOFControl.RANG,MAX_DISTANCE)
        self.cam = cam
        self.running = True
        self.frame_queue = deque(maxlen=1)

    def run(self):
        while self.running:
            frame = self.cam.requestFrame(200)
            
            if frame is not None:
                depth_buf = frame.getDepthData()
                amplitude_buf = frame.getAmplitudeData()
                self.cam.releaseFrame(frame)

                amplitude_buf *= (255 / 1024)
                amplitude_buf = np.clip(amplitude_buf, 0, 255)
                result_image = process_frame(depth_buf, amplitude_buf)
                
                ret, jpeg = cv2.imencode('.jpg', result_image)
                if ret:
                    self.frame_queue.append(jpeg.tobytes())
                else:
                    print("Failed to encode frame as JPEG")
            else:
                print("Failed to deque buffer")
            
            time.sleep(0.01)

    def get_frame(self):
        if self.frame_queue:
            return self.frame_queue[-1]
        else:
            return None

    def stop(self):
        self.running = False
        self.cam.stop()
        self.cam.close()



def find_webcam_index(device_name):
    command = "v4l2-ctl --list-devices"
    output = subprocess.check_output(command, shell=True, text=True)
    devices = output.split('\n\n')
    
    for device in devices:
        if device_name in device:
            lines = device.split('\n')
            for line in lines:
                if "video" in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith('/dev/video'):
                            print(part)
                            return (part[10:])


def set_servo_angle(servo, angle):
    duty_cycle = angle / 18 + 2
    # GPIO.output(servo, True)
    servo.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)
    # GPIO.output(servo, False)
    servo.ChangeDutyCycle(0)

# Camera feed class
class CameraFeed(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        webcam_index = int(find_webcam_index('3D USB'))
        self.camera = cv2.VideoCapture(webcam_index, apiPreference=cv2.CAP_V4L2)
        self.running = True
        self.frame_queue = deque(maxlen=1)

    def run(self):
        while self.running:
            success, frame = self.camera.read()
            if not success:
                break
            else:
                ret, jpeg = cv2.imencode('.jpg', frame)
                self.frame_queue.append(jpeg.tobytes())
                time.sleep(0.01)

    def get_frame(self):
        if self.frame_queue:
            return self.frame_queue[-1]
        else:
            return None

    def stop(self):
        self.running = False
        self.camera.release()

# Initialize CameraFeed instance
camera_feed = CameraFeed()
camera_feed.start()

cam_tof_feed = ArduCamCam()
cam_tof_feed.start()

# HTTP request handler
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open('index.html', 'rb') as f:
                    self.wfile.write(f.read())
            if self.path == '/led/on':
                GPIO.output(LED_PIN, GPIO.HIGH)
                GPIO.output(LED_PIN2, GPIO.HIGH)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'LED turned on')
            elif self.path == '/led/off':
                GPIO.output(LED_PIN, GPIO.LOW)
                GPIO.output(LED_PIN2, GPIO.LOW)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'LED turned off')
            elif self.path == '/video_feed2':
                self.send_response(200)
                self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
                self.end_headers()

                while True:
                    try:
                        frame = camera_feed.get_frame()
                        # print('video feed2')
                        if frame is None:
                            continue

                        self.wfile.write(b'--frame\r\n')
                        self.send_header('Content-type', 'image/jpeg')
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')

                        time.sleep(0.1)  # Adjust frame rate control if needed
                    except Exception as e:
                        break
            
            elif self.path == '/video_feed1':
                self.send_response(200)
                self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
                self.end_headers()

                while True:
                    try:
                        frame2 = cam_tof_feed.get_frame() #cam.requestFrame(200)
                        if frame2 is None:
                            continue

                        self.wfile.write(b'--frame\r\n')
                        self.send_header('Content-type', 'image/jpeg')
                        self.end_headers()
                        self.wfile.write(frame2)
                        self.wfile.write(b'\r\n')
                                                
                        # if frame2 != None :
                        #     print("getting frame")
                        #     depth_buf = frame2.getDepthData()
                        #     print('here now 2')
                        #     amplitude_buf = frame2.getAmplitudeData()
                        #     cam.releaseFrame(frame2)
                            
                        #     amplitude_buf*=(255/1024)
                        #     amplitude_buf = np.clip(amplitude_buf, 0, 255)
                        #     result_image = process_frame(depth_buf,amplitude_buf)
                        #     print('here now 3')
                        #     ret, jpeg2 = cv2.imencode('.jpg', result_image)
                        # # frame = cam_tof_feed.get_frame()
                        # # if frame is None:
                        # #     continue
                        
                        # self.wfile.write(b'--frame\r\n')
                        # self.send_header('Content-type', 'image/jpeg')
                        # self.end_headers()
                        # self.wfile.write(jpeg2.tobytes())
                        # self.wfile.write(b'\r\n')
                        # print('here now 3')
                        time.sleep(0.1)  # Adjust frame rate control if needed
                    except Exception as e:
                        print('exception')
                        break
            elif self.path.startswith('/servo/horizontal'):
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)
                angle = int(params.get('value', [0])[0])
                # print(angle)
                set_servo_angle(servo_horizontal, angle)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Horizontal servo angle updated')
            elif self.path.startswith('/servo/vertical'):
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)
                angle = int(params.get('value', [0])[0])
                set_servo_angle(servo_vertical, angle)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Vertical servo angle updated')
        except IOError:
            print(self.path)
            self.send_error(404, 'File Not Found: %s' % self.path)

# Threading mixin for concurrent HTTP server
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def run(server_class=ThreadedHTTPServer, handler_class=RequestHandler, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    # cam = ac.ArducamCamera()
    # if cam.open(ac.TOFConnect.CSI,0) != 0 :
    #     print("initialization failed")
    # if cam.start(ac.TOFOutput.DEPTH) != 0 :
    #     print("Failed to start camera")
    # cam.setControl(ac.TOFControl.RANG,MAX_DISTANCE)
    try:
        run()
    except KeyboardInterrupt:
        try:
            # print('in interrupt')
            camera_feed.stop()
            # print('camera feed stopped')
            servo_vertical.stop()
            servo_horizontal.stop()
            # print('servo stopped')
        except Exception:
            pass
        GPIO.cleanup(LED_PIN)
        GPIO.cleanup(LED_PIN2)
        GPIO.cleanup(SERVO_PIN_HORIZONTAL)
        GPIO.cleanup(SERVO_PIN_VERTICAL)
        
