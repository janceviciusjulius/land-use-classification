from tkinter import *

from osgeo import gdal

from domain.classification import Classification
from domain.download import Downloader
from domain.join import Join
from domain.merge import Merge
from domain.shared import Shared
from schema.constants import Constants
from schema.names import Name

gdal.UseExceptions()


def download_algorithm():
    shared: Shared = Shared()
    downloader: Downloader = Downloader(shared=shared)
    downloader.download_data()
    merge: Merge = Merge(
        shared=shared,
        interpolation=downloader.interpolation,
        start_date=downloader.start_date,
        end_date=downloader.end_date,
        max_cloud_cover=downloader.max_cloud_cover,
        folders=downloader.folders,
        files=downloader.files,
    )
    merge.process_data()


def join_algorithm():
    shared: Shared = Shared()
    join: Join = Join(shared=shared)
    join.join()


def classification_algorithm():
    print("OPA")
    shared: Shared = Shared()
    classification: Classification = Classification(shared=shared)
    classification.classify()


def main_page():
    window = Tk()
    window.title(Name.TITLE)

    Label(window, text=Name.CHOOSE, font=Name.FONT).grid(row=1, columnspan=2)

    btn1 = Button(window, text=Name.DOWNLOAD, command=lambda: download_algorithm())
    btn2 = Button(window, text=Name.JOIN, command=lambda: join_algorithm())
    btn3 = Button(window, text=Name.CLASSIFICATION, command=lambda: classification_algorithm())

    btn1.grid(row=2, columnspan=2, padx=5, pady=5, sticky=Constants.STICKY)
    btn2.grid(row=4, columnspan=2, padx=5, pady=5, sticky=Constants.STICKY)
    btn3.grid(row=6, columnspan=2, padx=5, pady=5, sticky=Constants.STICKY)

    close_btn = Button(window, text=Name.CLOSE, command=window.destroy)
    close_btn.grid(row=8, columnspan=2, padx=10, pady=10)

    window.mainloop()


if __name__ == "__main__":
    main_page()
