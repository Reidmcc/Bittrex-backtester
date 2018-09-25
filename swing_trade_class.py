from bittrex import *
bitrex_one = Bittrex("[API key]", "[API secret]", api_version=API_V1_1)
bittrex_two = Bittrex("[API key]", "[API secret]", api_version=API_V2_0)
# the two versions contained in the wrapper have different available commands; no reason not to use both
import statistics
from requests.exceptions import ConnectionError
from http.client import RemoteDisconnected
from http.client import HTTPException
from urllib3.exceptions import ProtocolError

st = statistics

class swing_trade:
    def __init__(self, coins):
        self.green = '\033[92m'
        self.red = '\u001b[31;1m'
        self.stop_col = '\033[0m'
        self.interval = 1
        self.lookback = 20
        self.long_lookback = 100
        self.interval = 1
        self.coins = (
            'BTC-XLM',
            'BTC-DOGE',
            'BTC-XMR',
            'BTC-ETC',
            'BTC-ADA',
            'BTC-TUSD'
            )
        self.coins = coins
        self.all_candles = []

    def run_test(self):
        result_sum = []
        total_profit = 0
        total_trades = 0

        base_funds = 1
        alt_funds = 0
        capital = 0
        trades = 0
        in_trade = False
        stop_loss = 0
        last_buy = 0
        won = 0
        lost = 0
        cur_trade_sym = ''

        for c in self.coins:
            der = self.calc_derived(c)
            self.all_candles.append(der)

        length = len(self.all_candles[0]) - 10

        for i in range(self.long_lookback + 1, length):
            for a in self.all_candles:

                symbol = a[i]['symbol']
                time_n = a[i]['time']
                close = a[i]['close']
                high = a[i]['high']
                low = a[i]['low']
                dev = a[i]['st_dev']
                ma = a[i]['m_avg']
                l_ma = a[i]['l_ma']
                N = a[i]['N']
                position = abs(close - ma)

                last_close = a[i - 1]['close']
                last_dev = a[i - 1]['st_dev']
                last_ma = a[i - 1]['m_avg']
                bench_l_ma = a[i - 1]['l_ma']
                last_postion = abs(last_close - last_ma)

                if not in_trade and close < ma and position > dev * 2 and l_ma > bench_l_ma:
                    price = close
                    last_buy = price
                    if symbol == 'BTC-DOGE':
                        stop_loss = price - N
                    else:
                        stop_loss = price - N * .4
                    alt_funds = (base_funds / price) * 0.9985
                    base_funds = 0
                    trades += 1
                    in_trade = True
                    cur_trade_sym = symbol
                    print(
                        str(time_n) + ' ' + symbol + " Price low and post out-of-band peak, bought " + "{:.2f}".format(
                            alt_funds) + self.green + " at " + "{:.8f}".format(
                            price) + self.stop_col)
                if in_trade and cur_trade_sym == symbol:
                    if close < stop_loss:
                        base_funds = (alt_funds * stop_loss) * 0.9985
                        capital = base_funds
                        alt_funds = 0
                        in_trade = False
                        lost += 1
                        print(
                            str(time_n) + ' ' + symbol + " Stop-loss triggered, sold at  " + self.red + "{:.8f}".format(
                                stop_loss) + self.stop_col + " resulting balance = " + "{:.3f}".format(base_funds))
                        print('')
                        print('')
                    elif close > ma and position > dev * 2 and close > last_buy * 1.02:  # or (symbol == 'BTC-DOGE' and close > last_buy * 1.05)):  #and position < last_postion:
                        price = close
                        base_funds = (alt_funds * price) * 0.9985
                        capital = base_funds
                        alt_funds = 0
                        in_trade = False
                        if close > last_buy:
                            color = self.green
                            won += 1
                        else:
                            color = self.red
                            lost += 1
                        print(str(
                            time_n) + ' ' + symbol + " Price high and post out-of-band peak, sold at  " + color + "{:.8f}".format(
                            close) + self.stop_col + " resulting balance = " + "{:.3f}".format(base_funds))
                        print('')
                        print('')

        print('Final capital = ' + str(capital))
        print("Made " + str(trades) + " trades")
        print("Won " + str(won) + " lost " + str(lost))

    def get_klines(self, pair, interval):
        klines = []
        got_klines = False

        while not got_klines:
            try:
                klines = bittrex_two.get_candles(pair, interval)
            except (ConnectionError, RemoteDisconnected, ProtocolError,
                    HTTPException) as e:
                print(str(e) + ' ' + str(e.__traceback__))
            else:
                got_klines = True
        return klines


    def calc_derived(self, symbol):
        candles = self.get_klines(symbol, 'hour')["result"]
        form_candles = []
        devs = []
        mas = []
        l_mas = []
        Ns = []
        init_range_tot = 0
        prev_N = 0
        rng = len(candles)

        for i in range(0, rng):
            if i % self.interval or self.interval == 1:
                open_c = float(candles[i]['O'])
                high_c = float(candles[i]['H'])
                low_c = float(candles[i]['L'])
                close_c = float(candles[i]['C'])
                time_c = candles[i]['T']
                form_candles.append(
                    {'symbol': symbol, 'open': open_c, 'high': high_c, 'low': low_c, 'close': close_c, 'time': time_c,
                     'st_dev': 0, 'm_avg': 0, "l_ma": 0, 'N': 0})

        length = len(form_candles)
        for i in range(0, length):
            if i <= self.lookback:
                dev = 0
            else:
                sample = []
                for j in (i - self.lookback, i - 1):
                    val = form_candles[j]['close']
                    sample.append(val)
                    dev = st.pstdev(sample)
            devs.append(dev)

        for i in range(0, length):
            if i <= self.lookback:
                ma = 0
            else:
                sample = []
                for j in (i - self.lookback, i - 1):
                    val = form_candles[j]['close']
                    sample.append(val)
                    ma = sum(sample) / len(sample)
            mas.append(ma)

        for i in range(0, length):
            if i <= self.long_lookback:
                l_ma = 0
            else:
                sample = []
                for j in (i - self.long_lookback, i - 1):
                    val = form_candles[j]['close']
                    sample.append(val)
                    l_ma = sum(sample) / len(sample)
            l_mas.append(l_ma)

        for i in range(0, length):
            close = form_candles[i]['close']
            high = form_candles[i]['high']
            low = form_candles[i]['low']
            if 0 < i < self.long_lookback:
                prev_c = form_candles[i - 1]['close']
                high_min_low = high - low
                high_min_prev = high - prev_c
                prev_min_low = prev_c - low
                diff_list = (high_min_low, high_min_prev, prev_min_low)
                max_diff = max(diff_list)
                init_range_tot += max_diff
                N = 0
            else:
                prev_c = form_candles[i - 1]['close']
                high_min_low = high - low
                high_min_prev = high - prev_c
                prev_min_low = prev_c - low
                diff_list = (high_min_low, high_min_prev, prev_min_low)
                max_diff = max(diff_list)
                if prev_N == 0:
                    N = (19 * init_range_tot + max_diff) / 20
                    prev_N = N
                else:
                    N = (19 * prev_N + max_diff) / 20
                    prev_N = N
            Ns.append(N)

        for i in range(0, length):
            form_candles[i]['st_dev'] = devs[i]
            form_candles[i]['m_avg'] = mas[i]
            form_candles[i]['l_ma'] = l_mas[i]
            form_candles[i]['N'] = Ns[i]

        return form_candles
