import argparse
import numpy as np

parser = argparse.ArgumentParser(description='Bandwidth  Variation.')
parser.add_argument('--bw-list', type=int, nargs='+',
                    help='list of bws (assumes kpbs)',
                    default=[12000, 100])
parser.add_argument('--time-list', type=int, nargs='+',
                    help='list of durations corresponding to each bw (assumes s)',
                    default=[10, 10])
parser.add_argument('--save-path', type=str,
                    help='path to save the file in',
                    required=True)
parser.add_argument('--smooth', action='store_true',
                    help='smoothly transits the bitrate over from first element of' 
                    'bw-list to the last element of bw-list over first and last' 
                    'elements of time-list',
                    required=True)
args = parser.parse_args()

def make_trace(t, bw, last_c, f):
    ''' t = duration (s), bw = bandwidth (kbps) '''
    tt_MTU = max(int(12000/bw), 1)
    count = max(int(bw/12000), 1)
    c = last_c
    while c <= t * 1000 + last_c:
        for i in range(count):
            c += tt_MTU
            f.write(str(c))
            f.write('\n')

    return c

f = open(args.save_path, "w")
last_c = 0
if args.smooth:
    assert(args.time_list[0] < args.time_list[-1])
    slope_sign = np.sign(args.bw_list[-1] - args.bw_list[0])
    bw_list = range(args.bw_list[0], args.bw_list[-1], slope_sign)
    delta_t = slope_sign * (args.time_list[-1] - args.time_list[0]) / (args.bw_list[-1] - args.bw_list[0])
    time_list = [delta_t for i in bw_list]
    for t, bw in zip(time_list, bw_list):
        last_c = make_trace(t, bw, last_c, f)
else:
    for t, bw in zip(args.time_list, args.bw_list):
        last_c = make_trace(t, bw, last_c, f)
f.close()

