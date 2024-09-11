import os.path

x = ("FileNotFoundError: [Errno 2] No such file or directory:"
     " '/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-04 0-0%/CLEANED 2024-09-01..2024-09-04 0-0%/4. 20240901 T34UDG 0.0%.tiff'"
     " -> '4. 20240901 T34UDG 0.0%.tiff/2024-09-01..2024-09-04 T34UDG.tiff'")


xx = "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-09-01..2024-09-04 0-0%/CLEANED 2024-09-01..2024-09-04 0-0%/4. 20240901 T34UDG 0.0%.tiff"


print(os.path.dirname(xx))