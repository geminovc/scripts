import imageio
import torch
import csv
import os
from skimage import img_as_float32
from first_order_model.logger import Logger
from first_order_model.modules.model import Vgg19, VggFace16
from first_order_model.reconstruction import frame_to_tensor, get_avg_visual_metrics
import lpips

original_lpips = lpips.LPIPS(net='vgg')
vgg_face_model = VggFace16()

if torch.cuda.is_available():
    original_lpips = original_lpips.cuda()
    vgg_face_model = vgg_face_model.cuda()

face_lpips = vgg_face_model.compute_loss

def visual_metrics(frame1, frame2, loss_fn_vgg):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tensor1 = frame_to_tensor(img_as_float32(frame1), device)
    tensor2 = frame_to_tensor(img_as_float32(frame2), device)
    return Logger.get_visual_metrics(tensor1, tensor2, loss_fn_vgg, original_lpips, face_lpips)

def save_average_metrics(metrics, save_dir, output_name):
    metrics_file = open(os.path.join(save_dir, output_name), 'wt')
    psnr, ssim, lpips_val, ssim_db, orig_lpips, face_lpips = get_avg_visual_metrics(metrics)
    writer = csv.writer(metrics_file)
    writer.writerow(['PSNR', 'SSIM', 'SSIM_DB', 'LPIPS'])
    writer.writerow([psnr, ssim, ssim_db, lpips_val])
    print(f'PSNR: {psnr}, SSIM: {ssim}, SSIM_DB: {ssim_db}, LPIPS: {orig_lpips} \n')
    metrics_file.close()

def get_loss_fn_vgg():
    vgg_model = Vgg19()
    if torch.cuda.is_available():
        vgg_model = vgg_model.cuda()
    loss_fn_vgg = vgg_model.compute_loss
    return loss_fn_vgg
