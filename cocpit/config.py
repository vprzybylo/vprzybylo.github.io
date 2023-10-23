"""
- holds all user-defined variables
- treated as global variables that do not change in any module
- used in each module through 'import cocpit.config as config'
- call using config.VARIABLE_NAME

isort:skip_file
"""


from comet_ml import Experiment  # isort:split
from ray import tune
import os
from dotenv import load_dotenv
import torch
import sys

# cocpit version used in docker and git
TAG = "v3.1.0"

# extract each image from sheet of images
PREPROCESS_SHEETS = False

# create and save CNN
BUILD_MODEL = True

# run the category classification on quality images of ice particles
ICE_CLASSIFICATION = False

# calculates geometric particle properties and appends to databases
GEOMETRIC_ATTRIBUTES = False

# adds a column for the date from the filename
ADD_DATE = False

# only run once in loop if building model
# arbitrary campaign name used
if BUILD_MODEL:
    CAMPAIGNS = ["OLYMPEX"]
else:
    CAMPAIGNS = [
        "MACPEX",
        "ATTREX",
        "ISDAC",
        "CRYSTAL_FACE_UND",
        "AIRS_II",
        "ARM",
        "CRYSTAL_FACE_NASA",
        "ICE_L",
        "IPHEX",
        "MC3E",
        "MIDCIX",
        "MPACE",
        "OLYMPEX",
        "POSIDON",
    ]

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Absolute path to to folder where the data and models live
# BASE_DIR = '/Volumes/TOSHIBA EXT/raid/data/cpi_data'
BASE_DIR = "/home/vanessa/hulk/cocpit"

# model to load
MODEL_PATH = f"{BASE_DIR}/saved_models/no_mask/{TAG}/e[15]_bs[64]_k0_vgg16.pt"

# workers for parallelization
NUM_CPUS = 10

# number of cpus used to load data in pytorch dataloaders
NUM_WORKERS = 2

# whether to save the individual extracted images
# used in process_png_sheets_with_text.py
SAVE_IMAGES = True

# percent of image that can intersect the border
CUTOFF = 10

# how many folds used in training (cross-validation)
# kold = 0 turns this off and splits the data according to valid_size
KFOLD = 0

# ray tune hyperoptimization
TUNE = False

# images read into memory at a time during training
BATCH_SIZE = [64]
BATCH_SIZE_TUNE = [32, 64, 128, 256]

# number of epochs to train model
MAX_EPOCHS = [30]
MAX_EPOCHS_TUNE = [20, 30, 40]

# dropout rate (in model_config)
DROP_RATE_TUNE = [0.0, 0.3, 0.5]

# dropout rate (in model_config)
WEIGHT_DECAY_TUNE = [1e-5, 1e-3, 1e-2, 1e-1]

# learning rate (in model_config)
LR_TUNE = [0.001, 0.01, 0.1]

# If evidential deep learning is True, the model outputs prediction uncertainty and minimizes evidence for out of distribution samples
EVIDENTIAL = False

# effect of the KL divergence in the loss for evidential deep learning
# (e.g., if >= epoch 10, prediction error term and evidence adjustment term equally weighted)
ANNEALING_STEP = 10 if EVIDENTIAL else 0

# percent of the training dataset to use as validation
VALID_SIZE = 0.20

# images read into memory at a time during training
BATCH_SIZE = [64]

# number of epochs to train model
MAX_EPOCHS = [5]

# names of each ice crystal class
CLASS_NAMES = [
    "aggregate",
    "budding rosette",
    "bullet rosette",
    "column",
    "compact irregular",
    "fragment",
    "planar polycrystal",
    "rimed",
    # "rimed column",
    "sphere",
]

# any abbreviations in folder names where the data lives for each class
CLASS_NAME_MAP = {
    "aggregate": "agg",
    "budding rosette": "budding",
    "bullet rosette": "bullet",
    "column": "column",
    "compact irregular": "compact_irreg",
    "fragment": "fragment",
    "planar polycrystal": "planar_polycrystal",
    "rimed": "rimed",
    # "rimed column": "rimed_col",
    "sphere": "sphere",
}

# models to train
MODEL_NAMES = [
    #     "efficient",
    #     "resnet18",
    #     "resnet34",
    #     "resnet152",
    #     "alexnet",
    "vgg16",
    #      "vgg19",
    #     "densenet169",
    #     "densenet201",
]
# models to train
MODEL_NAMES_TUNE = [
    "resnet18",
    "resnet34",
    "resnet152",
    "efficient",
    "alexnet",
    "vgg16",
    "vgg19",
    "densenet169",
    "densenet201",
]

CONFIG_RAY = {
    "BATCH_SIZE": tune.choice(BATCH_SIZE_TUNE),
    "MODEL_NAMES": tune.choice(MODEL_NAMES_TUNE),
    "LR": tune.choice(LR_TUNE),
    "WEIGHT_DECAY": tune.choice(WEIGHT_DECAY_TUNE),
    "DROP_RATE": tune.choice(DROP_RATE_TUNE),
    "MAX_EPOCHS": tune.choice(MAX_EPOCHS_TUNE),
}


