import os
import random

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset

DATASET_NAMES = [
    'BIPED',
    'BSDS',
    'BSDS300',
    'CID',
    'DCD',
    'MULTICUE', #5
    'PASCAL',
    'NYUD',
    'CLASSIC'
]  # 8


def dataset_info(dataset_name, is_linux=True):
    if is_linux:

        config = {
            'BSDS': {
                'img_height': 321,
                'img_width': 481,
                'test_list': 'test_pair.lst',
                'data_dir': '/opt/dataset/BSDS',  # mean_rgb
                'yita': 0.5
            },
            'BSDS300': {
                'img_height': 321,
                'img_width': 481,
                'test_list': 'test_pair.lst',
                'data_dir': '/opt/dataset/BSDS300',  # NIR
                'yita': 0.5
            },
            'PASCAL': {
                'img_height': 375,
                'img_width': 500,
                'test_list': 'test_pair.lst',
                'data_dir': '/opt/dataset/PASCAL',  # mean_rgb
                'yita': 0.3
            },
            'CID': {
                'img_height': 512,
                'img_width': 512,
                'test_list': 'test_pair.lst',
                'data_dir': '/opt/dataset/CID',  # mean_rgb
                'yita': 0.3
            },
            'NYUD': {
                'img_height': 425,
                'img_width': 560,
                'test_list': 'test_pair.lst',
                'data_dir': '/opt/dataset/NYUD',  # mean_rgb
                'yita': 0.5
            },
            'MULTICUE': {
                'img_height': 720,
                'img_width': 1280,
                'test_list': 'test_pair.lst',
                'data_dir': '/opt/dataset/MULTICUE',  # mean_rgb
                'yita': 0.3
            },
            'BIPED': {
                'img_height': 720,
                'img_width': 1280,
                'test_list': 'test_rgb.lst',
                'train_list': 'train_rgb.lst',
                'data_dir': '/opt/dataset/BIPED/edges',  # mean_rgb
                'yita': 0.5
            },
            'CLASSIC': {
                'img_height': 512,
                'img_width': 512,
                'test_list': None,
                'data_dir': 'data',  # mean_rgb
                'yita': 0.5
            },
            'DCD': {
                'img_height': 240,
                'img_width': 360,
                'test_list': 'test_pair.lst',
                'data_dir': '/opt/dataset/DCD',  # mean_rgb
                'yita': 0.2
            }
        }
    else:
        config = {
            'BSDS': {'img_height': 512,  # 321
                     'img_width': 512,  # 481
                     'test_list': 'test_pair.lst',
                     'data_dir': '../../dataset/BSDS',  # mean_rgb
                     'yita': 0.5},
            'BSDS300': {'img_height': 512,  # 321
                        'img_width': 512,  # 481
                        'test_list': 'test_pair.lst',
                        'data_dir': '../../dataset/BSDS300',  # NIR
                        'yita': 0.5},
            'PASCAL': {'img_height': 375,
                       'img_width': 500,
                       'test_list': 'test_pair.lst',
                       'data_dir': '/opt/dataset/PASCAL',  # mean_rgb
                       'yita': 0.3},
            'CID': {'img_height': 512,
                    'img_width': 512,
                    'test_list': 'test_pair.lst',
                    'data_dir': '../../dataset/CID',  # mean_rgb
                    'yita': 0.3},
            'NYUD': {'img_height': 425,
                     'img_width': 560,
                     'test_list': 'test_pair.lst',
                     'data_dir': '/opt/dataset/NYUD',  # mean_rgb
                     'yita': 0.5},
            'MULTICUE': {'img_height': 720,
                         'img_width': 1280,
                         'test_list': 'test_pair.lst',
                         'data_dir': '../../dataset/MULTICUE',  # mean_rgb
                         'yita': 0.3},
            'BIPED': {'img_height': 720,  # 720
                      'img_width': 1280,  # 1280
                      'test_list': 'test_rgb.lst',
                      'train_list': 'train_rgb.lst',
                      'data_dir': '../../dataset/BIPED/edges',  # WIN: '../.../dataset/BIPED/edges'
                      'yita': 0.5},
            'CLASSIC': {'img_height': 512,
                        'img_width': 512,
                        'test_list': None,
                        'train_list': None,
                        'data_dir': 'data',  # mean_rgb
                        'yita': 0.5},
            'DCD': {'img_height': 240,
                    'img_width': 360,
                    'test_list': 'test_pair.lst',
                    'data_dir': '/opt/dataset/DCD',  # mean_rgb
                    'yita': 0.2}
        }
    return config[dataset_name]


