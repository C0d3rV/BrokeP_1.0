from dataclasses import dataclass

@dataclass
class Agent:
    agent_id: int
    name: str
    brokerage_rate: float