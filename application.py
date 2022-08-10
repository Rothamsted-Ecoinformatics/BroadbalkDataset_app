#https://www.youtube.com/watch?v=Sb0A9i6d320


import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='streamlit tutorial',
                   page_icon=':herb:',
                   layout='wide'
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 400px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 500px;
        margin-left: -500px;
        margin-up: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache
def get_data_csv():
    df = pd.read_csv('Broadbalk Dataset/complete_dataset.csv')
    df = df.replace('*',np.nan)
    df['sub_plot'] = df['sub_plot'].replace(np.nan, '')
    df['grain'] = pd.to_numeric(df['grain'], errors= 'coerce')
    df['straw'] = pd.to_numeric(df['straw'], errors= 'coerce')
    df['plot'] = df['plot']
    df['complete_plot'] = df['plot'].astype(str) + ' ' + df['sub_plot']
    df = df.sort_values(by=["plot", "sub_plot", "harvest_year"])
    return df
df = get_data_csv()

@st.cache
def download_csv(df):
    return df.to_csv().encode('utf-8')

from datetime import date
from datetime import timedelta

today = date.today()
yesterday = today - timedelta(days = 1)
tomorrow = today + timedelta(days = 1)

today_date = today.strftime("%Y-%m-%d")
yesterday_date = yesterday.strftime("%Y-%m-%d")
tomorrow_date = tomorrow.strftime("%Y-%m-%d")

def get_temp_data_csv(site):
    dfmax = pd.read_csv('daily/daily_weather/maxmin_csv/d28_' + site + '_Maximum.csv')
    dfmax = dfmax.groupby(by=['ValidDate']).last().reset_index()
    dfmax = dfmax[['average']]
    dfmax.rename(columns={'average':'maxtemp'}, inplace=True)
    dfmin = pd.read_csv('daily/daily_weather/maxmin_csv/d28_' + site + '_Minimum.csv')
    dfmin = dfmin.groupby(by=['ValidDate']).last().reset_index()
    dfmin = dfmin[['ValidDate', 'average']]
    dfmin.rename(columns={'average':'mintemp'}, inplace=True)
    df = pd.concat([dfmin, dfmax], axis=1, join='inner')
    return df

def get_rainfall_data_csv(site, date):
    df_rainfall = pd.read_csv('daily/daily_weather/csv/d10_'+ site + '_' + date + '_Rainfall.csv')
    df_rainfall = df_rainfall[['ValidDate', 'average']]
    df_rainfall = df_rainfall.groupby(by=['ValidDate']).max().reset_index()
    return df_rainfall

# --- SIDEBAR ---

st.sidebar.header("Links")
url = "http://www.era.rothamsted.ac.uk/dataset/rbk1/01-OAWWYields"
st.sidebar.info("**Data source:** [Era@Rothamsted](%s)" % url)

st.sidebar.header('Filter Here')

all_plots = st.sidebar.checkbox('Select all plots', value=True)
if all_plots == True:
    df_plot = df
else:
    plot = st.sidebar.multiselect(
        'Selected plots:',
        options=df['complete_plot'].unique(),
        default=[])
    df_plot = df.query("complete_plot == @plot")
    st.sidebar.markdown('##')
    
    

if df_plot.empty:
    correct = False
else:
    max_year = int(df_plot['harvest_year'].max())
    min_year = int(df_plot['harvest_year'].min())

    year = st.sidebar.slider('Pick a period', min_year, max_year, (min_year, max_year), step=1)
    down_year = year[0]
    up_year = year[1]
    if (down_year != up_year):
        st.sidebar.write(f'from {down_year} to {up_year}')
    else:
        st.sidebar.write(f'in {up_year}')
    df_year = df_plot.query('harvest_year >= @down_year & harvest_year <= @up_year')
    st.sidebar.markdown('##')
    
    
    st.sidebar.subheader("Selected fertilizers")
    fertilizer_list = []
    check_list = []
    checked_fert = []
    df_fertilizer = df_year.sort_values(by=['fertilizer_code'])
    df_fertilizer = df_fertilizer['fertilizer_code']
    for fert in df_fertilizer.unique():
        fertilizer_list.append(fert)
        check_list.append(st.sidebar.checkbox(fert, True))
    for index in range(len(fertilizer_list)):
        if check_list[index] == True:
            checked_fert.append(fertilizer_list[index])
            
            
            
            
    df_selection = df_year.query("fertilizer_code == @checked_fert")
        
    if df_selection.empty:
        st.write("## Please select a fertilizer")
        correct = False
    else:
        correct = True   