class TestDataset(Dataset):
    def __init__(self,
                 data_root,
                 test_data,
                 mean_bgr,
                 img_height,
                 img_width,
                 test_list=None,
                 #  arg=None
                 ):
        if test_data not in DATASET_NAMES:
            raise ValueError(f"Unsupported dataset: {test_data}")

        self.data_root = data_root
        self.test_data = test_data
        self.test_list = test_list
        # self.arg = arg
        # self.mean_bgr = arg.mean_pixel_values[0:3] if len(arg.mean_pixel_values) == 4 \
        #     else arg.mean_pixel_values
        self.mean_bgr = mean_bgr
        self.img_height = img_height
        self.img_width = img_width
        self.data_index = self._build_index()

        print(f"mean_bgr: {self.mean_bgr}")

    def _build_index(self):
        sample_indices = []
        if self.test_data == "CLASSIC":
            # for single image testing
            images_path = os.listdir(self.data_root)
            labels_path = None
            sample_indices = [images_path, labels_path]
        else:
            # image and label paths are located in a list file

            if not self.test_list:
                raise ValueError(
                    f"Test list not provided for dataset: {self.test_data}")

            list_name = os.path.join(self.data_root, self.test_list)
            with open(list_name, 'r') as f:
                files = f.readlines()
            files = [line.strip() for line in files]
            pairs = [line.split() for line in files]
            images_path = [line[0] for line in pairs]
            labels_path = [line[1] for line in pairs]
            sample_indices = [images_path, labels_path]
        return sample_indices

    def __len__(self):
        return len(self.data_index[0])

    def __getitem__(self, idx):
        # get data sample
        # image_path, label_path = self.data_index[idx]
        image_path = self.data_index[0][idx]
        label_path = None if self.test_data == "CLASSIC" else self.data_index[1][idx]
        img_name = os.path.basename(image_path)
        file_name = os.path.splitext(img_name)[0] + ".png"

        # base dir
        if self.test_data.upper() == 'BIPED':
            img_dir = os.path.join(self.data_root, 'imgs', 'test')
            gt_dir = os.path.join(self.data_root, 'edge_maps', 'test')
        elif self.test_data.upper() == 'CLASSIC':
            img_dir = self.data_root
            gt_dir = None
        else:
            img_dir = self.data_root
            gt_dir = self.data_root

        # load data
        image = cv2.imread(os.path.join(img_dir, image_path), cv2.IMREAD_COLOR)
        if not self.test_data == "CLASSIC":
            label = cv2.imread(os.path.join(
                gt_dir, label_path), cv2.IMREAD_COLOR)
        else:
            label = None

        im_shape = [image.shape[0], image.shape[1]]
        image, label = self.transform(img=image, gt=label)

        return dict(images=image, labels=label, file_names=file_name, image_shape=im_shape)

    def transform(self, img, gt):
        # gt[gt< 51] = 0 # test without gt discrimination
        if self.test_data == "CLASSIC":
            img_height = img.shape[0] if img.shape[0] % 16 == 0 else (
                (img.shape[0] // 16) + 1) * 16
            img_width = img.shape[1] if img.shape[1] % 16 == 0 else (
                (img.shape[1] // 16) + 1) * 16
            # img_height = self.img_height
            # img_width = self.img_width
            print(
                f"actual size: {img.shape}, target size: {(img_width, img_height)}")
            # img = cv2.resize(img, (self.img_width, self.img_height))
            img = cv2.resize(img, (img_width, img_height))
            gt = None

        # Make images and labels at least 512 by 512
        elif img.shape[0] < 512 or img.shape[1] < 512:
            img = cv2.resize(img, (512, 512))
            gt = cv2.resize(gt, (512, 512))

        # Make sure images and labels are divisible by 2^4=16
        elif img.shape[0] % 16 != 0 or img.shape[1] % 16 != 0:
            img_width = ((img.shape[1] // 16) + 1) * 16
            img_height = ((img.shape[0] // 16) + 1) * 16
            img = cv2.resize(img, (img_width, img_height))
            gt = cv2.resize(gt, (img_width, img_height))

        # if self.yita is not None:
        #     gt[gt >= self.yita] = 1
        img = np.array(img, dtype=np.float32)
        # if self.rgb:
        #     img = img[:, :, ::-1]  # RGB->BGR
        img -= self.mean_bgr
        img = img.transpose((2, 0, 1))
        img = torch.from_numpy(img.copy()).float()

        if self.test_data == "CLASSIC":
            gt = np.zeros((img.shape[:2]))
            gt = torch.from_numpy(np.array([gt])).float()
        else:
            gt = np.array(gt, dtype=np.float32)
            if len(gt.shape) == 3:
                gt = gt[:, :, 0]
            gt /= 255.
            gt = torch.from_numpy(np.array([gt])).float()

        return img, gt


class BipedDataset(Dataset):
    train_modes = ['train', 'test', ]
    dataset_types = ['rgbr', ]
    data_types = ['aug', ]

    def __init__(self,
                 data_root,
                 img_height,
                 img_width,
                 mean_bgr,
                 train_mode='train',
                 dataset_type='rgbr',
                 #  is_scaling=None,
                 # Whether to crop image or otherwise resize image to match image height and width.
                 crop_img=False
                 #  arg=None
                 ):
        self.data_root = data_root
        self.train_mode = train_mode
        self.dataset_type = dataset_type
        self.data_type = 'aug'  # be aware that this might change in the future
        self.img_height = img_height
        self.img_width = img_width
        # self.scale = is_scaling
        # self.arg = arg
        # self.mean_bgr = arg.mean_pixel_values[0:3] if len(arg.mean_pixel_values) == 4 \
        #     else arg.mean_pixel_values
        self.mean_bgr = mean_bgr
        self.crop_img = crop_img

        self.data_index = self._build_index()

    def _build_index(self):
        assert self.train_mode in self.train_modes, self.train_mode
        assert self.dataset_type in self.dataset_types, self.dataset_type
        assert self.data_type in self.data_types, self.data_type

        data_root = os.path.abspath(self.data_root)
        images_path = os.path.join(data_root,
                                   'imgs',
                                   self.train_mode,
                                   self.dataset_type,
                                   self.data_type)
        labels_path = os.path.join(data_root,
                                   'edge_maps',
                                   self.train_mode,
                                   self.dataset_type,
                                   self.data_type)
        sample_indices = []
        for directory_name in os.listdir(images_path):
            image_directories = os.path.join(images_path, directory_name)
            for file_name_ext in os.listdir(image_directories):
                file_name = os.path.splitext(file_name_ext)[0]
                sample_indices.append(
                    (os.path.join(images_path, directory_name, file_name + '.jpg'),
                     os.path.join(labels_path, directory_name, file_name + '.png'),)
                )
        return sample_indices

    def __len__(self):
        return len(self.data_index)

    def __getitem__(self, idx):
        # get data sample
        image_path, label_path = self.data_index[idx]

        # load data
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        label = cv2.imread(label_path, cv2.IMREAD_GRAYSCALE)
        image, label = self.transform(img=image, gt=label)
        return dict(images=image, labels=label)

    def transform(self, img, gt):
        gt = np.array(gt, dtype=np.float32)
        if len(gt.shape) == 3:
            gt = gt[:, :, 0]
        # gt[gt< 51] = 0 # test without gt discrimination
        gt /= 255.
        # if self.yita is not None:
        #     gt[gt >= self.yita] = 1

        img = np.array(img, dtype=np.float32)
        # if self.rgb:
        #     img = img[:, :, ::-1]  # RGB->BGR
        img -= self.mean_bgr
        # data = []
        # if self.scale is not None:
        #     for scl in self.scale:
        #         img_scale = cv2.resize(img, None, fx=scl, fy=scl, interpolation=cv2.INTER_LINEAR)
        #         data.append(torch.from_numpy(img_scale.transpose((2, 0, 1))).float())
        #     return data, gt
        crop_size = self.img_height if self.img_height == self.img_width else 400

        if self.crop_img:
            _, h, w = gt.size()
            assert (crop_size < h and crop_size < w)
            i = random.randint(0, h - crop_size)
            j = random.randint(0, w - crop_size)
            img = img[:, i:i + crop_size, j:j + crop_size]
            gt = gt[:, i:i + crop_size, j:j + crop_size]
        else:
            img = cv2.resize(img,
                             dsize=(self.img_width, self.img_height))
            gt = cv2.resize(gt, dsize=(self.img_width, self.img_height))
        img = img.transpose((2, 0, 1))
        img = torch.from_numpy(img.copy()).float()
        gt = torch.from_numpy(np.array([gt])).float()
        return img, gt