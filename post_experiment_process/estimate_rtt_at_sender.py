""" get rtt estimation at sender over windows of time 
    using received acks from the receiver
"""
import numpy as np
import datetime as dt
from scipy import stats
import matplotlib.pyplot as plt
import argparse
import os


parser = argparse.ArgumentParser(description='Collect logs info.')
parser.add_argument('--save-dir', type=str,
                    help='directory to save logs and files in',
                    default='./rtt_results')
parser.add_argument('--output-name', type=str,
                    help='file to save final graph in',
                    default="rtt")
parser.add_argument('--log-path', type=str,
                    help='path to the log file', required=True)

args = parser.parse_args()


class RtcpSrPacket:
    def __init__(self, rtp_timestamp=0, packet_count=0, octet_count=0, arrival_time=0):
        self.packet_count = packet_count
        self.octet_count = octet_count
        self.arrival_time = arrival_time
        self.rtp_timestamp = rtp_timestamp


class RtcpRrPacket:
    def __init__(self, fraction_lost=0, packet_lost=0, highest_seq=0, lsr=0, dlsr=0, arrival_time=0):
        """
        lsr = last_sr_timestamp
        dlsr = delay_since_last_sr_timestamp
        arrival_time is at the receiver of the packet
        ■ Last sender report (LSR) time stamp—Indicates the middle 32 bits out of the 64-bit ntp_timestamp
        included in the most recent RTCP SR packet received form the source SSRC. 
        This field is set to 0 if no SR has been received.

        ■ Delay since last SR (DLSR)—Indicates the delay, expressed in units of 1/65,536 seconds,
        between receiving the last SR packet from the source SSRC and sending this RR block.
        This field is set to 0 if no SR packet has been received.
        """
        self.fraction_lost = fraction_lost
        self.packet_lost = packet_lost
        self.highest_seq = highest_seq
        self.lsr = lsr
        self.dlsr = dlsr
        self.arrival_time = arrival_time


class RtpPacket:
    def __init__(self, seq=0, time_stamp=0, payload=0, num_bytes=0, send_time=0):
        self.seq = seq
        self.time_stamp = time_stamp
        self.payload = payload
        self.num_bytes = num_bytes
        self.send_time = send_time


def get_RtpPacket(words_split):
    rtp_packet = RtpPacket()
    for word in words_split:
        if "seq" in word:
            rtp_packet.seq = int(word.split('=')[1][:-1])
        elif "ts=" in word:
            rtp_packet.time_stamp = int(word.split('=')[1][:-1])
        elif "payload" in word:
            rtp_packet.payload = int(word.split('=')[1][:-1])
    
    rtp_packet.send_time = dt.datetime.strptime(words_split[-2] + " " + words_split[-1], '%Y-%m-%d %H:%M:%S.%f')
    rtp_packet.num_bytes = int(words_split[7])
    return rtp_packet


def get_RtcpSrPacket(words_split):
    """
    ■ NTP Time Stamp field is a 64-bit value that indicates the time of the RTP time stamp
    that is included in the report. The format of the NTP packet is a 64-bit number: the top
    32 bits indicate the value in seconds, and the bottom 32 bits indicate the fraction of a second

    ■ RTP time stamp—The RTP time stamp in the header corresponds to the same instance of time as the
    NTP time stamp above it, but the RTP time stamp is represented in the same units of the sample clock
    of the RTP stream. This RTP-to-NTP correspondence allows for audio and video lip sync.

    ■ Sender packet count—The sender packet count indicates the total number of RTP packets sent since the
    stream started transmission, until the time this RTCP SR packet is generated.

    ■ Sender octet count—The sender octet count indicates the number of RTP payload octets sent since the stream
    started transmission, until the time this SR packet is generated. The sender resets the counter if the SSRC
    changes. This value can be used to estimate the average payload rate. The sender octet count does not include
    the length of the header or padding.
    """
    rtp_timestamp = int(words_split[5].split('=')[1][:-1])
    packet_count = int(words_split[6].split('=')[1][:-1])
    octet_count = int(words_split[7].split('=')[1][:-2])
    arrival_time = int(words_split[10].split(':')[1])
    return RtcpSrPacket(rtp_timestamp, packet_count, octet_count, arrival_time)


def get_RtcpRrPacket(words_split):
    rr_packet = RtcpRrPacket()
    for word in words_split:
        if "fraction_lost" in word:
            rr_packet.fraction_lost = int(word.split('=')[1][:-1])
        elif "packet_lost" in word:
            rr_packet.packet_lost = int(word.split('=')[1][:-1])
        elif "highest_seq" in word:
            rr_packet.highest_seq = int(word.split('=')[1][:-1])
        elif "dlsr" in word:
            rr_packet.dlsr = int(word.split('=')[1][:-3])
        elif "lsr" in word and "dlsr" not in word:
            rr_packet.lsr = int(word.split('=')[1][:-1])
        elif "time" in word:
            rr_packet.arrival_time = int(word.split(':')[1])
    return rr_packet


def get_rtt_over_windows(save_dir, window=1):
    sent_rtp_packets = []
    received_rtp_packets = []
    sent_rtcp_packets = []
    received_rtcp_sr_packets = []
    received_rtcp_rr_packets = []
    estimated_rtts = []
    received_estimated_time = []

    with open(f'{save_dir}') as receiver_log:
        for line in receiver_log:
            words = line.strip()
            words_split = words.split()
            if " > RTP" in words:
                pass
                #sent_rtp_packets.append(get_RtpPacket(words_split))
            #elif " < RTP " in words:
            #    received_rtp_packets.append(words_split[3:])
            #elif " > RTCP" in words:
            #    sent_rtcp_packets.append(words_split[3:])
            #elif " < RTCP " in words:
            #    if "RtcpSrPacket" in words:
            #        received_rtcp_sr_packets.append(get_RtcpSrPacket(words_split))
            #    elif "RtcpRrPacket" in words:
            #        #print(words)
            #       received_rtcp_rr_packets.append(get_RtcpRrPacket(words_split))
            elif "estimated rtt is" in words:
                estimated_rtts.append(float(words_split[4].split('.')[0]))

    print("Average estimated rtt", np.mean(estimated_rtts))
    return estimated_rtts


def get_emwa(array, alpha = 0.9):
    ewma = [array[0]]
    for i in range(1, len(array)):
        ewma.append(alpha * array[i] + (1 - alpha) * ewma[i-1])
    return ewma


if __name__ == "__main__":
    try:
        estimated_rtts = get_rtt_over_windows(args.log_path)
        if len(estimated_rtts) > 0:
            os.makedirs(args.save_dir, exist_ok=True)
            plt.figure()
            plt.plot(estimated_rtts , \
                    label = 'Webrtc sender_log', color='b')
            plt.plot(get_emwa(estimated_rtts) , \
                    label = 'EWMA of Webrtc sender_log', color='g')
            plt.xlabel('time')
            plt.ylabel('estimated rtt (s)')
            #plt.title(f'max estimated bitrate (kbps)')
            plt.legend()
            plt.savefig(f'{args.save_dir}/{args.output_name}.png')
    except Exception as e:
        print(e)
        pass

