import copy
import os
from functools import partial
from multiprocessing import Pool
from typing import List, Tuple

import cv2
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from twilio.rest import Client

import cocpit.config as config  # isort:split
from cocpit.auto_str import auto_str


@auto_str
class Image:
    """
    Reads, extracts, and performs morphological processing on png sheets of CPI images

    Args:
        open_dir (str): the path where the files are located
        file (str): file [including path] to sheet with cpi images
        save_dir (str): the path where the files are saved
        files (str): list of files to be processed
        widths (List[float]): width of rectangular roi frame
        heights (List[float]): height of rectangular roi frame
        particle_heights (List[float]): particle heights
        particle_widths (List[float]): particle widths
        cutoffs (List[float]): percent of particle intersecting border
    """

    def __init__(self, open_dir: str, file: str, save_dir: str):
        self.open_dir = open_dir
        self.file = file
        self.save_dir = save_dir
        self.files: List[str] = []
        self.widths: List[float] = []
        self.heights: List[float] = []
        self.particle_heights: List[float] = []
        self.particle_widths: List[float] = []
        self.cutoffs: List[float] = []

    def read_image(self, show_original: bool) -> None:
        """
        Reads sheet into memory

        Args:
            show_original (bool): whether to show the original sheet in an opencv window
        """
        print(self.open_dir + self.file)
        self.image = cv2.imread(self.open_dir + self.file)
        # make a copy so that image can be altered and processed
        height, width, channels = self.image.shape
        # crop for header (consistent at 25 pixels from top)
        self.image = self.image[25:height, 0:width]
        # make an unchanged copy
        self.image_og = copy.deepcopy(self.image)

        if show_original:
            cv2.imshow("original", self.image_og)
            cv2.waitKey(0)

    def dilate(self, show_dilate: bool) -> None:
        """
        Increases the object area and useful in joining broken parts of an image.
        """
        kernel = np.ones((10, 10), np.uint8)
        self.image = cv2.dilate(self.image, kernel, iterations=1)
        if show_dilate:
            cv2.imshow("Image", self.image)
            cv2.waitKey(0)

    def find_sheet_contours(self) -> List[int]:
        """
        Find all contours on sheet and convert to b/w

        Returns:
            cnts (List[int]): contours from cv2.findContours
        """
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # threshold the binary sheet
        # contours dependent on hardcoded threshold - some thin white boundaries are 253 so 252 picks these up
        self.thresh = cv2.threshold(gray, 252, 255, cv2.THRESH_BINARY_INV)[1]
        (cnts, _) = cv2.findContours(
            self.thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        return cnts

    def remove_text(self, cnts: List[int], small_thresh: float = 200) -> None:
        """
        Removes text such as date/time stamp by drawing over small contours in white.
        If the text is on the particle itself and connected to the largest contour, it stays
        Should a very small particle be < 200 px^2, it is also masked

        Args:
            cnts (List[int]): list of contours
            small_thresh (float): mask areas in px smaller than this threshold
        """
        # only mask contours with small area (aka the text)
        for c in cnts:
            if cv2.contourArea(c) < small_thresh:
                cv2.drawContours(
                    self.thresh, [c], 0, (255, 255, 255), -1
                )  # -1 fills contour

    def largest_contour(self, cnts):
        """
        Find largest contour out of list of contours on image

        Args:
            cnts (list): list of contours
        """
        self.largest_cnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]

    def particle_dimensions(self) -> Tuple[float, float]:
        """
        Calculate the length and width of particles in microns
        from a rectangular bounding box
        CPI probe: 1 px = 2.3 microns
        """
        rect = cv2.minAreaRect(self.largest_cnt)
        (_, _), (width, height), _ = rect
        return width * 2.3, height * 2.3

    def cutoff(self):
        """
        Determines the % of pixels that intersect
        the border or perimeter of the image
        """
        locations = np.where(self.thresh != 0)
        count = sum(
            xl == 5 or yl == 5 or xl == self.height - 5 or yl == self.width - 5
            for xl, yl in zip(locations[0], locations[1])
        )

        return (count / (2 * self.height + 2 * self.width)) * 100

    def save_image(self, cropped):
        """
        Save cropped image

        Args:
            cropped (np.array): cropped image from sheet
        """
        if not os.path.exists(self.save_dir):
            print("making dir ", self.save_dir)
            os.makedirs(self.save_dir)
        cv2.imwrite(self.save_dir + self.file_out, cropped)

    def extract_contours(self, show_cropped):
        """
        Finds, extracts and saves ROIs from sheets
        Saves filename, width, height, and cutoff to lists for a df

        Parameters:
            show_cropped (bool): whether to show the ROI regions
        """

        (cnts, _) = cv2.findContours(
            self.thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # draw = cv2.drawContours(self.image, cnts, -1, (0,0,255), -1)
        # cv2.imshow("Image", draw)
        # cv2.waitKey(0)
        for i, c in enumerate(cnts):
            # remove small particles that have numbers attached to largest contour
            if cv2.contourArea(c) > 200:
                # crop the rectangles/contours from the sheet
                # save width and height for cutoff calculation
                rect = cv2.boundingRect(c)
                x, y, self.width, self.height = rect

                cropped = self.image_og[y : y + self.height, x : x + self.width]

                if show_cropped:
                    cv2.imshow("cropped", cropped)
                    cv2.waitKey(0)

                # converts ROI cropped regions to b/w
                # overwrites self.thresh from whole sheet to particle rectangle
                gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                self.thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV)[1]

                # find contours within cropped regions
                (cnts, _) = cv2.findContours(
                    self.thresh.copy(),
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_NONE,
                )

                # make sure the thresholding picks up a contour in the rectangle
                # and cutoff criteria is met
                cutoff = self.cutoff()
                if (
                    cnts
                    and cutoff < config.CUTOFF
                    and self.width > 50
                    and self.height > 50
                ):

                    # calculate particle length and width
                    self.largest_contour(cnts)
                    (
                        particle_width,
                        particle_height,
                    ) = self.particle_dimensions()

                    # resize the cropped images to be the same size for CNN
                    # cropped = cv2.resize(
                    #     cropped, (1000, 1000), interpolation=cv2.INTER_AREA
                    # )

                    # get cutoff of each particle and append to list to append to df
                    self.cutoffs.append(cutoff)
                    self.file_out = self.file[:-4] + "_" + str(i) + ".png"
                    self.files.append(self.file_out)
                    self.widths.append(self.width)  # of rectangular roi frame
                    self.heights.append(self.height)  # of rectangular roi frame
                    self.particle_heights.append(particle_height)
                    self.particle_widths.append(particle_width)

                    if config.SAVE_IMAGES:
                        self.save_image(cropped)


