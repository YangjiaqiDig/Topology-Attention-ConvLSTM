import torch
import random
import numpy as np
from pre_processing import *
import torch.nn as nn
from random import randint
from PIL import Image, ImageSequence
import glob
from torch.utils.data.dataset import Dataset
from torch.utils.data import DataLoader, TensorDataset


def DataTrain(train_path, label_path):
    image_arr = Image.open(str(train_path))
    mask_arr = Image.open(str(label_path))

    img_as_np = []
    orig_img_as_np = []
    for i, img_as_img in enumerate(ImageSequence.Iterator(image_arr)):
        if i not in [idx for idx in range(80, 100)]:
            singleImage_as_np = np.asarray(img_as_img)
            img_as_np.append(singleImage_as_np)
            orig_img_as_np.append(singleImage_as_np)

    msk_as_np = []
    orig_msk_as_np = []
    for j, label_as_img in enumerate(ImageSequence.Iterator(mask_arr)):
        if j not in [idx for idx in range(80, 100)]:
            singleLabel_as_np = np.asarray(label_as_img)
            msk_as_np.append(singleLabel_as_np)
            orig_msk_as_np.append(singleLabel_as_np)

    img_as_np, orig_img_as_np = np.stack(img_as_np, axis=0), np.stack(orig_img_as_np, axis=0)
    msk_as_np, orig_msk_as_np = np.stack(msk_as_np, axis=0), np.stack(orig_msk_as_np, axis=0)

    img_as_np, msk_as_np = flip(img_as_np, msk_as_np)

    # Noise Determine {0: Gaussian_noise, 1: uniform_noise
    if randint(0, 1):
        gaus_sd, gaus_mean = randint(0, 20), 0
        img_as_np = add_gaussian_noise(img_as_np, gaus_mean, gaus_sd)
    else:
        l_bound, u_bound = randint(-20, 0), randint(0, 20)
        img_as_np = add_uniform_noise(img_as_np, l_bound, u_bound)

    # change brightness
    pix_add = randint(-20, 20)
    img_as_np = change_brightness(img_as_np, pix_add)

    img_as_np, orig_img_as_np = normalization2(img_as_np.astype(float), max=1, min=0), normalization2(
        orig_img_as_np.astype(float), max=1, min=0)
    # print(msk_as_np[0])
    msk_as_np, orig_msk_as_np = msk_as_np / 255, orig_msk_as_np / 255

    img_as_tensor = torch.from_numpy(img_as_np).float()
    msk_as_tensor = torch.from_numpy(msk_as_np).long()
    orig_img_as_tensor, orig_msk_as_tensor = torch.from_numpy(orig_img_as_np).float(), torch.from_numpy(
        orig_msk_as_np).long()

    img_as_tensor = torch.cat((img_as_tensor, orig_img_as_tensor), 0)
    msk_as_tensor = torch.cat((msk_as_tensor, orig_msk_as_tensor), 0)

    return (img_as_tensor, msk_as_tensor)