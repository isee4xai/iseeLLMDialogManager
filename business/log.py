# import json
# from business.bt.nodes.type import State


# class Logger:

#     def __init__(self) -> None:
#         self.node_variables = ['question',
#                                'variable', 'value', 'endpoint', 'params']
#         self.exec_variables = ['question', 'variable']
#         self.storage = list()
#         with open('data/isee-node-execution.json', 'r') as _file:
#             self.exec_json = json.load(_file)
#         with open('data/isee-node.json', 'r') as _file:
#             self.node_json = json.load(_file)
#         with open('data/isee-bases.json', 'r') as _file:
#             self.bases = json.load(_file)

#         self.exec_json_str = json.dumps(self.exec_json)
#         self.node_json_str = json.dumps(self.node_json)
#         self.node_json = json.loads(self.node_json_str)
#         self.exec_json = json.loads(self.exec_json_str)
#         self.keys = set()

#     def log(self, node, **kwargs):
#         self.storage.append([node, kwargs])

#     def json_history(self):
#         nodes = dict()
#         execs = []
#         exec_index = 0
#         for idx in range(len(self.storage)):
#             node_id, node = self.json_node(self.storage[idx][0])
#             exec_index = exec_index+1 if node_id in nodes else 0
#             nodes[node_id] = node
#             exec = self.json_execution(
#                 self.storage[idx][0], self.storage[idx][1], execs[-1] if execs else None, exec_index)
#             execs.append(exec)
#         history = {}
#         history['nodes'] = list(nodes.values())
#         history['executions'] = execs
#         history_str = json.dumps(history)
#         for key in self.bases:
#             history_str = history_str.replace(key, self.bases[key])
#         history = json.loads(history_str)
#         return history

#     def json_node(self, _node):
#         node = self.node_json.copy()
#         node_str = json.dumps(node)
#         node_str = node_str.replace("<node_id>", _node.id)
#         node_str = node_str.replace("<node_concept>", type(_node).__name__)
#         node = json.loads(node_str)
#         properties = []
#         for (k, v) in _node.__dict__.items():
#             if k in self.node_variables:
#                 kv = node["<bt_IRI>properties"]["<bt_IRI>hasDictionaryMember"][0].copy()
#                 kv["<bt_IRI>pairKey"] = k
#                 kv["<bt_IRI>pair_value_object"] = str(v)
#                 properties.append(kv)
#         node["<bt_IRI>properties"]["<bt_IRI>hasDictionaryMember"] = properties
#         return _node.id, node

#     def json_execution(self, _node, _exec_params, _previous, index):
#         exec = self.exec_json.copy()
#         exec_str = json.dumps(exec)
#         exec_str = exec_str.replace("<node_id>", _node.id)
#         exec_str = exec_str.replace("<node_concept>", type(_node).__name__)
#         exec_str = exec_str.replace("<start_dt>", _node.start.isoformat())
#         exec_str = exec_str.replace("<end_dt>", _node.end.isoformat())
#         exec = json.loads(exec_str)
#         if _previous:
#             exec["<prov_IRI>wasInformedBy"]["instance"] = _previous["instance"]
#         else:
#             exec["<prov_IRI>wasInformedBy"] = {}
#         exec["<bt_exec_IRI>outcome"]["<prov_IRI>value"]["@value"] = True if _node.status == State.SUCCESS else False
#         properties = []
#         for (k, v) in _exec_params.items():
#             if k in self.exec_variables:
#                 kv = exec["<prov_IRI>generated"]["<bt_IRI>properties"]["<bt_IRI>hasDictionaryMember"][0].copy()
#                 kv["<bt_IRI>pairKey"] = k
#                 kv["<bt_IRI>pair_value_object"] = v if type(
#                     v) == dict else v if type(v) == bool else json.loads(v)
#                 properties.append(kv)
#         exec["<prov_IRI>generated"]["<bt_IRI>properties"]["<bt_IRI>hasDictionaryMember"] = properties
#         exec["instance"] = exec["instance"]+"_"+str(index)
#         return exec

import json
from business.bt.nodes.type import State


