"""
Retrives data loaders from Pytorch
"""

import cocpit.config as config  # isort: split
import os
import random
from typing import List, Optional, Union

import numpy as np
import torch
import torch.utils.data
import torch.utils.data.sampler as sampler
from PIL import Image, ImageFile
from torch.utils.data import Dataset
from torchvision import datasets, transforms

from cocpit.auto_str import auto_str

ImageFile.LOAD_TRUNCATED_IMAGES = True


@auto_str
class ImageFolderWithPaths(datasets.ImageFolder):
    """
    - Custom dataset that includes image file paths.
    - Used in get_data in this module

    Args:
        root (str): data directory
        transform (transforms.Compose): transformations based on train, val, or test
    """

    # Override the __getitem__ method. This is the method that dataloader calls
    def __getitem__(self, index):
        # this is what ImageFolder normally returns
        original_tuple = super().__getitem__(index)
        # the image file path
        path = self.imgs[index][0]
        # make a new tuple that includes original and the path
        tuple_with_path = original_tuple + (path,)
        return (tuple_with_path, index)


@auto_str
class TestDataSet(Dataset):
    """
    - Create dataloader for new or unseen testing data
    - Used in notenooks/check_classifications.ipynb for example instantiation
    - Applies transformations such as resizing and normalization

    Args:
        open_dir (Optional[str, List[str]]): directory holding the data to open
        file_list (List[str]): list of filenames
    """

    def __init__(self, open_dir: Union[str, List[str]], file_list: List[str]):

        self.open_dir = open_dir
        self.file_list = list(file_list)
        self.transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]
        )

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        if len([self.open_dir]) == 1 or self.open_dir == "":
            path = os.path.join(self.open_dir, self.file_list[idx])
        else:
            path = os.path.join(self.open_dir[idx], self.file_list[idx])

        image = Image.open(path)
        tensor_image = self.transform(image)
        return (tensor_image, path)


def get_data(phase: str) -> ImageFolderWithPaths:
    """
    - Use the Pytorch ImageFolder class to read in training data
    - Training data needs to be organized all in one folder with subfolders for each class
    - Applies transforms and data augmentation

    Args:
        phase (str): 'train' or 'val'
    Returns:
        data (tuple): (image, label, path)
    """

    transform_dict = {
        "train": transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.RandomHorizontalFlip(),
                # transforms.RandomVerticalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        ),
        "val": transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        ),
    }

    return ImageFolderWithPaths(root=config.DATA_DIR, transform=transform_dict[phase])


def balanced_sampler(train_labels: List[int]) -> sampler.WeightedRandomSampler:
    """
    - Creates weights for each class for use in the dataloader sampler argument
    - Lower count classes are sampled more frequently and higher count classes are sampled less frequently
    - Only used in the training dataloader

    Args:
        train_labels (List[int]): numerically labeled classes for training dataset

    Returns:
        class_sample_counts (List): number of samples per class
        train_samples_weights (torch.DoubleTensor): weights for each class for sampling
    """
    class_sample_counts = [0] * len(config.CLASS_NAMES)
    for target in train_labels:
        class_sample_counts[target] += 1
    print(
        "counts per class in training data (before sampler): ",
        class_sample_counts,
    )

    class_weights = 1.0 / torch.Tensor(class_sample_counts)
    train_samples_weights = [
        float(class_weights[class_id]) for class_id in train_labels
    ]
    return sampler.WeightedRandomSampler(
        train_samples_weights, len(train_samples_weights), replacement=True
    )


def seed_worker(worker_id: int) -> None:
    """https://pytorch.org/docs/stable/notes/randomness.html"""
    torch_seed = torch.initial_seed()
    random.seed(torch_seed + worker_id)
    if torch_seed >= 2**30:  # make sure torch_seed + workder_id < 2**32
        torch_seed = torch_seed % 2**30
    np.random.seed(torch_seed + worker_id)


def create_loader(
    data: torch.utils.data.Subset,
    batch_size: int,
    sampler: Optional[torch.utils.data.Sampler],
    pin_memory: bool = True,
) -> torch.utils.data.DataLoader:
    """
    Make an iterable of batches across a dataset

    Args:
        data (torch.utils.data.Subset): the dataset to load
        batch_size (int): number of images to be read into memory at a time
        sampler (torch.utils.data.Sampler): the method used to iterate over indices of dataset (e.g., random shuffle)
        pin_memory (bool): For data loading, passing pin_memory=True to a DataLoader will automatically
                           put the fetched data Tensors in pinned memory, and thus enables faster data
                           transfer to CUDA-enabled GPUs.
    Returns:
        torch.utils.data.DataLoader: a dataset to be iterated over using sampling strategy

    """
    g = torch.Generator()
    g.manual_seed(0)

    return torch.utils.data.DataLoader(
        data,
        batch_size=batch_size,
        sampler=sampler,
        num_workers=config.NUM_WORKERS,
        pin_memory=pin_memory,
        worker_init_fn=seed_worker,
        generator=g,
    )


def save_valloader(val_data: torch.utils.data.Subset) -> None:
    """
    Save validation dataloader based on paths in config.py

    Args:
        val_data (torch.utils.data.Subset): the validation dataset
    """
    # directory to save validation data to
    # for later inspection of predictions
    VAL_LOADER_SAVE_DIR = f"{config.BASE_DIR}/saved_val_loaders/{config.TAG}/"

    VAL_LOADER_SAVENAME = (
        f"{VAL_LOADER_SAVE_DIR}e{config.MAX_EPOCHS}_"
        f"bs{config.BATCH_SIZE}_"
        f"k{config.KFOLD}_"
        f"{len(config.MODEL_NAMES)}model(s).pt"
    )

    if not os.path.exists(VAL_LOADER_SAVE_DIR):
        os.makedirs(VAL_LOADER_SAVE_DIR)
    torch.save(val_data, VAL_LOADER_SAVENAME)
