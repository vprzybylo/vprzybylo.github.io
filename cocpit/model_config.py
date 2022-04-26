"""
model configurations for:
    - dropout
    - optimizer
    - device settings (cpu/gpu)
    - parameters to update
"""
import cocpit
import cocpit.config as config
import torch
from torch import nn, optim


class ModelConfig:
    """Model Configurations"""

    def __init__(self, model):
        self.model = model

    def update_params(self, feature_extract=False):
        """
        When feature extracting, we only want to update the parameters
        of the last layer, or in other words, we only want to update the
        parameters for the layer(s) we are reshaping. Therefore, we do
        not need to compute the gradients of the parameters that we are
        not changing, so for efficiency we set the .requires_grad attribute
        to False. This is important because by default, this attribute is
        set to True. Then, when we initialize the new layer and by default
        the new parameters have .requires_grad=True so only the new layer’s
        parameters will be updated. When we are finetuning we can leave all
        of the .required_grad’s set to the default of True.
        """
        params_to_update = self.model.parameters()
        if feature_extract:
            params_to_update = [
                param
                for _, param in self.model.named_parameters()
                if param.requires_grad
            ]

        print("model params: ", self.count_parameters())

        return params_to_update

    def count_parameters(self):
        """
        number of model parameters to update
        """
        return sum(p.numel() for p in self.model.parameters() if p.requires_grad)

    def optimizer(self):
        return optim.SGD(self.update_params(), lr=0.01, momentum=0.9, nesterov=True)

    def set_dropout(self, drop_rate: float = 0.1):
        """
        technique to fight overfitting and improve neural network generalization
        """
        for _, child in self.model.named_children():
            if isinstance(child, torch.nn.Dropout):
                child.p = drop_rate
            self.set_dropout(child, drop_rate=drop_rate)

    def to_device(self):
        """
        push model to gpu(s) if available
        """
        if torch.cuda.device_count() > 1:
            print("Using", torch.cuda.device_count(), "GPUs!")
            self.model = nn.DataParallel(self.model)
        self.model = self.model.to(config.DEVICE)


def main(model_name):
    model = cocpit.models.initialize_model(model_name)
    m = ModelConfig(model)
    m.to_device()
    return m.optimizer(), m.model