# model to load
MODEL_PATH = f"{BASE_DIR}/saved_models/no_mask/{TAG}/e[15]_bs[64]_k1_vgg16.pt"
if EVIDENTIAL:
    MODEL_PATH = f"{BASE_DIR}/saved_models/no_mask/evidential/{TAG}/e[30]_bs[64]_k0_1model(s).pt"

# directory to save the trained model to
MODEL_SAVE_DIR = f"{BASE_DIR}/saved_models/{TAG}/"
if EVIDENTIAL:
    MODEL_SAVE_DIR = f"{BASE_DIR}/saved_models/evidential/{TAG}/"

MODEL_SAVENAME = (
    f"{MODEL_SAVE_DIR}e{MAX_EPOCHS}_"
    f"bs{BATCH_SIZE}_"
    f"k{KFOLD}_"
    f"{len(MODEL_NAMES)}model(s).pt"
)

# directory to save validation data to
# for later inspection of predictions
VAL_LOADER_SAVE_DIR = f"{BASE_DIR}/saved_val_loaders/{TAG}/"
if EVIDENTIAL:
    VAL_LOADER_SAVE_DIR = f"{BASE_DIR}/saved_val_loaders/evidential/{TAG}/"

VAL_LOADER_SAVENAME = (
    f"{VAL_LOADER_SAVE_DIR}e{MAX_EPOCHS}_val_loader20_"
    f"bs{BATCH_SIZE}_"
    f"k{KFOLD}_"
    f"{len(MODEL_NAMES)}model(s).pt"
) 

# directory that holds the training data
DATA_DIR = f"{BASE_DIR}/cpi_data/training_datasets/{TAG}/hand_labeled_noaug/"

# whether to save the model
SAVE_MODEL = True

# If the validation dataset is coming from a csv
VAL_PREDEFINED = False

# Start with a pretrained model and only update the final layer weights
# from which we derive predictions
FEATURE_EXTRACT = False

# Update all of the model’s parameters (retrain). Default = False
USE_PRETRAINED = False

# write training loss and accuracy to csv
SAVE_ACC = True

# directory for saving training accuracy and loss csv's
ACC_SAVE_DIR = f"{BASE_DIR}/saved_accuracies/{TAG}/"
if EVIDENTIAL:
    ACC_SAVE_DIR = f"{BASE_DIR}/saved_accuracies/evidential/{TAG}/"

#  filename for saving training accuracy and loss
ACC_SAVENAME_TRAIN = (
    f"{ACC_SAVE_DIR}train_acc_loss_e{max(MAX_EPOCHS)}_"
    f"bs{max(BATCH_SIZE)}_k{KFOLD}_"
    f"{len(MODEL_NAMES)}model(s).csv"
)
#  output filename for validation accuracy and loss
ACC_SAVENAME_VAL = (
    f"{ACC_SAVE_DIR}val_acc_loss_e{max(MAX_EPOCHS)}_"
    f"bs{max(BATCH_SIZE)}_k{KFOLD}_"
    f"{len(MODEL_NAMES)}model(s).csv"
)
# output filename for precision, recall, F1 file
METRICS_SAVENAME = (
    f"{ACC_SAVE_DIR}val_metrics_e{max(MAX_EPOCHS)}_"
    f"bs{max(BATCH_SIZE)}_k{KFOLD}_"
    f"{len(MODEL_NAMES)}model(s).csv"
)

CONF_MATRIX_SAVENAME = f"{BASE_DIR}/plots/conf_matrix.png"
CLASSIFICATION_REPORT_SAVENAME = f"{BASE_DIR}/plots/classification_report.png"

# where to save final databases to
FINAL_DIR = f"{BASE_DIR}/final_databases/vgg16/{TAG}/"
if not os.path.exists(FINAL_DIR):
    os.makedirs(FINAL_DIR)

# log experiment to comet for tracking?
LOG_EXP = False
NOTEBOOK = os.path.basename(sys.argv[0]) != "__main__.py"
load_dotenv()  # loading sensitive keys from .env file
if LOG_EXP and not NOTEBOOK and BUILD_MODEL:
    print("logging to comet ml...")
    API_KEY = os.getenv("API_KEY")
    WORKSPACE = os.getenv("WORKSPACE")
    PROJECT_NAME = os.getenv("PROJECT_NAME")
    experiment = Experiment(
        api_key=API_KEY,
        project_name=PROJECT_NAME,
        workspace=WORKSPACE,
    )

    params = {
        variable: eval(variable)
        for variable in [
            "TAG",
            "KFOLD",
            "BATCH_SIZE",
            "MAX_EPOCHS",
            "CLASS_NAMES",
            "VALID_SIZE",
            "MODEL_NAMES",
            "DATA_DIR",
            "SAVE_ACC",
            "NUM_WORKERS",
        ]
    }

    experiment.log_parameters(params)
    experiment.add_tag(TAG)
else:
    experiment = None
