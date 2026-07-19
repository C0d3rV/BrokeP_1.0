# Business Rules

## BR-01
### Record Trade
#### Description
Records an executed BUY trade for a client.
#### Trigger
Broker confirms the trade execution.
#### Processing
1. Validate trade details.
2. Calculate Gross Value.
3. Save the trade.
4. Update client balance.
#### Output
Trade is recorded successfully.
#### Validation
- Client must exist.
- Script is required.
- Quantity must be greater than 0.
- Price must be greater than 0.

---

## BR-02
### Close Trade
#### Description
Closes an existing OPEN trade when the client exits the position.
#### Trigger
Broker records the exit price.
#### Processing
1. Retrieve the open trade.
2. Record exit details.
3. Calculate Profit/Loss.
4. Calculate Net Profit/Loss.
5. Update client balance.
6. Mark trade as CLOSED.
#### Output
Trade is closed successfully.
#### Validation
- Trade must exist.
- Trade must be OPEN.
- Sell quantity must not exceed bought quantity.

---

## BR-03
### Calculate Gross Value
#### Description
Calculates the total value of a trade before any charges.
#### Formula
Gross Value = Quantity × Price
#### Output
Gross Value

---

## BR-04
### Calculate Brokerage
#### Description
Calculates the brokerage charged by the primary broker.
#### Processing
- If manual brokerage is entered, use it.
- Otherwise calculate using the configured brokerage rate.
#### Output
Brokerage

---

## BR-05
### Calculate Service Fee
#### Description
Calculates the service fee charged to the client.
#### Processing
- If manual service fee is entered, use it.
- Otherwise calculate using the configured service fee rate.
#### Output
Service Fee

---

## BR-06
### Calculate Profit / Loss
#### Description
Calculates the realised profit or loss of a closed trade.
#### Formula
Profit/Loss = (Sell Price − Buy Price) × Quantity
#### Output
Profit/Loss

---

## BR-07
### Calculate Net Profit / Loss
#### Description
Calculates the final profit or loss after charges.
#### Formula
Net Profit/Loss = Profit/Loss − Brokerage − Service Fee
#### Output
Net Profit/Loss

---

## BR-08
### Update Client Balance
#### Description
Updates the client's running ledger balance after every trade or cash transaction.
#### Processing
- Add realised profit.
- Deduct realised loss.
- Add cash deposits.
- Deduct cash withdrawals.
- Apply manual adjustments.
#### Output
Updated Balance

---

## BR-09
### Record Cash Transaction
#### Description
Records money received from or paid to the client.
#### Transaction Types
- Deposit
- Withdrawal
- Adjustment
#### Processing
1. Record the transaction.
2. Update client balance.
#### Output
Cash transaction recorded.

---

## BR-10
### Determine Trade Status
#### Description
Determines whether a trade is OPEN or CLOSED.
#### Processing
- If exit details are not recorded, Status = OPEN.
- If exit details are recorded, Status = CLOSED.
#### Output
Trade Status

---

## BR-11
### Generate Client Statement
#### Description
Generates the client's ledger for a selected period.
#### Includes
- All trades
- Open trades
- Closed trades
- Cash transactions
- Running balance
- Total Brokerage
- Total Service Fee
- Total Profit/Loss
- Net Profit/Loss
#### Output
Client Statement

---

## BR-12
### Generate Daily P/L Report
#### Description
Generates the daily trade summary that is shared with the client.
#### Includes
- Trades executed during the day.
- Open trades.
- Closed trades.
- Profit/Loss.
- Net Profit/Loss.
- Running Balance.
#### Output
Daily P/L Report