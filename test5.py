import cv2
import numpy as np
from datetime import datetime  

quadrant_coordinates = {
    1: (1502, 26, 1740, 266),
    2: (1264, 24, 1502, 263),
    3: (1253, 263, 1495, 503),
    4: (1495, 266, 1737, 506),
}

def detect_ball(frame, previous_quadrant):
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    
    blurred = cv2.GaussianBlur(gray, (15, 15), 0)

    
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=50,
        param1=100,
        param2=30,
        minRadius=10,
        maxRadius=100
    )

    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            
            center = (i[0], i[1])
            radius = i[2]

            
            roi = frame[max(0, center[1] - radius):center[1] + radius,
                       max(0, center[0] - radius):center[0] + radius]

            
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

           
            color_ranges = {
                'pear': ([20, 50, 50], [40, 255, 255]),
                'white': ([0, 0, 200], [180, 30, 255]),
                'pine_green': ([0,139,139], [1,121,111]),
                'salmon': ([0, 120, 100], [10, 255, 255]),
            }

            ball_color = 'pine_green'
            for color, (lower, upper) in color_ranges.items():
                lower = np.array(lower, dtype=np.uint8)
                upper = np.array(upper, dtype=np.uint8)

                mask = cv2.inRange(hsv_roi, lower, upper)
                if cv2.countNonZero(mask) > 0.5 * mask.size:
                    ball_color = color
                    break

            
            
            cv2.circle(frame, center, radius, (0, 255, 0), 3)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ball_position = (center[0], center[1])
            current_quadrant = get_quadrant(ball_position)
            if current_quadrant is not None:
             if previous_quadrant is None:
               print(f"timestamp {timestamp} quadrant {current_quadrant} color {ball_color} Entry")
               previous_quadrant = current_quadrant
             elif current_quadrant != previous_quadrant:
               print(f"timestamp {timestamp} quadrant {previous_quadrant} color {ball_color} Exit")
               previous_quadrant = None

            return current_quadrant

    
    

def get_quadrant(ball_position):
    for quadrant, (x_start, y_start, x_end, y_end) in quadrant_coordinates.items():
        if x_start <= ball_position[0] <= x_end and y_start <= ball_position[1] <= y_end:
            return quadrant
    return None

cap = cv2.VideoCapture('AI Assignment video.mp4')

previous_quadrant = None

while True:
    ret, frame = cap.read()

    if not ret:
        break

    
    result_frame = detect_ball(frame, previous_quadrant)

    

    
    previous_quadrant = result_frame

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
