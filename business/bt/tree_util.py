import json
from typing import Dict
import data.parser as parser
import business.bt.nodes.node as node
import business.bt.nodes.factory as node_factory
import business.bt.bt as bt
from business.bt.nodes.action import GreeterNode, ExplainerNode
from business.bt.clarification_node import LLMClarificationQuestionNode, RepeatUntilNode # Import the RepeatUntilNode

# Define the node types that can have the LLMClarificationQuestionNode inserted after them
# nodes_that_allow_clarification = [GreeterNode, ExplainerNode] 
nodes_that_allow_clarification = [ExplainerNode] 

def generate_tree_from_file(path, co):
    _parser = parser.TreeFileParser(path)
    return generate_tree(_parser, co)

def generate_tree_from_obj(obj, co):
    _parser = parser.TreeObjParser(obj)
    return generate_tree(_parser, co)

def generate_tree(parser, co):
    nodes: Dict[str, node.Node] = {}

    # First, create all nodes
    for node_id in parser.bt_nodes:
        type_name = parser.bt_nodes[node_id]["Concept"]
        id = parser.bt_nodes[node_id]["id"]
        label = parser.bt_nodes[node_id]["Instance"]

        # Create Node according to its type with factory
        currentNode = node_factory.makeNode(type_name, id, label)
        nodes[node_id] = currentNode

    # Link the nodes together and insert clarification nodes where needed
    for n in parser.bt_nodes:
        nodes.get(n).co = co

        if parser.bt_nodes[n]["Concept"] in ["Priority", "Sequence", "Replacement", "Variant", "Complement", "Supplement"]:
            children = parser.bt_nodes[n]["firstChild"]
            previous_node = None
            while children is not None:
                child_node = nodes.get(children["Id"])

                # Attach the original child node
                nodes.get(n).children.append(child_node)

                # If the child node is a type that allows clarification, insert the clarification node after it
                if isinstance(child_node, tuple(nodes_that_allow_clarification)):
                    clarification_node = LLMClarificationQuestionNode(f"clarification_{child_node.id}")
                    clarification_node.co = co

                    # Wrap the clarification node with a RepeatUntilNode
                    rep_till_fail_node = RepeatUntilNode(f"reptillfail_{clarification_node.id}")
                    rep_till_fail_node.children = [clarification_node]
                    rep_till_fail_node.co = co
                    print(f"Inserting Clarification Node after {child_node.id} - {rep_till_fail_node.repeat_condition}")

                    # Insert the RepeatUntilNode after the child node in the list of children
                    nodes.get(n).children.append(rep_till_fail_node)

                children = children["Next"]

        elif parser.bt_nodes[n]["Concept"] in ["RepeatUntilSuccess", "RepeatUntilFailure", "Limiter", "Repeater", "Inverter"]:
            children = parser.bt_nodes[n]["firstChild"]
            child_node = nodes.get(children["Id"])

            # Attach the original child node
            nodes.get(n).children = [child_node]

            # Insert Clarification Node if necessary, wrapped in a RepeatUntilNode
            if isinstance(child_node, tuple(nodes_that_allow_clarification)):
                clarification_node = LLMClarificationQuestionNode(f"clarification_{child_node.id}")
                clarification_node.co = co

                rep_till_fail_node = RepeatUntilNode(f"reptillfail_{clarification_node.id}")
                rep_till_fail_node.children = [clarification_node]
                rep_till_fail_node.co = co
                print(f"Inserting Clarification Node after {child_node.id} - {rep_till_fail_node.repeat_condition}")

                nodes.get(n).children.append(rep_till_fail_node)

        # Node-specific properties
        if parser.bt_nodes[n]["Concept"] in ["RepeatUntilSuccess", "RepeatUntilFailure", "Limiter", "Repeater"]:
            nodes.get(n).limit = parser.bt_nodes[n]["properties"]["maxLoop"]

        if parser.bt_nodes[n]["Concept"] in ["Question", "Need Question", "Persona Question", "Knowledge Question", "Confirm Question", "Target Question", "Target Type Question"]:
            nodes.get(n).question = parser.bt_nodes[n]["properties"]["question"]
            nodes.get(n).variable = parser.bt_nodes[n]["properties"]["variable"]

        if parser.bt_nodes[n]["Concept"] == "Greeter":
            nodes.get(n).variable = parser.bt_nodes[n]["properties"]["variable"]

        if parser.bt_nodes[n]["Concept"] == "Information":
            nodes.get(n).message = parser.bt_nodes[n]["properties"]["message"]

        # Handling modifiers
        if parser.bt_nodes[n]["Concept"] in ["World Modifier", "Usecase Modifier"]:
            if parser.bt_nodes[n]["properties"]:
                key = list(parser.bt_nodes[n]["properties"].keys())[0]
                nodes.get(n).variable = key
                val = parser.bt_nodes[n]["properties"][key]
                nodes.get(n).value = bool(val == "True")

        # Handling conditions
        if parser.bt_nodes[n]["Concept"] in ["Equal", "Condition"]:
            nodes.get(n).variables = {key: bool(val == "True") for key, val in parser.bt_nodes[n]["properties"].items()}
        
        if parser.bt_nodes[n]["Concept"] == "Equal Value":
            nodes.get(n).variables = {key: val for key, val in parser.bt_nodes[n]["properties"].items()}

        if parser.bt_nodes[n]["Concept"] == "Explanation Method":
            nodes.get(n).params = parser.bt_nodes[n]["params"] if "params" in parser.bt_nodes[n] else {}
            nodes.get(n).endpoint = parser.bt_nodes[n]["Instance"]

        if parser.bt_nodes[n]["Concept"] == "User Question":
            nodes.get(n).params = parser.bt_nodes[n]["params"] if "params" in parser.bt_nodes[n] else {}

    # Set the root node
    root_id = parser.bt_root
    root = node.RootNode('0')
    root.co = co
    root.children.append(nodes.get(root_id))

    return bt.Tree(root, nodes)

