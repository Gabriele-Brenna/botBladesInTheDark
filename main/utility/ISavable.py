import copy
import json
from typing import List, Union


class ISavable:
    def save_to_dict(self) -> dict:
        return json.loads(json.dumps(copy.deepcopy(self), default=lambda o: o.__dict__, indent=5))


def pop_dict_items(data: dict, items: List[str]):
    for elem in items:
        data.pop(elem)


def save_to_json(to_save: Union[List[ISavable], ISavable]) -> str:
    if isinstance(to_save, ISavable):
        return json.dumps(to_save.save_to_dict(), indent=5)
    else:
        temp = []
        for i in range(len(to_save)):
            temp.append(to_save[i].save_to_dict())
        return json.dumps(temp, indent=5)
