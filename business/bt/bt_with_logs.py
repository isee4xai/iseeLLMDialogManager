# import business.bt.tree_util as tg
# import business.bt.nodes.node as node
# from typing import Dict
# import business.coordinator as c
# from business.bt.nodes.composite import ExplanationStrategyNode, EvaluationStrategyNode
# import pickle
# import os
# import logging

# # Set up logging
# logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bt_log.txt'),
#                     level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')

# class BehaviourTree:

#     def __init__(self, co):
#         self.tree = tg.generate_tree_from_file("data/ee_v5.json", co)
#         self.co = co
#         tg.printTree(self.tree.root)
#         self.save_tree("bt_tree.obj")
#         logging.info("Initial tree structure saved.")

#     def save_tree(self, filename: str):
#         """
#         Save the behavior tree to a pickle file.

#         :param filename: The name of the file to save the tree.
#         """
#         path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
#         with open(path, 'wb') as f:
#             pickle.dump(self.tree, f)
#         logging.info(f"Tree saved to {path}")

#     async def run(self):
#         """
#         Run the behavior tree.
#         """
#         await self.tree.root.tick()
#         logging.info("Behavior tree execution started.")

#     def restart(self):
#         """
#         Restart the behavior tree.
#         """
#         pass

#     def plug_strategy(self, _sub_tree, replace_node_type):
#         """
#         Plug a strategy subtree into the behavior tree.

#         :param _sub_tree: The subtree to be plugged in.
#         :param replace_node_type: The type of strategy node to be replaced.
#         """
#         if replace_node_type == "Explanation Strategy":
#             strategy_node = [n for n in self.tree.nodes.values() if isinstance(n, ExplanationStrategyNode)][0]
#         elif replace_node_type == "Evaluation Strategy":
#             strategy_node = [n for n in self.tree.nodes.values() if isinstance(n, EvaluationStrategyNode)][0]
#         strategy_node.children = [_sub_tree.root]
#         logging.info(f"Plugged in new strategy for {replace_node_type}")

# class Tree:
#     def __init__(self, root: node.Node, nodes: Dict[str, node.Node]) -> None:
#         """
#         Initialize the Tree object.

#         :param root: The root node of the tree.
#         :param nodes: A dictionary of nodes in the tree.
#         """
#         self.root = root
#         self.nodes = nodes
#         self.currentNode = root

#     def goToNextDepthFirst(self):
#         """
#         Traverse the tree to the next node in depth-first order.
#         """
#         pass

#     def findParent(self, _node: node.Node) -> Optional[node.Node]:
#         """
#         Find the parent of a given node.

#         :param _node: The node whose parent is to be found.
#         :return: The parent node if found, otherwise None.
#         """
#         res = None
#         for n in self.nodes:
#             if hasattr(self.nodes[n], "children"):
#                 for child in self.nodes[n].children:
#                     if child == _node:
#                         res = self.nodes[n]
#             elif hasattr(self.nodes[n], "child"):
#                 if self.nodes[n].child == _node:
#                     res = self.nodes[n]
#         return res

#     def replaceChild(self, _parent: node.Node, _node: node.Node) -> None:
#         """
#         Replace a child node with another node.

#         :param _parent: The parent node whose child is to be replaced.
#         :param _node: The new node to replace the old child node.
#         """
#         if hasattr(_parent, "children"):
#             index = 0
#             for child in _parent.children:
#                 if child.id == _node.id:
#                     _parent.children[index] = _node
#                 index += 1
#         elif hasattr(_parent, "child"):
#             _parent.child = _node



# import business.bt.tree_util as tg
# import business.bt.nodes.node as node
# from typing import Dict
# import business.coordinator as c
# from business.bt.nodes.composite import ExplanationStrategyNode, EvaluationStrategyNode
# from business.bt.llm_clarification_question_node import LLMClarificationQuestionNode
# import pickle
# import os

# # Test
# class BehaviourTree:

#     def __init__(self, co):
#         self.tree = tg.generate_tree_from_file("data/ee_v5.json", co)
#         self.co = co
#         tg.printTree(self.tree.root)
#         self.save_tree("bt_tree.obj")
#         self.add_clarification_nodes()
#         self.save_tree("bt_post_tree.obj")

#     def add_clarification_nodes(self):
#         for n in self.tree.nodes.values():
#             if isinstance(n, (node.GreeterNode, node.ConfirmNode, node.ExplainerNode, node.EvaluationQuestionNode, node.TargetQuestionNode)):
#                 clarification_node = LLMClarificationQuestionNode("clarification_" + n.id, self.co)
#                 parent_node = self.tree.findParent(n)
#                 if parent_node:
#                     self.tree.insert_after(parent_node, n, clarification_node)

#     def save_tree(self, filename: str):
#         path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
#         with open(path, 'wb') as f:
#             pickle.dump(self.tree, f)

#     async def run(self):
#         await self.tree.root.tick()

#     def restart(self):
#         pass

