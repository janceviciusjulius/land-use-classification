import os


class Shared:

    @staticmethod
    def create_folder():
        path = os.path.join(os.getcwd(), options.SHP_folder_name)
        if not isdir(path):
            os.mkdir(path)
        return path