from typing import List, Dict

class Bind:
    def __init__(self, func_name: str, params: List[str]) -> None:
        self.func_name = func_name
        self.params = params


class KeyManager:
    def __init__(self) -> None:
        self.methods: Dict[str, Bind] = {}
        self.methods["h"] = Bind("prev_grid", [])
        self.methods["l"] = Bind("next_grid", [])


    def get_method(self, key: str) -> Bind:
        if (key not in self.methods):
            return None
        return self.methods[key]
