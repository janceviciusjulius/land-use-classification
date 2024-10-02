from tkinter import *

from osgeo import gdal

from domain.classification import Classification
from domain.download import Downloader
from domain.join import Join
from domain.merge import Merge
from domain.shared import Shared

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
    shared: Shared = Shared()
    classification: Classification = Classification(shared=shared)


def main_page():
    window = Tk()
    window.title("System")

    Label(window, text="Choose an algorithm", font="Lucida 14 bold").grid(row=1, columnspan=2)

    btn1 = Button(window, text="Download Sentinel data", command=lambda: download_algorithm())
    btn2 = Button(window, text="Join/Crop", command=lambda: join_algorithm())
    btn3 = Button(window, text="Data Classification", command=lambda: classification_algorithm())

    btn1.grid(row=2, columnspan=2, padx=5, pady=5, sticky="ew")
    btn2.grid(row=4, columnspan=2, padx=5, pady=5, sticky="ew")
    btn3.grid(row=6, columnspan=2, padx=5, pady=5, sticky="ew")

    close_btn = Button(window, text="Close program", command=window.destroy)
    close_btn.grid(row=8, columnspan=2, padx=10, pady=10)

    window.mainloop()


if __name__ == "__main__":
    main_page()
