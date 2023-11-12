import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import cv2
from pyzbar.pyzbar import decode
import numpy as np
from playsound import playsound
import threading
import time

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def success():
    playsound("success.wav")


def bad():
    playsound("wrong-47985.mp3")


def check_user_status(username, password):
    try:
        response = requests.get(f"https://localhost:7018/api/user/checkUserStatus?username={username}&password={password}", verify=False)

        if response.content:
            response_json = response.json()
            message = response_json['message']

            if response_json["success"]:
                name = response_json["data"]["name"]
                surname = response_json["data"]["surname"]
                last_day = response_json["data"]["membershipExpirationDate"]
                return True, f"{message} {name} {surname}", f"Uyelik sonu: {last_day}"
            else:
                return False, message, None

    except Exception as e:
        return False, str(e), None



def process_qr_code(frame, qr_data):
    if "*onyedieylulgym*" in qr_data:
        username, password = qr_data.split("*onyedieylulgym*")

        success_flag, message, date = check_user_status(username, password)

        if success_flag:
            cv2.rectangle(frame, (15, 0), (1440, 150), (255, 255, 255), -1)
            cv2.putText(frame, message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
            cv2.putText(frame, date, (20, 110), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
            sound_thread = threading.Thread(target=success)
            sound_thread.start()
        else:
            cv2.rectangle(frame, (15, 0), (1400, 80), (255, 255, 255), -1)
            cv2.putText(frame, message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            nopass_thread = threading.Thread(target=bad)
            nopass_thread.start()
    else:
        cv2.rectangle(frame, (15, 0), (1000, 80), (255, 255, 255), -1)
        cv2.putText(frame, "Geçerli QR kodu okutun", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        nopass_thread = threading.Thread(target=bad)
        nopass_thread.start()



def main():

    cap = cv2.VideoCapture(0)
    last_qr_data = None
    last_qr_time = None
    ignore_duration = 4

    while True:
        _, frame = cap.read()
        frame = cv2.resize(frame, (1440, 980))

        qr_info = decode(frame)

        if len(qr_info) > 0:
            qr = qr_info[0]
            data = qr.data
            rect = qr.rect
            polygon = qr.polygon

            cv2.rectangle(frame, (rect.left, rect.top), (rect.left + rect.width, rect.top + rect.height), (0, 255, 0), 3)
            cv2.polylines(frame, [np.array(polygon)], True, (255, 0, 0), 3)

            qr_data = data.decode()

            if qr_data == last_qr_data and time.time() - last_qr_time < ignore_duration:
                continue

            last_qr_data = qr_data
            last_qr_time = time.time()

            process_qr_code(frame, qr_data)

        cv2.imshow("QR kod ekrani", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
