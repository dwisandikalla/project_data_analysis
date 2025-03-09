import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_weekly_df(df):
    weekly_df = df.resample(rule='W', on='dteday').agg({
        'cnt' : 'sum'
    })
    weekly_df = weekly_df.reset_index()
    return weekly_df

def create_day_df(df):
    day_df = df.groupby(by='dteday').agg({
        'cnt' : 'sum',
        'casual' : 'sum',
        'registered':'sum'
    })
    day_df = day_df.reset_index()
    return day_df

def create_byweathersit_group_df(df):
    byweathersit_group_df = df.groupby(by="weathersit_group").agg({
        'casual' : 'sum',
        'registered' : 'sum',
        'cnt' : 'sum'
    }).reindex(["Clear", "Mist/Fog", "Light Rain/Light Stroms", "Heavy Rain/Snow"]).fillna(0)
    return byweathersit_group_df

def create_byseason_group_df(df):
    byseason_group_df = df.groupby(by='season_group').agg({
        'casual' : 'sum',
        'registered' : 'sum',
        'cnt' : 'sum'
    })
    return byseason_group_df

def create_cluster_df(df):
    q1 = df['temp'].quantile(0.25)
    q3 = df['temp'].quantile(0.75)

    q11 = df['windspeed'].quantile(0.25)
    q31 = df['windspeed'].quantile(0.75)

    def create_cluster(row):
        workingday = row['workingday']
        temp = row['temp']
        windspeed = row['windspeed']

        cluster =' '

        #membuat cluster
        if workingday == 0 and temp < q1 and windspeed < q11:
            return 'cluster 01'
        elif workingday == 0 and temp >= q1 and temp <= q3 and windspeed >= q11 and windspeed <= q31:
            return 'cluster 02'
        elif workingday == 0 and temp > q3 and windspeed > q31:
            return 'cluster 03'
        elif workingday == 1 and temp < q1 and windspeed < q11:
            return 'cluster 04'
        elif workingday == 1 and temp >= q1 and temp <= q3 and windspeed >= q11 and windspeed <= q31:
            return 'cluster 05'
        elif workingday == 1 and temp > q3 and windspeed > q31:
            return 'cluster 06'
        elif workingday == 0 and temp < q1 and windspeed > q31:
            return 'cluster 07'
        elif workingday == 0 and temp > q3 and windspeed < q11:
            return 'cluster 08'
        elif workingday == 1 and temp < q1 and windspeed > q31:
            return 'cluster 09'
        elif workingday == 1 and temp > q3 and windspeed < q11:
            return 'cluster 10'
        elif workingday == 0 and temp >= q1 and temp <= q3 and windspeed < q11:
            return 'cluster 11'
        else:
            return 'cluster 12'
    df['cluster']=df.apply(create_cluster, axis=1)
    return df


all_df = pd.read_csv('Dashboard/days_df.csv')

datetime_columns = ['dteday']
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()
 
with st.sidebar:
    st.sidebar.header('Analisis Penyewaan Sepeda')
    st.image("Dashboard/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Masukkan Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    st.sidebar.header('Dibuat oleh: ')
    st.sidebar.text('Dwi Sandi Kalla')

main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                (all_df["dteday"] <= str(end_date))]

weekly_df = create_weekly_df(main_df)
day_df = create_day_df(main_df)
byweathersit_group_df = create_byweathersit_group_df(main_df)
byseason_group_df = create_byseason_group_df(main_df)
cluster_df = create_cluster_df(main_df)

st.header('Dashboard Analisis Penyewaan Sepeda')

st.subheader('Penyewaan')

col1, col2, col3 = st.columns(3)

with col1:
    total_cnt = weekly_df.cnt.sum()
    st.metric('Total seluruh penyewa', value=total_cnt)
with col2:
    total_casual = day_df.casual.sum()
    st.metric('Penyewa kasual', value=total_casual)
with col3:
    total_regis = day_df.registered.sum()
    st.metric('Penyewa terdaftar', value=total_regis)

st.subheader('Penyewaan Mingguan')

fig_weekly, ax_weekly = plt.subplots(figsize=(16,8))
ax_weekly.set_title('Tren Penyewaan Mingguan', fontsize=30, loc='left')
ax_weekly.plot(weekly_df['dteday'], weekly_df['cnt'], marker='o', color='blue')
ax_weekly.tick_params(axis='y', labelsize=20)
ax_weekly.tick_params(axis='x', labelsize=15)

st.pyplot(fig_weekly)

st.subheader('Penyewaan Harian')

fig_day, ax_day = plt.subplots(figsize=(16,8))
ax_day.set_title('Tren Penyewaan Harian', fontsize=30, loc='left')
ax_day.plot(day_df['dteday'], day_df['cnt'], marker='o', color='blue')
ax_day.tick_params(axis='y', labelsize=20)
ax_day.tick_params(axis='x', labelsize=15)

st.pyplot(fig_day)

st.subheader('Total Penyewaan Sepeda Berdasarkan Kondisi Cuaca')

fig, ax = plt.subplots(nrows = 1, ncols = 3, figsize=(35,15))

colors = ['blue', 'red', 'red', 'red']

