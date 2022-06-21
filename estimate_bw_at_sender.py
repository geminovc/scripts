""" get bandwidth estimation at sender over windows of time 
    using received acks from the receiver
"""
import numpy as np
import datetime as dt

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


def get_bw_over_windows(save_dir, window=1):
    sent_rtp_packets = []
    received_rtp_packets = []
    sent_rtcp_packets = []
    received_rtcp_sr_packets = []
    received_rtcp_rr_packets = []
    estimated_max_bws = []

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
            elif "maximum bitrate" in words:
                estimated_max_bws.append(float(words_split[6]) / 1000)

    prev_lsr = 0
    prev_highest_seq = 0
    for packet in received_rtcp_rr_packets:
        print(((packet.highest_seq - packet.packet_lost) - (prev_highest_seq)) * 1300 * 8 
                / ((packet.arrival_time >> 16) & 0xFFFFFFFF - packet.dlsr - packet.lsr))
        prev_lsr = packet.lsr
        prev_highest_seq = packet.highest_seq
    
    prev_octet_count = 0
    prev_arrival_time = 0
    prev_rtp_timestamp = 0
    for packet in received_rtcp_sr_packets:
        #print((packet.octet_count - prev_octet_count) * 8 /(packet.rtp_timestamp - packet.arrival_time), "kbps")
        prev_octet_count = packet.octet_count
        prev_arrival_time = packet.arrival_time
        prev_rtp_timestamp = packet.rtp_timestamp
    
    total_num_bytes = 0
    prev_send_time = 0
    for packet in sent_rtp_packets:
        for x in received_rtcp_sr_packets:
            if x.rtp_timestamp == packet.time_stamp:
                pass
                #print(x.rtp_timestamp, packet.time_stamp)
    print("estimated_max_bws", np.mean(estimated_max_bws))
    return estimated_max_bws

def get_emwa(array, alpha = 0.9):
    ewma = [array[0]]
    for i in range(1, len(array) - 1):
        ewma.append(alpha * array[i] + (1 - alpha) * ewma[i-1])
    return ewma

print("#################################################################")
from scipy import stats
import matplotlib.pyplot as plt
file_name = 'test2'
graph_dir = 'bw_results'
bws = [5, 25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 600, 1000, 2000, 3000, 4000, 6000, 12000]
x = []
y = []
yerr = []
for bw in bws:
    print(bw)
    try:
        estimated_max_bws = get_bw_over_windows(
                f'/data4/pantea/nets_scripts/end2end_experiments/{file_name}_{bw}kbps/run0/sender.log'
                )
        if len(estimated_max_bws) > 0:
            print(estimated_max_bws)
            plt.figure()
            plt.plot(estimated_max_bws , label = 'Webrtc sender_log', color='b')
            plt.plot(get_emwa(estimated_max_bws) , label = 'EWMA of Webrtc sender_log', color='g')
            plt.plot([bw for i in estimated_max_bws], label = 'original', color='r')
            plt.xlabel('time')
            plt.ylabel('estimated (kbps)')
            plt.title(f'max estimated bitrate for {bw}kbps')
            plt.legend()
            plt.show()
            plt.savefig(f'{graph_dir}/{file_name}_{bw}.pdf')

            x.append(bw)
            y.append(np.mean(estimated_max_bws))  # compute mean
            yerr.append([np.mean(estimated_max_bws) - min(estimated_max_bws), \
                    max(estimated_max_bws) - np.mean(estimated_max_bws)])
            #print(stats.describe(estimated_max_bws))
    except Exception as e:
        print(e)
        pass


yerr = np.transpose(yerr)  # yerr should be 2xN matrix
plt.figure()
plt.errorbar(x, y, yerr=yerr, fmt='b^', color='b', label= 'Webrtc sender_log')
plt.plot(x, x , label = 'original', color='r')
plt.xlabel("link bandwidth (kbps)")
plt.ylabel('estimated bw (kbps)')
plt.title("max estimated bw by sender")
plt.legend()
plt.savefig(f'{graph_dir}/{file_name}_all.pdf')

#    get_bw_over_windows(f'/data4/pantea/nets_scripts/end2end_experiments/mahimahi_{bw}kbps/run0/receiver.log')
#
#estimated_max_bws = get_bw_over_windows(f'/data4/pantea/nets_scripts/end2end_experiments/mahimahi_pantea_hq_1000kbps/run0/sender.log')

