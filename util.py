import logging
import os

import numpy as np
import torch
from PIL import Image
from dataset import *

logger = logging.getLogger(__file__)


def get_dataset(args):
    train_path = args.dataset_path_train
    label_path = args.dataset_path_label
    if args.dataset_cache and os.path.isfile(args.dataset_cache):
        logger.info("Load enhanced dataset before DataLoader from cache at %s", args.dataset_cache)
        train = torch.load(args.dataset_cache)

    else:
        logger.info("Start Prepare enhanced dataset before DataLoader %s", train_path)
        train = DataTrain(train_path, label_path)
        torch.save(train, args.dataset_cache)
    validSep_beg = int(len(train[0]) / 5 * (args.valid_round - 1))
    validSep_end = int(len(train[0]) / 5 * args.valid_round)

    trainData = (torch.cat([train[0][:validSep_beg], train[0][validSep_end:]], dim=0),
                 torch.cat([train[1][:validSep_beg], train[1][validSep_end:]], dim=0))
    validData = (train[0][validSep_beg:validSep_end],
                 train[1][validSep_beg:validSep_end])
    trainDataSet = DataLoaderForUnet(trainData)
    validDataSet = DataLoaderForUnet(validData)
    logger.info("trainDataSet size %s", len(trainData))

    return (trainDataSet, validDataSet)


def accuracy_check(labels, pred_class):
    ims = [labels, pred_class]
    np_ims = []
    for item in ims:
        if 'str' in str(type(item)):
            item = np.array(Image.open(item))
        elif 'PIL' in str(type(item)):
            item = np.array(item)
        elif 'torch' in str(type(item)):
            item = item.numpy()
        np_ims.append(item)

    compare = np.equal(np_ims[0], np_ims[1])
    accuracy = np.sum(compare)

    return accuracy / len(np_ims[0].flatten())


def accuracy_for_batch(labels, pred_class, args):
    total_acc = 0
    batch_size = labels.size()[0]
    for index in range(batch_size):
        total_acc += accuracy_check(labels, pred_class)
    return total_acc / batch_size


def save_prediction(likelihood_map, pred_class, args, batch, epoch):
    img_as_np, pred_as_np = likelihood_map.cpu().data.numpy(), pred_class.cpu().data.numpy()

    img_as_np, pred_as_np = img_as_np * 255, pred_as_np * 255
    img_as_np, pred_as_np = img_as_np.astype(np.uint8), pred_as_np.astype(np.uint8)
    # print(img_as_np, img_as_np.shape)
    img, pred = Image.fromarray(img_as_np.squeeze(0)), Image.fromarray(pred_as_np.squeeze(0))
    path = args.save_folder + '/valid_' + str(args.valid_round) + '/saved_images' + '/epoch_' + str(epoch) + '/'
    if not os.path.exists(path):
        os.makedirs(path)
    # SAVE Valid Likelihood Images and Prediction
    export_name_lh = str(batch) + 'lh.png',
    export_name_pred = str(batch) + 'pred.png'
    img.save(path + export_name_lh)
    pred.save(path + export_name_pred)


def save_groundTrue(images, labels, args, batch, epoch):
    img_as_np = images.cpu().data.numpy()
    label_as_np = labels.cpu().data.numpy()

    img_as_np, label_as_np = img_as_np * 255, label_as_np * 255
    img_as_np, label_as_np = img_as_np.astype(np.uint8), label_as_np.astype(np.uint8)
    # print(img_as_np, img_as_np.shape)

    img, label = Image.fromarray(img_as_np.squeeze(0)), Image.fromarray(label_as_np.squeeze(0))
    path = args.save_folder + '/valid_' + str(args.valid_round) + '/saved_images' + '/epoch_' + str(epoch) + '/'
    if not os.path.exists(path):
        os.makedirs(path)
    # SAVE Valid ground true Images
    export_name_orig = str(batch) + 'orig.png'
    export_name_gt = str(batch) + 'gt.png'
    img.save(path + export_name_orig)
    label.save(path + export_name_gt)