def run(
    file,
    open_dir,
    save_dir,
    show_original=False,
    show_dilate=False,
    show_cropped=False,
):
    """
    main method calls
    """

    img = Image(open_dir, file, save_dir)
    img.read_image(show_original)
    # when this is uncommented, the image frame is underestimated by 4 pixels
    img.dilate(show_dilate)
    cnts = img.find_sheet_contours()
    img.remove_text(cnts)
    img.extract_contours(show_cropped)

    return (
        img.files,
        img.widths,
        img.heights,
        img.particle_widths,
        img.particle_heights,
        img.cutoffs,
    )


def make_df(
    save_df, files, widths, heights, particle_widths, particle_heights, cutoffs
):
    """
    creates df with original image and particle widths, heights, and % cutoff
    writes to csv file for each campaign
    """

    cutoffs_formatted = ["%.2f" % elem for elem in cutoffs]
    df_dict = {
        "filename": files,
        "frame width [pixels]": widths,
        "frame height [pixels]": heights,
        "particle width [microns]": particle_widths,
        "particle height [microns]": particle_heights,
        "cutoff [%]": cutoffs_formatted,
    }
    df = pd.DataFrame(df_dict)

    #    len_before = len(df)
    #     df.drop_duplicates(
    #         subset=[
    #             "frame width",
    #             "frame height",
    #             "particle width",
    #             "particle height",
    #             "cutoff",
    #         ],
    #         keep="first",
    #         inplace=True,
    #     )
    #     print(len(df))
    #     print("removed %d duplicates" % (len_before - len(df)))

    df.to_csv(save_df, index=False)


def send_message():
    """
    use twilio to receive a text when the processing has finished!
    register for an account and then:
    add ACCOUNT_SID, AUTH_TOKEN, and PHONE_NUMBER to a .env file
    """
    load_dotenv()
    account_sid = os.getenv("ACCOUNT_SID")
    auth_token = os.getenv("AUTH_TOKEN")
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body="Processing Complete!",
        from_="+19285175160",  # Provided phone number
        to=os.getenv("PHONE_NUMBER"),
    )  # Your phone number
    message.sid


def main(
    sheet_dir,
    save_dir,
    save_df,
    show_original,
    show_dilate,
    show_cropped,
):

    files = os.listdir(sheet_dir)
    p = Pool(processes=config.NUM_CPUS)
    results = p.map(
        partial(run, open_dir=sheet_dir, save_dir=save_dir),
        files,
    )

    p.close()
    p.join()

    results = np.array(results, dtype=object)

    files = np.concatenate(results[:, 0])
    widths = np.concatenate(results[:, 1])
    heights = np.concatenate(results[:, 2])
    particle_widths = np.concatenate(results[:, 3])
    particle_heights = np.concatenate(results[:, 4])
    cutoffs = np.concatenate(results[:, 5])

    make_df(
        save_df,
        files,
        widths,
        heights,
        particle_widths,
        particle_heights,
        cutoffs,
    )
    # send_message()
