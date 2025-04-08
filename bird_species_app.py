import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import psycopg2
import pandas as pd


connection = psycopg2.connect(
    host="localhost",
    database="MDTm37",
    user="postgres",        
    password="post38"
)
cursor = connection.cursor()
Bird_analysis = st.sidebar.radio('Analysis',['Home','Distribution of Admin unit and habitat type','Temporal Analysis','Spatial analysis',
                                          'Species Analysis','Environmental conditions','Distance and Flyover Trends','Observer trends',
                                          'conservation Insights'])

cursor.execute('SELECT * FROM "Bird_Species";')
data = cursor.fetchall()
df = pd.DataFrame(data,columns=['Admin_Unit_Code','Site_Name','Plot_Name', 'Location_Type', 'Year','Date', 'Start_Time', 'End_Time', 'Observer', 'Visit',
'Interval_Length', 'ID_Method', 'Distance', 'Flyover_Observed', 'Sex','Common_Name', 'Scientific_Name', 'AcceptedTSN', 'NPSTaxonCode',
'AOU_Code', 'PIF_Watchlist_Status', 'Regional_Stewardship_Status','Temperature', 'Humidity', 'Sky', 'Wind', 'Disturbance',
'Initial_Three_Min_Cnt', 'TaxonCode', 'Previously_Obs'])

if Bird_analysis == 'Home':
    st.title('BIRD SPECIES ANALYSIS OF FOREST AND GRASSLAND')
    st.image(r'C:\Users\B.Preethi\Downloads\bald-eagle-flying.jpg')
    st.dataframe(df)

if Bird_analysis == 'Distribution of Admin unit and habitat type': 
    fig = px.histogram(df, x="Admin_Unit_Code", nbins=30,color='Admin_Unit_Code' ,title='Distribution of Species Across Administrative Units')
    st.plotly_chart(fig)
    fig1 = px.histogram(df, x="Location_Type", nbins=30,color='Location_Type' ,title='Distribution of Species Across Location type')
    st.plotly_chart(fig1)

if Bird_analysis == 'Temporal Analysis':
    df['year'] =df['Date'].dt.year
    df['month'] = df['Date'].dt.month
    df['month'] = df['Date'].dt.month_name()
    #define functions to get seasons
    def get_seasons(month):
        if month in ['December','January','February']:
            return 'winter'
        elif month in ['March','April','May']:
            return 'spring'
        elif month in ['June','July','August']:
            return 'summer'
        else:
            return 'Atumn'
        
    df['seasons'] = df['month'].apply(get_seasons)
    fig = px.scatter(df,x='year',y='month',color='month',title="Temporal Distribution of Species by Year and Month")
    st.plotly_chart(fig)
    season_count =df['seasons'].value_counts().sort_index()
    # Create a pie chart to show the distribution of species across different seasons
    fig1 = px.pie(values=season_count,names=season_count.index, title="Species Distribution Across Seasons")            
    st.plotly_chart(fig1)
    # start time 
    df['Start_Time'] = pd.to_datetime(df['Start_Time'], format='%H:%M:%S', errors='coerce')
    df['Start_hour'] = df['Start_Time'].dt.hour
    start_hour_count = df.groupby(['Start_hour','Initial_Three_Min_Cnt']).size().reset_index(name='count')
    fig2 = px.bar(start_hour_count,x='Start_hour',y='count',color='Initial_Three_Min_Cnt',title='start time of bird activity')
    st.plotly_chart(fig2)
    # End time 
    df['End_Time'] = pd.to_datetime(df['End_Time'], format='%H:%M:%S', errors='coerce')
    df['End_hour'] = df['End_Time'].dt.hour
    End_hour_count = df.groupby(['End_hour','Initial_Three_Min_Cnt']).size().reset_index(name='count')
    fig3 = px.bar( End_hour_count,x='End_hour',y='count',color='Initial_Three_Min_Cnt',title='end time in bird activity')
    st.plotly_chart(fig3)
    
if Bird_analysis == 'Spatial analysis':
    # Location vise analysis
    grouped_count=df.groupby(['Location_Type','Admin_Unit_Code']).size().reset_index(name='count')
    fig = px.bar(grouped_count,x='Location_Type',y='count', color='Admin_Unit_Code',title='identify biodiversity hotspots')
    st.plotly_chart(fig)
    # plotlevel analysis
    species_plot= df.groupby('Plot_Name')['Common_Name'].nunique().reset_index(name='species count')
    fig_plotlevel = px.scatter(species_plot, x='Plot_Name', y='species count', title='Species Per Plot')
    st.plotly_chart(fig_plotlevel)

if Bird_analysis=='Species Analysis':
    species_count= df.groupby(['Location_Type','Scientific_Name']).size().reset_index(name='count')
    fig=px.bar(species_count,x='Scientific_Name', y='count',color='Location_Type',title='Species Counts by Location and Species')
    st.plotly_chart(fig)
#Activity Patterns: Check the Interval_Length and ID_Method columns to identify the most common activity types (e.g., Singing)
    activity_count=df['ID_Method'].value_counts()
    fig1 = px.pie(values=activity_count,names=activity_count.index,title='species Activity patterns')
    st.plotly_chart(fig1)

    fig4 = px.bar(df,x='Interval_Length',color_discrete_sequence=['green'],title='Intervel_Lenghth patterns')
    st.plotly_chart(fig4)
    
