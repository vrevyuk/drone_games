from construct import (
    ByteSwapped, Array, BitStruct, BitsInteger,
    Byte, If, Const, Switch, Tell, this,
    Enum, Int16ub, Int24ub, Int8sb, Int8ub,
)
from construct.core import Struct

SYNC_BYTE_BIN_STRING = b"\xc8"
SYNC_BYTE = int.from_bytes(SYNC_BYTE_BIN_STRING, byteorder="big")


class PacketsTypes(Enum):
    GPS = 0x02
    BATTERY_SENSOR = 0x08
    HEARTBEAT = 0x0B
    VIDEO_TRANSMITTER = 0x0F
    LINK_STATISTICS = 0x14
    RC_CHANNELS_PACKED = 0x16
    ATTITUDE = 0x1E


PAYLOADS_SIZE: "dict[int, int]" = {
    PacketsTypes.GPS: 15,
    PacketsTypes.BATTERY_SENSOR: 8,
    PacketsTypes.HEARTBEAT: 1,
    PacketsTypes.VIDEO_TRANSMITTER: 6,
    PacketsTypes.LINK_STATISTICS: 10,
    PacketsTypes.RC_CHANNELS_PACKED: 22,
    PacketsTypes.ATTITUDE: 6,
}

payload_heartbeat = Struct("origin_device_address" / Int8ub)

payload_battery_sensor = Struct(
    "voltage" / Int16ub,
    "current" / Int16ub,
    "capacity" / Int24ub,
    "remaining" / Int8ub
)

payload_link_statistics = Struct(
    "uplink_rssi_ant_1" / Int8ub,
    "uplink_rssi_ant_2" / Int8ub,
    "uplink_link_quality" / Int8ub,
    "uplink_snr" / Int8sb,
    "diversity_active_antenna" / Enum(Int8ub, ANTENNA_1=0, ANTENNA_2=1),
    "rf_mode" / Enum(Int8ub, RF_4_FPS=0, RF_50_FPS=1, RF_150_FPS=2),
    "uplink_tx_power"
    / Enum(
        Int8ub,
        TX_POWER_0_MW=0,
        TX_POWER_10_MW=1,
        TX_POWER_25_MW=2,
        TX_POWER_100_MW=3,
        TX_POWER_500_MW=4,
        TX_POWER_1000_MW=5,
        TX_POWER_2000_MW=6,
    ),
    "downlink_rssi" / Int8ub,
    "downlink_link_quality" / Int8ub,
    "downlink_snr" / Int8sb,
)

crsf_header = Struct(
    "sync_byte" / Const(SYNC_BYTE_BIN_STRING),
    "frame_length" / Int8ub,
    "data_offset" / Tell,
    "packet_type" / Int8ub,
    "destination_address" / If(this.packet_type > 0x27, Int8ub),
    "origin_address" / If(this.packet_type > 0x27, Int8ub),
)

payload_rc_channels_packed = ByteSwapped(
    BitStruct("channels" / Array(16, BitsInteger(11)))
)

crsf_frame = Struct(
    "header" / crsf_header,
    "payload"
    / Switch(
        this.header.packet_type,
        {
            PacketsTypes.HEARTBEAT: payload_heartbeat,
            PacketsTypes.BATTERY_SENSOR: payload_battery_sensor,
            PacketsTypes.LINK_STATISTICS: payload_link_statistics,
            PacketsTypes.RC_CHANNELS_PACKED: payload_rc_channels_packed,
        },
        default=Array(this.frame_length - 2, Byte),
    ),
    "crc_offset" / Tell,
    "CRC" / Int8ub,
)