import os
import signal
import time
import json
import serial
import websockets
import asyncio
import threading
from crsf import CRSF, Channel

controller_uart = "/dev/tty.usbserial-006FD147"
# controller_uart = "/dev/ttyS0"

MIN_VALUE = 172
MID_VALUE = 997
MAX_VALUE = 1322


class Uart2CRSF:
    def __init__(self):
        self.yaw = MID_VALUE
        self.throttle = MIN_VALUE
        self.pitch = MID_VALUE
        self.roll = MID_VALUE
        self.ch1 = MIN_VALUE
        self.ch2 = MIN_VALUE
        self.ch3 = MIN_VALUE
        self.ch4 = MIN_VALUE
        self.ch5 = MIN_VALUE
        self.ch6 = MIN_VALUE
        self.tx_thread = None
        self.rc_thread = None
        self.write_crsf_stop = threading.Event()
        self.controller_port = serial.Serial(controller_uart, 425000)
        self.crsf = CRSF()

    def start(self):
        tx_thread = threading.Thread(target=self.write_2_uart, name="write to uart")
        tx_thread.start()

    def stop(self):
        self.write_crsf_stop.set()
        self.controller_port.close()

    def write_2_uart(self):
        while not self.write_crsf_stop.is_set():
            try:
                tx_buffer = self.crsf.handle_output(
                    self.yaw, self.throttle, self.pitch, self.roll,
                    self.ch1, self.ch2, self.ch3, self.ch4, self.ch5, self.ch6
                )
                # print([self.yaw, self.throttle, self.pitch, self.roll, self.ch1, self.ch2, self.ch3, self.ch4, self.ch5, self.ch6])
                if tx_buffer:
                    self.controller_port.write(tx_buffer)
                    self.controller_port.flush()

                time.sleep(0.05)
            except Exception as error:
                print(error)

        print("writing to uart has been stopped")

    def set_values(self, array_values):
        if len(array_values) != 10:
            raise Exception(f'array length is {len(array_values)} but requires 10 [yaw, throttle, pitch, roll, ch1, '
                            f'ch2, ch3, ch4, ch5, ch6]')
        #print([self.yaw, self.throttle, self.pitch, self.roll, self.ch1, self.ch2, self.ch3, self.ch4, self.ch5, self.ch6])
        for index in range(len(array_values)):
            #print(f'{index} => {array_values[index]}', type(array_values[index]))
            if index == 0:
                self.yaw = max(min(int(array_values[index]), 1500), 500)
            elif index == 1:
                self.throttle = max(min(int(array_values[index]), 500), 172)
            elif index == 2:
                self.pitch = max(min(int(array_values[index]), 1150), 800)
            elif index == 3:
                self.roll = max(min(int(array_values[index]), 1150), 850)
            elif index == 4:
                self.ch1 = int(array_values[index])
            elif index == 5:
                self.ch2 = int(array_values[index])
            elif index == 6:
                self.ch3 = int(array_values[index])
            elif index == 7:
                self.ch4 = int(array_values[index])
            elif index == 8:
                self.ch5 = int(array_values[index])
            elif index == 9:
                self.ch6 = int(array_values[index])
        #print([self.yaw, self.throttle, self.pitch, self.roll, self.ch1, self.ch2, self.ch3, self.ch4, self.ch5, self.ch6])


uart_crsf_writer = Uart2CRSF()
print("uart_crsf_writer created", uart_crsf_writer)
uart_crsf_writer.start()
print("uart_crsf_writer started")


async def handler(websocket):
    print("handler entered")
    while not uart_crsf_writer.write_crsf_stop.is_set():
        response_code = 200
        response_text = "OK"
        try:
            message = await websocket.recv()
            print('Received from client: ', message)

            data = json.loads(message)
            print('Received JSON from client: ', type(data) is dict, data)
            if type(data) is dict:
                cmd = data.get("cmd")
                payload = data.get("payload")
                if cmd == "rc_send" and payload is not None:
                    uart_crsf_writer.set_values(payload)
                else:
                    response_text = f'Unknown "{cmd}" command or wrong payload'
                    response_code = 400
                    print(response_text)
            else:
                response_code = 400
                response_text = f'Unknown data: "{data}"'

            await websocket.send(json.dumps({'response_code': response_code, 'response_text': response_text}))
            await asyncio.sleep(0)
        except Exception as e:
            print(e)
            response_text = str(e)
            response_code = 500
            await websocket.send(json.dumps({'response_code': response_code, 'response_text': response_text}))


async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with websockets.serve(handler, "", 8001) as soket:  # listen at port 8001
        print('WEBSOCKET SERVER STARTED')
        await stop


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KEYBOARD INTERRUPT")
    finally:
        uart_crsf_writer.stop()
        print('EXIT')
