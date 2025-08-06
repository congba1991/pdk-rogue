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

class RogueRegion:
    def __init__(self, region_name: str):
        self.region_name = region_name
        self.maps = []

    def add_map(self, rogue_map):
        if isinstance(rogue_map, RogueMap):
            self.maps.append(rogue_map)
        else:
            raise TypeError("Must add a RogueMap instance.")

    def __repr__(self):
        return f"RogueRegion({self.region_name})"

    def __str__(self):
        return f"Region: {self.region_name} ({len(self.maps)} maps)"

