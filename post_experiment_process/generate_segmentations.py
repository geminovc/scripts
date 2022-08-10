import argparse
import sys
import torch
from torch import nn
from torch.autograd import Variable
from torchvision import transforms
import torch.nn.functional as F
import numpy as np
import cv2
import imageio
import os
from PIL import Image
from torchvision.utils import save_image

from original_bilayer.external.Graphonomy.networks import deeplab_xception_transfer, graph



class SegmentationWrapper(nn.Module):
    def __init__(self, num_gpus, pretrained_weights_dir):
        super(SegmentationWrapper, self).__init__()
        self.use_gpus = num_gpus > 0

        self.net = deeplab_xception_transfer.deeplab_xception_transfer_projection_savemem(
            n_classes=20, hidden_layers=128, source_classes=7)
        
        if self.use_gpus:
            x = torch.load(f'{pretrained_weights_dir}/pretrained_weights/graphonomy/pretrained_model.pth')
        else:
            x = torch.load(f'{pretrained_weights_dir}/pretrained_weights/graphonomy/pretrained_model.pth', \
            map_location=torch.device('cpu'))

        self.net.load_source_model(x)

        if self.use_gpus:
            self.net.cuda()

        self.net.eval()

        # transforms
        self.rgb2bgr = transforms.Lambda(lambda x:x[:, [2,1,0],...])

        # adj
        adj2_ = torch.from_numpy(graph.cihp2pascal_nlp_adj).float()
        adj1_ = Variable(torch.from_numpy(graph.preprocess_adj(graph.pascal_graph)).float())

        cihp_adj = graph.preprocess_adj(graph.cihp_graph)
        adj3_ = Variable(torch.from_numpy(cihp_adj).float())

        if self.use_gpus:
            self.adj2_test = adj2_.unsqueeze(0).unsqueeze(0).expand(1, 1, 7, 20).cuda().transpose(2, 3)
            self.adj3_test = adj1_.unsqueeze(0).unsqueeze(0).expand(1, 1, 7, 7).cuda()
            self.adj1_test = adj3_.unsqueeze(0).unsqueeze(0).expand(1, 1, 20, 20).cuda()
        else:
            self.adj2_test = adj2_.unsqueeze(0).unsqueeze(0).expand(1, 1, 7, 20).transpose(2, 3)
            self.adj3_test = adj1_.unsqueeze(0).unsqueeze(0).expand(1, 1, 7, 7)
            self.adj1_test = adj3_.unsqueeze(0).unsqueeze(0).expand(1, 1, 20, 20)

        # Erosion kernel
        SIZE = 5

        grid = np.meshgrid(np.arange(-SIZE//2+1, SIZE//2+1), np.arange(-SIZE//2+1, SIZE//2+1))[:2]
        self.kernel = (grid[0]**2 + grid[1]**2 < (SIZE / 2.)**2).astype('uint8')

    def forward(self, imgs):
        b, t = imgs.shape[:2]
        imgs = imgs.view(b*t, *imgs.shape[2:])

        inputs = self.rgb2bgr(imgs)
        inputs = Variable(inputs, requires_grad=False)

        if self.use_gpus:
            inputs = inputs.cuda()

        outputs = []
        with torch.no_grad():
            for input in inputs.split(1, 0):
                outputs.append(self.net.forward(input, self.adj1_test, self.adj3_test, self.adj2_test))
        outputs = torch.cat(outputs, 0)

        outputs = F.softmax(outputs, 1)

        segs = 1 - outputs[:, [0]] # probabilities for FG

        # Erosion
        segs_eroded = []
        for seg in segs.split(1, 0):
            seg = cv2.erode(seg[0, 0].cpu().numpy(), self.kernel, iterations=1)
            segs_eroded.append(torch.from_numpy(seg))
        segs = torch.stack(segs_eroded)[:, None].to(imgs.device)

        return segs

video_name = '/video-conf/scratch/pantea/fom_personalized_1024/xiran/test/0_1.mp4'
filename = 'xiran_1'
segs_dir = '/video-conf/scratch/vibhaa_tardy/segs/'
pretrained_weights_dir = '/video-conf/scratch/pantea'
num_gpus = 1
imgs_segs = []
BATCH_SIZE = 10

net_seg = SegmentationWrapper(num_gpus, pretrained_weights_dir)
reader = imageio.get_reader(video_name, 'ffmpeg')
to_tensor = transforms.ToTensor()

batch_num = 0
frame_num = 0
for frame in reader:
    img = Image.fromarray(frame)
    imgs_segs.append((to_tensor(img) - 0.5) * 2)
    frame_num += 1

    if len(imgs_segs) == BATCH_SIZE:
        imgs_segs = torch.stack(imgs_segs, 0)[None]
        if num_gpus > 0:        
            imgs_segs = imgs_segs.cuda()
        segs = net_seg(imgs_segs)[None]
        imgs_segs = []
        segs_path = f'{segs_dir}/{filename}/{batch_num}'
        os.makedirs(f'{segs_dir}/{filename}', exist_ok=True)
        torch.save(segs, segs_path + '.pt')
        print(f'finished {frame_num} frames')
        batch_num += 1