if Bird_analysis == 'Environmental conditions':
    st.sidebar.header("Filters")
    corr_matrix=df[['Temperature','Humidity']].corr()
    st.dataframe(corr_matrix)
    summary_stats = df[['Temperature','Humidity']].describe()
    st.dataframe(summary_stats )
    
    # Allow user to select a specific bird species
    bird_species = st.sidebar.multiselect(
                "Select Temperature",options=df['Common_Name'].unique(),
                default=df['Common_Name'].unique()[:5] ) # Show first 5 as default
    
    filtered_df = df[df['Common_Name'].isin(bird_species)]

    # Allow user to select a specific observation type
    observation_type = st.sidebar.selectbox(
                        "Select Observation Metric",options=['Initial_Three_Min_Cnt', 'Distance'],index=0 ) # 'Initial_Three_Min_Cnt'
    st.subheader("Temperature")
    
    fig_temp = px.scatter(filtered_df, x='Temperature',y=observation_type,color='Common_Name',hover_data=['Sky', 'Wind'],
                                title=f"'{observation_type}' vs. Temperature",
                                labels={'Initial_Three_Min_Cnt': 'Initial Count', 'Distance': 'Distance (m)'})

    st.plotly_chart(fig_temp)

    # --- Humidity ---
    st.subheader("Humidity")
    fig_humidity = px.scatter(filtered_df,x='Humidity',y=observation_type,color='Common_Name',
    hover_data=['Sky', 'Wind', observation_type],title=f"'{observation_type}' vs. Humidity",
    labels={'Initial_Three_Min_Cnt': 'Initial Count', 'Distance': 'Distance (m)'})

    st.plotly_chart(fig_humidity)
    
    fig_wind = px.box(df,x='Wind',color_discrete_sequence=['purple'],title='Wind condition')
    st.plotly_chart(fig_wind)
    # sky
    fig_sky = px.pie(df,names='Sky',title='Sky condition during observation')
    st.plotly_chart(fig_sky)
    #Disturbance
    fig5=px.histogram(df,x='Disturbance',nbins=30,title='Disturbance frequency')
    st.plotly_chart(fig5)
    
if Bird_analysis == 'Distance and Flyover Trends':
    distance_per_species=df.groupby(['Distance','Common_Name']).size().reset_index(name='count')
    fig_d = px.bar(distance_per_species,x='Distance',y='count',color='Common_Name',title='Distance per species count')
    st.plotly_chart(fig_d)
    # Flyover observer trends
    flyover_count = df['Flyover_Observed'].value_counts().reset_index()
    flyover_count.columns = ['flyover_observed', 'frequency']
    fig_fly = px.pie(flyover_count,
                        names='flyover_observed',
                        values='frequency',
                        title='Flyover Observed Frequency',
                        labels={'flyover_observed': 'Flyover Observed', 'frequency': 'Frequency'})
    st.plotly_chart(fig_fly)

if Bird_analysis == 'Observer trends':
    observer_count = df['Observer'].value_counts()
    fig_obs = px.bar_polar(r=observer_count.values,
                       theta=observer_count.index,
                       title='Observer Trends')
    st.plotly_chart(fig_obs)
    # Species Diversity per Observer
    species_diversity = df.groupby('Observer')['Common_Name'].nunique()
    fig6 =px.bar(x=species_diversity.index, y=species_diversity.values,title='number of species by observer',
                 labels={'x': 'Observer', 'y': 'Species Counts'},color_discrete_sequence=['red'])  
    st.plotly_chart(fig6)
    # visits
    visit_count =df['Visit'].value_counts()
    fig7 = px.line(x=visit_count.index,y=visit_count.values,title='Visit count')
    st.plotly_chart(fig7)
    
if Bird_analysis == 'conservation Insights':
    # true is At-risk species
    st.subheader("conservation of at risk species")

    conserve_risk = df.groupby('PIF_Watchlist_Status')['Common_Name'].value_counts().reset_index(name='count')
    risk_df = conserve_risk [(conserve_risk['PIF_Watchlist_Status']==True)]
    st.dataframe(risk_df)
    fig_conserv = px.scatter(conserve_risk, x='Common_Name', y='count', color='PIF_Watchlist_Status',
                         title='Conservation Status by Common Name',
                         labels={'x': 'Common Name', 'y': 'Number of Species'},
                         hover_name='Common_Name',  # Display common name on hover
                         hover_data=['PIF_Watchlist_Status', 'count'])
    st.plotly_chart(fig_conserv)
    # priority within region
    Priority = df.groupby('Regional_Stewardship_Status')['Common_Name'].value_counts().reset_index(name='count')
    risk_region=Priority[(Priority['Regional_Stewardship_Status']==True)]
    st.dataframe(risk_region)
    fig_p = px.scatter(Priority,x='Common_Name',y='count',color='Regional_Stewardship_Status',
                          title='priority Region')
    st.plotly_chart(fig_p)
    # aou code
    aou_distribution = df['AOU_Code'].value_counts().reset_index(name='species_count')
    fig_aou = px.bar(aou_distribution,x='AOU_Code',y='species_count',title='AOU Distribution')
    st.plotly_chart(fig_aou)
    # aou regional priority
    AOU_conservation = df.groupby('AOU_Code')[['PIF_Watchlist_Status','Regional_Stewardship_Status']].sum().reset_index()
    fig_aou_conserv = px.scatter(AOU_conservation, x='AOU_Code',
                             y=['PIF_Watchlist_Status', 'Regional_Stewardship_Status'],
                             title='Conservation Status within Each AOU Code',
                             labels={'AOU_Code': 'AOU Code', 'value': 'Number of Species'}) 
    st.plotly_chart(fig_aou_conserv)