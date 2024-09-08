from tkinter import *

from domain.download import Downloader
from domain.merge import Merge
from domain.shared import Shared


def download_algorithm():
    shared: Shared = Shared()
    downloader: Downloader = Downloader(shared=shared)
    # merge: Merge = Merge(shared=shared)
    downloader.download_data()


def main_page():
    window = Tk()
    window.title("System")

    Label(window, text="Choose an algorithm", font="Lucida 14 bold").grid(row=1, columnspan=2)

    btn1 = Button(
        window,
        text="Download Sentinel data",
        command=lambda: download_algorithm(),
    )
    btn1.grid(row=2, columnspan=2, padx=5, pady=5, sticky="ew")

    close_btn = Button(window, text="Close program", command=window.destroy)
    close_btn.grid(row=4, columnspan=2, padx=10, pady=10)

    window.mainloop()


if __name__ == "__main__":
    main_page()
