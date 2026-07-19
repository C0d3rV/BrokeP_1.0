# Business Rules

## BR-01
### Create Trade
#### Description
Creates a trade when the broker confirms that a client's buy/sell order has been executed.
#### Inputs
- Client Name
- Broker Name
- Symbol
- Trade Type (BUY / SELL)
- Trade Date
- Price
- Quantity
- Brokerage
- Service Fee
- Expiry (Optional)
- Remarks
#### Output
Trade is successfully recorded.
---
## BR-02
### Edit Trade
#### Description
Allows an existing trade to be modified if incorrect details were entered.
#### Inputs
- Trade ID
- Updated Trade Details
#### Output
Trade is updated and all dependent calculations are refreshed.
---
## BR-03
### Delete Trade
#### Description
Deletes an existing trade from the ledger.
#### Inputs
- Trade ID
#### Output
Trade is removed and all dependent calculations are refreshed.
---
## BR-04
### Calculate Gross Value
#### Description
Calculates the total value of a trade before any charges.
#### Formula
```
Gross Value = Quantity × Price
```
#### Inputs
- Quantity
- Price
#### Output
Gross Value
---
## BR-05
### Calculate Service Fee
#### Description
Calculates the service fee charged to the client.
#### Inputs
- Gross Value
- Service Fee Rate
- Manual Service Fee (Optional)
#### Output
Service Fee
---
## BR-06
### Calculate Net Settlement
#### Description
Calculates the actual cash impact of a trade.
#### Formula
BUY
```
Net Settlement = Gross Value + Service Fee
```

SELL
```
Net Settlement = Gross Value - Service Fee
```
#### Inputs
- Trade Type
- Gross Value
- Service Fee
#### Output
Net Settlement
---
## BR-07
### Calculate Running Balance
#### Description
Calculates the client's latest balance after every trade or cash transaction.
#### Inputs
- Previous Balance
- Net Settlement
- Cash Deposits
- Cash Withdrawals
- Manual Adjustments
#### Output
Updated Client Balance
---
## BR-08
### Record Cash Transaction
#### Description
Records any deposit, withdrawal or manual adjustment made by the client.
#### Inputs
- Client Name
- Transaction Type (Deposit / Withdrawal / Adjustment)
- Amount
- Transaction Date
- Remarks
#### Output
Cash transaction is recorded and client balance is updated.
---
## BR-09
### Determine Position Status
#### Description
Determines whether a position is Open or Closed.
#### Formula
```
Net Quantity = Total Bought Quantity - Total Sold Quantity
```

If
```
Net Quantity = 0
```
Position Status = **Closed**

Else
Position Status = **Open**
#### Inputs
- Buy Quantity
- Sell Quantity
#### Output
Position Status
---
## BR-10
### Calculate Profit / Loss
#### Description
Calculates the realised profit or loss for closed positions.
#### Formula
```
P/L = (Sell Price - Buy Price) × Closed Quantity
```
#### Inputs
- Buy Price
- Sell Price
- Closed Quantity
#### Output
Profit / Loss
---
## BR-11
### Generate Client Statement
#### Description
Generates a statement for a selected client and date range.
#### Inputs
- Client Name
- Date Range
#### Output
Statement containing:
- Trades
- Cash Transactions
- Open Positions
- Closed Positions
- Running Balance
---
## BR-12
### Validate Trade
#### Description
Validates all mandatory trade information before saving.
#### Validation
- Client must exist.
- Quantity must be greater than 0.
- Price must be greater than 0.
- Trade Type must be BUY or SELL.
- Trade Date is mandatory.
#### Output
Trade is saved if validation succeeds.
Otherwise, an appropriate validation error is displayed.