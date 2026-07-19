# BR-01
## Create trade
### Description
A Trade is created whenever the broker confirms the order executed.
### Trigger
User clicks 'Save Trade'
### Inputs
Client name,
Trade type,
Script,
Quantity,
Price,
Trade date,
Broker fee,
Client brokerage,
Remarks
### Processing
1. Validate required fields.
2. Create Trade Object
3. Calculate gross value
4. Store the trade
### Outputs
Trade successfully created
### Validation
Quantity > 0
Price > 0
Client exists
### Exceptions
If validation fails.
Trade is not created.
Show validation error.

# BR-002
## Gross Value
### Description
Gross Value represents the total value of the trade before brokerage.
### Formula
Gross Value = Quantity × Price
### Inputs
Quantity
Price
### Output
Gross Value
### Validation
Quantity > 0
Price > 0

# BR-003
## Client Brokerage
### Description
Brokerage charged to the client.
### Inputs
Gross Value
Brokerage Rate
Manual Override
### Processing
If Manual Override exists
Use Manual Override
Else
Brokerage = Gross Value × Brokerage Rate
### Output
Client Brokerage

# BR-004
## Balance Calculation
### Description
Calculates the client's current balance.
### Inputs
Opening Balance
Trade Settlements
Cash Deposits
Cash Withdrawals
### Formula
Closing Balance = Opening Balance + Trade Settlements + Cash Deposits - Cash Withdrawals
### Output
Closing Balance

# BR-005
## Open Position
### Description
A trade remains open until it has been squared off.
### Processing
If Exit Trade exists
    Status = CLOSED
Else
    Status = OPEN






