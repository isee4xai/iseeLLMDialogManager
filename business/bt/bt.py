import business.bt.tree_util as tg
import business.bt.nodes.node as node
from typing import Dict
import business.coordinator as c
from business.bt.nodes.composite import ExplanationStrategyNode, EvaluationStrategyNode
from business.bt.clarification_node import LLMClarificationQuestionNode

class BehaviourTree:

	def __init__(self, co):
		self.tree = tg.generate_tree_from_file("data/ee_v5.json", co)
		tg.printTree(self.tree.root)

	async def run(self):
		await self.tree.root.tick()
		
	def restart(self): 
		pass

	def plug_strategy(self, _sub_tree, replace_node_type):
		# there is always a stategy node
		if replace_node_type == "Explanation Strategy":
			strategy_node = [n for n in self.tree.nodes.values() if isinstance(n, ExplanationStrategyNode)][0]
		elif replace_node_type == "Evaluation Strategy":
			strategy_node = [n for n in self.tree.nodes.values() if isinstance(n, EvaluationStrategyNode)][0]
		strategy_node.children =[_sub_tree.root]
		# tg.printTree(self.tree.root)

class Tree :
	def __init__(self, root : node.Node, nodes : Dict[str, node.Node]) -> None:
		self.root = root
		self.nodes = nodes
		self.currentNode = root

	def goToNextDepthFirst(self) :
		pass

	def findParent(self, _node):
		res = None
		for n in self.nodes:
			if(hasattr(self.nodes[n], "children")):
				for child in self.nodes[n].children :
					if(child == _node):
						res = self.nodes[n]
			elif(hasattr(self.nodes[n], "child")):
				if(self.nodes[n].child == _node):
					res = self.nodes[n]
		return res

	def replaceChild(self, _parent, _node):
		if(hasattr(_parent, "children")):
			index = 0
			for child in _parent.children :
				if(child.id == _node.id):
					_parent.children[index] = _node
				index += 1
		elif(hasattr(_parent, "child")):
			_parent.child = _node
