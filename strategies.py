from PyQt5.QtGui import *  # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import ta # type: ignore

class StrategyManager:
    def __init__(self, app):
        self.app = app

    def macd_strategy(self, df):
        # Перевернуть DataFrame
        df_reversed = df[::-1]
        
        # Рассчитать MACD на перевернутом DataFrame
        macd = ta.trend.MACD(df_reversed['close'])
        df_reversed['macd'] = macd.macd()
        df_reversed['macd_signal'] = macd.macd_signal()

        df = df_reversed[::-1]

        # Рисуем индикаторы
        self.app.canvas.ax2.plot(df.index, df['macd'], label='MACD', color='blue', linestyle='--', alpha = 0.5)
        self.app.canvas.ax2.plot(df.index, df['macd_signal'], label='MACD Signal', color='orange', alpha = 0.5)

        transactions = []
        profit_factor = 1.5
        profit_percent = 3
        open_price = 0
        open_time = 0
        type = 1 # 1 - long, -1 - short
        current_balance = 100
        balance = [[],[]]
        balance[0].append(current_balance)
        balance[1].append(df.index[-1])
        position_size = 1
        trade_open = False 
        percent5 = int(len(df) / 50)

        for i in range(len(df) - 1, 0, -1):
            if (len(df)-i) % percent5 == 0:
                self.app.bar.setValue(int((len(df)-i) / len(df) * 100)) 
            if trade_open:
                if (df['high'].iloc[i] >= tp and type == 1) or (df['low'].iloc[i] <= tp and type == -1):
                    close_price = tp
                    close_time = df.index[i]
                    result = 1
                    trade_open = False
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    current_balance = current_balance+current_balance*position_size*0.01*profit_percent
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                elif (df['low'].iloc[i] <= sl and type == 1) or (df['high'].iloc[i] >= sl and type == -1):
                    close_price = sl
                    close_time = df.index[i]
                    result = 0
                    trade_open = False
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    current_balance = current_balance-current_balance*position_size*0.01*profit_percent/profit_factor
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                else:
                    balance[0].append(current_balance+current_balance*position_size*((df['open'].iloc[i]+df['close'].iloc[i])/2/open_price-1)*type)
                    balance[1].append(df.index[i])  

            if not trade_open:
                if df['macd'].iloc[i-1] > df['macd_signal'].iloc[i-1] and df['macd'].iloc[i] < df['macd_signal'].iloc[i]:
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    tp = open_price * (1+0.01*profit_percent)
                    sl = open_price * (1-0.01*profit_percent/profit_factor)
                    type = 1
                    trade_open = True
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i]) 
                if df['macd'].iloc[i-1] < df['macd_signal'].iloc[i-1] and df['macd'].iloc[i] > df['macd_signal'].iloc[i]:
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    tp = open_price * (1-0.01*profit_percent)
                    sl = open_price * (1+0.01*profit_percent/profit_factor)
                    type = -1
                    trade_open = True
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])

        balance[0].append(current_balance)
        balance[1].append(df.index[0])
        return transactions, balance

    def macd_v2_strategy(self, df):
        # Перевернуть DataFrame
        df_reversed = df[::-1]
        
        # Рассчитать MACD на перевернутом DataFrame
        macd = ta.trend.MACD(df_reversed['close'])
        bollinger = ta.volatility.BollingerBands(df_reversed['close'])
        df_reversed['macd'] = macd.macd()
        df_reversed['macd_signal'] = macd.macd_signal()
        df_reversed['bollinger_high'] = bollinger.bollinger_hband()
        df_reversed['bollinger_low'] = bollinger.bollinger_lband()

        df = df_reversed[::-1]

        # Рисуем индикаторы
        self.app.canvas.ax2.plot(df.index, df['macd'], label='MACD', color='blue', linestyle='--', alpha = 0.5)
        self.app.canvas.ax2.plot(df.index, df['macd_signal'], label='MACD Signal', color='orange', alpha = 0.5)
        self.app.canvas.ax1.plot(df.index, df['bollinger_high'], label='BB High', color='red', alpha = 0.5)
        self.app.canvas.ax1.plot(df.index, df['bollinger_low'], label='BB Low', color='green', alpha = 0.5)

        transactions = []
        profit_factor = 1.5
        profit_percent = 3
        open_price = 0
        open_time = 0
        type = 1 # 1 - long, -1 - short
        current_balance = 100
        balance = [[],[]]
        balance[0].append(current_balance)
        balance[1].append(df.index[-1])
        position_size = 1
        trade_open = False 

        for i in range(len(df) - 1, 0, -1):
            if trade_open:
                if (df['high'].iloc[i] >= tp and type == 1) or (df['low'].iloc[i] <= tp and type == -1):
                    close_price = tp
                    close_time = df.index[i]
                    result = 1
                    trade_open = False
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    current_balance = current_balance+current_balance*position_size*0.01*profit_percent
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                elif (df['low'].iloc[i] <= sl and type == 1) or (df['high'].iloc[i] >= sl and type == -1):
                    close_price = sl
                    close_time = df.index[i]
                    result = 0
                    trade_open = False
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    current_balance = current_balance-current_balance*position_size*0.01*profit_percent/profit_factor
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                else:
                    balance[0].append(current_balance+current_balance*position_size*((df['open'].iloc[i]+df['close'].iloc[i])/2/open_price-1)*type)
                    balance[1].append(df.index[i])  

            if not trade_open:
                if df['macd_signal'].iloc[i-1] < df['macd_signal'].iloc[i-2] and df['macd_signal'].iloc[i] > df['macd_signal'].iloc[i-1]:
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    tp = open_price * (1+0.01*profit_percent)
                    sl = open_price * (1-0.01*profit_percent/profit_factor)
                    type = 1
                    trade_open = True
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i]) 
                if df['macd_signal'].iloc[i-1] > df['macd_signal'].iloc[i-2] and df['macd_signal'].iloc[i] < df['macd_signal'].iloc[i-1]:
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    tp = open_price * (1-0.01*profit_percent)
                    sl = open_price * (1+0.01*profit_percent/profit_factor)
                    type = -1
                    trade_open = True
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])

        balance[0].append(current_balance)
        balance[1].append(df.index[0])
        return transactions, balance

    def macd_v3_strategy(self, df):
        # Перевернуть DataFrame
        df_reversed = df[::-1]
        
        # Рассчитать MACD на перевернутом DataFrame
        macd = ta.trend.MACD(df_reversed['close'])
        bollinger = ta.volatility.BollingerBands(df_reversed['close'])
        df_reversed['macd'] = macd.macd()
        df_reversed['macd_signal'] = macd.macd_signal()
        df_reversed['bollinger_high'] = bollinger.bollinger_hband()
        df_reversed['bollinger_low'] = bollinger.bollinger_lband()

        df = df_reversed[::-1]

        # Рисуем индикаторы
        self.app.canvas.ax2.plot(df.index, df['macd'], label='MACD', color='blue', linestyle='--', alpha = 0.5)
        self.app.canvas.ax2.plot(df.index, df['macd_signal'], label='MACD Signal', color='orange', alpha = 0.5)
        self.app.canvas.ax1.plot(df.index, df['bollinger_high'], label='BB High', color='red', alpha = 0.5)
        self.app.canvas.ax1.plot(df.index, df['bollinger_low'], label='BB Low', color='green', alpha = 0.5)

        df = df[::-1]

        transactions = []
        profit_factor = 1.5
        profit_percent = 3
        open_price = 0
        open_time = 0
        type = 1 # 1 - long, -1 - short
        current_balance = 100
        balance = [[],[]]
        balance[0].append(current_balance)
        balance[1].append(df.index[0])
        position_size = 1
        trade_open = False 

        for i in range(len(df)):
            if trade_open:
                if df['macd'].iloc[i-1] > df['macd'].iloc[i-2] and df['macd'].iloc[i] < df['macd'].iloc[i-1] and type == 1:
                    close_price = df['close'].iloc[i]
                    close_time = df.index[i]
                    if close_price > open_price:
                        result = 1
                        tp = close_price
                        sl = open_price
                    else:
                        result = 0
                        tp = open_price
                        sl = close_price
                    trade_open = False
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    current_balance = current_balance+current_balance*position_size*(close_price-open_price)/open_price
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                elif df['macd'].iloc[i-1] < df['macd'].iloc[i-2] and df['macd'].iloc[i] > df['macd'].iloc[i-1] and type == -1:
                    close_price = df['close'].iloc[i]
                    close_time = df.index[i]
                    if close_price < open_price:
                        result = 1
                        tp = close_price
                        sl = open_price
                    else:
                        result = 0
                        tp = open_price
                        sl = close_price
                    trade_open = False
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    current_balance = current_balance+current_balance*position_size*(open_price - close_price)/open_price
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                else:
                    balance[0].append(current_balance+current_balance*position_size*((df['open'].iloc[i]+df['close'].iloc[i])/2/open_price-1)*type)
                    balance[1].append(df.index[i])  

            if not trade_open:
                if df['macd'].iloc[i-1] < df['macd'].iloc[i-2] and df['macd'].iloc[i] > df['macd'].iloc[i-1]:
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    type = 1
                    trade_open = True
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i]) 
                if df['macd'].iloc[i-1] > df['macd'].iloc[i-2] and df['macd'].iloc[i] < df['macd'].iloc[i-1]:
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    type = -1
                    trade_open = True
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])

        balance[0].append(current_balance)
        balance[1].append(df.index[-1])
        df = df[::-1]
        return transactions, balance

    def bollinger_vwap_strategy(self, df):
        # Убедиться, что все данные числовые
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        # Перевернуть DataFrame для удобства расчета индикаторов
        df_reversed = df[::-1]
        
        # Расчитываем индикаторы
        macd = ta.trend.MACD(df_reversed['close'])
        df_reversed['macd'] = macd.macd()
        df_reversed['macd_signal'] = macd.macd_signal()
        bollinger = ta.volatility.BollingerBands(df_reversed['close'])
        df_reversed['bollinger_high'] = bollinger.bollinger_hband()
        df_reversed['bollinger_low'] = bollinger.bollinger_lband()
        vwap = ta.volume.VolumeWeightedAveragePrice(df_reversed['high'], df_reversed['low'], df_reversed['close'], df_reversed['volume'], window = 200)
        df_reversed['vwap'] = vwap.vwap

        df = df_reversed[::-1]
        
        # Рисуем индикаторы
        self.app.canvas.ax1.plot(df.index, df['bollinger_high'], label='BB High', color='red', alpha = 0.5)
        self.app.canvas.ax1.plot(df.index, df['bollinger_low'], label='BB Low', color='green', alpha = 0.5)
        self.app.canvas.ax1.plot(df.index, df['vwap'], label='VWAP', color='orange', linestyle='--', alpha = 0.5)

        transactions = []
        current_balance = 100
        balance = [[], []]
        balance[0].append(current_balance)
        balance[1].append(df.index[-1])
        position_size = 1
        trade_open = False
        open_price = 0
        open_time = 0
        profit_factor = 1.5
        profit_percent = 1
        tp = 0
        sl = 0
        type = 0  # 1 - long, -1 - short

        for i in range(len(df)-201, 00, -1):
            if trade_open:
                if (df['high'].iloc[i] >= tp and type == 1) or (df['low'].iloc[i] <= tp and type == -1):
                    close_price = tp
                    close_time = df.index[i]
                    result = 1
                    trade_open = False
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    current_balance = current_balance+current_balance*position_size*0.01*profit_percent
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                elif (df['low'].iloc[i] <= sl and type == 1) or (df['high'].iloc[i] >= sl and type == -1):
                    close_price = sl
                    close_time = df.index[i]
                    result = 0
                    trade_open = False
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    current_balance = current_balance-current_balance*position_size*0.01*profit_percent/profit_factor
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                else:
                    balance[0].append(current_balance+current_balance*position_size*((df['open'].iloc[i]+df['close'].iloc[i])/2/open_price-1)*type)
                    balance[1].append(df.index[i])  
            else:
                if (df['close'].iloc[i] < df['bollinger_low'].iloc[i]) and \
                (df['close'].iloc[i-15:i] > df['vwap'].iloc[i-15:i]).all():
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    tp = open_price * (1+0.01*profit_percent)
                    sl = open_price * (1-0.01*profit_percent/profit_factor)
                    type = 1  # long
                    trade_open = True
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                
                elif (df['close'].iloc[i] > df['bollinger_high'].iloc[i]) and \
                    (df['close'].iloc[i-15:i] < df['vwap'].iloc[i-15:i]).all():
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    tp = open_price * (1-0.01*profit_percent)
                    sl = open_price * (1+0.01*profit_percent/profit_factor)
                    type = -1  # short
                    trade_open = True
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])

        balance[0].append(current_balance)
        balance[1].append(df.index[0])
        return transactions, balance

    def bollinger_v2(self, df):
        # Убедиться, что все данные числовые
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

        df_reversed = df[::-1]

        # Расчитываем индикаторы
        macd = ta.trend.MACD(df_reversed['close'])
        df_reversed['macd'] = macd.macd()
        df_reversed['macd_signal'] = macd.macd_signal()
        bollinger = ta.volatility.BollingerBands(df_reversed['close'])
        df_reversed['bollinger_high'] = bollinger.bollinger_hband()
        df_reversed['bollinger_low'] = bollinger.bollinger_lband()

        df = df_reversed[::-1]

        # Рисуем индикаторы
        self.app.canvas.ax1.plot(df.index, df['bollinger_high'], label='BB High', color='red', alpha = 0.5)
        self.app.canvas.ax1.plot(df.index, df['bollinger_low'], label='BB Low', color='green', alpha = 0.5)

        transactions = []
        current_balance = 100
        balance = [[], []]
        balance[0].append(current_balance)
        balance[1].append(df.index[-1])
        position_size = 1
        trade_open = False
        open_price = 0
        open_time = 0
        profit_factor = 1.5
        profit_percent = 1
        tp = 0
        sl = 0
        type = 0  # 1 - long, -1 - short

        for i in range(len(df)-201, 00, -1):
            if trade_open:
                if (df['high'].iloc[i] >= tp and type == 1) or (df['low'].iloc[i] <= tp and type == -1):
                    close_price = tp
                    close_time = df.index[i]
                    result = 1
                    trade_open = False
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    current_balance = current_balance+current_balance*position_size*0.01*profit_percent
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                elif (df['low'].iloc[i] <= sl and type == 1) or (df['high'].iloc[i] >= sl and type == -1):
                    close_price = sl
                    close_time = df.index[i]
                    result = 0
                    trade_open = False
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    current_balance = current_balance-current_balance*position_size*0.01*profit_percent/profit_factor
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                else:
                    balance[0].append(current_balance+current_balance*position_size*((df['open'].iloc[i]+df['close'].iloc[i])/2/open_price-1)*type)
                    balance[1].append(df.index[i])  
            else:
                if (df['low'].iloc[i] < df['bollinger_low'].iloc[i]) and (df['close'].iloc[i] > df['open'].iloc[i]) and ((df['bollinger_high'].iloc[i] - df['bollinger_low'].iloc[i]) / ((df['bollinger_high'].iloc[i] + df['bollinger_low'].iloc[i])/2) > 0.03):
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    tp = open_price * (1+0.01*profit_percent)
                    sl = open_price * (1-0.01*profit_percent/profit_factor)
                    type = 1  # long
                    trade_open = True
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                
                if (df['high'].iloc[i] > df['bollinger_high'].iloc[i]) and (df['close'].iloc[i] < df['open'].iloc[i])and ((df['bollinger_high'].iloc[i] - df['bollinger_low'].iloc[i]) / ((df['bollinger_high'].iloc[i] + df['bollinger_low'].iloc[i])/2) > 0.03):
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    tp = open_price * (1-0.01*profit_percent)
                    sl = open_price * (1+0.01*profit_percent/profit_factor)
                    type = -1  # short
                    trade_open = True
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])

        balance[0].append(current_balance)
        balance[1].append(df.index[0])
        return transactions, balance
    
    def Supertrend(self, df, atr_period, multiplier):
        high = df['high']
        low = df['low']
        close = df['close']
        
        # calculate ATR
        price_diffs = [high - low, 
                    high - close.shift(), 
                    close.shift() - low]
        true_range = pd.concat(price_diffs, axis=1)
        true_range = true_range.abs().max(axis=1)
        atr = true_range.ewm(alpha=1/atr_period,min_periods=atr_period).mean() 
        # df['atr'] = df['tr'].rolling(atr_period).mean()
        
        # HL2 is simply the average of high and low prices
        hl2 = (high + low) / 2
        final_upperband = upperband = hl2 + (multiplier * atr)
        final_lowerband = lowerband = hl2 - (multiplier * atr)
        
        # initialize Supertrend column to True
        supertrend = [True] * len(df)
        
        for i in range(1, len(df.index)):
            
            # if current close price crosses above upperband
            if close.iloc[i] > final_upperband.iloc[i-1]:
                supertrend[i] = True
            # if current close price crosses below lowerband
            elif close.iloc[i] < final_lowerband.iloc[i-1]: 
                supertrend[i] = False
            # else, the trend continues
            else:
                supertrend[i] = supertrend[i-1]
                
                # adjustment to the final bands
                if supertrend[i] == True and final_lowerband.iloc[i] < final_lowerband.iloc[i-1]:
                    final_lowerband.iloc[i] = final_lowerband.iloc[i-1]
                if supertrend[i] == False and final_upperband.iloc[i] > final_upperband.iloc[i-1]:
                    final_upperband.iloc[i] = final_upperband.iloc[i-1]

            # to remove bands according to the trend direction
            if supertrend[i] == True:
                final_upperband.iloc[i] = np.nan
            else:
                final_lowerband.iloc[i] = np.nan
        
        return pd.DataFrame({
            'Supertrend': supertrend,
            'Final Lowerband': final_lowerband,
            'Final Upperband': final_upperband
        }, index=df.index)

    def supertrend_strategy(self, df):
        df_reversed = df[::-1]
        period = 16
        multiplier = 5

        # Calculate SuperTrend
        sti = self.Supertrend(df_reversed, period, multiplier)
        df_reversed = df_reversed.join(sti)
        macd = ta.trend.MACD(df_reversed['close'])
        df_reversed['macd'] = macd.macd()
        df_reversed['macd_signal'] = macd.macd_signal()
        bollinger = ta.volatility.BollingerBands(df_reversed['close'])
        df_reversed['bollinger_high'] = bollinger.bollinger_hband()
        df_reversed['bollinger_low'] = bollinger.bollinger_lband()
        vwap = ta.volume.VolumeWeightedAveragePrice(df_reversed['high'], df_reversed['low'], df_reversed['close'], df_reversed['volume'], window = 500)
        df_reversed['vwap'] = vwap.vwap

        df = df_reversed[::-1]
        
        # Рисуем индикаторы
        #self.app.canvas.ax1.plot(df.index, df['bollinger_high'], label='BB High', color='white', alpha = 0.5)
        #self.app.canvas.ax1.plot(df.index, df['bollinger_low'], label='BB Low', color='white', alpha = 0.5)
        self.app.canvas.ax1.plot(df.index, df['vwap'], label='VWAP', color='orange', linestyle='--', alpha = 0.5)
        self.app.canvas.ax2.plot(df.index, df['macd'], label='Macd', color='white', alpha = 0.5)
        self.app.canvas.ax2.plot(df.index, df['macd_signal'], label='Macd signal', color='blue', alpha = 0.5)
        #self.app.canvas.ax2.plot(df.index, df['Supertrend'], label='SuperTrend', color='yellow', linestyle='--', alpha=0.5)
        self.app.canvas.ax1.plot(df.index, df['Final Lowerband'], label='Final Lowerband', color='green', linestyle='--', alpha=0.5)
        self.app.canvas.ax1.plot(df.index, df['Final Upperband'], label='Final Upperband', color='red', linestyle='--', alpha=0.5)

        transactions = []
        open_price = 0
        open_time = 0
        type = 1  # 1 - long, -1 - short
        current_balance = 100
        balance = [[], []]
        balance[0].append(current_balance)
        balance[1].append(df.index[-1])
        position_size = 1
        trade_open = False
        percent5 = int(len(df) / 50)

        for i in range(len(df) - 12, 0, -1):
            if (len(df) - i) % percent5 == 0:
                self.app.bar.setValue(int((len(df) - i) / len(df) * 100))
            
            if trade_open:
                if df['Supertrend'].iloc[i+1] != df['Supertrend'].iloc[i]:
                    if type == 1:
                        close_price = df['Final Lowerband'].iloc[i+1]
                    else:
                        close_price = df['Final Upperband'].iloc[i+1]
                    close_time = df.index[i]
                    result = 1 if (type == 1 and close_price > open_price) or \
                                (type == -1 and close_price < open_price) else 0
                    if result == 1:
                        tp = close_price
                        sl = open_price
                        current_balance += current_balance * position_size * abs((close_price - open_price) / open_price)
                    else:
                        tp = open_price
                        sl = close_price
                        current_balance -= current_balance * position_size * abs((close_price - open_price) / open_price)
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                    trade_open = False
                else:
                    balance[0].append(current_balance + current_balance * position_size * ((df['open'].iloc[i] + df['close'].iloc[i]) / 2 / open_price - 1) * type)
                    balance[1].append(df.index[i])

            if not trade_open:
                if df['Supertrend'].iloc[i+1] < df['Supertrend'].iloc[i]:
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    type = 1
                    trade_open = True
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                elif df['Supertrend'].iloc[i+1] > df['Supertrend'].iloc[i]:
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    type = -1
                    trade_open = True
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])

        balance[0].append(current_balance)
        balance[1].append(df.index[0])

        """
        wins = 0
        losses = 0
        winrate = 0
        for tp, sl, open_price, open_time, close_time, close_price, type, result in transactions:
            if result == 1:
                wins += 1
            else:
                losses += 1
        if wins+losses == 0:
            winrate = 0
        else:
            winrate = round(wins/(wins+losses)*100, ndigits=2)
        profit = round((balance[0][-1]-balance[0][0])/balance[0][0]*100, ndigits=2)

        
        print(str('period: ' + str(period)))
        print(str('multiplier: ' + str(multiplier)))

        print(str('Profit: ' + str(profit)))
        print(str('Winrate: ' + str(winrate)))
        print(str('Trades: ' + str(wins+losses)+'\n'))
        """

        return transactions, balance
    

    def supertrend_percent_strategy(self, df):
        df_reversed = df[::-1]
        period = 16
        multiplier = 5

        # Calculate SuperTrend
        sti = self.Supertrend(df_reversed, period, multiplier)
        df_reversed = df_reversed.join(sti)
        macd = ta.trend.MACD(df_reversed['close'])
        df_reversed['macd'] = macd.macd()
        df_reversed['macd_signal'] = macd.macd_signal()
        bollinger = ta.volatility.BollingerBands(df_reversed['close'])
        df_reversed['bollinger_high'] = bollinger.bollinger_hband()
        df_reversed['bollinger_low'] = bollinger.bollinger_lband()
        vwap = ta.volume.VolumeWeightedAveragePrice(df_reversed['high'], df_reversed['low'], df_reversed['close'], df_reversed['volume'], window = 500)
        df_reversed['vwap'] = vwap.vwap

        df = df_reversed[::-1]
        
        # Рисуем индикаторы
        self.app.canvas.ax1.plot(df.index, df['bollinger_high'], label='BB High', color='white', alpha = 0.5)
        self.app.canvas.ax1.plot(df.index, df['bollinger_low'], label='BB Low', color='white', alpha = 0.5)
        #self.canvas.ax1.plot(df.index, df['vwap'], label='VWAP', color='orange', linestyle='--', alpha = 0.5)
        #self.canvas.ax2.plot(df.index, df['macd'], label='Macd', color='white', alpha = 0.5)
        #self.canvas.ax2.plot(df.index, df['macd_signal'], label='Macd signal', color='blue', alpha = 0.5)
        #self.canvas.ax2.plot(df.index, df['Supertrend'], label='SuperTrend', color='yellow', linestyle='--', alpha=0.5)
        self.app.canvas.ax1.plot(df.index, df['Final Lowerband'], label='Final Lowerband', color='green', linestyle='--', alpha=0.5)
        self.app.canvas.ax1.plot(df.index, df['Final Upperband'], label='Final Upperband', color='red', linestyle='--', alpha=0.5)

        transactions = []
        open_price = 0
        open_time = 0
        profit_factor = 1.5
        profit_percent = 2
        type = 1  # 1 - long, -1 - short
        current_balance = 100
        balance = [[], []]
        balance[0].append(current_balance)
        balance[1].append(df.index[-1])
        position_size = 1
        trade_open = False
        percent5 = int(len(df) / 50)
        tp = 0
        sl = 0 

        for i in range(len(df) - 12, 0, -1):
            if (len(df) - i) % percent5 == 0:
                self.app.bar.setValue(int((len(df) - i) / len(df) * 100))
            
            if trade_open:
                if (df['high'].iloc[i] >= tp and type == 1) or (df['low'].iloc[i] <= tp and type == -1):
                    close_price = tp
                    close_time = df.index[i]
                    result = 1
                    trade_open = False
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    current_balance = current_balance+current_balance*position_size*0.01*profit_percent
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                elif (df['low'].iloc[i] <= sl and type == 1) or (df['high'].iloc[i] >= sl and type == -1):
                    close_price = sl
                    close_time = df.index[i]
                    result = 0
                    trade_open = False
                    transactions.append((tp, sl, open_price, open_time, close_time, close_price, type, result))
                    current_balance = current_balance-current_balance*position_size*0.01*profit_percent/profit_factor
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                else:
                    balance[0].append(current_balance+current_balance*position_size*((df['open'].iloc[i]+df['close'].iloc[i])/2/open_price-1)*type)
                    balance[1].append(df.index[i])  

            if not trade_open:
                if df['Supertrend'].iloc[i+1] < df['Supertrend'].iloc[i]:
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    type = 1
                    trade_open = True
                    tp = open_price * (1+0.01*profit_percent)
                    sl = open_price * (1-0.01*profit_percent/profit_factor)
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])
                elif df['Supertrend'].iloc[i+1] > df['Supertrend'].iloc[i]:
                    open_price = df['close'].iloc[i]
                    open_time = df.index[i]
                    type = -1
                    trade_open = True
                    tp = open_price * (1-0.01*profit_percent)
                    sl = open_price * (1+0.01*profit_percent/profit_factor)
                    balance[0].append(current_balance)
                    balance[1].append(df.index[i])

        balance[0].append(current_balance)
        balance[1].append(df.index[0])

        """
        wins = 0
        losses = 0
        winrate = 0
        for tp, sl, open_price, open_time, close_time, close_price, type, result in transactions:
            if result == 1:
                wins += 1
            else:
                losses += 1
        if wins+losses == 0:
            winrate = 0
        else:
            winrate = round(wins/(wins+losses)*100, ndigits=2)
        profit = round((balance[0][-1]-balance[0][0])/balance[0][0]*100, ndigits=2)

        
        print(str('period: ' + str(period)))
        print(str('multiplier: ' + str(multiplier)))

        print(str('Profit: ' + str(profit)))
        print(str('Winrate: ' + str(winrate)))
        print(str('Trades: ' + str(wins+losses)+'\n'))
        """

        return transactions, balance