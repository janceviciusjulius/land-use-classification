def generate_parameters():
    download_process: bool = False
    x = 0
    while not download_process:

        print(x)
        if x >= 10:
            download_process = True
        x += 1


generate_parameters()
