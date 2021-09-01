import sys
import logging
from scapy.all import *

""" strip the vp8 payload descriptor
    coded up to spec in section 4.2 of RFC 7741
"""
def strip_vp8_payload_descriptor(payload):
    first_octet = payload[0]
    stripped_payload = payload[1:]
    logging.debug("descriptor first octet", first_octet, byte_as_bits(first_octet), hex(first_octet))

    # check for X bit set
    if not 0b10000000 & first_octet:
        logging.debug("NO X bit")
        return stripped_payload

    second_octet = stripped_payload[0]
    stripped_payload = stripped_payload[1:]
    logging.debug("descriptor second octet",  second_octet, byte_as_bits(second_octet), hex(first_octet))

    # check for I bit
    if 0b10000000 & second_octet:
        logging.debug("picture ID present")
        picture_id_first_octet = stripped_payload[0]
        stripped_payload = stripped_payload[1:]
        if 0b10000000 & picture_id_first_octet:
            logging.debug("15 bit picture id")
            stripped_payload = stripped_payload[1:]
        
    # check for L bit
    if 0b01000000 & second_octet:
        logging.debug("L bit set")
        stripped_payload = stripped_payload[1:]

    # check for T or K bit
    if 0b00110000 & second_octet:
        logging.debug("T or K bit set")
        stripped_payload = stripped_payload[1:]
    
    return stripped_payload


""" parse the vp8 header and see the frame is a keyframe or not
    based on RFC 7741 and RFC 6386
"""
def is_keyframe(payload):
    first_octet = payload[0]
    logging.debug("header first octet", first_octet, byte_as_bits(first_octet), hex(first_octet))

    # P bit - inverse keyframe bit
    if not 0b00000001 & first_octet:
        return True
    return False


""" print byte as bit string 
"""
def byte_as_bits(byte):
    return "{0:b}".format(byte)

logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
bind_layers(UDP, RTP, dport=40107)

packet_reader = PcapReader(sys.argv[1])
count = 0
cur_frame_size = 0

""" go through packets, and only look at packets from video sender
    and RTP/VP8 packets identified by destination port
    and payload type
"""
for packet in packet_reader:
    if IP in packet and UDP in packet:
        if packet[IP].src == "100.64.0.2" and packet[UDP].dport == 40107:
            if RTP in packet:
                if packet[RTP].payload_type == 97:
                    # first packet of frame
                    if cur_frame_size == 0:
                        payload = packet[Raw].load
                        vp8_payload = strip_vp8_payload_descriptor(payload)
                        keyframe = is_keyframe(vp8_payload)
                        logging.debug(packet[RTP].payload.load.hex())
                        logging.debug(payload.hex())

                    cur_frame_size += len(packet)

                    # check if frame has ended
                    if packet[RTP].marker == 1:
                        print("Frame: ", packet[RTP].timestamp, "size: ", cur_frame_size, "keyframe:", keyframe)
                        cur_frame_size = 0

                    logging.debug(len(packet))
                    logging.debug(packet.payload.layers())
            count += 1
    if count == 2000:
        break