# --- MAINPAGE ---

st.title(':sunny: Weather')

selectbox = st.selectbox('Select a Site',
                         ('BroomsBarn', 'Cranwell'))
site = selectbox
df_temp = get_temp_data_csv(site)
df_rainfall = get_rainfall_data_csv(site, today_date)

today_max = df_temp.loc[df_temp['ValidDate'] == today_date,['maxtemp']]
today_min = df_temp.loc[df_temp['ValidDate'] == today_date,['mintemp']]
yesterday_max = df_temp.loc[df_temp['ValidDate'] == yesterday_date,['maxtemp']]
yesterday_min = df_temp.loc[df_temp['ValidDate'] == yesterday_date,['mintemp']]
tomorrow_max = df_temp.loc[df_temp['ValidDate'] == tomorrow_date,['maxtemp']]
tomorrow_min = df_temp.loc[df_temp['ValidDate'] == tomorrow_date,['mintemp']]
today_rainfall = df_rainfall.loc[df_rainfall['ValidDate'] == today_date,['average']]
tomorrow_rainfall = df_rainfall.loc[df_rainfall['ValidDate'] == tomorrow_date,['average']]

st.write('### Today')
col1, col2, col3 = st.columns(3)
col1.metric("Minimum", 
            str(today_min.values[0][0]) + " °C",
            str(round(today_min.values[0][0] - yesterday_min.values[0][0], 1)) + " °C",
            delta_color='off')
col2.metric("Maximum",
            str(today_max.values[0][0]) + " °C",
            str(round(today_max.values[0][0] - yesterday_max.values[0][0], 1)) + " °C",
            delta_color='off')
col3.metric("Rainfall",
            str(today_rainfall.values[0][0]))

st.write('### Tomorrow')
col1, col2, col3 = st.columns(3)
col1.metric("Minimum", 
            str(tomorrow_min.values[0][0]) + " °C",
            str(round(tomorrow_min.values[0][0] - today_min.values[0][0], 1)) + " °C",
            delta_color='off')
col2.metric("Maximum",
            str(tomorrow_max.values[0][0]) + " °C",
            str(round(tomorrow_max.values[0][0] - today_max.values[0][0], 1)) + " °C",
            delta_color='off')
col3.metric("Rainfall",
            str(tomorrow_rainfall.values[0][0]))

st.markdown('##')


if (correct == True):
    st.title(':seedling: DataSet')

# TOP

