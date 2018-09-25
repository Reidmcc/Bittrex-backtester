from swing_trade_class import swing_trade

coins = (
    'BTC-XLM',
    'BTC-DOGE',
    'BTC-XMR',
    'BTC-ETC',
    'BTC-ADA',
    'BTC-TUSD'
    )

st = swing_trade(coins)

st.run_test()
