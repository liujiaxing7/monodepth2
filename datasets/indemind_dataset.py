from __future__ import absolute_import, division, print_function

import os
import skimage.transform
import numpy as np
import PIL.Image as pil

from kitti_utils import generate_depth_map
from .mono_dataset import MonoDataset


class IndemindDataset(MonoDataset):
    """Superclass for different types of KITTI dataset loaders
    """
    def __init__(self, *args, **kwargs):
        super(IndemindDataset, self).__init__(*args, **kwargs)

        # NOTE: Make sure your intrinsics matrix is *normalized* by the original image size.
        # To normalize you need to scale the first row by 1 / image_width and the second row
        # by 1 / image_height. Monodepth2 assumes a principal point to be exactly centered.
        # If your principal point is far from the center you might need to disable the horizontal
        # flip augmentation.
        self.K = np.array([[0.486, 0, 0.537, 0],
                           [0, 0.778, 0.507, 0],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]], dtype=np.float32)

        # self.check_image()

    def check_image(self):
        from tqdm import tqdm
        print("check bad image")
        with open('{}_bad_images.txt'.format("train" if self.is_train else "val"), 'w') as file:
            for f in tqdm(self.filenames):
                image_group = {}
                folder, image_group[0], image_group[-1], image_group[1], side = f.split()
                for key, val in image_group.items():
                    try:
                        self.loader(self.get_image_path(folder, val, 'l'))
                        self.loader(self.get_image_path(folder.replace('cam0', 'cam1'), val, 'r'))
                    except:
                        file.write(f+'\n')
                        break

    def check_depth(self):
        return False

    def get_image_path(self, folder, file_name, side):
        image_path = os.path.join(self.data_path, folder, file_name)
        # print(folder, " ", file_name, " ", side, " ", image_path)
        return image_path

    def get_color(self, folder, file_name, side, do_flip):
        color = self.loader(self.get_image_path(folder, file_name, side))

        if do_flip:
            color = color.transpose(pil.FLIP_LEFT_RIGHT)

        return color

    def get_images(self, index, do_flip):
        do_flip = False
        inputs = {}
        image_group = {}

        folder, image_group[0], image_group[-1], image_group[1], side = self.filenames[index].split()

        # print('{} item--------------------'.format(index))
        # print(self.filenames[index])
        for i in self.frame_idxs:
            # print("id: ", i)
            if i == "s":
                other_side = {"r": "l", "l": "r"}[side]
                inputs[("color", i, -1)] = self.get_color(folder.replace('cam0', 'cam1'), image_group[0], other_side, do_flip)
            else:
                inputs[("color", i, -1)] = self.get_color(folder, image_group[i], side, do_flip)

        return inputs, side, do_flip
