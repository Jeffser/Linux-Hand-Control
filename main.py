#from mouse_linux_wayland import *
import os
if os.geteuid() == 0: from tablet_linux import *
else:
    print("Running in limited mode, to interact with the system please run with root privilages")
    from test_interface import * 
import cv2, mediapipe as mp, numpy as np, time
from math import acos, degrees, dist
gestures = [
    {"status": False, "fingers": ["thumb", "index"], "function": mouse_click, "parameters": [0,0]},
    {"status": False, "fingers": ["thumb", "middle"], "function": mouse_click, "parameters": [2,0]},
    {"status": False, "fingers": ["thumb", "ring"], "function": key_super, "parameters": [0]}
]
special_gestures = [
    {"status": False, "total_steps": 1, "current_steps": 1}
]

def palm_centroid(coordinates_list : list):
    coordinates = np.array(coordinates_list)
    centroid = np.mean(coordinates, axis=0)
    centroid = int(centroid[0]), int(centroid[1])
    return centroid

def detect_fingers(results, width : int, height : int):
    hands = [None, None]
    for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
        coordinates = {
            "wrist": [0],
            "thumb": [1, 2, 3, 4],
            "index": [5, 6, 7, 8],
            "middle": [9, 10, 11, 12],
            "ring": [13, 14, 15, 16],
            "pinky": [17, 18, 19, 20],
            "palm": []
        }   
        for finger in coordinates.keys():
            for index in range(len(coordinates[finger])):
                x = int(hand_landmarks.landmark[coordinates[finger][index]].x * width)
                y = int(hand_landmarks.landmark[coordinates[finger][index]].y * height)
                coordinates[finger][index] = [x, y]
        coordinates["palm"].append(palm_centroid([coordinates["wrist"][0], coordinates["thumb"][0], coordinates["index"][0], coordinates["middle"][0], coordinates["ring"][0], coordinates["pinky"][0]]))
        if results.multi_handedness[i].classification[0].label == "Left": hands[0] = coordinates
        else: hands[1] = coordinates
    return hands
            
def calculate_finger_angle(coordinates_list : dict):
    hands = []
    for coordinates in coordinates_list:
        if coordinates is None: 
            hands.append(None)
            continue
        angles = {
            "thumb": 0,
            "index": 0,
            "middle": 0,
            "ring": 0,
            "pinky": 0
        }
        for finger in angles.keys():
            p1 = np.array(coordinates[finger][1])
            p2 = np.array(coordinates[finger][2])
            p3 = np.array(coordinates[finger][3])

            l1 = np.linalg.norm(p2 - p3)
            l2 = np.linalg.norm(p1 - p3)
            l3 = np.linalg.norm(p1 - p2)

            try:
                angles[finger] = degrees(acos((l1**2 + l3**2 - l2**2) / (2 * l1 * l3)))
            except:
                angles[finger] = 0
        hands.append(angles)
    return hands

def main():
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    #cap.set(cv2.CAP_PROP_FPS, 30)

    with mp_hands.Hands(
        model_complexity=1,
        max_num_hands=2,
        min_detection_confidence=0.9,
        min_tracking_confidence=0.9
    ) as hands:
        while True:
            initial_time = time.time()
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            height, width, _ = frame.shape
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            results = hands.process(frame)

            last_results = None

            if results.multi_hand_landmarks:
                last_results = results
            elif last_results is not None:
                results = last_results

            if results.multi_hand_landmarks is not None:
                coordinates = detect_fingers(results, width, height)
                angles = calculate_finger_angle(coordinates)                

                #pressure = dist(coordinates[0]["thumb"][3], coordinates[0]["index"][3])
                #if pressure < 30: pressure = pressure / 30 * 100
                #else: pressure = 0
                
                border = 100
                if coordinates[0] is not None and coordinates[1] is not None: #2 hand mode
                    primary_hand = 1
                    secundary_hand = 0
                else: #1 hand mode
                    hand_index = -1
                    if coordinates[0] is not None: hand_index = 0
                    elif coordinates[1] is not None: hand_index = 1
                    else: continue #If for some reason it doesn't find a hand this far in, I don't think it's possible tho
                    primary_hand = hand_index
                    secundary_hand = hand_index


                move_point = coordinates[primary_hand]["index"][3]
                if primary_hand == secundary_hand: move_point = coordinates[primary_hand]["palm"][0]
                tablet_move(max(0, move_point[0]-border) / (width-border*2) * 100, max(0, move_point[1]-border) / (height-border*2) * 100)

                
                for gesture in gestures:
                    if dist(coordinates[secundary_hand][gesture["fingers"][0]][3], coordinates[secundary_hand][gesture["fingers"][1]][3]) < 30:
                        if gesture["status"] == False:
                            gesture["function"](*gesture["parameters"])
                            gesture["status"] = True
                    elif gesture["status"]: gesture["status"] = False

                #Special Getures

                closed_finger_count = 0
                for finger in ["index", "middle", "ring", "pinky"]:
                    if dist(coordinates[secundary_hand][finger][3], coordinates[secundary_hand]["wrist"][0]) < dist(coordinates[secundary_hand][finger][1], coordinates[secundary_hand]["wrist"][0]): closed_finger_count += 1
                if closed_finger_count >= 3 and dist(coordinates[secundary_hand]["thumb"][3], coordinates[secundary_hand]["wrist"][0]) > dist(coordinates[secundary_hand]["thumb"][1], coordinates[secundary_hand]["wrist"][0]):
                    special_gestures[0]["status"] = True
                    special_gestures[0]["current_steps"] = special_gestures[0]["total_steps"]
                    mouse_click(mode=1)
                elif special_gestures[0]["status"]:
                    special_gestures[0]["current_steps"] -= (time.time() - initial_time) * 10
                if special_gestures[0]["current_steps"] < 0:
                    special_gestures[0]["status"] = False
                    mouse_click(mode=2)
                


                mp_drawing.draw_landmarks(
                    frame,
                    results.multi_hand_landmarks[0],
                    mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style()
                )
                if len(results.multi_hand_landmarks) == 2:
                    mp_drawing.draw_landmarks(
                        frame,
                        results.multi_hand_landmarks[1],
                        mp_hands.HAND_CONNECTIONS,
                        mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                        mp.solutions.drawing_styles.get_default_hand_connections_style()
                    )
            else:
                mouse_click(mode=2)
            cv2.putText(frame, "{:.2f}".format(1 / abs(time.time() - initial_time)), (15, 65), 1, 5, (255, 255, 255), 2)
            cv2.imshow("Camera View", frame)
            if cv2.waitKey(1) & 0xFF == 27 or cv2.getWindowProperty('Camera View', cv2.WND_PROP_VISIBLE) < 1: break
if __name__ == "__main__":
    main()