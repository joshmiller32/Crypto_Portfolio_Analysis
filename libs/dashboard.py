#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
#get_ipython().run_line_magic('matplotlib', 'inline')     <--- Christian is having an error with this, commented out to see if it breaks.
import hvplot.pandas
import libs.montecarlo as mc
import seaborn as sns
import panel as pn
import libs.apis as apis
from panel.interact import interact
import random

from iexfinance.stocks import get_historical_data
import iexfinance as iex


def get_assets_hist_data(tickers_dict={"index":[],"crypto":[]}, years=2):
    
    
    if ( len(tickers_dict["index"]) + len(tickers_dict["crypto"]) ) < 1:
              return "Empty list of assets"
        
    #Defining starting dat to get historical data.
    data_start_date = datetime.now() + timedelta(int(-365*years))

    #getting indeces historical prices form IEX
    if len(tickers_dict["index"]) > 0:
              print(f"received {tickers_dict['index']}")
              portfolio_indx_prices = apis.get_historic_data(ticker = tickers_dict["index"], 
                                                     start_date = data_start_date)

    #getting cryptos historical prices form cryptocompare
    if len(tickers_dict["crypto"]) > 0:
              print(f"received {tickers_dict['crypto']}")
              btc_daily_price = apis.get_crypto_daily_price(tickers_dict["crypto"],limit=int(years*365))

    #Creating the portfolio dataframe depending on the kind of portfolio (crypto only, index only, or both)
    portfolio_hist_prices = pd.DataFrame()
    
    #For index only
    if len(tickers_dict["index"]) > 0 and len(tickers_dict["crypto"]) == 0:
              portfolio_hist_prices = portfolio_indx_prices
              print(portfolio_hist_prices.head())
        
    #For crypto only    
    elif len(tickers_dict["index"]) == 0 and len(tickers_dict["crypto"]) > 0:
              portfolio_hist_prices = btc_daily_price
              print(portfolio_hist_prices.head())
        
    #For both
    else: #concatenating both dataframes   
        portfolio_hist_prices = pd.concat([portfolio_indx_prices,btc_daily_price],axis=1,join="inner")
        print(portfolio_hist_prices.head())
        
          
    portfolio_hist_prices.dropna(inplace=True)
    portfolio_hist_prices = portfolio_hist_prices[(portfolio_hist_prices[portfolio_hist_prices.columns] != 0).all(axis=1)]

    #formating dataframes
    portfolio_hist_prices = apis.normalize_dataframe(portfolio_hist_prices)
    portfolio_daily_retn = portfolio_hist_prices.pct_change().copy()
    
    #Save both hist. prices and hist. daily returns dataframes packed in a list to be able to return in the funtion.
    hist_price_ret_df = [ portfolio_hist_prices, portfolio_daily_retn ]
    
    return hist_price_ret_df


