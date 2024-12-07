import websockets
from simple_websocket import Client
import time
import cv2 as cv
import threading
import json

server_url = "ws://192.168.1.71:8001/"
window_name = "Drone Games"

async def websocket_main():
    # asyncio.run(websocket_main)
    async with websockets.connect(server_url) as ws:
        while True:
            # msg = input("Enter messages: ")
            msg = '{"cmd":"rc_send", "payload":[997,997,997,997,997,997,997,997,997,997]}'
            if msg == "quit":
                await ws.close()
                break
            if len(msg) > 0:
                await ws.send(msg)
            time.sleep(1)
            response = await ws.recv()
            print(response)

class DroneControl:
    yaw = 997
    throttle = 997
    pitch = 997
    roll = 997
    ch1 = 997
    ch2 = 997
    ch3 = 997
    ch4 = 997
    ch5 = 997
    ch6 = 997

    wsClient = None

    def __init__(self, websocket_client):
        self.wsClient = websocket_client
        self.stopThread = threading.Event()

    def start(self):
        droneControlThread = threading.Thread(target=self.__send, name="drone control thread")
        droneControlThread.start()

    def stop(self):
        self.ch1 = 997
        time.sleep(0.5)
        self.stopThread.set()

    def __send(self):
        while not self.stopThread.is_set():
            data = dict({
                'cmd': 'rc_send',
                'payload': [
                    self.yaw, self.throttle, self.pitch, self.roll,
                    self.ch1, self.ch2, self.ch3, self.ch4, self.ch5, self.ch6
                ]
            })
            self.wsClient.send(json.dumps(data))
            time.sleep(0.05)

    def set(self, yaw=None, throttle=None, pitch=None, roll=None, ch1=None, ch2=None, ch3=None, ch4=None, ch5=None, ch6=None):
        if yaw is not None:
            self.yaw = int(yaw)
        if throttle is not None:
            self.throttle = int(throttle)
        if pitch is not None:
            self.pitch = int(pitch)
        if roll is not None:
            self.roll = int(roll)
        if ch1 is not None:
            self.ch1 = int(ch1)
        if ch2 is not None:
            self.ch2 = int(ch2)
        if ch3 is not None:
            self.ch3 = int(ch3)
        if ch4 is not None:
            self.ch4 = int(ch4)
        if ch5 is not None:
            self.ch5 = int(ch5)
        if ch6 is not None:
            self.ch6 = int(ch6)


def main():
    print(server_url)
    wsClient = Client.connect(server_url)
    droneControl = DroneControl(wsClient)
    droneControl.start()

    cv.namedWindow(window_name, cv.WINDOW_NORMAL)
    cv.createTrackbar("arm", window_name, 172, 1800, lambda val: droneControl.set(ch1=val))
    cv.createTrackbar("throttle", window_name, 172, 1800, lambda val: droneControl.set(throttle=val))
    cv.createTrackbar("yaw", window_name, 997, 1800, lambda val: droneControl.set(yaw=val))
    cv.createTrackbar("pitch", window_name, 997, 1800, lambda val: droneControl.set(pitch=val))
    cv.createTrackbar("roll", window_name, 997, 1800, lambda val: droneControl.set(roll=val))
    # cv.createButton('', lambda val: print(val))
    cv.resizeWindow(window_name, 300, 100)

    isRunning = True

    while isRunning:
        key = cv.waitKey(1)
        if key == 27:
            isRunning = False

    droneControl.stop()
    wsClient.close()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
