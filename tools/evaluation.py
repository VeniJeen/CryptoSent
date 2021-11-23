import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
from statsmodels.tsa.stattools import grangercausalitytests
import numpy as np
import pandas as pd

def get_timeseries(df,value):
    fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')
    fig.show()


def get_ts_2axis(sent,btc,resample_period='w',btc_transformation='diff'):

    sdmin=datetime.strftime(sent.index.min(),'%Y-%m-%d')
    sdmax=datetime.strftime(sent.index.max(),'%Y-%m-%d')
    
    sent=sent.resample(resample_period).sum()
    btc=btc[sdmin:sdmax].resample(resample_period).mean()
    
  
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=sent.index, y=sent, name="Sentiment"),
        secondary_y=False,
    )

    if btc_transformation=='diff':
        fig.add_trace(
            go.Scatter(x=btc.index, y=btc.diff(), name="Bitcoin Avg"),
            secondary_y=True,
        )

    if btc_transformation=='pct_change':
        fig.add_trace(
            go.Scatter(x=btc.index, y=btc.pct_change(), name="Bitcoin Avg"),
            secondary_y=True,
        )
    # Add figure title
    fig.update_layout(
        title_text=f"BTC vs Sentiment - Resample ({resample_period})"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Sentiment  </b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>BTC Price</b>", secondary_y=True)

    fig.show()


def get_granger_causality(data ,maxlag=4, test='ssr_chi2test', verbose=False):

    #gc_test=['ssr_ftest','ssr_chi2test','lrtest','params_ftest'] 
    psave=[]
    cols=[]
    variables=data.columns
    df = pd.DataFrame(np.zeros((maxlag,len(variables))), columns=variables)
    for c in df.columns:
        for r in df.columns:
            if c!=r:
                test_result = grangercausalitytests(data[[r, c]], maxlag=maxlag, verbose=False)
                p_values = [round(test_result[i+1][0][test][1],4) for i in range(maxlag)]
                if verbose: print(f'Y = {r}, X = {c}, P Values = {p_values}')
                cols.append(f'Y_{r}__X_{c}')
                psave.append(p_values)
    df=pd.DataFrame(np.array(psave).T,columns=cols)
    return df