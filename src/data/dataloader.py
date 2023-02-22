import torch
from torch.utils.data import Dataset, DataLoader, SubsetRandomSampler, RandomSampler
import glob
import os
import numpy as np
import pytest


class ReflowDataset(Dataset):
    def __init__(self, geom, heatmap, recipe, sep=' '):
        self.geom = glob.glob(os.path.join(geom, "*"))
        self.heatmap = glob.glob(os.path.join(heatmap, "*"))
        self.recipe = glob.glob(os.path.join(recipe, "*"))
        self.recipe_id = np.unique([int(c.split("/")[-1].split(".")[0]) for c in self.recipe])

    def __len__(self):
        return len(self.recipe_id)

    def __getitem__(self, recipe_idx):
        print(recipe_idx)

        geom = torch.stack([torch.FloatTensor(np.loadtxt(c, delimiter=" ")) for c in self.geom if recipe_idx == int(c.split("/")[-1].split("-")[0])], dim=0)
        heatmap = torch.stack([torch.FloatTensor(np.loadtxt(c, delimiter=" ")) for c in self.heatmap if recipe_idx == int(c.split("/")[-1].split("-")[0])], dim=0)

        x = torch.stack([geom, heatmap], dim=1)
        y = torch.concat([torch.FloatTensor(np.loadtxt(c, delimiter=" ")) for c in self.recipe if recipe_idx == int(c.split("/")[-1].split(".")[0])], dim=0)

        return x, y


def generate_dataloader(geom_path, heatmap_path, recipe_path, batch_size, train=True, M=None):
    dataset = ReflowDataset(geom_path, heatmap_path, recipe_path)
    if train:

        if len(dataset) < M:
            indices = np.random.randint(0, len(dataset), M)
            sampler = SubsetRandomSampler(indices)
        else:
            sampler = RandomSampler(dataset, replacement=True)

        dataloader = DataLoader(dataset, sampler=sampler, batch_size=batch_size)

    else:
        dataloader = DataLoader(dataset, shuffle=False, batch_size=1)

    return dataloader