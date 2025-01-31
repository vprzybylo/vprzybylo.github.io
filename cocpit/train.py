"""Training methods"""
import csv
import os

import numpy as np
import torch

import cocpit
from cocpit import config as config
from cocpit.performance_metrics import Metrics


class Train(Metrics):
    """Perform training methods on batched dataset

    Args:
        f (cocpit.fold_setup.FoldSetup): instance of FoldSetup class
        epoch (int): epoch index in training loop
        epochs (int): total epochs for training loop
        model_name (str): name of model architecture
        kfold (int): number of folds use in k-fold cross validation
        c (model_config.ModelConfig): instance of ModelConfig class
    """

    def __init__(
        self,
        f: cocpit.fold_setup.FoldSetup,
        epoch: int,
        epochs: int,
        model_name: str,
        kfold: int,
        c: cocpit.model_config.ModelConfig,
    ):
        super().__init__(f, epoch, epochs)
        self.model_name = model_name
        self.kfold = kfold
        self.c = c

    def label_counts(self, label_cnts: np.ndarray, labels: torch.Tensor) -> np.ndarray:
        """
        Calculate the # of labels per batch to ensure weighted random sampler is correct

        Args:
            label_cnts (np.ndarray): number of labels per class from all batches before
            labels (torch.Tensor): class/label names
        Returns:
            label_cnts (np.ndarray): sum of label counts from prior batches plus current batch
        """

        for n, _ in enumerate(config.CLASS_NAMES):
            label_cnts[n] += len(np.where(labels.numpy() == n)[0])
        print("LABEL COUNT = ", label_cnts)
        return label_cnts

    def forward(self) -> None:
        """perform forward operator and make predictions"""
        with torch.set_grad_enabled(True):
            outputs = self.c.model(self.inputs)
            self.loss = self.c.criterion(outputs, self.labels)
            _, self.preds = torch.max(outputs, 1)
            self.loss.backward()  # compute updates for each parameter
            self.c.optimizer.step()  # make the updates for each parameter

    def iterate_batches(self, print_label_count: bool = False) -> None:
        """iterate over a batch in a dataloader and train

        Args:
            print_label_count (bool): if True print class counts when iterating batches
        """

        label_cnts_total = np.zeros(len(config.CLASS_NAMES))
        for self.batch, ((inputs, labels, _), _) in enumerate(
            self.f.dataloaders["train"]
        ):
            if print_label_count:
                self.label_counts(label_cnts_total, labels)

            self.inputs = inputs.to(config.DEVICE)
            self.labels = labels.to(config.DEVICE)

            # zero the parameter gradients
            self.c.optimizer.zero_grad()
            self.forward()
            self.batch_metrics()
            if (self.batch + 1) % 5 == 0:
                self.print_batch_metrics("train")

    def write_output(self) -> None:
        """
        Write acc and loss to csv file within model, epoch, kfold iteration
        """
        #  directory for saving training accuracy and loss csv's
        ACC_SAVE_DIR = f"{config.BASE_DIR}/saved_accuracies/{config.TAG}/"
        if not os.path.exists(ACC_SAVE_DIR):
            os.makedirs(ACC_SAVE_DIR)
        # filename for saving training accuracy and loss
        ACC_SAVENAME_TRAIN = (
            f"{ACC_SAVE_DIR}train_acc_loss_e{max(config.MAX_EPOCHS)}_"
            f"bs{max(config.BATCH_SIZE)}_k{config.KFOLD}_"
            f"{len(config.MODEL_NAMES)}model(s).csv"
        )

        with open(ACC_SAVENAME_TRAIN, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    self.model_name,
                    self.epoch,
                    self.kfold,
                    self.f.batch_size,
                    self.epoch_acc.cpu().numpy(),
                    self.epoch_loss,
                ]
            )
            file.close()

    def run(self) -> None:
        """call above functions to run training"""
        self.iterate_batches()
        self.epoch_metrics()
        self.log_epoch_metrics("epoch_acc_train", "epoch_loss_train")
        self.print_epoch_metrics("Train")
        if config.SAVE_ACC:
            self.write_output()
