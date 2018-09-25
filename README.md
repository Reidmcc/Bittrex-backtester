# Bittrex-backtester
Back-tester for multi-currency swing trading on the Bittrex cryptocurrency exchange.

Simulates trading against N currencies on shared trigger states (contrarian Bollinger band breaks mainly), assuming you trade with all your capital on the first available trigger across currencies. It has *not* been live-tested, use at thy own risk.

Despite using Bittrex data the fee multiplyers are set to mimic Poloniex fees. Bittrex's .25% fee eats most of the profits for this strategy. 
