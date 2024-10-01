from business.bt.nodes.action import ActionNode, Succeder, Failer, GreeterNode, InitialiserNode, KnowledgeQuestionNode, TargetQuestionNode
from business.bt.nodes.action import QuestionNode, NeedQuestionNode, PersonaQuestionNode, ExplainerNode, EvaluationQuestionNode, CompleteNode
from business.bt.nodes.action import ConfirmNode, TargetTypeQuestionNode, UserQuestionNode
from business.bt.nodes.modifier import UsecaseModifierNode, WorldModifierNode
from business.bt.nodes.condition import ConditionNode, EqualNode, EqualValueNode
from business.bt.nodes.composite import SequenceNode, PriorityNode, EvaluationStrategyNode, ExplanationStrategyNode
from business.bt.nodes.hybrid import SupplementNode, ComplementNode, ReplacementNode, VariantNode
from business.bt.nodes.decorator import LimitActivationNode, RepeatNode, RepTillFailNode, RepTillSuccNode, InverterNode
from business.bt.nodes.node import Node
from business.bt.clarification_node import LLMClarificationQuestionNode, RepeatUntilNode



def makeNode(type, id, label):
    res = Node(0)

    if type == "Action":
        res = ActionNode(id)
    elif type == "World Modifier":
        res = WorldModifierNode(id)
    elif type == "Usecase Modifier":
        res = UsecaseModifierNode(id)
    elif type == "Failer":
        res = Failer(id)
    elif type == "Question":
        res = QuestionNode(id)
    elif type == "Evaluation Question":
        res = EvaluationQuestionNode(id)
    elif type == "Succeeder":
        res = Succeder(id)
    elif type == "Explanation Method":
        res = ExplainerNode(id)
    elif type == "Need Question":
        res = NeedQuestionNode(id)
    elif type == "Knowledge Question":
        res = KnowledgeQuestionNode(id)
    elif type == "Target Question":
        res = TargetQuestionNode(id)
    elif type == "Target Type Question":
        res = TargetTypeQuestionNode(id)
    elif type == "Persona Question":
        res = PersonaQuestionNode(id)
    elif type == "Initialiser":
        res = InitialiserNode(id)
    elif type == "Greeter":
        res = GreeterNode(id)
    elif type == "Confirm Question":
        res = ConfirmNode(id)
    elif type == "Complete":
        res = CompleteNode(id)
    elif type == "User Question":
        res = UserQuestionNode(id)

    elif type == "Condition":
        res = ConditionNode(id)
    elif type == "Equal":
        res = EqualNode(id)
    elif type == "Equal Value":
        res = EqualValueNode(id)

    elif type == "Priority":
        res = PriorityNode(id)
    elif type == "Sequence":
        res = SequenceNode(id)
    elif type == "Evaluation Strategy":
        res = EvaluationStrategyNode(id)
    elif type == "Explanation Strategy":
        res = ExplanationStrategyNode(id)

    elif type == "Replacement":
        res = ReplacementNode(id)
    elif type == "Variant":
        res = VariantNode(id)
    elif type == "Complement":
        res = ComplementNode(id)
    elif type == "Supplement":
        res = SupplementNode(id)        

    elif type == "RepeatUntilFailure":
        res = RepTillFailNode(id)
    elif type == "RepeatUntilSuccess":
        res = RepTillSuccNode(id)
    elif type == "Limiter":
        res = LimitActivationNode(id)
    elif type == "Inverter":
        res = InverterNode(id)
    elif type == "Repeater":
        res = RepeatNode(id)
    # ADDED
    elif type == "LLMClarificationQuestionNode":
        res = LLMClarificationQuestionNode(id)
    elif type == "RepeatUntil":
        res = RepeatUntilNode(id)

    else:
        print("no type", type, id, label)

    return res
