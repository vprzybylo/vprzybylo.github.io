"""
Holds the class for ipywidget buttons to
label incorrect predictions from a dataloader.
The dataloader, model, and all class variables
are initialized in notebooks/move_wrong_predictions.ipynb
"""

import shutil

import ipywidgets
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import clear_output, display
from ipywidgets import AppLayout, Button
from PIL import Image

import cocpit.config as config


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items()),
        )

    cls.__str__ = __str__
    return cls


@auto_str
class GUI:
    '''
    creates buttons in notebooks/move_wrong_predictions.ipynb
    to label wrong predictions from validation dataloader
    '''

    def __init__(
        self, all_labels, all_paths, all_topk_probs, all_topk_classes, all_max_preds
    ):
        '''
        requires human labels, image absolute paths, the top k probabilities output
        by the model for a bar chart of predictions, the top k class names that
        correspond to the top k probabilities, and the class index with
        the highest probability
        '''
        self.index = 0
        self.count = 0  # number of moved images
        self.all_labels = all_labels
        self.all_paths = all_paths
        self.all_topk_probs = all_topk_probs
        self.all_topk_classes = all_topk_classes
        self.all_max_preds = all_max_preds

    def make_buttons(self):
        '''
        use ipywidgets to create a box for the image, bar chart, dropdown,
        and next button
        '''
        self.center = ipywidgets.Output()  # center image with predictions

        self.label = self.all_labels[self.index]
        self.menu = ipywidgets.Dropdown(
            options=config.CLASS_NAMES,
            description="Category:",
            value=config.CLASS_NAMES[self.label],
        )
        self.bar_chart()

        self.menu.observe(self.on_change, names='value')

        # create button that progresses through incorrect predictions
        self.forward = Button(description="Next")
        self.forward.on_click(self.on_button_next)

    def on_change(self, change):
        '''
        when a class in the dropdown is selected, move the image and save
        it to the specified class
        '''
        self.save_image(change)

    def on_button_next(self, b):
        '''
        when the next button is clicked, make a new image and bar chart appear
        by updating the index within the wrong predictions by 1
        '''
        self.index = self.index + 1
        self.bar_chart()

        # keep the default dropdown value to agg
        # don't want it to change based on previous selection
        self.menu.value = config.CLASS_NAMES[self.label]

    def bar_chart(self):
        '''
        use the human and model labels and classes to
        create a bar chart with the top k predictions
        from the image at the current index
        '''
        self.label = self.all_labels[self.index]
        self.path = self.all_paths[self.index]
        self.topk_probs = self.all_topk_probs[self.index]
        self.topk_classes = self.all_topk_classes[self.index]
        self.max_pred = self.all_max_preds[self.index]

        # puts class names in order based on probabilty of prediction
        crystal_names = [config.CLASS_NAMES[e] for e in self.topk_classes]

        # add chart to ipywidgets.Output()
        with self.center:
            self.view_classifications(crystal_names)

    def view_classifications(self, crystal_names):
        '''
        bar chart code
        outputs top k predictions for a given image
        '''
        clear_output()  # so that the next fig doesnt display below
        try:
            fig, (ax1, ax2) = plt.subplots(
                constrained_layout=True, figsize=(5, 7), ncols=1, nrows=2
            )
            image = Image.open(self.path)
            ax1.imshow(image)
            ax1.set_title(
                f"Human Labeled as: {config.CLASS_NAMES[self.label]}\n"
                f"Model Labeled as: {crystal_names[0]}"
            )
            ax1.axis("off")

            y_pos = np.arange(len(self.topk_probs))
            ax2.barh(y_pos, self.topk_probs, align="center")
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(crystal_names)
            ax2.tick_params(axis="y", rotation=45)
            ax2.invert_yaxis()  # labels read top-to-bottom
            ax2.set_title("Class Probability")
            plt.show()

        except FileNotFoundError:
            print("This file was already moved and cannot be found. Please hit Next.")
            pass

    def save_image(self, change):
        '''
        move the image based on dropdown selection
        '''
        filename = self.path.split("/")[-1]

        data_dir = f'/data/data/cpi_data/training_datasets/hand_labeled_resized_{config.TAG}_sideplanes_copy/'
        # print(f"{data_dir}{config.CLASS_NAMES[self.label]}/{filename}")
        # print(f"{data_dir}{change.new}/{filename}")
        try:
            shutil.move(
                f"{data_dir}{config.CLASS_NAMES[self.label]}/{filename}",
                f"{data_dir}{change.new}/{filename}",
            )
            self.count += 1
            print(f'moved {self.count} images')

        except FileNotFoundError:
            print(self.path)
            print("File Not Found. Not moving.")
            pass
