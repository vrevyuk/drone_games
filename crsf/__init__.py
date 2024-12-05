__version__ = "0.0.1"

from .crsf_utils import crsf_crc, crsf_frame_crc
from .crsf_structure import crsf_frame, PAYLOADS_SIZE, PacketsTypes, SYNC_BYTE_BIN_STRING


class Channel:
    LOW = 900
    MIDDLE = 997
    HIGH = 1010

    def __init__(self, initial_value):
        self.__value = initial_value

    @property
    def is_low(self):
        return self.__value <= Channel.LOW

    @property
    def is_middle(self):
        return (Channel.MIDDLE - 100) <= self.__value <= (Channel.MIDDLE + 100)

    @property
    def is_high(self):
        return self.__value >= Channel.HIGH

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def l_value(self):
        if self.is_high:
            return 1
        elif self.is_middle:
            return 0
        else:
            return -1


class DroneControlState:
    def __init__(self):
        self.errors = []
        self.roll = 997
        self.pitch = 997
        self.yaw = 997
        self.throttle = 172
        self.ch1 = Channel(172)
        self.ch2 = Channel(172)
        self.ch3 = Channel(172)
        self.ch4 = Channel(172)
        self.ch5 = Channel(172)
        self.ch6 = Channel(172)

    def update_channels(self, chs: list):
        for index in range(0, len(chs)):
            value = chs[index]
            if index == 15:
                self.roll = value
            elif index == 14:
                self.pitch = value
            elif index == 13:
                self.throttle = value
            elif index == 12:
                self.yaw = value
            elif index == 11:
                self.ch1.value = value
            elif index == 10:
                self.ch2.value = value
            elif index == 9:
                self.ch3.value = value
            elif index == 8:
                self.ch4.value = value
            elif index == 7:
                self.ch5.value = value
            elif index == 6:
                self.ch6.value = value

    def log_error(self, error: Exception):
        self.errors.append(error)
        if len(self.errors) > 100:
            self.errors.pop(0)

    @property
    def control_drone(self):
        return f"""
THROTTLE: {self.throttle}; YAW: {self.yaw}; PITCH: {self.pitch}; ROLL: {self.roll};
"""

    def __str__(self):
        return str(
            f"""
roll: {self.roll}, pitch: {self.pitch}, yaw: {self.yaw}, throttle: {self.throttle}, 
ch1: {self.ch1}, ch2: {self.ch2}, ch3: {self.ch3}, ch4: {self.ch4}, ch5: {self.ch5}, ch6: {self.ch6}
error: {len(self.errors)}
"""
        )


class CRSF:
    def __init__(self):
        self.buffer = bytearray()
        self.state = DroneControlState()

    def handle_input(self, input_bytes):
        self.buffer.extend(input_bytes)
        while True:
            syn_byte_index = self.buffer.find(SYNC_BYTE_BIN_STRING)
            if syn_byte_index == -1:
                break

            if len(self.buffer) <= (syn_byte_index + 1):
                break

            payload_length = self.buffer[syn_byte_index + 1]
            if len(self.buffer) < (syn_byte_index + 1 + payload_length):
                break

            frame_data = self.buffer[syn_byte_index:syn_byte_index + 1 + payload_length + 1]
            del self.buffer[:syn_byte_index + 1 + payload_length + 1]

            # print(frame_data)
            if len(frame_data) == payload_length + 2:
                try:
                    frame = crsf_frame.parse(self.buffer)
                    # print(frame)

                    # print(crsf_frame_crc(frame_data), frame.CRC)
                    if crsf_frame_crc(frame_data) == frame.CRC:
                        if frame.header.packet_type == PacketsTypes.RC_CHANNELS_PACKED:
                            self.state.update_channels(frame.payload.channels)
                    else:
                        self.state.log_error(Exception("WRONG CRC"))

                except Exception as error:
                    self.state.log_error(error)

    def handle_output(self, yaw, throttle, pitch, roll, ch1, ch2, ch3, ch4, ch5, ch6):
        frame = crsf_frame.build({
            "header": {
                "frame_length": PAYLOADS_SIZE.get(PacketsTypes.RC_CHANNELS_PACKED) + 2,
                "packet_type": PacketsTypes.RC_CHANNELS_PACKED,
                "origin_address": 0,
                "destination_address": 0,
            },
            "payload": {
                "channels": [172, 172, 172, 172, 172, 172, ch6, ch5, ch4, ch3, ch2, ch1, yaw, throttle, pitch, roll]
            },
            "CRC": 0xff
        })
        crc = crsf_frame_crc(frame)
        frame = bytearray(frame)
        frame[-1] = crc
        return frame