sns.barplot(x=byweathersit_group_df.index, y=byweathersit_group_df['casual'], ax=ax[0], palette=colors)
ax[0].set_title('Berdasarkan Casual', fontsize=20)
ax[0].set_xlabel('Cuaca', labelpad=20, fontsize=15)
ax[0].set_ylabel('Jumlah Penyewa', labelpad=20, fontsize=15)
ax[0].tick_params(axis='x', labelsize=15)
ax[0].tick_params(axis='y', labelsize=15)

sns.barplot(x=byweathersit_group_df.index, y=byweathersit_group_df['registered'], ax=ax[1], palette=colors)
ax[1].set_title('Berdasarkan Registered', fontsize=20)
ax[1].set_xlabel('Cuaca', labelpad=20, fontsize=15)
ax[1].set_ylabel('Jumlah Penyewa', labelpad=20, fontsize=15)
ax[1].tick_params(axis='x', labelsize=15)
ax[1].tick_params(axis='y', labelsize=15)

sns.barplot(x=byweathersit_group_df.index, y=byweathersit_group_df['cnt'], ax=ax[2], palette=colors)
ax[2].set_title('Berdasarkan Total Penyewa', fontsize=20)
ax[2].set_xlabel('Cuaca', labelpad=20, fontsize=15)
ax[2].set_ylabel('Jumlah Penyewa', labelpad=20, fontsize=15)
ax[2].tick_params(axis='x', labelsize=15)
ax[2].tick_params(axis='y', labelsize=15)

st.pyplot(fig)

st.subheader('Total Penyewaan Sepeda Berdasarkan Musim')

fig_1, ax = plt.subplots(nrows = 1, ncols = 3, figsize=(35,15))

sns.barplot(x='season_group', y='casual', data=byseason_group_df, ax=ax[0], palette=colors)
ax[0].set_title('Berdasarkan Casual', fontsize=20)
ax[0].set_xlabel('Musim', labelpad=20, fontsize=15)
ax[0].set_ylabel('Jumlah Penyewa', labelpad=20, fontsize=15)
ax[0].tick_params(axis='x', labelsize=12)
ax[0].tick_params(axis='y', labelsize=12)

sns.barplot(x='season_group', y='registered', data=byseason_group_df, ax=ax[1], palette=colors)
ax[1].set_title('Berdasarkan Registered', fontsize=20)
ax[1].set_xlabel('Musim', labelpad=20, fontsize=15)
ax[1].set_ylabel('Jumlah Penyewa', labelpad=20, fontsize=15)
ax[1].tick_params(axis='x', labelsize=12)
ax[1].tick_params(axis='y', labelsize=12)

sns.barplot(x='season_group', y='cnt', data=byseason_group_df, ax=ax[2], palette=colors)
ax[2].set_title('Berdasarkan Total Penyewa', fontsize=20)
ax[2].set_xlabel('Musim', labelpad=20, fontsize=15)
ax[2].set_ylabel('Jumlah Penyewa', labelpad=20, fontsize=15)
ax[2].tick_params(axis='x', labelsize=12)
ax[2].tick_params(axis='y', labelsize=12)

plt.suptitle('Jumlah Penyewa Berdasarkan Musim',y=1,fontsize=25)
st.pyplot(fig_1)

st.subheader('Clusterisasi Berdasarkan Workingday, Temp, Windspeed')

fig_2, ax = plt.subplots(nrows=3, figsize=(35, 50))

sns.scatterplot(x='temp', y='cnt', hue='cluster', data=cluster_df, ax=ax[0])
ax[0].set_title('Scatterplot Clustering (Temp vs. cnt)', fontsize=20)
ax[0].set_xlabel('Temperature', labelpad=20, fontsize=25)
ax[0].set_ylabel('Jumlah Penyewa', labelpad=20, fontsize=25)
ax[0].tick_params(axis='x', labelsize=20)
ax[0].tick_params(axis='y', labelsize=20)
ax[0].legend(title='Cluster', fontsize=20)

sns.scatterplot(x='workingday', y='cnt', hue='cluster', data=cluster_df, ax=ax[1])
ax[1].set_title('Scatterplot Clustering (Workingday vs. cnt)', fontsize=20)
ax[1].set_xlabel('Workingday', labelpad=20, fontsize=25)
ax[1].set_ylabel('Jumlah Penyewa', labelpad=20, fontsize=25)
ax[1].tick_params(axis='x', labelsize=20)
ax[1].tick_params(axis='y', labelsize=20)
ax[1].legend(title='Cluster', fontsize=20)

sns.scatterplot(x='windspeed', y='cnt', hue='cluster', data=cluster_df, ax=ax[2])
ax[2].set_title('Scatterplot Clustering (Windspeed vs. cnt)', fontsize=20)
ax[2].set_xlabel('Windspeed', labelpad=20, fontsize=25)
ax[2].set_ylabel('Jumlah Penyewa', labelpad=20, fontsize=25)
ax[2].tick_params(axis='x', labelsize=20)
ax[2].tick_params(axis='y', labelsize=20)
ax[2].legend(title='Cluster', fontsize=20)

plt.tight_layout()

st.pyplot(fig_2)