def corr_plot(portfolio_daily_retn):
    title_font = {'family': 'monospace',
            'color':  'blue',
            'weight': 'bold',
            'size': 15,
            }
    correlated = portfolio_daily_retn.corr()
    # Generate a mask for the upper triangle
    mask = np.zeros_like(correlated, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    # Set up the matplotlib figure
    correlated_plot, ax = plt.subplots(figsize=(12, 8))

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(correlated, mask=mask, cmap="coolwarm", vmax=1, vmin =-1, 
                center=0,square=True, linewidths=.5, annot=True )
    plt.title(f"Correlation Map of Portfolio\n",fontdict=title_font)
    #ax.set_facecolor("aliceblue")

     #correlated_plot = sns.heatmap(correlated, vmin=-1, vmax=1, annot=True,cmap="coolwarm") 
    plt.close()
    return pn.Pane(correlated_plot)

def get_corr_pane(portfolio_daily_retn):
    header_text = pn.panel(
        
    "<marquee> <bold>The latest news on crypto and finance here:</bold>&nbsp;<mar> BTC up 20,000.00% in last year, 7.77% today,&nbsp;"
    +" ETH up 400,000.00% in the last year, 9.99% today,&nbsp; "
    +" Trump lost re-election due to poor results,&nbsp; Global peace achieved yesterday at UN,&nbsp; "
    +" S&P500 down 10% in the last year, down 1.21%, today,&nbsp; "
    +"cryptocurrencies are being used more than dollar for international trading,&nbsp; XRP up 27.89% today,&nbsp; "
    +" Satoshi just gave away his millions of BTC to the most needed people in the developing world,&nbsp; "
    +" military war on drugs has been replaced by an educational war "
    +"on drugs and regulation of legal point of sales,&nbsp; drug cartels in bankruptcy, &nbsp;"
    +" Colombians achieved peace for first time in more than 60 years...&nbsp;</mar></marquee>", 
    align = "center"
    )

    side_text = pn.pane.Markdown(
'''
<style>

body {
    background-color: #FFFFFF;
}

mar {
  color: #006600;
  text-align: center;
  font-family: "Times New Roman", Times, serif;
  font-style: normal;
  font-size: 17px;
}

#leftbox {
    color: black;
}

bold{
    font-weight: bold;
    color: #003300;
    text-align: center;
    font-family: "Times New Roman", Times, serif;
    font-style: oblique;
    font-size: 24px;
    font-variant: small-caps;
}

p {
  color: #006600;
  font-size: 17px;
}

h1 {
    font-size: 30px;
    font-variant: small-caps;
    font-weight: bold;
    font-family: Arial, Helvetica, sans-serif;
}

h2 {
  color: #006600;
  font-family: Arial, Helvetica, sans-serif;
}

cr {
    font-size: 14px;
    font-style: italic;
    color: #33CCFF;
}
</style>
            
<div id="leftbox"> 
<h1>The Correlation Heat Map</h1>
</div>

<h2> The Formula </h2>

<img src= 'https://www.statisticshowto.datasciencecentral.com/wp-content/uploads/2009/11/pearsons.gif' height="260" width="550">
<br><cr>Image coutresy of<a href='https://www.statisticshowto.datasciencecentral.com/probability-and-statistics/correlation-coefficient-formula/#Pearson'> Statistics How To</a></cr> 
<p> Correlation between sets of data is a measure of how well they are related. <br>
The most common measure of correlation in stats is the Pearson Correlation. <br>
The full name is the Pearson Product Moment Correlation (PPMC). It shows the <br>
linear relationship between two sets of data. In simple terms, it answers the <br> 
question, Can I draw a line graph to represent the data? </p>
''',
        align= "center",
        width_policy = "max",
    )
    
    lower_text = pn.pane.Markdown('''
<h2><bold>Important:</bold> Correlation does not imply causation!</h2>
        ''',
                                  align= "center",
                                  width_policy = "max",
                                 )###??????????
    #WARNING:param.Markdown11741: Setting non-parameter attribute
    #max_with=5 using a mechanism intended only for parameters
    left_row = pn.Row(side_text, align="start")
    middle_row = pn.Row(corr_plot(portfolio_daily_retn),align="center", width_policy="fit")
    both_row = pn.Row(left_row, middle_row)
    
    corr_pane = pn.Column(header_text,both_row,lower_text,align="center", sizing_mode='stretch_both')
    
    return corr_pane
    
    

def sharp_rt_plot(portfolio_daily_retn):
    
    title_font = {'family': 'monospace',
            'color':  'blue',
            'weight': 'bold',
            'size': 15,
            }
    label_font = {'family': 'monospace',
            'color':  'green',
            'weight': 'bold',
            'size': 12,
            }
   
    bar_colors=["midnightblue","royalblue","indigo","darkcyan","darkgreen","maroon",
               "purple","darkorange","slategray","forestgreen"]

    sharp_ratios = portfolio_daily_retn.mean()*np.sqrt(252)/portfolio_daily_retn.std()

    sr_plot = plt.figure(figsize = (12,8));
    plt.bar(x = sharp_ratios.index, height=sharp_ratios,  color=random.sample(bar_colors,len(sharp_ratios.index)))
    plt.title(f"Sharp Ratios of Portfolio\n",fontdict=title_font)
    plt.ylabel("Sharp Ratio",fontdict=label_font)
    plt.xlabel("Assets",fontdict=label_font)
    plt.axhline(sharp_ratios.mean(), color='r')
    plt.close()
    return pn.Pane(sr_plot)


def plot_mont_carl(monte_carlo_sim):
    plot_title = f"Monte-Carlo Simulation of Portfolio"
    monte_carlo_sim_plot = monte_carlo_sim.hvplot(title=plot_title,figsize=(36,20),legend=False)
    return monte_carlo_sim_plot


def get_conf_interval(last_row_db,q=[0.05, 0.95]):
    confidence_interval = last_row_db.quantile(q=q)
    return confidence_interval


def plot_conf(values=None,conf=[0,0]):
    conifidence_plot = plt.figure(figsize=(12,8));
    plt.hist(x = values,bins=20)
    plt.axvline(conf.iloc[0], color='r')
    plt.axvline(conf.iloc[1], color='r')
    plt.close()
    return pn.Pane(conifidence_plot)

def bb_plot(df):
    bb_plot = plt.figure(figsize=(12,8));
    plt.plot(df.close)
    plt.plot(df.volatility_bbh, label='High BB')
    plt.plot(df.volatility_bbl, label='Low BB')
    plt.plot(df.volatility_bbm, label='EMA BB')
    plt.title('Bollinger Bands')
    plt.legend()
    plt.close()
    return pn.Pane(bb_plot)

def ichi_plot(df):
    ichi_plot = plt.figure(figsize=(12,8));
    plt.plot(df.close)
    plt.plot(df.trend_ichimoku_a, label='Ichimoku a')
    plt.plot(df.trend_ichimoku_b, label='Ichimoku b')
    plt.title('Ichimoku Kinko Hyo')
    plt.legend()
    plt.close()
    return pn.Pane(ichi_plot)

def ema_plot(df):
    ema_plot = plt.figure(figsize=(12,8));
    plt.plot(df.close)
    plt.plot(df.volatility_bbm, label='EMA BB')
    plt.title('Exponential Moving Average')
    plt.legend()
    plt.close()
    return pn.Pane(ema_plot)

def macd_plot(df):
    macd_plot = plt.figure(figsize=(12,8));
    plt.plot(df.trend_macd, label='MACD');
    plt.plot(df.trend_macd_signal, label='MACD Signal')
    plt.plot(df.trend_macd_diff, label='MACD Difference')
    plt.title('MACD, MACD Signal and MACD Difference')
    plt.legend()
    plt.close()
    return pn.Pane(macd_plot)


def get_dashboard(tickers_dict={"index":[],"crypto":[]}, years=2, mc_trials=500, mc_sim_days=252, weights=None):
    
    data = get_assets_hist_data(tickers_dict=tickers_dict, years=years)
    if type(data) == str:
        return data
    
    mc_sim = mc.monte_carlo_sim(data[0],trials = mc_trials, sim_days = mc_sim_days, weights = weights)
    #reset variables to clean old data remanents
    years, mc_trials, mc_sim_days, weights = 2,500, 252, None
    if type(mc_sim) == str: print(mc_sim)
    
    risk_tabs = pn.Tabs(
        ("Correlation of portfolio",get_corr_pane(data[1])),
        ("Sharp Ratios", sharp_rt_plot(data[1])),
        #background="whitesmoke"
    )


    montecarlo_tabs = pn.Tabs(
        ("monte Carlo Simulation",plot_mont_carl(mc_sim)),
        ("Confidence Intervals", plot_conf(mc_sim.iloc[-1],get_conf_interval(mc_sim.iloc[-1]))),
        #background="whitesmoke"
    )

    techl_analysis_tabs = pn.Tabs(
#        ("Exp. Moving Avg.",ema_plot(ta_df)),
#        ("Bollinger Bands", bb_plot(ta_df)),
#        ("MACD",macd_plot(ta_df)),
 #       ("Ichimoku Kinkō Hyō", ichi_plot(ta_df)),
    #    background="whitesmoke"
    )

    tabs = pn.Tabs(
        ("Risk",risk_tabs),
        ("Monte Carlo Simulation", montecarlo_tabs),
        ("Tecnical Analysis", techl_analysis_tabs),
        ("Report", "in construction"),
        #background="whitesmoke",
        tabs_location = "left",
        align = "start"
    )

    panel = tabs

    return panel


# In[ ]:




