import os
from os.path import exists
from pathlib import Path


def path_finder(file_name: str) -> str:
    """
    Method used to find the path of a given file.

    :param file_name: name of the file
    :return:
    """
    resources_path = get_resources_folder()
    file_path = os.path.join(resources_path, file_name)
    if exists(file_path):
        return file_path
    file_path = os.path.join(resources_path, "lang")
    file_path = os.path.join(file_path, file_name)
    if exists(file_path):
        return file_path


def get_resources_folder() -> str:
    resources_path = Path(__file__).parent.parent.parent.resolve()
    return os.path.join(resources_path, "resources")


def get_font(font_name: str) -> str:
    resource = get_resources_folder()
    font_folder = os.path.join(resource, "fonts")
    return os.path.join(font_folder, font_name)
