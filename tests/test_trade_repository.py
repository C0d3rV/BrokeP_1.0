import pytest
from app.database.repositories import trade_repository, client_repository, agent_repository


@pytest.fixture
def client_and_agent(test_db):
    """Common setup: every trade needs a valid client_id and agent_id (FK)."""
    client_id = client_repository.insert_client("Kailash")
    agent_id = agent_repository.insert_agent("Gagan", 0.035)
    return client_id, agent_id


def test_open_trade_creates_open_status(client_and_agent):
    client_id, agent_id = client_and_agent
    trade_id = trade_repository.open_trade(
        client_id=client_id, agent_id=agent_id, segment="EQUITY", symbol="INFY",
        quantity=400, entry_date="2026-06-01", entry_price=1214,
        entry_brokerage=343.42, remarks=None
    )

    trade = trade_repository.get_trade_by_id(trade_id)
    assert trade.status == "OPEN"
    assert trade.symbol == "INFY"
    assert trade.exit_price is None
    assert trade.gross_pl is None


def test_close_trade_updates_fields(client_and_agent):
    client_id, agent_id = client_and_agent
    trade_id = trade_repository.open_trade(
        client_id=client_id, agent_id=agent_id, segment="EQUITY", symbol="INFY",
        quantity=400, entry_date="2026-06-01", entry_price=1214,
        entry_brokerage=343.42
    )

    trade_repository.close_trade(
        trade_id=trade_id, exit_date="2026-06-02", exit_price=1239,
        exit_brokerage=350.0, service_fee=10, gross_pl=10000, net_pl=9296.58
    )

    closed = trade_repository.get_trade_by_id(trade_id)
    assert closed.status == "CLOSED"
    assert closed.exit_price == 1239
    assert closed.gross_pl == 10000
    assert closed.net_pl == 9296.58


def test_cannot_close_already_closed_trade(client_and_agent):
    client_id, agent_id = client_and_agent
    trade_id = trade_repository.open_trade(
        client_id=client_id, agent_id=agent_id, segment="EQUITY", symbol="INFY",
        quantity=400, entry_date="2026-06-01", entry_price=1214,
        entry_brokerage=343.42
    )
    trade_repository.close_trade(
        trade_id=trade_id, exit_date="2026-06-02", exit_price=1239,
        exit_brokerage=350.0, service_fee=10, gross_pl=10000, net_pl=9296.58
    )

    with pytest.raises(ValueError):
        trade_repository.close_trade(
            trade_id=trade_id, exit_date="2026-06-03", exit_price=1250,
            exit_brokerage=350.0, service_fee=10, gross_pl=14000, net_pl=13296.58
        )


def test_close_nonexistent_trade_raises(client_and_agent):
    with pytest.raises(ValueError):
        trade_repository.close_trade(
            trade_id=9999, exit_date="2026-06-02", exit_price=1239,
            exit_brokerage=350.0, service_fee=10, gross_pl=10000, net_pl=9296.58
        )


def test_get_open_trades_for_client(client_and_agent):
    client_id, agent_id = client_and_agent
    trade_repository.open_trade(
        client_id=client_id, agent_id=agent_id, segment="EQUITY", symbol="INFY",
        quantity=400, entry_date="2026-06-01", entry_price=1214, entry_brokerage=343.42
    )
    trade_repository.open_trade(
        client_id=client_id, agent_id=agent_id, segment="EQUITY", symbol="WIPRO",
        quantity=100, entry_date="2026-06-02", entry_price=183, entry_brokerage=12.81
    )

    open_trades = trade_repository.get_open_trades_for_client(client_id)
    assert len(open_trades) == 2


def test_get_all_open_and_closed_trades(client_and_agent):
    client_id, agent_id = client_and_agent
    t1 = trade_repository.open_trade(
        client_id=client_id, agent_id=agent_id, segment="EQUITY", symbol="INFY",
        quantity=400, entry_date="2026-06-01", entry_price=1214, entry_brokerage=343.42
    )
    trade_repository.open_trade(
        client_id=client_id, agent_id=agent_id, segment="EQUITY", symbol="WIPRO",
        quantity=100, entry_date="2026-06-02", entry_price=183, entry_brokerage=12.81
    )
    trade_repository.close_trade(
        trade_id=t1, exit_date="2026-06-02", exit_price=1239,
        exit_brokerage=350.0, service_fee=10, gross_pl=10000, net_pl=9296.58
    )

    assert len(trade_repository.get_all_open_trades()) == 1
    assert len(trade_repository.get_all_closed_trades()) == 1