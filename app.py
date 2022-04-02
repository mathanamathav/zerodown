import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime,date, timedelta
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import DecomposeResult, seasonal_decompose

url='https://drive.google.com/file/d/1FIcHqGCfM-8-SU6pbW6DOOCJNJgKAx-k/view?usp=sharing'
file_id=url.split('/')[-2]
dwn_url='https://drive.google.com/uc?id=' + file_id
st.set_page_config(layout="wide")



def plot_seasonal_decompose(result:DecomposeResult,city,column,dates:pd.Series=None):
    title = " Seasonal Decomposition "+city+" of the "+column+" attribute"
    x_values = dates if dates is not None else np.arange(len(result.observed))
    return (
        make_subplots(
            rows=4,
            cols=1,
            subplot_titles=["Observed", "Trend", "Seasonal", "Residuals"],
        )
        .add_trace(
            go.Scatter(x=x_values, y=result.observed, mode="lines", name='Observed'),
            row=1,
            col=1,
        )
        .add_trace(
            go.Scatter(x=x_values, y=result.trend, mode="lines", name='Trend'),
            row=2,
            col=1,
        )
        .add_trace(
            go.Scatter(x=x_values, y=result.seasonal, mode="lines", name='Seasonal'),
            row=3,
            col=1,
        )
        .add_trace(
            go.Scatter(x=x_values, y=result.resid, mode="lines", name='Residual'),
            row=4,
            col=1,
        )
        .update_layout(
            height=900, title=f'<b>{title}</b>', margin={'t':100}, title_x=0.5, showlegend=False
        )
    )
    
st.title("US Housing Market Dashboard")


@st.cache
def load_data(dwn_url):
    data = pd.read_csv(dwn_url,sep = '\t')
    # data = pd.read_csv(dwn_url,sep='\t')

    return data

uploaded_file = st.file_uploader("Choose a CSV file")
df = load_data(uploaded_file)
st.write(df.head())

@st.cache
def geomap_chart(df,column_attr):
    """
        function to plot map based on started
    """
    fig = px.choropleth(df,
                    locations='state', 
                    locationmode="USA-states", 
                    scope="usa",
                    title="US MAP from 2018-2022",
                    color=opt_column,
                    color_continuous_scale="Viridis_r", 
                    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, )
    fig.update_layout(geo=dict(bgcolor= 'rgba(0,0,0,0)'))
    return fig


    # def line_chart(df,column_attr="total_homes_sold"):
    #     """
    #         function to plot line based on started
    #     """
    #     return fig

column = list(df.columns)
column = column[1:]
column.remove('region_id')
column.remove('region_type_id')
column.remove('region_name')
column.remove('period_begin')
column.remove('period_end')
column.remove('duration')
column.remove('state')



opt_column = st.selectbox(
        'What is your column attribute you want to visualize?',
        column)

start_time = st.slider(
     "When do you start?",
     min_value=date(2017,1,2),
     max_value=date(2022,3,14),
     step =timedelta(days=7),
     format="YYYY-MM-DD")
st.write("Start time:", start_time)

filter_df = df[df["period_begin"] == str(start_time)]
k = filter_df[['state',opt_column]].groupby(['state'],as_index=False).mean()
k = k[:-1]
st.plotly_chart(geomap_chart(k,opt_column), use_container_width=True)



st.header("Line Chart")
states = df['state'].unique()

option_state = st.selectbox(
    'What is your state?',
    states)

data = df[df['state']==option_state]

option_region = st.selectbox(
    'What is your region type you want to visualize?',
    ('County','Metro'))

if option_region == "County":
    val = 0
else:
    val = 1

data = df[df['region_type_id']==val]

option_city = st.selectbox(
    'What is your region city you want to visualize?',
    data['region_name'].unique())


data = df[df['region_name']==option_city]


option_column = st.selectbox(
    'What is your column attribute you want to visualize?',
    column,key = 123)

data_2 = data[option_column].rolling(12).mean()
data_2.fillna(0)
column.remove('average_adjustment_average_homes_delisted')
column.remove('average_adjustment_average_new_listings')
column.remove('average_adjustment_average_homes_sold')
column.remove('average_adjustment_pending_sales')


fig = go.Figure()
fig.add_scatter(x=data['period_begin'],y=data[option_column],mode="lines",name='1 week avg')

                    
fig.add_scatter(x=data['period_begin'],y=data_2,mode="lines",name='12 week avg')
# fig.update_layout(
#     showlegend=False
# ) 
fig.update_layout(title="Plot for the city "+option_city+" from 2018 to 2019",
                xaxis_title='Staring Date 2018 - 2022',
                yaxis_title=option_column
)

st.plotly_chart(fig, use_container_width= True)



         

decomposition = seasonal_decompose(data[option_column], model='additive', period=52)
fig = plot_seasonal_decompose(decomposition,option_city,option_column,dates=data['period_begin'])
st.plotly_chart(fig, use_container_width=True)


data_bar = df[df["period_begin"] == str(start_time)]
data_bar.sort_values([option_column])
data_bar = data_bar[:15]

fig = px.bar(data_bar, x="region_name", y=option_column,color="region_name")  
st.plotly_chart(fig, use_container_width=True)

# df_cor = df[df['period_begin'] == str(start_time)]
data_bar = data_bar[column]

data_bar = data_bar.fillna(0)

data_cor = data_bar.corr()
fig = px.imshow(data_cor)
fig.update_layout(
    width = 1200, height = 1200,
    )
st.plotly_chart(fig, use_container_width=True)



st.header("Pie Chart")
tmp = df[['region_type_id', 'total_homes_sold']]
fig = px.pie(tmp,names = 'region_type_id',color = 'region_type_id',color_discrete_sequence=px.colors.sequential.RdBu, title = 'Number of Counties and Metros')
fig.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart( fig,use_container_width=True)
fig = px.pie(tmp, values = 'total_homes_sold', names = 'region_type_id',color = 'region_type_id' , color_discrete_sequence=px.colors.sequential.RdBu, title = 'Total no of Households sold in Counties and Metros')
fig.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig,use_container_width=True)
with st.expander('Inference'):
    st.write("""The chart above shows some numbers I picked for you.
        I rolled actual dice for these, so they're *guaranteed* to
        be random.""")