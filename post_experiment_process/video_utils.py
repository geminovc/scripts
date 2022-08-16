import imageio
import torch
import os
from skimage import img_as_float32
from first_order_model.logger import Logger
from first_order_model.modules.model import Vgg19
from first_order_model.reconstruction import frame_to_tensor, get_avg_visual_metrics

def visual_metrics(frame1, frame2, loss_fn_vgg):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tensor1 = frame_to_tensor(img_as_float32(frame1), device)
    tensor2 = frame_to_tensor(img_as_float32(frame2), device)
    return Logger.get_visual_metrics(tensor1, tensor2, loss_fn_vgg)

def save_average_metrics(metrics, save_dir, output_name):
    metrics_file = open(os.path.join(save_dir, output_name), 'wt')
    psnr, ssim, lpips_val, ssim_db = get_avg_visual_metrics(metrics)
    print(f'PSNR: {psnr}, SSIM: {ssim}, SSIM_DB: {ssim_db}, LPIPS: {lpips_val} \n')
    metrics_file.write(f'PSNR: {psnr}, SSIM: {ssim}, SSIM_DB: {ssim_db}, LPIPS: {lpips_val}')
    metrics_file.flush()
    metrics_file.close()

def get_loss_fn_vgg():
    vgg_model = Vgg19()
    if torch.cuda.is_available():
        vgg_model = vgg_model.cuda()
    loss_fn_vgg = vgg_model.compute_loss
    return loss_fn_vgg
