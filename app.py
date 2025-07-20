import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
   page_title="Charlottesville Housing Crisis Analysis",
   page_icon="🏘️",
   layout="wide"
)

# Custom CSS
st.markdown("""
<style>
   /* General text styling */
   .stMarkdown p, .stMarkdown li, .stMarkdown {
       color: #6c757d;
   }
   
   /* Headers in blue */
   h1, h2, h3, h4, h5, h6,
   .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
   .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
       color: #1f77b4 !important;
   }
   
   /* Bold text and highlights in blue */
   .stMarkdown strong, .stMarkdown b {
       color: #1f77b4 !important;
   }
   
   /* Metric labels in gray, values in blue */
   [data-testid="metric-container"] label {
       color: #6c757d !important;
   }
   [data-testid="metric-container"] [data-testid="stMetricValue"] {
       color: #1f77b4 !important;
   }
   
   /* Tab text */
   .stTabs [data-baseweb="tab-list"] {
       color: #6c757d;
   }
   
   .impact-box {
       background-color: #f8f9fa;
       padding: 20px;
       border-radius: 10px;
       margin: 10px 0;
       border-left: 5px solid #dc3545;
       color: #6c757d;
   }
   .impact-box h3, .impact-box h4, .impact-box b {
       color: #1f77b4 !important;
   }
   
   .positive-box {
       background-color: #e7f3ff;
       padding: 20px;
       border-radius: 10px;
       margin: 10px 0;
       border-left: 5px solid #1f77b4;
       color: #6c757d;
   }
   .positive-box h3, .positive-box h4, .positive-box b {
       color: #1f77b4 !important;
   }
   
   /* Dataframe text */
   .stDataFrame {
       color: #6c757d;
   }
   
   /* Info boxes */
   .stAlert {
       color: #6c757d;
   }
   
   /* Input labels */
   .stTextInput label {
       color: #6c757d !important;
   }
   
   /* Selectbox labels */
   .stSelectbox label {
       color: #6c757d !important;
   }
</style>
""", unsafe_allow_html=True)

# Title
st.title("Charlottesville Housing Crisis Analysis")
st.markdown("Understanding the City of Charlottesville's Affordable Housing Crisis")
st.markdown("**Introduction:** Since I moved to Charlottesville in 2024 I kept hearing about the housing crisis and its affect on the community. I wanted to understand the data behind these claims and see how the housing market has changed over time. I also wanted to see who owns most in the city as and how big is theis crisis. I decided to create this dashboard to visualize the data and tell the story of how the housing market has changed in Charlottesville. I hope this dashboard will help raise awareness about the housing crisis and spark discussions about possible solutions.")
st.markdown("Data sources: City of Charlottesville Open Data Portal")
st.markdown("Last updated: June 2024")

# Load all data
@st.cache_data(show_spinner=False)
def load_all_data():
   try:
       data = {
           'sales': pd.read_csv('Real_Estate_Sales.csv'),
           'all_assessments': pd.read_csv('Real_Estate_All_Assessments.csv'),
           'parcel_boundary_details': pd.read_csv('Parcel_Boundary_Area_Details.csv')
       }
       return data
   except Exception as e:
       st.error(f"Error loading data: {str(e)}")
       return None

# Process sales data
@st.cache_data
def process_sales_data(sales_df):
   sales = sales_df.copy()
   sales['SaleDate'] = pd.to_datetime(sales['SaleDate'], format='%Y/%m/%d %H:%M:%S+00', errors='coerce')
   sales = sales.dropna(subset=['SaleDate'])
   sales['Year'] = sales['SaleDate'].dt.year
   sales['Month'] = sales['SaleDate'].dt.month
   sales = sales[(sales['SaleAmount'] > 10000)] # Filter out sales below $10,000 AS these are likely non-market transactions
   return sales

# Load data
data = load_all_data()