def printTree(root, level=0):
    print(" - " * level, root.toString())
    if hasattr(root, "children"):
        for child in root.children:
            printTree(child, level + 1)

# import json
# from typing import Dict
# import data.parser as parser
# import business.bt.nodes.node as node
# import business.bt.nodes.factory as node_factory
# import business.bt.bt as bt
# from business.bt.nodes.action import GreeterNode, ExplainerNode
# from business.bt.clarification_node import LLMClarificationQuestionNode, RepeatUntilNode # Import the RepeatUntilNode

# # Define the node types that can have the LLMClarificationQuestionNode inserted after them
# # nodes_that_allow_clarification = [GreeterNode, ExplainerNode] 
# nodes_that_allow_clarification = [ExplainerNode] 

# def generate_tree_from_file(path, co):
#     _parser = parser.TreeFileParser(path)
#     return generate_tree(_parser, co)

# def generate_tree_from_obj(obj, co):
#     _parser = parser.TreeObjParser(obj)
#     return generate_tree(_parser, co)

# def generate_tree(parser, co):
#     nodes: Dict[str, node.Node] = {}

#     # First, create all nodes
#     for node_id in parser.bt_nodes:
#         type_name = parser.bt_nodes[node_id]["Concept"]
#         id = parser.bt_nodes[node_id]["id"]
#         label = parser.bt_nodes[node_id]["Instance"]

#         # Create Node according to its type with factory
#         currentNode = node_factory.makeNode(type_name, id, label)
#         nodes[node_id] = currentNode

#     # Link the nodes together and insert clarification nodes where needed
#     for n in parser.bt_nodes:
#         nodes.get(n).co = co

#         if parser.bt_nodes[n]["Concept"] in ["Priority", "Sequence", "Replacement", "Variant", "Complement", "Supplement"]:
#             children = parser.bt_nodes[n]["firstChild"]
#             previous_node = None

#             while children is not None:
#                 child_node = nodes.get(children["Id"])

#                 # Attach the original child node
#                 nodes.get(n).children.append(child_node)

#                 # Check if this is the last child in the sequence
#                 is_last_child = children.get("Next") is None

#                 # If the child node is a type that allows clarification and it's not the last child, insert the clarification node
#                 if isinstance(child_node, tuple(nodes_that_allow_clarification)) and not is_last_child:
#                     clarification_node = LLMClarificationQuestionNode(f"clarification_{child_node.id}")
#                     clarification_node.co = co

