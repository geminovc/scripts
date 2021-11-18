import sys
import logging
import datetime as dt
from scapy.all import *

logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

""" strip the vp8 payload descriptor
    coded up to spec in section 4.2 of RFC 7741
"""
def strip_vp8_payload_descriptor(payload):
    first_octet = payload[0]
    stripped_payload = payload[1:]
    logging.debug("descriptor first octet %s %s %x", first_octet, \
            byte_as_bits(first_octet), hex(first_octet))

    # check for X bit set
    if not 0b10000000 & first_octet:
        logging.debug("NO X bit")
        return stripped_payload

    second_octet = stripped_payload[0]
    stripped_payload = stripped_payload[1:]
    logging.debug("descriptor second octet %s %s %x", second_octet, \
            byte_as_bits(second_octet), hex(first_octet))

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
    logging.debug("header first octet %s %s %x", first_octet,
            byte_as_bits(first_octet), hex(first_octet))

    # P bit - inverse keyframe bit
    if not 0b00000001 & first_octet:
        return True
    return False


""" print byte as bit string 
"""
def byte_as_bits(byte):
    return "{0:b}".format(byte)


""" go through packets, and only look at packets from video sender
    and RTP/VP8 packets identified by destination port
    and payload type and gather information

    Arguments: 
        pcap_filename: name of the pcap file
        window: aggregation window for bitrate info

    Returns:
        frame data - dictionary with frame timestamps, size and type
        bitrates - timeseries of bitrate in sequence of windows separated
                    by type
"""
def gather_trace_statistics(pcap_filename, window=1):
    bind_layers(UDP, RTP)
    
    frame_data = []
    bitrates = {'video': [], 'audio': [], 'keypoints': []}
    count = 0
    cur_frame_size = 0
    window_num = 0
    last_window_start = -1
    bytes_so_far = {'video': 0, 'audio': 0, 'keypoints':0}
    packet_reader = PcapReader(pcap_filename)

    for packet in packet_reader:
        if IP in packet and UDP in packet:
            if packet[IP].src == "100.64.0.2":
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
                            frame_data.append({'timestamp': packet[RTP].timestamp,
                                'size': cur_frame_size,
                                'keyframe': keyframe})
                            cur_frame_size = 0

                        packet_type = 'video'
                    
                    elif packet[RTP].payload_type == 'something':
                        packet_type = 'audio'

                    else: 
                        packet_type = 'keypoints'

                    # dump last window's bitrate
                    time = dt.datetime.fromtimestamp(packet.time)
                    if last_window_start == -1:
                        last_window_start = time

                    if ((time - last_window_start).seconds > window):
                        for p in bitrates.keys():
                            bitrates[p].append(bytes_so_far[p] * 8)
                            bytes_so_far[p] = 0
                        last_window_start += dt.timedelta(0, window)
                    
                    bytes_so_far[packet_type] += len(packet)

                    logging.debug(len(packet))
                    logging.debug(packet.payload.layers())
                
                count += 1

    print(f'Read {count} packets total')

    return {'frame_data': frame_data, 'bitrates': bitrates}
