# Net Option Pricing Effect (NOPE)
A repository for NOPE data, research, results, utilities, etc.

Original conception by Lily Francus ([@nope_its_lily](https://twitter.com/nope_its_lily)).

Join the [discord](https://discord.gg/YyNcHqqb) to talk with us more about NOPE or help development.

# FAQ

### What is NOPE?
NOPE (Net Options Pricing Effect) refers to the effect on a stock's price due to the delta-gamma hedging performed by options market makers. NOPE, as a possibly useful indicator for market sentiment and dealer positioning, is measured on a given equity as the sum (weighted by daily contract volume) of the call and put deltas associated with all option strikes/expiries currently traded for that equity, normalized by the daily share volume.

### How does NOPE work? 
NOPE operates on the following assumptions: 
1. Options market makers take the short side of any call and put options transactions logged for the day 
2. Options market makers seek to minimize risk by dynamically hedging their short options positions, buying or shorting the underlying stock in proportion to the delta of the options traded. For example, an ATM (at-the-money) call contract is 50 delta, and so represents 50 shares hedged long by the dealer. 

Given these assumptions, options trading in large amounts can potentially drive the price of the underlying to a certain extent. In the instances when the counterparty hedge exceeds market depth, one should expect to see some movement in market price. Additionally - so long as dealers are positioned in this manner - any significant price movements could be further amplified by the necessary rebalancing of these hedges. 

To gauge roughly the size of this effect at a given moment, the NOPE model takes into account the delta of all options contracts traded so far for the day and normalizes it against the total number of shares traded. In other words, NOPE effectively represents a snapshot of the number of shares (expected to be) hedged due to options traded, divided by total shares traded.

### How does one use NOPE?
The most popular reference is this blog post: [Interpreting the NOPE: A Brief User’s Guide](https://nope-its-lily.medium.com/interpreting-the-nope-a-brief-users-guide-41c57c1b47a0)

Please note that nothing in the blog post or this repository is financial advice, or even guaranteed to be up-to-date on the latest NOPE information or trading strategies.


### What does the NOPE number mean?
The value of NOPE is dimensionless as the units in the formula cancel each other out. Conceptually a good description is that NOPE is the likelihood that Market Makers will have to impact the market to hedge.