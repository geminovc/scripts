from skimage.metrics import peak_signal_noise_ratio
from skimage.metrics import structural_similarity
import lpips
import numpy as np

""" get per frame visual metrics based on predicted and original frame 
"""
def get_quality(prediction, original):
    psnr = peak_signal_noise_ratio(original, prediction)
    ssim = structural_similarity(original, prediction, multichannel=True)

    # TODO: tensorify/send to CUDA
    lpips = 0 #loss_fn_vgg(original, prediction)

    return {'psnr': psnr, 'ssim': ssim, 'lpips': lpips}


""" average out visual metrics across all frames as aggregated in
    the metrics_dict dictionary element
"""
def get_average_visual_metrics(metrics_dict):
    psnrs = [m['psnr'] for m in metrics_dict]
    psnr = np.average(psnrs)

    ssims = [m['ssim'] for m in metrics_dict]
    ssim = np.average(ssims)

    lpips = [m['lpips'] for m in metrics_dict]
    lpip = np.average(lpips)

    return psnr, ssim, lpip