#                     # Wrap the clarification node with a RepeatUntilNode
#                     rep_till_fail_node = RepeatUntilNode(f"reptillfail_{clarification_node.id}")
#                     rep_till_fail_node.children = [clarification_node]
#                     rep_till_fail_node.co = co
#                     print(f"Inserting Clarification Node after {child_node.id} - {rep_till_fail_node.repeat_condition}")

#                     # Insert the RepeatUntilNode after the child node in the list of children
#                     nodes.get(n).children.append(rep_till_fail_node)

#                 # Move to the next child
#                 children = children.get("Next")

#         elif parser.bt_nodes[n]["Concept"] in ["RepeatUntilSuccess", "RepeatUntilFailure", "Limiter", "Repeater", "Inverter"]:
#             children = parser.bt_nodes[n]["firstChild"]
#             child_node = nodes.get(children["Id"])

#             # Attach the original child node
#             nodes.get(n).children = [child_node]

#             # Insert Clarification Node if necessary, wrapped in a RepeatUntilNode
#             if isinstance(child_node, tuple(nodes_that_allow_clarification)):
#                 clarification_node = LLMClarificationQuestionNode(f"clarification_{child_node.id}")
#                 clarification_node.co = co

#                 rep_till_fail_node = RepeatUntilNode(f"reptillfail_{clarification_node.id}")
#                 rep_till_fail_node.children = [clarification_node]
#                 rep_till_fail_node.co = co
#                 print(f"Inserting Clarification Node after {child_node.id} - {rep_till_fail_node.repeat_condition}")

#                 nodes.get(n).children.append(rep_till_fail_node)

#         # Node-specific properties
#         if parser.bt_nodes[n]["Concept"] in ["RepeatUntilSuccess", "RepeatUntilFailure", "Limiter", "Repeater"]:
#             nodes.get(n).limit = parser.bt_nodes[n]["properties"]["maxLoop"]

#         if parser.bt_nodes[n]["Concept"] in ["Question", "Need Question", "Persona Question", "Knowledge Question", "Confirm Question", "Target Question", "Target Type Question"]:
#             nodes.get(n).question = parser.bt_nodes[n]["properties"]["question"]
#             nodes.get(n).variable = parser.bt_nodes[n]["properties"]["variable"]

#         if parser.bt_nodes[n]["Concept"] == "Greeter":
#             nodes.get(n).variable = parser.bt_nodes[n]["properties"]["variable"]

#         if parser.bt_nodes[n]["Concept"] == "Information":
#             nodes.get(n).message = parser.bt_nodes[n]["properties"]["message"]

#         # Handling modifiers
#         if parser.bt_nodes[n]["Concept"] in ["World Modifier", "Usecase Modifier"]:
#             if parser.bt_nodes[n]["properties"]:
#                 key = list(parser.bt_nodes[n]["properties"].keys())[0]
#                 nodes.get(n).variable = key
#                 val = parser.bt_nodes[n]["properties"][key]
#                 nodes.get(n).value = bool(val == "True")

#         # Handling conditions
#         if parser.bt_nodes[n]["Concept"] in ["Equal", "Condition"]:
#             nodes.get(n).variables = {key: bool(val == "True") for key, val in parser.bt_nodes[n]["properties"].items()}
        
#         if parser.bt_nodes[n]["Concept"] == "Equal Value":
#             nodes.get(n).variables = {key: val for key, val in parser.bt_nodes[n]["properties"].items()}

#         if parser.bt_nodes[n]["Concept"] == "Explanation Method":
#             nodes.get(n).params = parser.bt_nodes[n]["params"] if "params" in parser.bt_nodes[n] else {}
#             nodes.get(n).endpoint = parser.bt_nodes[n]["Instance"]

#         if parser.bt_nodes[n]["Concept"] == "User Question":
#             nodes.get(n).params = parser.bt_nodes[n]["params"] if "params" in parser.bt_nodes[n] else {}

#     # Set the root node
#     root_id = parser.bt_root
#     root = node.RootNode('0')
#     root.co = co
#     root.children.append(nodes.get(root_id))

#     return bt.Tree(root, nodes)

# def printTree(root, level=0):
#     print(" - " * level, root.toString())
#     if hasattr(root, "children"):
#         for child in root.children:
#             printTree(child, level + 1)
