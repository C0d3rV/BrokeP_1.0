from app.database.repositories import trade_repository, client_repository, agent_repository
from app.domain.validators.trade_validator import validate_trade_entry, validate_trade_close
from app.domain.calculations.pnl import gross_value, brokerage, gross_pl, net_pl


def open_trade(client_id: int, agent_id: int, segment: str, symbol: str,
               quantity: int, entry_date: str, entry_price: float,
               manual_brokerage: float = None, entry_service_fee: float = 0,
               expiry_date: str = None, remarks: str = None) -> int:
    validate_trade_entry(client_id, agent_id, segment, symbol,
                          quantity, entry_price, entry_date)

    if client_repository.get_client_by_id(client_id) is None:
        raise ValueError(f"Client {client_id} does not exist")

    agent = agent_repository.get_agent_by_id(agent_id)
    if agent is None:
        raise ValueError(f"Agent {agent_id} does not exist")

    entry_value = gross_value(entry_price, quantity)
    entry_brokerage = brokerage(
        buy_value=entry_value, sell_value=0,
        rate=agent.brokerage_rate, manual_override=manual_brokerage
    )

    return trade_repository.open_trade(
        client_id=client_id, agent_id=agent_id, segment=segment, symbol=symbol,
        quantity=quantity, entry_date=entry_date, entry_price=entry_price,
        entry_brokerage=entry_brokerage, entry_service_fee=entry_service_fee,
        expiry_date=expiry_date, remarks=remarks
    )


def close_trade(trade_id: int, exit_date: str, exit_price: float,
                 exit_service_fee: float = 0, manual_brokerage: float = None) -> None:
    validate_trade_close(exit_price, exit_date)

    trade = trade_repository.get_trade_by_id(trade_id)
    if trade is None:
        raise ValueError(f"Trade {trade_id} does not exist")
    if trade.status != "OPEN":
        raise ValueError(f"Trade {trade_id} is already closed")

    agent = agent_repository.get_agent_by_id(trade.agent_id)
    if agent is None:
        raise ValueError(f"Agent {trade.agent_id} does not exist")

    exit_value = gross_value(exit_price, trade.quantity)
    exit_brokerage = brokerage(
        buy_value=0, sell_value=exit_value,
        rate=agent.brokerage_rate, manual_override=manual_brokerage
    )

    gpl = gross_pl(trade.entry_price, exit_price, trade.quantity)
    npl = net_pl(gpl, trade.entry_brokerage, exit_brokerage,
                 trade.entry_service_fee, exit_service_fee)

    trade_repository.close_trade(
        trade_id=trade_id, exit_date=exit_date, exit_price=exit_price,
        exit_brokerage=exit_brokerage, exit_service_fee=exit_service_fee,
        gross_pl=gpl, net_pl=npl
    )


def get_open_trades_for_client(client_id: int):
    return trade_repository.get_open_trades_for_client(client_id)


def get_closed_trades_for_client(client_id: int):
    return trade_repository.get_closed_trades_for_client(client_id)


def list_all_open_trades():
    return trade_repository.get_all_open_trades()


def list_all_closed_trades():
    return trade_repository.get_all_closed_trades()