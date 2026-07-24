from app.database.repositories import agent_repository
from app.domain.validators.agent_validator import validate_agent

def create_agent(name: str, brokerage_rate: float) -> int:
    validate_agent(name, brokerage_rate)
    return agent_repository.insert_agent(name, brokerage_rate)

def get_agent(agent_id: int):
    agent = agent_repository.get_agent_by_id(agent_id)
    if agent is None:
        raise ValueError(f"Agent {agent_id} does not exist")
    return agent

def list_agents():
    return agent_repository.get_all_agents()

def change_brokerage_rate(agent_id: int, new_rate: float) -> None:
    if new_rate is None or new_rate < 0:
        raise ValueError("Brokerage rate must be zero or positive")
    agent_repository.update_brokerage_rate(agent_id, new_rate)