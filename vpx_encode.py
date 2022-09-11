import os
import sys
import tempfile
import itertools
import subprocess as sub
import multiprocessing as mp
import matplotlib.pyplot as plt

VPX_COMMAND = [
    "vpxenc",
    "--webm",
    "--codec={version}",
    "--rt",
    "--passes=1",
    "--lag-in-frames=0",
    "--cpu-used=8",
    "--threads=1",
    "--target-bitrate={bitrate}",
    "--kf-min-dist=1000000",
    "--kf-max-dist=1000000",
    "--static-thresh=0",
    "--min-q=4",
    "--max-q=63",
    "--resize-allowed=0",
    "--undershoot-pct=100",
    "--overshoot-pct=100",
    "-o", "{output}",
    "{input}"
]

CHROMIUM_COMMAND = [
    "vpxenc",
    "--webm",
    "--codec={version}",
    "--rt",
    "--passes=1",
    "--threads=2",
    "--end-usage=cbr",
    "--target-bitrate={bitrate}",
    "--buf-initial-sz=500",
    "--buf-optimal-sz=600",
    "--lag-in-frames=0",
    "--static-thresh=0",
    "--min-q=2",
    "--max-q=63",
    "--resize-allowed=0",
    "--undershoot-pct=100",
    "--overshoot-pct=15",
    "-o", "{output}",
    "{input}"
]

def run_vpx(version, input_file, output_file, bitrate):
    options = {
        "version": version,
        "input": input_file,
        "output": output_file,
        "bitrate": bitrate
    }

    command = [x.format(**options) for x in CHROMIUM_COMMAND]
    print(" ".join(command))
    sub.check_call(command, stdout=sub.DEVNULL, stderr=sub.DEVNULL)

def get_bitrate(filename):
    command = f'ffprobe "{filename}" |& grep bitrate'
    output = sub.check_output(command, shell=True, executable="/bin/bash").decode('utf-8')
    output = output.strip().split(", ")[-1].split(": ")
    assert output[0] == "bitrate"
    output = output[1].split(" ")
    assert len(output) == 2
    assert output[1] == "kb/s"
    return int(output[0])

def get_metric(metric, source, target):
    command = f'ffmpeg -y -i {source} -i {target} -lavfi {metric}=stats_file=/dev/null -f null - |& tail -n1'
    output = sub.check_output(command, shell=True, executable="/bin/bash").decode('utf-8')
    output = output.strip().split(" ")
    assert output[0] == f'[Parsed_{metric}_0'
    output = output[3:]
    assert output[0] == 'SSIM' if metric == "ssim" else 'PSNR'

    if metric == "ssim":
        assert output[-2].startswith("All:")
        output = output[-1].strip("()")
        return float(output)
    elif metric == "psnr":
        output = output[-3].split(":")
        assert output[0] == "average"
        return float(output[1])

def do_one_test(k):
    version = k[0]
    bitrate = k[1]
    input_file = k[2]

    #with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = tempfile.mkdtemp()
    output_file = os.path.join(tmpdir, "output.webm")
    run_vpx(version, input_file, output_file, bitrate)
    output_bitrate = get_bitrate(output_file)
    ssim = get_metric("ssim", input_file, output_file)
    psnr = get_metric("psnr", input_file, output_file)

    print(f'> {version}, {bitrate} done.\n', end='')
    return (version, bitrate, output_bitrate, ssim, psnr)

def get_results(input_file, versions, bitrates):
    keys = []

    for v in versions:
        for b in bitrates:
            keys += [(v, b, input_file)]

    with mp.Pool(processes=os.cpu_count() // 4) as pool:
        results = pool.map(do_one_test, keys)

    return results

def plot_results(results, version, metric):
    p = []

    for res in results:
        if res[0] == version:
            p += [(res[2], res[3] if metric == 'ssim' else res[4])]

    p.sort(key=lambda x: x[0])

    plt.plot(*zip(*p), marker='*', label=version.upper())
    plt.ylabel(metric.upper())
    plt.xlabel('Bitrate (kbps)')

def combine_results(results, metric, name):
    plt.clf()
    plot_results(results, 'vp8', metric)
    #plot_results(results, 'vp9', metric)
    plt.legend()
    plt.savefig(f'{name}_{metric}.pdf')

results = get_results("1_1024.y4m", ['vp8'], [100, 200, 300, 400, 500, 750, 1000])
combine_results(results, 'psnr', f'chromium')
combine_results(results, 'ssim', f'chromium')
