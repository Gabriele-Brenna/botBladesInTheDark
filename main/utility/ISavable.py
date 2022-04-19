import copy
import json
from typing import List


class ISavable:
    def save_to_dict(self) -> dict:
        return json.loads(json.dumps(copy.deepcopy(self), default=lambda o: o.__dict__, indent=5))


def pop_dict_items(data: dict, items: List[str]):
    for elem in items:
        data.pop(elem)


def save_to_json(to_save: List[ISavable]) -> str:
    len_to_save = len(to_save)
    if len_to_save == 1:
        return json.dumps(to_save[0].save_to_dict(), indent=5)
    elif len_to_save > 1:
        temp = []
        for i in range(len_to_save):
            temp.append(to_save[i].save_to_dict())
        return json.dumps(temp, indent=5)
