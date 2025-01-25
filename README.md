# Backtester Project: Understanding Stock Strategies with Python

## 📖 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Concepts Explained](#-key-concepts-explained)
3. [How to Use the Backtester](#-how-to-use-the-backtester)
4. [Interpreting the Results](#-interpreting-the-results)
5. [Troubleshooting](#-troubleshooting)
6. [Glossary](#-glossary)

---

##  Project Overview
This Python script helps you compares growths using a Simple Moving Averages Crossover Trading Strategy to simply just buying and holding the stocks. For example,  
*"Would a strategy based on moving averages have outperformed simply buying and holding AAPL stock?"*  

This helps investors:
- Avoid costly mistakes in real markets
- Compare strategies objectively
- Understand risk/reward tradeoffs

This incorporates a very basic GUI that enables parameters for Short MA, Long MA, backtesting duration and the stock ticker code, to compute the metric data.



---

## Key Concepts Explained - (For myself really, since I did not know anything at all before even getting into this project.)

### What is Backtesting?
Backtesting lets you test how a trading strategy **would have performed** in the past using historical data. 

### 1. Moving Averages (core logic behind the strategy)
| Term         | Explanation                                                                 | Example          |
|--------------|-----------------------------------------------------------------------------|------------------|
| **Short MA** | Average price over a short period (e.g., 20 days) - detects recent trends   | 20-day MA = $150 |
| **Long MA**  | Average price over a long period (e.g., 50 days) - shows overall direction  | 50-day MA = $145 |

**Crossover Strategy**:  
- **Buy Signal**: When Short MA crosses **above** Long MA ("Golden Cross")  
- **Sell Signal**: When Short MA crosses **below** Long MA ("Death Cross")  


### 2. Adjusted Close vs. Close (Initially confused me so I noted it down anyways)
| Metric          | Explanation                                                                 | Why It Matters                          |
|-----------------|-----------------------------------------------------------------------------|-----------------------------------------|
| **Close**       | Actual closing price of the stock on that day                               | Shows raw market price                 |
| **Adj Close**   | Adjusted for corporate actions (dividends, stock splits)                    | Reflects true investment growth        |

Example: If AAPL does a 2:1 stock split:  
- **Close** drops from $150 → $75  
- **Adj Close** stays consistent to preserve historical comparisons  

### 3. Sharpe Ratio
A measure of **risk-adjusted returns**. (Higher = Better)  
- Sharpe Ratio of 1 = Good  
- Sharpe Ratio of 2 = Excellent  
- Negative = Strategy lost money  

Formula:  
`(Average Return - Risk-Free Rate) / Standard Deviation of Returns`

### 4. Buy & Hold
The simplest strategy: Buy stock and hold it regardless of market fluctuations.  
- **Pros**: Low effort, no transaction costs  
- **Cons**: Exposed to all market downturns  

---

## 🛠 How to Use the Backtester

### Step 1: Install Requirements
```bash
pip install pandas yfinance matplotlib numpy 
```
Gathers real life historical data from Yahoo! Finance.

