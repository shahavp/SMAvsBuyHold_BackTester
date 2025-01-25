

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk




## Backtester Engine 
class Backtester:



    def __init__(self, ticker, start_date, end_date):
        """
        Initialise the Backtester object

        This constructor sets up the initial state of the Backtester, including
        loading the historical price data for the specified stock and date range.

        Parameters:
        ticker (str): The stock ticker symbol.
        start_date (str): The start date for the backtest period in 'YYYY-MM-DD' format.
        end_date (str): The end date for the backtest period in 'YYYY-MM-DD' format.

        Attributes:
        ticker (str): The stock ticker symbol.
        start_date (str): The start date of the backtest period.
        end_date (str): The end date of the backtest period.
        data (pandas.DataFrame): Historical price data for the specified stock and date range.
        results (None): Placeholder for backtest results, initialised as null.
        cumulative_returns (None): Placeholder for cumulative returns, initialised as null.
        """
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.data = self._load_data()
        self.results = None
        self.cumulative_returns = None


        







    def _load_data(self):
        """
        PRIVATE METHOD
        Fetch historical price data from Yahoo Finance for the specified stock and date range.

        This method uses the yfinance library to download historical stock data.
        It retrieves the Adjusted Close price (named price for simplicity)

        Returns:
        - pandas.DataFrame: A DataFrame containing the historical price data.
                              The DataFrame has a single column named 'price',
                              which contains the adjusted closing prices for each trading day.

        """
        data = yf.download(self.ticker, start=self.start_date, end=self.end_date, auto_adjust=False) #auto-adjust false ensures a column for adjusted close and close prices
        return data[['Adj Close']].rename(columns={'Adj Close': 'price'})

    






    def compute_metrics(self):
        """
        Compute and return key performance metrics for the backtest.

        This method calculates various performance metrics based on the results
        of a previously run backtest. It computes total return, annualized return,
        Sharpe ratio, and maximum drawdown.

        Returns:
        - A dictionary containing the following metrics:
            - 'total_return' (float): The total return of the strategy over the entire period.
            - 'annualized_return' (float): The annualized return of the strategy.
            - 'sharpe_ratio' (float): The Sharpe ratio, a measure of risk-adjusted return.
            - 'max_drawdown' (float): The maximum drawdown, representing the largest peak-to-trough decline.


        """

        if self.results is None:
            raise ValueError("Backtest not run yet.")

        returns = self.results['net_returns']
        cumulative_returns = self.results['cumulative_returns']

        # Basic metrics
        total_return = cumulative_returns.iloc[-1]
        annualized_return = (1 + total_return) ** (252/len(self.data)) - 1
        sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
        max_drawdown = (cumulative_returns / cumulative_returns.cummax() - 1).min()

        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }

    






    def run_backtest(self, short_window, long_window, transaction_cost=0.001):
        """
        Execute a moving average crossover strategy backtest.
        
        Param:
            short_window (int): Number of days for short-term moving average
            long_window (int): Number of days for long-term moving average
            transaction_cost (float, optional): Percentage cost per transaction 
            Applied on position changes. Defaults to 0.1% (in future versions can be edited)

        Returns result of compute_metrics() containing performance statistics
        
            
            
        Populates:
            self.results (DataFrame): Contains all intermediate calculations
            self.cumulative_returns (Series): Cumulative return series

        """

        data = self.data.copy()
        
         #Calculate short/long moving averages
        price_series = data['price'].squeeze()  # Convert DataFrame column to Series
        data['short_ma'] = price_series.rolling(short_window).mean()
        data['long_ma'] = price_series.rolling(long_window).mean()
        
        #Generate buy/sell signals based on MA crossovers
        data['signal'] = np.where(data['short_ma'] > data['long_ma'], 1, -1)
        data['positions'] = data['signal'].diff()
        
        # Remove NaN values
        data = data.dropna()
        
        # Calculate returns accounting for transaction costs
        data['strategy_returns'] = (
        data['signal'].shift(1)      # Series
        * price_series.pct_change()  # Series
    )
        

        # Store results in self.results DataFrame
        data['transaction_costs'] = np.abs(data['positions'].shift(1)) * transaction_cost
        data['net_returns'] = data['strategy_returns'] - data['transaction_costs']
        data['cumulative_returns'] = (1 + data['net_returns']).cumprod()
        



        # Return performance metrics from compute_metrics()
        self.results = data
        self.cumulative_returns = data['cumulative_returns']
        return self.compute_metrics()
    






    def plot_results(self):
        """
        Visualize backtest results with two subplots:
        - Price series with moving averages and trading signals
        - Cumulative returns vs buy-and-hold strategy
        
        
        Upper plot shows:
            - Price series
            - Short/long moving averages
            - Buy signals (green triangles)
            - Sell signals (red triangles)
            
            Lower plot compares:
            - Strategy cumulative returns
            - Buy-and-hold cumulative returns
        """
        if self.results is None:
            raise ValueError("Backtest not run yet.")
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # Price and moving averages
        ax1.plot(self.results['price'], label='Adj Close')
        ax1.plot(self.results['short_ma'], label=f'Short MA ({self.results["short_ma"].count()})')
        ax1.plot(self.results['long_ma'], label=f'Long MA ({self.results["long_ma"].count()})')
        ax1.set_title(f'{self.ticker} Price and Moving Averages')
        ax1.set_ylabel("Price (USD)")
        ax1.legend()
        
        # Buy/sell signals
        buys = self.results[self.results['positions'] > 0]
        sells = self.results[self.results['positions'] < 0]
        ax1.scatter(buys.index, buys['price'], marker='^', color='g', label='Buy')
        ax1.scatter(sells.index, sells['price'], marker='v', color='r', label='Sell')
        
        # Cumulative returns - Buy Hold Strategy Plots
        ax2.plot(self.results['cumulative_returns'], label='MA Strategy')
        ax2.plot((1 + self.results['price'].pct_change()).cumprod(), label='Buy & Hold')
        ax2.set_title('Cumulative Returns')
        ax2.set_ylabel("Cumulative Returns (Normalised to 1)")
        ax2.legend()

    
        fig.canvas.manager.set_window_title("Buy & Hold Strategy VS SMA Strategy for " + self.ticker + " from " + self.start_date + " to " + self.end_date)
        
        plt.tight_layout()
        plt.show()








