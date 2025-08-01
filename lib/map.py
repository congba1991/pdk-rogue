from enum import IntEnum, auto
from dataclasses import dataclass


@dataclass
class Modifier:
    surrender_life_cost: int = 1
    turn_damage_multiplier: float = 1.0


@dataclass
class NodeModifier(Modifier):
    visible: bool = False


class RogueNodeType(IntEnum):
    Fight = auto()
    Mystery = auto()
    Shop = auto()


class RogueNodeReward:
    def __init__(self, reward_type, value):
        self.reward_type = reward_type
        self.value = value

    def __repr__(self):
        return f"{self.reward_type}({self.value})"

    def __str__(self):
        return f"{self.reward_type}: {self.value}"


class RogueNode:
    def __init__(
        self,
        name: str,
        node_type: RogueNodeType,
        node_reward: RogueNodeReward,
        node_modifier: NodeModifier = None,
        visited: bool = False,
    ):
        self.name = name
        self.node_modifier = node_modifier
        self.node_type = node_type
        self.node_reward = node_reward
        self.visited = visited


class RogueMap:
    def __init__(self, map_name: str):
        self.map_name = map_name
        self.rogue_nodes = []

    def add_child(self, child_node: RogueNode):
        if isinstance(child_node, RogueNode):
            self.rogue_nodes.append(child_node)
        else:
            raise TypeError("Child must be a RogueNode instance.")

    def __repr__(self):
        return f"RogueNode({self.map_name})"
