import json


class TreeFileParser:
    def __init__(self, path):
        with open(path, 'r') as BT_file:
            self.bt_struct = json.load(BT_file)
            self.bt_nodes = self.bt_struct["nodes"]
            self.bt_root = self.bt_struct["root"]


class TreeObjParser:
    def __init__(self, obj):
        self.bt_struct = obj
        self.bt_nodes = self.bt_struct["nodes"]
        self.bt_root = self.bt_struct["root"]