#     def plug_strategy(self, _sub_tree, replace_node_type):
#         if replace_node_type == "Explanation Strategy":
#             strategy_node = [n for n in self.tree.nodes.values() if isinstance(n, ExplanationStrategyNode)][0]
#         elif replace_node_type == "Evaluation Strategy":
#             strategy_node = [n for n in self.tree.nodes.values() if isinstance(n, EvaluationStrategyNode)][0]
#         strategy_node.children = [_sub_tree.root]

# class Tree:
#     def __init__(self, root: node.Node, nodes: Dict[str, node.Node]) -> None:
#         self.root = root
#         self.nodes = nodes
#         self.currentNode = root

#     def goToNextDepthFirst(self):
#         pass

#     def findParent(self, _node):
#         res = None
#         for n in self.nodes:
#             if hasattr(self.nodes[n], "children"):
#                 for child in self.nodes[n].children:
#                     if child == _node:
#                         res = self.nodes[n]
#             elif hasattr(self.nodes[n], "child"):
#                 if self.nodes[n].child == _node:
#                     res = self.nodes[n]
#         return res

#     def insert_after(self, parent_node, target_node, new_node):
#         if hasattr(parent_node, "children"):
#             index = parent_node.children.index(target_node)
#             parent_node.children.insert(index + 1, new_node)
#         elif hasattr(parent_node, "child"):
#             if parent_node.child == target_node:
#                 parent_node.child = new_node
#                 new_node.child = target_node.child

#     def replaceChild(self, _parent, _node):
#         if hasattr(_parent, "children"):
#             index = 0
#             for child in _parent.children:
#                 if child.id == _node.id:
#                     _parent.children[index] = _node
#                 index += 1
#         elif hasattr(_parent, "child"):
#             _parent.child = _node


import business.bt.tree_util as tg
import business.bt.nodes.node as node
from typing import Dict
import business.coordinator as c
from business.bt.nodes.composite import ExplanationStrategyNode, EvaluationStrategyNode
from business.bt.llm_clarification_question_node import LLMClarificationQuestionNode
import pickle
import os
import logging

# Set up logging
logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bt_log.txt'),
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class BehaviourTree:

    def __init__(self, co):
        self.tree = tg.generate_tree_from_file("data/ee_v5.json", co)
        self.co = co
        tg.printTree(self.tree.root)
        self.save_tree("bt_tree.obj")
        logging.info("Initial tree structure saved.")
        self.add_clarification_nodes()
        self.save_tree("bt_post_tree.obj")
        logging.info("Tree structure with clarification nodes saved.")

    def add_clarification_nodes(self):
        for n in self.tree.nodes.values():
            if isinstance(n, (node.GreeterNode, node.ConfirmNode, node.ExplainerNode, node.EvaluationQuestionNode, node.TargetQuestionNode)):
                clarification_node = LLMClarificationQuestionNode("clarification_" + n.id, self.co)
                parent_node = self.tree.findParent(n)
                if parent_node:
                    self.tree.insert_after(parent_node, n, clarification_node)
                    logging.info(f"Added clarification node for {n.id} after {parent_node.id}")

    def save_tree(self, filename: str):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(path, 'wb') as f:
            pickle.dump(self.tree, f)
        logging.info(f"Tree saved to {path}")

    async def run(self):
        await self.tree.root.tick()

    def restart(self):
        pass

    def plug_strategy(self, _sub_tree, replace_node_type):
        if replace_node_type == "Explanation Strategy":
            strategy_node = [n for n in self.tree.nodes.values() if isinstance(n, ExplanationStrategyNode)][0]
        elif replace_node_type == "Evaluation Strategy":
            strategy_node = [n for n in self.tree.nodes.values() if isinstance(n, EvaluationStrategyNode)][0]
        strategy_node.children = [_sub_tree.root]
        logging.info(f"Plugged in new strategy for {replace_node_type}")

class Tree:
    def __init__(self, root: node.Node, nodes: Dict[str, node.Node]) -> None:
        self.root = root
        self.nodes = nodes
        self.currentNode = root

    def goToNextDepthFirst(self):
        pass

    def findParent(self, _node: node.Node) -> Optional[node.Node]:
        res = None
        for n in self.nodes:
            if hasattr(self.nodes[n], "children"):
                for child in self.nodes[n].children:
                    if child == _node:
                        res = self.nodes[n]
            elif hasattr(self.nodes[n], "child"):
                if self.nodes[n].child == _node:
                    res = self.nodes[n]
        return res

    def insert_after(self, parent_node: node.Node, target_node: node.Node, new_node: node.Node) -> None:
        if hasattr(parent_node, "children"):
            index = parent_node.children.index(target_node)
            parent_node.children.insert(index + 1, new_node)
        elif hasattr(parent_node, "child"):
            if parent_node.child == target_node:
                parent_node.child = new_node
                new_node.child = target_node.child

    def replaceChild(self, _parent: node.Node, _node: node.Node) -> None:
        if hasattr(_parent, "children"):
            index = 0
            for child in _parent.children:
                if child.id == _node.id:
                    _parent.children[index] = _node
                index += 1
        elif hasattr(_parent, "child"):
            _parent.child = _node
