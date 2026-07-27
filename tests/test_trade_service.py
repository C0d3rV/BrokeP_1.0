import pytest
from app.services import trade_service
from app.database.repositories import client_repository, agent_repository


@pytest.fixture
def client_and_agent(test_db):
    client_id = client_repository.insert_client("Kailash")
    agent_id = agent_repository.insert_agent("Archna", 0.035)
    return client_id, agent_id


def test_open_trade_computes_brokerage_correctly(client_and_agent):
    """Regression check against real INFY row: buy 1214 x 400, rate 0.035%."""
    client_id, agent_id = client_and_agent

    trade_id = trade_service.open_trade(
        client_id=client_id, agent_id=agent_id, segment="EQUITY",
        symbol="INFY", quantity=400, entry_date="2026-06-01", entry_price=1214
    )

    trades = trade_service.get_open_trades_for_client(client_id)
    trade = trades[0]

    assert trade.entry_brokerage == 169.96
    assert trade.status == "OPEN"


def test_open_trade_invalid_client_raises(client_and_agent):
    _, agent_id = client_and_agent
    with pytest.raises(ValueError):
        trade_service.open_trade(
            client_id=9999, agent_id=agent_id, segment="EQUITY",
            symbol="INFY", quantity=400, entry_date="2026-06-01", entry_price=1214
        )


def test_open_trade_invalid_agent_raises(client_and_agent):
    client_id, _ = client_and_agent
    with pytest.raises(ValueError):
        trade_service.open_trade(
            client_id=client_id, agent_id=9999, segment="EQUITY",
            symbol="INFY", quantity=400, entry_date="2026-06-01", entry_price=1214
        )


def test_open_trade_invalid_quantity_raises(client_and_agent):
    client_id, agent_id = client_and_agent
    with pytest.raises(ValueError):
        trade_service.open_trade(
            client_id=client_id, agent_id=agent_id, segment="EQUITY",
            symbol="INFY", quantity=0, entry_date="2026-06-01", entry_price=1214
        )


def test_full_trade_lifecycle_matches_real_pnl(client_and_agent):
    """End-to-end regression against the real INFY row: entry 1214, exit 1239,
    qty 400 -> gross_pl 10000."""
    client_id, agent_id = client_and_agent

    trade_id = trade_service.open_trade(
        client_id=client_id, agent_id=agent_id, segment="EQUITY",
        symbol="INFY", quantity=400, entry_date="2026-06-01", entry_price=1214
    )

    trade_service.close_trade(
        trade_id=trade_id, exit_date="2026-06-02", exit_price=1239, service_fee=0
    )

    closed_trades = trade_service.get_closed_trades_for_client(client_id)
    closed = closed_trades[0]

    assert closed.gross_pl == 10000
    assert closed.entry_brokerage == 169.96
    assert closed.exit_brokerage == 173.46
    assert closed.net_pl == pytest.approx(10000 - 169.96 - 173.46, abs=0.01)
    assert closed.status == "CLOSED"


def test_close_already_open_trade_only_once(client_and_agent):
    client_id, agent_id = client_and_agent
    trade_id = trade_service.open_trade(
        client_id=client_id, agent_id=agent_id, segment="EQUITY",
        symbol="INFY", quantity=400, entry_date="2026-06-01", entry_price=1214
    )
    trade_service.close_trade(trade_id=trade_id, exit_date="2026-06-02", exit_price=1239)

    with pytest.raises(ValueError):
        trade_service.close_trade(trade_id=trade_id, exit_date="2026-06-03", exit_price=1250)


def test_manual_brokerage_override_on_close(client_and_agent):
    client_id, agent_id = client_and_agent
    trade_id = trade_service.open_trade(
        client_id=client_id, agent_id=agent_id, segment="EQUITY",
        symbol="INFY", quantity=400, entry_date="2026-06-01", entry_price=1214
    )
    trade_service.close_trade(
        trade_id=trade_id, exit_date="2026-06-02", exit_price=1239,
        manual_brokerage=100
    )

    closed = trade_service.get_closed_trades_for_client(client_id)[0]
    assert closed.exit_brokerage == 100