class Logger:

    def __init__(self) -> None:
        self.node_variables = ['question',
                               'variable', 'value', 'endpoint', 'params']
        self.exec_variables = ['question', 'variable']
        self.storage = list()
        with open('data/isee-node-execution.json', 'r') as _file:
            self.exec_json = json.load(_file)
        with open('data/isee-node.json', 'r') as _file:
            self.node_json = json.load(_file)
        with open('data/isee-bases.json', 'r') as _file:
            self.bases = json.load(_file)

        self.exec_json_str = json.dumps(self.exec_json)
        self.node_json_str = json.dumps(self.node_json)
        self.node_json = json.loads(self.node_json_str)
        self.exec_json = json.loads(self.exec_json_str)
        self.keys = set()

    def log(self, node, **kwargs):
        self.storage.append([node, kwargs])

    def json_history(self):
        nodes = dict()
        execs = []
        exec_index = 0
        for idx in range(len(self.storage)):
            node_id, node = self.json_node(self.storage[idx][0])
            exec_index = exec_index+1 if node_id in nodes else 0
            nodes[node_id] = node
            exec = self.json_execution(
                self.storage[idx][0], self.storage[idx][1], execs[-1] if execs else None, exec_index)
            
            # Check if the node has clarification data and append it to execution
            if hasattr(self.storage[idx][0], 'clarification_data') and self.storage[idx][0].clarification_data:
                clarification_data = self.storage[idx][0].clarification_data  # Access the clarification data
                clarification_group = {
                    "<CLR_EXEC>": []  # Create a special key for clarification execution
                }
                for key, value in clarification_data.items():
                    clarification_group["<CLR_EXEC>"].append({
                        key: value
                    })
                
                # Add the <CLR_EXEC> group as a new member to hasDictionaryMember
                exec["CLR_EXEC"] = clarification_group

            execs.append(exec)
        history = {}
        history['nodes'] = list(nodes.values())
        history['executions'] = execs
        history_str = json.dumps(history)
        for key in self.bases:
            history_str = history_str.replace(key, self.bases[key])
        history = json.loads(history_str)
        return history

    def json_node(self, _node):
        node = self.node_json.copy()
        node_str = json.dumps(node)
        node_str = node_str.replace("<node_id>", _node.id)
        node_str = node_str.replace("<node_concept>", type(_node).__name__)
        node = json.loads(node_str)
        properties = []
        for (k, v) in _node.__dict__.items():
            if k in self.node_variables:
                kv = node["<bt_IRI>properties"]["<bt_IRI>hasDictionaryMember"][0].copy()
                kv["<bt_IRI>pairKey"] = k
                kv["<bt_IRI>pair_value_object"] = str(v)
                properties.append(kv)
        node["<bt_IRI>properties"]["<bt_IRI>hasDictionaryMember"] = properties
        return _node.id, node

    def json_execution(self, _node, _exec_params, _previous, index):
        exec = self.exec_json.copy()
        exec_str = json.dumps(exec)
        exec_str = exec_str.replace("<node_id>", _node.id)
        exec_str = exec_str.replace("<node_concept>", type(_node).__name__)
        exec_str = exec_str.replace("<start_dt>", _node.start.isoformat())
        exec_str = exec_str.replace("<end_dt>", _node.end.isoformat())
        exec = json.loads(exec_str)
        if _previous:
            exec["<prov_IRI>wasInformedBy"]["instance"] = _previous["instance"]
        else:
            exec["<prov_IRI>wasInformedBy"] = {}
        exec["<bt_exec_IRI>outcome"]["<prov_IRI>value"]["@value"] = True if _node.status == State.SUCCESS else False
        properties = []
        for (k, v) in _exec_params.items():
            if k in self.exec_variables:
                kv = exec["<prov_IRI>generated"]["<bt_IRI>properties"]["<bt_IRI>hasDictionaryMember"][0].copy()
                kv["<bt_IRI>pairKey"] = k
                kv["<bt_IRI>pair_value_object"] = v if type(
                    v) == dict else v if type(v) == bool else json.loads(v)
                properties.append(kv)
        exec["<prov_IRI>generated"]["<bt_IRI>properties"]["<bt_IRI>hasDictionaryMember"] = properties
        exec["instance"] = exec["instance"]+"_"+str(index)
        return exec
