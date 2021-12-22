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
            go.Scatter(x=btc.index, y=btc.pct_change(), name=f"Bitcoin {btc_transformation}"),
            secondary_y=True,
        )

    if btc_transformation=='none':
        fig.add_trace(
            go.Scatter(x=btc.index, y=btc, name=f"Bitcoin {btc_transformation}"),
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
    fig.update_yaxes(title_text=f"<b>BTC Price {btc_transformation}</b>", secondary_y=True)

    fig.show()

def result_processing(sentiment,coin_price,resample_period='d'):
    sdmin=datetime.strftime(sentiment.index.min(),'%Y-%m-%d')
    sdmax=datetime.strftime(sentiment.index.max(),'%Y-%m-%d')
    sent=sentiment.resample(resample_period).sum()
    btc=coin_price[sdmin:sdmax].resample(resample_period).mean()
    merres=pd.concat([sent,btc],axis=1)
    merres.loc[:,'avg_hl_diff']=merres.avg_hl.diff()
    merres.loc[:,'avg_hl_pct_change']=merres.avg_hl.pct_change()
    merres.loc[:,'sent_db_shift']=sent.shift(1)
    merres.loc[:,'sent_db_ptc_change']=sent.pct_change()
    return merres


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



####### Time Series Evaluation Metrics #######

def errors(x,Y):
    return [Y[i]-x[i] for i in range(len(x))]

def abolute_errors(x,Y):
    return [abs(Y[i]-x[i]) for i in range(len(x))]

    
def mean_error(x,Y):
    return np.mean([Y[i]-x[i] for i in range(len(x))])

from sklearn.metrics import mean_absolute_error as mae
from sklearn.metrics import mean_absolute_percentage_error as mape
from sklearn.metrics import r2_score as r2  
from sklearn.metrics import mean_squared_error as mse   #squared=False:rmse
#from sklearn.metrics import mean_squared_log_error as msle      #squared=False:rmsle

evaluation_metrics=[mean_error,mae,mape,mse]
evaluation_metrics_names=['me','mae','mape','mse','rmse']

def evaluate_pred(x,Y,model_name='m1'):
    scores=[]
    for metric in evaluation_metrics:
        scores.append(metric(x,Y))
    scores.append(mse(x,Y,squared=False))
    output=pd.DataFrame(
        np.array(scores),
        index=evaluation_metrics_names,
        columns=[model_name])
    return output

