import argparse

parser = argparse.ArgumentParser(description='Bandwidth  Variation.')
parser.add_argument('--bw-list', type=int, nargs='+',
                    help='list of bws (assumes kpbs)',
                    default=[12000, 100, 12000])
parser.add_argument('--time-list', type=int, nargs='+',
                    help='list of durations corresponding to each bw (assumes s)',
                    default=[10, 10, 10])
parser.add_argument('--save-path', type=str,
                    help='path to save the file in',
                    required=True)
args = parser.parse_args()

def make_trace(t, bw, last_c, f):
    ''' t = duration (s), bw = bandwidth (kbps) '''
    tt_MTU = max(int(12000/bw), 1)
    count = max(int(bw/12000), 1)
    c = last_c
    while c <= t * 1000:
        for i in range(count):
            c += tt_MTU
            f.write(str(c))
            f.write('\n')

    return c

f = open(args.save_path, "w")
last_c = 0
for t, bw in zip(args.time_list, args.bw_list):
    last_c = make_trace(t, bw, last_c, f)
f.close()