if data:
   sales_processed = process_sales_data(data['sales'])
   
   # Community Impact Overview
   st.header("Housing Affordability Crisis Overview")
   
   # Calculate key community metrics
   median_income = 69829  # 2023 median household income in Charlottesville
   affordable_home_price = median_income * 3  # Traditional affordability ratio
   Last_Year_median_price = sales_processed[sales_processed['Year'] >= 2024]['SaleAmount'].median()
   affordability_gap = Last_Year_median_price - affordable_home_price
   
   # Recent price changes
   recent_prices = sales_processed[sales_processed['Year'] >= 2024]['SaleAmount'].median()
   older_prices = sales_processed[sales_processed['Year'] >= 2020]['SaleAmount'].median()
   price_increase_pct = ((recent_prices - older_prices) / older_prices) * 100
   
   col1, col2, col3, col4 = st.columns(4)
   with col1:
       st.metric(
           "Median Home Price (2024)",
           f"${Last_Year_median_price:,.0f}",
           f"↑ {price_increase_pct:.0f}% vs 2020",
           delta_color="inverse" 
       )
   with col2:
       st.metric(
           "Affordable Price \n (Based on median income in 2023.)",
           f"${affordable_home_price:,.0f}",
           f"Gap: ${affordability_gap:,.0f}",
           delta_color="off"
       )
   with col3:
       homes_affordable = len(sales_processed[(sales_processed['Year'] >= 2020) & 
                                             (sales_processed['SaleAmount'] <= affordable_home_price)])
       total_recent_sales = len(sales_processed[sales_processed['Year'] >= 2020])
       affordable_pct = (homes_affordable / total_recent_sales * 100) if total_recent_sales > 0 else 0
       st.metric(
           "Affordable Home Sales %",
           f"{affordable_pct:.1f}%",
           "Since 2020",
           delta_color="off"
       )
   with col4:
       income_needed = Last_Year_median_price / 3  # Income needed for median home
       st.metric(
           "Income Needed for Median Home",
           f"${income_needed:,.0f}",
           f"{income_needed/median_income:.1f}x median income",
           delta_color="off"
       )
   
   #Start the story
   st.header("The Story of Charlottesville's Housing Crisis")
   
   
   st.markdown("""
   ### A Community Transformed
   Let's explore how this happened, starting with the numbers that tell our story...
   The median property value in Charlottesville was \$**460,000** in **2023**, which is **1.5** times larger than the national average of \$**303,400**. Between **2021** and **2024** the median property value increased from \$**395,000** to \$**525,000**, a **32.9%** increase. The homeownership rate in Charlottesville, VA is **43.7%**, which is lower than the national average of **65%**.
   """)
   
   # Price increase narrative
   yearly_stats = sales_processed.groupby('Year')['SaleAmount'].agg(['median', 'mean', 'count']).reset_index()
   yearly_stats.columns = ['Year', 'MedianPrice', 'AveragePrice', 'Sales']
   yearly_stats = yearly_stats[yearly_stats['Year'] >= 2000]
   
   # Calculate key statistics for the narrative
   price_2000 = yearly_stats[yearly_stats['Year'] == 2000]['MedianPrice'].iloc[0] if len(yearly_stats[yearly_stats['Year'] == 2000]) > 0 else 0
   price_2024 = yearly_stats[yearly_stats['Year'] == 2024]['MedianPrice'].iloc[0] if len(yearly_stats[yearly_stats['Year'] == 2024]) > 0 else 0
   total_increase = ((price_2024 - price_2000) / price_2000 * 100) if price_2000 > 0 else 0
   
   st.markdown(f"""
   
   In the year 2000, the median home in Charlottesville sold for \$**{price_2000:,.0f}**. 
   Fast forward to 2024, and that same typical home now costs **${price_2024:,.0f}**.
   
   That's an increase of **{total_increase:.0f}%** - far outpacing income growth in the community.
   """)
   
   # The Growing Affordability Gap Chart
   st.subheader("The Growing Affordability Gap")
   
   # Calculate 75th percentile
   percentile_75 = sales_processed.groupby('Year')['SaleAmount'].quantile(0.75).reset_index()
   percentile_75.columns = ['Year', 'Percentile75']
   yearly_stats = yearly_stats.merge(percentile_75, on='Year', how='left')
   
   # Income mapping
   income_by_year = {
       2000: 32903, 2001: 33223, 2002: 32785, 2003: 31363, 2004: 31246,
       2005: 33041, 2006: 35147, 2007: 37195, 2008: 42948, 2009: 39030,
       2010: 42240, 2011: 43980, 2012: 44535, 2013: 44601, 2014: 47218,
       2015: 49775, 2016: 50727, 2017: 54739, 2018: 58933, 2019: 59471,
       2020: 59598, 2021: 63470, 2022: 67177, 2023: 69829, 2024: None
   }
   
   yearly_stats['MedianIncome'] = yearly_stats['Year'].map(income_by_year)
   yearly_stats['AffordablePrice'] = yearly_stats['MedianIncome'] * 3
   
   # Calculate the price increase from 2020 to 2024
   price_2020 = yearly_stats[yearly_stats['Year'] == 2020]['MedianPrice'].iloc[0] if len(yearly_stats[yearly_stats['Year'] == 2020]) > 0 else 0
   price_2024 = yearly_stats[yearly_stats['Year'] == 2024]['MedianPrice'].iloc[0] if len(yearly_stats[yearly_stats['Year'] == 2024]) > 0 else 0
   recent_increase = ((price_2024 - price_2020) / price_2020 * 100) if price_2020 > 0 else 0
   
   # Create the figure
   fig_afford = go.Figure()
   
   # Add median price line 
   for i in range(len(yearly_stats)):
       if i > 0:
           # Determine color based on year
           if yearly_stats.iloc[i]['Year'] <= 2021:
               line_color = 'lightgray'
           else:
               line_color = '#1f77b4'
           
           # Draw line segment
           fig_afford.add_trace(go.Scatter(
               x=[yearly_stats.iloc[i-1]['Year'], yearly_stats.iloc[i]['Year']],
               y=[yearly_stats.iloc[i-1]['MedianPrice'], yearly_stats.iloc[i]['MedianPrice']],
               mode='lines',
               line=dict(color=line_color, width=3),
               showlegend=False,
               hoverinfo='skip'
           ))
   
   # Add average price line 
   for i in range(len(yearly_stats)):
       if i > 0:
           # Determine color based on year
           if yearly_stats.iloc[i]['Year'] <= 2021:
               line_color = 'darkgray'
           else:
               line_color = '#ff7f0e'  
           
           # Draw line segment
           fig_afford.add_trace(go.Scatter(
               x=[yearly_stats.iloc[i-1]['Year'], yearly_stats.iloc[i]['Year']],
               y=[yearly_stats.iloc[i-1]['AveragePrice'], yearly_stats.iloc[i]['AveragePrice']],
               mode='lines',
               line=dict(color=line_color, width=3),
               showlegend=False,
               hoverinfo='skip'
           ))
   
   # Add 75th percentile line 
   for i in range(len(yearly_stats)):
       if i > 0:
           # Determine color based on year
           if yearly_stats.iloc[i]['Year'] <= 2021:
               line_color = 'darkgray'
           else:
               line_color = '#838530'
           
           # Draw line segment
           fig_afford.add_trace(go.Scatter(
               x=[yearly_stats.iloc[i-1]['Year'], yearly_stats.iloc[i]['Year']],
               y=[yearly_stats.iloc[i-1]['Percentile75'], yearly_stats.iloc[i]['Percentile75']],
               mode='lines',
               line=dict(color=line_color, width=3),
               showlegend=False,
               hoverinfo='skip'
           ))
   
   # Add markers only for post-2021 data
   post_2021_data = yearly_stats[yearly_stats['Year'] > 2021]
   
   fig_afford.add_trace(go.Scatter(
       x=post_2021_data['Year'],
       y=post_2021_data['MedianPrice'],
       mode='markers',
       name='Median Home Price',
       marker=dict(size=8, color='#1f77b4'),
       hovertemplate='%{y:$,.0f}<extra></extra>'
   ))
   
   fig_afford.add_trace(go.Scatter(
       x=post_2021_data['Year'],
       y=post_2021_data['AveragePrice'],
       mode='markers',
       name='Average Home Price',
       marker=dict(size=8, color='#ff7f0e'),
       hovertemplate='%{y:$,.0f}<extra></extra>'
   ))
   
   fig_afford.add_trace(go.Scatter(
       x=post_2021_data['Year'],
       y=post_2021_data['Percentile75'],
       mode='markers',
       name='75th Percentile Price',
       marker=dict(size=8, color='#838530'),
       hovertemplate='%{y:$,.0f}<extra></extra>'
   ))
   
   # Affordable price 
   fig_afford.add_trace(go.Scatter(
       x=yearly_stats['Year'], 
       y=yearly_stats['AffordablePrice'],
       mode='lines+markers',
       name='Affordable Price (3x Median Income)',
       line=dict(color='green', width=3, dash='dash')
   ))
   
   #  vertical line at 2021 
   fig_afford.add_vline(
       x=2021,
       line_dash="dash",
       line_color="gray",
       line_width=2
   )
   
   #  annotation about the recent increase
   fig_afford.add_annotation(
       x=2021,
       y=max(yearly_stats['Percentile75'].max(), yearly_stats['MedianPrice'].max()) * 0.95,
       text=f"<b>Post-pandemic surge:</b><br>Home prices increased {recent_increase:.0f}%<br>in just 4 years (2020-2024).<br>This dramatic spike has made<br>homeownership unattainable<br>for most local families.",
       showarrow=True,
       arrowhead=2,
       arrowsize=1,
       arrowwidth=2,
       arrowcolor="gray",
       ax=-100,
       ay=-60,
       bgcolor="rgba(255,255,255,0.9)",
       bordercolor="rgba(0,0,0,0)",  
       borderwidth=0,
       font=dict(size=12, color="gray")
   )
   
   fig_afford.update_layout(
       title=dict(
           text='Housing Prices vs. What Families Can Afford',
           font=dict(color='#1f77b4', size=20)
       ),
       yaxis_title='Price ($)',
       yaxis=dict(
           range=[0, max(yearly_stats['Percentile75'].max(), yearly_stats['AveragePrice'].max()) * 1.1],
           tickprefix='$',
           ticksuffix='',
           showgrid=True,
           gridcolor='lightgray'
       ),
       xaxis_title='Year',
       hovermode='x unified',
       height=600,
       showlegend=True,
       font=dict(color='#6c757d')
   )
   st.plotly_chart(fig_afford, use_container_width=True)
   
   # Assessment Values Over Time
   st.subheader("Property Assessment Values Over Time")
   
   # Process assessment data
   all_assessments = data['all_assessments'].copy()
   assessment_stats = all_assessments.groupby('TaxYear')['TotalValue'].agg(['median', 'mean']).reset_index()
   assessment_stats.columns = ['Year', 'MedianAssessment', 'AverageAssessment']
   assessment_stats = assessment_stats[assessment_stats['Year'] >= 2000]
   
   # Create the assessment chart
   fig_assessment = go.Figure()
   
   #  median assessment line
   fig_assessment.add_trace(go.Scatter(
       x=assessment_stats['Year'],
       y=assessment_stats['MedianAssessment'],
       mode='lines+markers',
       name='Median Assessment Value',
       line=dict(color='#1f77b4', width=3),
       marker=dict(size=6)
   ))
   
   #  average assessment line
   fig_assessment.add_trace(go.Scatter(
       x=assessment_stats['Year'],
       y=assessment_stats['AverageAssessment'],
       mode='lines+markers',
       name='Average Assessment Value',
       line=dict(color='#ff7f0e', width=3),
       marker=dict(size=6)
   ))
   
   # Calculate assessment increase
   assessment_2021 = assessment_stats[assessment_stats['Year'] == 2021]['MedianAssessment'].iloc[0] if len(assessment_stats[assessment_stats['Year'] == 2021]) > 0 else 0
   assessment_latest = assessment_stats.iloc[-1]['MedianAssessment']
   assessment_increase = ((assessment_latest - assessment_2021) / assessment_2021 * 100) if assessment_2021 > 0 else 0

    #  vertical line at 2021 
   fig_assessment.add_vline(
       x=2021,
       line_dash="dash",
       line_color="gray",
       line_width=2
   )


   #  annotation 
   fig_assessment.add_annotation(
    x=2021,
    y=assessment_stats['AverageAssessment'].max() * 0.85,
    text=f"<b>Assessment Growth:</b><br>Median assessments increased<br>{assessment_increase:.0f}% since 2021.<br>This dramatic increase affects<br>property taxes and overall<br>housing affordability.",
    showarrow=True,
    arrowhead=2,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="gray",
    ax=-100,
    ay=-60,
    bgcolor="rgba(255,255,255,0.9)",
    bordercolor="rgba(0,0,0,0)",
    borderwidth=0,
    font=dict(size=12, color="gray")
)

   fig_assessment.update_layout(
    title=dict(
        text='Median and Average Property Assessment Values Over Time',
        font=dict(color='#1f77b4', size=20)
    ),
    yaxis_title='Assessment Value ($)',
    yaxis=dict(
        tickprefix='$',
        showgrid=True,
        gridcolor='lightgray'
    ),
    xaxis_title='Year',
    hovermode='x unified',
    height=500,
    showlegend=True,
    font=dict(color='#6c757d')
    )

   st.plotly_chart(fig_assessment, use_container_width=True)

   # Explanation of the charts
   st.markdown("""
   ### 📊 What These Charts Tell Us

   **Why Look at Multiple Metrics?**  
     Both charts reveal a consistent story: whether you examine actual sales prices or the city's annual property assessments, home values have skyrocketed especially after COVID-19.

   **The Numbers Don't Lie:**
   - **Sales prices** increased by **41%** (median) from 2020 to 2024
   - **Assessment values** increased by **43%** (median) over the same period
   - Both show the steepest increases occurring after 2021

   **Why Focus on Median and 75th Percentile Instead of Average?**
   
    The **median** provides a more accurate picture of what a typical home costs because it's not skewed by extreme values. When a few luxury mansions sell for millions or distressed properties sell far below market, the average gets pulled up or down dramatically that's why you see the average line jumping around more than the median.

   The **75th percentile** shows us the upper-middle range of the market these aren't the most expensive homes, but they represent properties that are increasingly out of reach for most families.

   **The Bottom Line:**
   No matter which metric you examine median sales, average sales, or city assessments they all point to the same troubling reality: home values are rising far faster than incomes, making homeownership increasingly impossible for local families.
   """)
   
   # Sales Activity by Year
   st.subheader("Sales Activity Over Time")
   
   #  sales count by year since 2000
   sales_by_year = sales_processed[sales_processed['Year'] >= 2000].groupby('Year').size().reset_index(name='SalesCount')
   
   # sales activity chart
   fig_sales = go.Figure()
   
   #  sales count line 
   for i in range(len(sales_by_year)):
       if i > 0:
           # Determine color based on year
           if sales_by_year.iloc[i]['Year'] <= 2021:
               line_color = 'lightgray'
           else:
               line_color = '#1f77b4'
           
           # Draw line segment
           fig_sales.add_trace(go.Scatter(
               x=[sales_by_year.iloc[i-1]['Year'], sales_by_year.iloc[i]['Year']],
               y=[sales_by_year.iloc[i-1]['SalesCount'], sales_by_year.iloc[i]['SalesCount']],
               mode='lines',
               line=dict(color=line_color, width=3),
               showlegend=False,
               hoverinfo='skip'
           ))
   
   #  markers only for post-2021 data
   post_2021_sales = sales_by_year[sales_by_year['Year'] > 2021]
   
   fig_sales.add_trace(go.Scatter(
       x=post_2021_sales['Year'],
       y=post_2021_sales['SalesCount'],
       mode='markers',
       name='Annual Sales Count',
       marker=dict(size=8, color='#1f77b4'),
       hovertemplate='%{y:,.0f} sales<extra></extra>'
   ))
   
   #  vertical line at 2021 
   fig_sales.add_vline(
       x=2021,
       line_dash="dash",
       line_color="gray",
       line_width=2
   )
   
   # Calculate recent sales trend
   sales_2021 = sales_by_year[sales_by_year['Year'] == 2021]['SalesCount'].iloc[0] if len(sales_by_year[sales_by_year['Year'] == 2021]) > 0 else 0
   sales_2024 = sales_by_year[sales_by_year['Year'] == 2024]['SalesCount'].iloc[0] if len(sales_by_year[sales_by_year['Year'] == 2024]) > 0 else 0
   sales_change = ((sales_2024 - sales_2021) / sales_2021 * 100) if sales_2021 > 0 else 0
   
   #  annotation about recent sales activity
   fig_sales.add_annotation(
       x=2021,
       y=max(sales_by_year['SalesCount']) * 0.85,
       text=f"<b>Market Activity Post-2021:</b><br>Sales volume changed by {sales_change:.0f}%<br>from 2021 to 2024.<br>This reflects how the market<br>responded to rapid price changes.",
       showarrow=True,
       arrowhead=2,
       arrowsize=1,
       arrowwidth=2,
       arrowcolor="gray",
       ax=-100,
       ay=-60,
       bgcolor="rgba(255,255,255,0.9)",
       bordercolor="rgba(0,0,0,0)",
       borderwidth=0,
       font=dict(size=12, color="gray")
   )
   
   fig_sales.update_layout(
       title=dict(
           text='Annual Sales Activity Since 2000',
           font=dict(color='#1f77b4', size=20)
       ),
       yaxis_title='Number of Sales',
       xaxis_title='Year',
       hovermode='x unified',
       height=500,
       showlegend=True,
       font=dict(color='#6c757d')
   )
   st.plotly_chart(fig_sales, use_container_width=True)
   
 
   
   # Income Disparity Analysis Chart
   st.subheader("The Reality of Income Inequality and Housing Access")

   st.markdown("""
   Based on the latest data from the U.S. Census Bureau 2023, the median household income for Black families is \$**36,541** and the median household income for White families is \$**86,259**. When you look at both numbers, they are still far away from the current housing prices, but it looks more impossible for Black families to own in the city.
   """)

   #  income disparity data
   income_data = pd.DataFrame({
       'Family Type': ['Black Families', 'White Families'],
       'Median Income': [36541, 86259],
       'Affordable Home Price (3x Income)': [109641, 258777]
   })

   # Create the chart
   fig_income = go.Figure()

   # Add income bars
   fig_income.add_trace(go.Bar(
     x=income_data['Family Type'],
     y=income_data['Median Income'],
     name='Median Household Income',
     marker_color=['gray', 'gray'],
     text=['Median income', 'Median income'],
     textposition='inside',
     textfont=dict(color='Black', size=14),
     yaxis='y'
    ))

   # Add affordable price bars (secondary y-axis)
   fig_income.add_trace(go.Bar(
     x=income_data['Family Type'],
     y=income_data['Affordable Home Price (3x Income)'],
     name='Affordable Home Price (3x Income)',
     marker_color=["#1f77b4", '#1f77b4'],
     text=['Affordbil house price for black families', 'Affordbil house price for wight families'],
     textposition='inside',
     textfont=dict(color='Black', size=12),
     yaxis='y2',
     opacity=0.7
    ))

    #Add horizontal line for median home price in 2023 - CHANGED TO BLUE
   fig_income.add_hline(
     y=500000,
     line_dash="dash",
     line_color="#1f77b4",  
     line_width=3,
     annotation_text="Median Home Price 2023: $459,000",
     annotation_position="top right",
     annotation=dict(
        font_size=14,
        font_color="#1f77b4", 
        bgcolor="rgba(255,255,255,0.8)"
         )
    )

 #  annotation for Black families 
   fig_income.add_annotation(
    x=-0.3,  
    y=130000,  
    text="<b>Black Families Reality:</b><br> Need to earn <b>$153,000</b><br>(4.1x current income)<br>to afford median home",
    showarrow=True,
    arrowhead=2,
    arrowsize=1.5,
    arrowwidth=3,
    arrowcolor="gray",
    
    ax=50,   
    ay=-220,    
    bgcolor="rgba(255,255,255,0.9)",
    bordercolor="gray",
    borderwidth=0,
    font=dict(size=11, color="gray"),
    align="left"
   )

   # Add annotation for White families
   fig_income.add_annotation(
    x=1.1,  
    y=290000,  
    text="<b>White Families Reality:</b><br>• Need to earn <b>$153,000</b><br>(1.7x current income)<br>to afford median home",
    showarrow=True,
    arrowhead=2,
    arrowsize=1.5,
    arrowwidth=3,
    arrowcolor="gray",
    
    ax=100,  
    ay=-130,    
    bgcolor="rgba(255,255,255,0.9)",
    bordercolor="gray",
    borderwidth=0,
    font=dict(size=11, color="gray"),
    align="left"
    )
   
   # Update layout with dual y-axis
   fig_income.update_layout(
       title=dict(
           text='Income Inequality and Housing Affordability Gap',
           font=dict(color='#1f77b4', size=20)
       ),
       xaxis_title='Family Demographics',
       yaxis=dict(
           title='Annual Income ($)',
           side='left',
           range=[0, 600000]
       ),
       yaxis2=dict(
           title='Affordable Home Price ($)',
           side='right',
           overlaying='y',
           range=[0, 600000]
       ),
       height=700,  
       showlegend=True,
       legend=dict(
           orientation="h",
           yanchor="bottom",
           y=1.02,
           xanchor="right",
           x=1
       ),
       font=dict(color='#6c757d'),
       barmode='group'
   )

   st.plotly_chart(fig_income, use_container_width=True)
   
   st.markdown("---")
   
   # Property Search Feature
   st.subheader("🔍 Check Your Property's Assessment History")
   st.markdown("Curious about how your own property's value has changed? Enter your address below(the property must be in Charlottesville):")
   
   search_address = st.text_input(
       "Enter property address:",
       placeholder="e.g., 123 MAIN ST or just MAIN ST",
       help="Type part of an address to search."
   )
   
   if search_address:
       all_assessments = data['all_assessments'].copy()
       all_assessments['FullAddress'] = all_assessments['StreetNumber'].astype(str) + ' ' + all_assessments['StreetName'].astype(str)
       
       matching_properties = all_assessments[
           all_assessments['FullAddress'].str.contains(search_address.upper(), case=False, na=False) |
           all_assessments['StreetName'].str.contains(search_address.upper(), case=False, na=False)
       ]
       
       if len(matching_properties) > 0:
           unique_addresses = matching_properties[['ParcelNumber', 'FullAddress']].drop_duplicates()
           
           if len(unique_addresses) > 1:
               selected_address = st.selectbox(
                   f"Found {len(unique_addresses)} properties. Select one:",
                   options=unique_addresses['FullAddress'].tolist()
               )
               selected_parcel = unique_addresses[unique_addresses['FullAddress'] == selected_address]['ParcelNumber'].iloc[0]
           else:
               selected_address = unique_addresses['FullAddress'].iloc[0]
               selected_parcel = unique_addresses['ParcelNumber'].iloc[0]
           
           property_history = all_assessments[all_assessments['ParcelNumber'] == selected_parcel].sort_values('TaxYear')
           
           if len(property_history) > 0:
               col1, col2 = st.columns([2, 1])
               
               with col1:
                   fig_assessment = go.Figure()
                   fig_assessment.add_trace(go.Scatter(
                       x=property_history['TaxYear'],
                       y=property_history['TotalValue'],
                       mode='lines+markers',
                       name='Total Assessed Value',
                       line=dict(color='blue', width=3)
                   ))
                   
                   fig_assessment.update_layout(
                       title=f'Assessment History: {selected_address.strip()}',
                       xaxis_title='Year',
                       yaxis_title='Assessed Value ($)',
                       hovermode='x unified'
                   )
                   st.plotly_chart(fig_assessment, use_container_width=True)
               
               with col2:
                   latest_assessment = property_history.iloc[-1]
                   assessment_2021 = property_history[property_history['TaxYear'] == 2021]
                   assessment_2021 = assessment_2021.iloc[0]
                   total_change = latest_assessment['TotalValue'] - assessment_2021['TotalValue']
                   pct_change = (total_change / assessment_2021['TotalValue'] * 100)
                   
                   st.metric("Current Value", f"${latest_assessment['TotalValue']:,.0f}")
                   st.metric("Change since 2021", 
                             f"${total_change:,.0f}", f"{pct_change:.1f}%")
   
   st.markdown("---")
   
   # The main ownership analysis
   st.header("Who Really Owns The City?")
   st.markdown("""
   ### The Changing Face of Property Ownership
   
   As housing becomes an investment commodity, we need to ask: who actually owns the city? The answer might surprise you.
   """)
   
   # Load and process the parcel boundary data
   parcel_details = data['parcel_boundary_details'].copy()
   
   # Clean the data and identify local vs non-local owners
   parcel_details = parcel_details.dropna(subset=['OwnerCityState'])
   parcel_details = parcel_details.copy()
   parcel_details.loc[:, 'OwnerCityState_Clean'] = parcel_details['OwnerCityState'].astype(str).str.strip().str.upper()
   parcel_details.loc[:, 'IsLocal'] = parcel_details['OwnerCityState_Clean'] == 'CHARLOTTESVILLE VA'
   
   # Calculate ownership statistics
   total_parcels = len(parcel_details)
   local_parcels = parcel_details['IsLocal'].sum()
   non_local_parcels = total_parcels - local_parcels
   local_pct = (local_parcels / total_parcels * 100) if total_parcels > 0 else 0
   
   # Calculate land area statistics
   total_land_area = parcel_details['LotSquareFeet'].sum()
   local_land_area = parcel_details[parcel_details['IsLocal']]['LotSquareFeet'].sum()
   non_local_land_area = parcel_details[~parcel_details['IsLocal']]['LotSquareFeet'].sum()
   local_land_pct = (local_land_area / total_land_area * 100) if total_land_area > 0 else 0
   
   # Display key metrics
   col1, col2, col3, col4 = st.columns(4)
   with col1:
       st.metric("Total Properties", f"{total_parcels:,}")
   with col2:
       st.metric("Local Ownership", f"{local_pct:.1f}%", f"{local_parcels:,} properties")
   with col3:
       st.metric("Non-Local Ownership", f"{100-local_pct:.1f}%", f"{non_local_parcels:,} properties")
   with col4:
       st.metric("Non-Local Land Control", f"{100-local_land_pct:.1f}%", f"{non_local_land_area/43560:.0f} acres")
   
   # Top Property Owners Analysis
   st.subheader("Who Are The Biggest Property Owners?")
   
   try:
       # Calculate top owners directly from parcel_details
       if 'Assessment' in parcel_details.columns:
           top_owners = (
               parcel_details.groupby('OwnerName')
               .agg(
                   TotalProperties=('OwnerName', 'size'),
                   TotalSquareFeet=('LotSquareFeet', 'sum'),
                   TotalAssessment=('Assessment', 'sum')
               )
               .reset_index()
           )
       else:
           top_owners = (
               parcel_details.groupby('OwnerName')
               .agg(
                   TotalProperties=('OwnerName', 'size'),
                   TotalSquareFeet=('LotSquareFeet', 'sum')
               )
               .reset_index()
           )
           top_owners['TotalAssessment'] = 0
       
       # Sort by total properties
       top_owners = top_owners.sort_values(by='TotalProperties', ascending=False)
       
       top_owners['TotalAcres'] = top_owners['TotalSquareFeet'] / 43560
       top_owners['FormattedAcres'] = top_owners['TotalAcres'].apply(lambda x: f"{x:.1f} acres")
       top_owners['FormattedAssessment'] = top_owners['TotalAssessment'].apply(lambda x: f"${x:,.0f}")
       
       # Show expandable table
       st.markdown("**Click to expand and see more property owners:**")
       
       # Create display dataframe
       display_columns = ['OwnerName', 'TotalProperties']
       if 'Assessment' in parcel_details.columns:
           display_columns.append('FormattedAssessment')
       
       display_df = top_owners[display_columns].copy()
       display_df.columns = ['Owner Name', 'Properties', 'Total Assessment Value'] + (['Total Assessment Value'] if len(display_columns) > 3 else [])
       
       # Use expander for the table
       with st.expander("Property Owners Table", expanded=True):
           st.dataframe(display_df, use_container_width=True, height=None)
       
       # Get top 10 for charts
       top_10_owners = top_owners.head(10)
       
       # Create horizontal bar charts
       col1, col2 = st.columns(2)
       
       with col1:
           # top owners by total properties
           fig_top_owners = px.bar(
               top_10_owners,
               x='TotalProperties',
               y='OwnerName',
               title='Top 10 Owners by Number of Properties',
               labels={'OwnerName': 'Owner Name', 'TotalProperties': 'Number of Properties'},
               text='TotalProperties',
               color='TotalProperties',
               color_continuous_scale='Blues',
               orientation='h'
           )
           fig_top_owners.update_layout(
               yaxis={'categoryorder': 'total ascending'},
               height=500
           )
           st.plotly_chart(fig_top_owners, use_container_width=True)
       
       with col2:
           # top owners by total acres
           fig_top_acres = px.bar(
               top_10_owners,
               x='TotalAcres',
               y='OwnerName',
               title='Top 10 Owners by Total Land Area',
               labels={'OwnerName': 'Owner Name', 'TotalAcres': 'Total Acres'},
               text='TotalAcres',
               color='TotalAcres',
               color_continuous_scale='Blues',
               orientation='h'
           )
           fig_top_acres.update_layout(
               yaxis={'categoryorder': 'total ascending'},
               height=500
           )
           fig_top_acres.update_traces(texttemplate='%{text:.1f}')
           st.plotly_chart(fig_top_acres, use_container_width=True)
       
       # assessment values CHART
       if 'TotalAssessment' in top_10_owners.columns:
           st.subheader("And Here's What Their Properties Are Really Worth")
           
           # Create the figure 
           fig_assessment = go.Figure()
           
           # Sort data for the chart
           assessment_data = top_10_owners.sort_values('TotalAssessment', ascending=True)
           
           
           for i in range(len(assessment_data)):
               if i >= len(assessment_data) - 2:  # Top 2 bars
                   bar_color = '#1f77b4'  
               else:
                   bar_color = 'lightgray' 
               
               # Add each bar individually
               fig_assessment.add_trace(go.Bar(
                   x=[assessment_data.iloc[i]['TotalAssessment']],
                   y=[assessment_data.iloc[i]['OwnerName']],
                   orientation='h',
                   marker_color=bar_color,
                   showlegend=False,
                   text=f"${assessment_data.iloc[i]['TotalAssessment']:,.0f}",
                   textposition='outside',
                   hovertemplate='%{text}<extra></extra>'
               ))
           
           # Update layout
           fig_assessment.update_layout(
               title=dict(
                   text='Top 10 Property Owners by Total Assessment Value',
                   font=dict(color='#1f77b4', size=20)
               ),
               xaxis_title='Total Assessment Value ($)',
               yaxis_title='',
               height=600,
               margin=dict(l=300),
               font=dict(color='#6c757d'),
               xaxis=dict(
                   gridcolor='lightgray',
                   tickformat='$,.0f'
               ),
               bargap=0.15,
               barmode='overlay'
           )
           
           # Add annotation 
           fig_assessment.add_annotation(
               x=assessment_data.iloc[-1]['TotalAssessment'] * 0.8,  
               y=len(assessment_data) - 1.5,  
               text="<b>Key Finding:</b><br>The top property owner by<br>assessment value controls significantly<br>more valuable real estate than all other major owners combined.<br>While the City of Charlottesville owns more properties in the city<br> by number and land size, the university dwarfs top property owners by assessed value",
               showarrow=True,
               arrowhead=2,
               arrowsize=1,
               arrowwidth=2,
               arrowcolor="gray",
               ax=0,    
               ay=100,  
               bgcolor="rgba(255,255,255,0.9)",
               bordercolor="rgba(0,0,0,0)",
               borderwidth=0,
               font=dict(size=12, color="gray"),
               align="center"
           )
           
           st.plotly_chart(fig_assessment, use_container_width=True)
           
   except Exception as e:
       st.error(f"Error analyzing top property owners: {str(e)}")
       st.write("Available columns in parcel_details:", list(parcel_details.columns))
   
   #  pie chart for ownership 
   st.subheader("The Big Picture: Local vs Outside Control")
   
   # Create two columns 
   chart_col, note_col = st.columns([1, 1])
   
   with chart_col:
       ownership_data = pd.DataFrame({
           'Type': ['Local', 'Non-Local'],
           'Count': [local_parcels, non_local_parcels]
       })
       
       fig = px.pie(ownership_data, values='Count', names='Type', 
                   title='Local vs Non-Local Ownership',
                   color_discrete_map={'Local': '#2E8B57', 'Non-Local': '#DC143C'})
       
       fig.update_layout(
           height=400,
           width=400,
           showlegend=True,
           legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.05)
       )
       st.plotly_chart(fig, use_container_width=False)
   
   with note_col:
       st.markdown("""
       ### 📝 What This Means
       
       **Local Ownership** includes:
       - Properties owned by people with Charlottesville, VA addresses
       - Residents who live in the community
       
       **Non-Local Ownership** includes:
       - Out-of-state investors
       - Property management companies
       - Landlords from other cities/states
       
       ### 🏘️ Community Impact
       
       When properties are owned by non-locals:
       - **Higher rents** as investments prioritize profits
       - **Less community investment** and neighborhood stability  
       - **Wealth extraction** - profits leave our local economy
       - **Reduced local control** over housing decisions
       """)
   
   
   
   # Summary Section - End of the story
   st.header("What This All Means for Our Community")
   
   st.markdown(f"""
   ### The Complete Picture
   
   **The Affordability Crisis:**
   - Home prices have increased {total_increase:.0f}% since 2000, far outpacing income growth
   - Only {affordable_pct:.1f}% of recent home sales are affordable to median-income families
   - The gap between what people earn and what homes cost keeps growing
   - The medin home price increased by **{recent_increase:.0f}%** from 2020 to 2024 alone, making it impossible for many families to buy a home
   - House crisis ivolves everyone, but especially impacts Black families who face a much larger affordability gap
   
   **Who Controls the City:**
   - **{local_pct:.1f}%** of properties are owned by Charlottesville residents
   - **{100-local_pct:.1f}%** are owned by non-local investors, landlords, or institutions
   - Non-local owners control **{100-local_land_pct:.1f}%** of the total land area
   - That's approximately **{non_local_land_area/43560:.0f} acres** controlled by outsiders
   - UVA is the largest single property owner by assessed value, controlling more than all other major owners combined.
   - The City of Charlottesville owns more properties by number and land size, but the university dwarfs top property owners by assessed value.
   
   **This isn't just about numbers - it's about our community's future and who gets to call Charlottesville home.**

   """)

else:
   st.error("Unable to load data. Please check file paths and try again.")