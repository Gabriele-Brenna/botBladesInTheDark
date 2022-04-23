import copy
import json
from typing import List, Union


class ISavable:
    """
    This class models an interface used to get a dictionary of an object that implements it
    """
    def save_to_dict(self) -> dict:
        """
        This method is used to get the dictionary of the object that can then be saved in json format
        :return:
        """
        return json.loads(json.dumps(copy.deepcopy(self), default=lambda o: o.__dict__, indent=5))


def pop_dict_items(data: dict, items: List[str]):
    """
    This method is used to pop a list of items contained inside a dictionary

    :param data: dictionary
    :param items: list of keys representing the items to remove
    """
    for elem in items:
        data.pop(elem)


def save_to_json(to_save: Union[List[ISavable], ISavable]) -> str:
    """
    This method is used to save an object or a list of object in a string with json syntax

    :param to_save: is either an object or a list of object that inherit from ISavable
    :return: string with json syntax
    """
    if isinstance(to_save, ISavable):
        return json.dumps(to_save.save_to_dict(), indent=5)
    else:
        temp = []
        for i in range(len(to_save)):
            temp.append(to_save[i].save_to_dict())
        return json.dumps(temp, indent=5)
