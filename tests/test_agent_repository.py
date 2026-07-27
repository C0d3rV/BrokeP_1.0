from app.database.repositories import agent_repository


def test_insert_and_get_agent(test_db):
    agent_id = agent_repository.insert_agent("Gagan", 0.035)
    agent = agent_repository.get_agent_by_id(agent_id)

    assert agent is not None
    assert agent.name == "Gagan"
    assert agent.brokerage_rate == 0.035


def test_get_nonexistent_agent_returns_none(test_db):
    assert agent_repository.get_agent_by_id(9999) is None


def test_get_all_agents(test_db):
    agent_repository.insert_agent("Gagan", 0.035)
    agent_repository.insert_agent("Rohit", 0.04)

    agents = agent_repository.get_all_agents()
    names = {a.name for a in agents}

    assert names == {"Gagan", "Rohit"}


def test_update_brokerage_rate(test_db):
    agent_id = agent_repository.insert_agent("Gagan", 0.035)
    agent_repository.update_brokerage_rate(agent_id, 0.05)

    updated = agent_repository.get_agent_by_id(agent_id)
    assert updated.brokerage_rate == 0.05


def test_update_nonexistent_agent_raises(test_db):
    import pytest
    with pytest.raises(ValueError):
        agent_repository.update_brokerage_rate(9999, 0.05)


def test_search_agents_by_name(test_db):
    agent_repository.insert_agent("Gagan", 0.035)
    agent_repository.insert_agent("Gagan Deep", 0.04)
    agent_repository.insert_agent("Rohit", 0.03)

    results = agent_repository.search_agents_by_name("Gagan")
    assert len(results) == 2