if (correct == True):
    search = False
    nb_collect = int(df_selection['grain'].count())
    max_grain_size = float(df_selection['grain'].max())
    average_biomass = float((df_selection['grain'] + df_selection['straw']).mean())
    star_grain = ':star:' * (int(max_grain_size/2)+1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Filtered Results')
        st.subheader(nb_collect)
    with col2:
        st.subheader('Maximum Grain Size')
        st.subheader(f'{max_grain_size} {star_grain}')
    st.markdown('---')
    
    #st.dataframe(df_selection)
    
    with st.container():
        average = st.radio("Average by:",
                         ['Each year', '5 years', '10 years'],
                         horizontal=True)
        shape = st.radio("Shape style:",
                         ['linear', 'spline'],
                         horizontal=True)
        
        if average == 'Each year':
            main_plot = px.line(data_frame=df_selection,
                                x='harvest_year',
                                y='grain', color='complete_plot', 
                                title='<b>First Chart</b>',
                                range_y=[0, max_grain_size + 1],
                                range_x=[down_year, up_year],
                                line_group="plot", hover_name="plot",
                                line_shape=shape, render_mode="svg"
            )
            st.plotly_chart(main_plot)
        elif average == '5 years':
            df_interval = df_selection.copy()
            df_interval['plot'] = df_interval['plot'].astype(float)
            df_interval['five_years'] = (df_interval['harvest_year'].astype(int)//5)*5
            df_interval['plot_5y'] = df_interval['five_years'].astype(str) + '_' + df_interval['complete_plot']
            df_5y = df_interval['grain'].groupby(by=df_interval['plot_5y']).mean().rename('average yield')
            df_interval = pd.merge(df_interval, df_5y, on='plot_5y')

            df_group = df_interval.groupby(by=['plot_5y']).first().sort_values(by=['plot', 'sub_plot']).reset_index()
            main_plot = px.line(data_frame=df_group,
                                x='harvest_year',
                                y='average yield', color='complete_plot', 
                                title='<b>First Chart</b>',
                                range_y=[0, max_grain_size + 1],
                                range_x=[down_year, up_year],
                                line_group="plot", hover_name="plot",
                                line_shape=shape, render_mode="svg"
            )
            st.plotly_chart(main_plot)
        else:
            df_interval = df_selection.copy()
            df_interval['plot'] = df_interval['plot'].astype(float)
            df_interval['ten_years'] = (df_interval['harvest_year'].astype(int)//10)*10
            df_interval['plot_10y'] = df_interval['ten_years'].astype(str) + '_' + df_interval['complete_plot']
            df_10y = df_interval['grain'].groupby(by=df_interval['plot_10y']).mean().rename('average yield')
            df_interval = pd.merge(df_interval, df_10y, on='plot_10y')

            df_group = df_interval.groupby(by=['plot_10y']).first().sort_values(by=['plot', 'sub_plot']).reset_index()
            main_plot = px.line(data_frame=df_group,
                                x='harvest_year',
                                y='average yield', color='complete_plot', 
                                title='<b>First Chart</b>',
                                range_y=[0, max_grain_size + 1],
                                range_x=[down_year, up_year],
                                line_group="plot", hover_name="plot",
                                line_shape=shape, render_mode="svg"
            )
            st.plotly_chart(main_plot)
        
        grain_size_by_fertilizer = (
            df_selection.groupby(by=['fertilizer_code']).mean()[['grain']].sort_values(by='grain')
        )
        
        grain_size_by_fertilizer['grain'] = grain_size_by_fertilizer.round(2)
        
        
        fig_grain = px.bar(
            grain_size_by_fertilizer,
            x='grain',
            y=grain_size_by_fertilizer.index,
            labels={'grain': "Average grain size"},
            orientation='h',
            title="<b>Second Chart</b>",
            #color_discrete_sequence=[],
            template='plotly_white'
        )
        
        fig_grain.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=(dict(showgrid=False))
        )
        
        st.plotly_chart(fig_grain)

    
    with st.expander('Dataframe'):
        order = st.radio("Order by:",
                         ['Plot name', 'Harvest year', 'Fertilizer', 'Cultivar', 'Grain size'],
                         horizontal=True)
        
        if order == 'Plot name':
            df_show = df_selection[['complete_plot', 'harvest_year', 'fertilizer_code', 'cultivar', 'grain']].copy()
            df_show = df_show.sort_values(by=['complete_plot', 'harvest_year'])
        elif order == 'Harvest year':
            df_show = df_selection[['harvest_year', 'complete_plot', 'fertilizer_code', 'cultivar', 'grain']].copy()
            df_show = df_show.sort_values(by=['harvest_year', 'complete_plot'])
        elif order == 'Fertilizer':
            df_show = df_selection[['fertilizer_code', 'complete_plot', 'harvest_year', 'cultivar', 'grain']].copy()
            df_show = df_show.sort_values(by=['fertilizer_code', 'complete_plot', 'harvest_year'])
        elif order == 'Cultivar':
            df_show = df_selection[['cultivar', 'complete_plot', 'harvest_year', 'fertilizer_code', 'grain']].copy()
            df_show = df_show.sort_values(by=['cultivar', 'complete_plot', 'harvest_year'])
        elif order == 'Grain size':
            df_show = df_selection[['grain', 'complete_plot', 'harvest_year', 'fertilizer_code', 'cultivar']].copy()
            df_show = df_show.sort_values(by=['complete_plot', 'harvest_year'])
            desc = st.checkbox("Descending", False)
            df_show = df_show.sort_values(by=['grain'], ascending= not desc)
        df_show = df_show.reset_index(drop=True)
        df_show = df_show.astype(str)
        st.download_button("Download",
                           data=download_csv(df_show),
                           file_name='Filtered_Dataset.csv',
                           mime='text/csv')
        st.table(df_show)

