def backtextAPI(root, ticker, endYear, endMonth, endDay, startYear, startMonth, startDay, shortSMA, longSMA):

    """ 
    Helper function for the form.
    Retrieves form data from the Tkinter Widgets.
    Executes backtest using this data and calls functions to plot the results.
    """


    #Retrieves form data, and converts it to appropriate format
    actualStart = startYear.get() + "-" + startMonth.get() + "-" + startDay.get()
    actualEnd = endYear.get() + "-" + endMonth.get() + "-" + endDay.get()
    tickerGet = ticker.get().upper()
    longSMAGet = int(longSMA.get())
    shortSMAGet = int(shortSMA.get())

    #Destroys form and widgets
    root.destroy()


    #No error checking mechanism as such (outside scope for a limited basic project)
    try:
        #Loading screen
        loading = tk.Label(window,
            text="Loading ...",
        )
        loading.pack()

        print("Backtest intialising...")


        # Initialize backtester
        bt = Backtester(tickerGet, actualStart, actualEnd)
        
        # Run backtest with parameters, and recieves metric data
        metrics = bt.run_backtest(short_window=shortSMAGet, long_window=longSMAGet)

        print("Backtest Completed!")
        
        # Print results
        print("Backtest Results:")
        resultsContent = ""
        for k, v in metrics.items():
            #Formats into a string paragraph for both Tkinter and terminal output.
            resultsContent = resultsContent + f"{k.replace('_', ' ').title():<20} {v:.2%}\n" if isinstance(v, float) else f"{k.replace('_', ' ').title():<20} {v:.2f}\n"


        #Prints to terminal
        print(resultsContent)


        #Prints to tkinter window
        loading.pack_forget()
        tk.Label(window,
            text=resultsContent,
            font="Arial 14"
        ).grid(row=0, column=0, padx=5, pady=5)
        
        # Visualize results
        bt.plot_results()
    


    except:
        print("ERROR with input variables. Check the following:\nEnsure all inputs done correctly.\n Check ticker symbol. Ensure dates follow YYYY-MM-DD.\nEnsure all inputs are integers with exception of ticker.\nUse valid dates - no error checking mechanisms.\n")

    




# Executes when the python script is executed directly.
if __name__ == "__main__":


    ## Form GUI code

    window = tk.Tk()
    window.title("Buy and Hold Vs SMA BackTest")
    window.resizable(False, False)

    root = tk.Frame(window)
    root.grid(row=0,column=0)

    

    # Ticker field
    tk.Label(
        root,
        text="Stock Ticker Code:",
    ).grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)
    ticker = ttk.Entry(root)
    ticker.grid(row=0, column=2, padx=5, pady=5, ipadx=5)

    # Start Date field
    tk.Label(
        root,
        text="Start (YYYY/MM/DD):",
    ).grid(row=1, column=1, padx=5, pady=5, sticky=tk.E)
    startDate = tk.Frame(root)
    startDate.grid(row=1, column=2)
    startYear = ttk.Entry(startDate, width=8)
    startYear.grid(row=0, column=1, padx=4, pady=5)
    startMonth = ttk.Entry(startDate, width=4)
    startMonth.grid(row=0, column=2, padx=2, pady=5)
    startDay = ttk.Entry(startDate, width=4)
    startDay.grid(row=0, column=3, padx=2, pady=5)

    

    # End Date field
    tk.Label(
        root,
        text="End (YYYY/MM/DD):",
    ).grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)
    endDate = tk.Frame(root)
    endDate.grid(row=2, column=2)
    endYear = ttk.Entry(endDate, width=8)
    endYear.grid(row=0, column=1, padx=4, pady=5)
    endMonth = ttk.Entry(endDate, width=4)
    endMonth.grid(row=0, column=2, padx=2, pady=5)
    endDay = ttk.Entry(endDate, width=4)
    endDay.grid(row=0, column=3, padx=2, pady=5)


    

   

    # Short SMA Days field
    tk.Label(
        root,
        text="Short SMA Days (rec: 50):",
    ).grid(row=3, column=1, padx=5, pady=5, sticky=tk.E)
    shortSMA = ttk.Entry(root)
    shortSMA.grid(row=3, column=2, padx=5, pady=5, ipadx=5)

    # Long SMA Days  field
    tk.Label(
        root,
        text="Long SMA Days (rec: 200):",
    ).grid(row=4, column=1, padx=5, pady=5, sticky=tk.E)
    longSMA = ttk.Entry(root)
    longSMA.grid(row=4, column=2, padx=5, pady=5, ipadx=5)

    # Submit button
    submit = ttk.Button(
        root,
        text="Submit",
        command= lambda: backtextAPI(root, ticker, endYear, endMonth, endDay, startYear, startMonth, startDay, shortSMA, longSMA)
    )
    submit.grid(row=5, column=2, padx=5, pady=5, sticky=tk.E)


    #Displays initial form.
    root.mainloop()












    