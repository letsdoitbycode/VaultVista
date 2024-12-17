import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# Set up Streamlit app configuration
st.set_page_config(page_title="Expense Prediction Dashboard", layout="wide")

# Title Section
st.markdown(
    """
    <style>
        .title {
            font-size: 3rem;
            text-align: center;
            color: #333;
        }
        .subtitle {
            font-size: 1.2rem;
            text-align: center;
            color: #777;
        }
    </style>
    <div class="title">Expense Prediction Dashboard</div>
    <div class="subtitle">Analyze and Predict Your Monthly Expenses with Insightful Visuals</div>
    """,
    unsafe_allow_html=True
)


# Load pre-trained model
model = load_model('model/my_model.h5')

# Function to preprocess data
def preprocess_data(df, features, scaler):
    scaled_data = scaler.fit_transform(df[features])
    return scaled_data

# Function to create sequences
def create_sequences(data, time_steps):
    X = []
    for i in range(len(data) - time_steps):
        X.append(data[i:i + time_steps])
    return np.array(X)

# Sidebar File Upload
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file:
    # Load and display input data
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("File uploaded successfully!")

    # Display uploaded data
    st.write("### Uploaded Data")
    st.dataframe(df.head(), height=250)

    # Define required columns
    required_columns = [
        'MonthlyIncome', 'HousingRent', 'FoodAndDining', 'Transportation',
        'Educational', 'Entertainment', 'PersonalCare', 'Technology',
        'HealthWellness', 'Grocery', 'Miscellaneous', 'TotalExpenses'
    ]

    if all(col in df.columns for col in required_columns):
        # Preprocess the data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = preprocess_data(df, required_columns, scaler)
        time_steps = 6
        X = create_sequences(scaled_data, time_steps)

        # Predict next 3 months
        predicted_scaled = model.predict(X[-1:])
        predicted_actual = scaler.inverse_transform(predicted_scaled.reshape(-1, len(required_columns)))

        # Prepare predicted data for display
        predicted_expenses = pd.DataFrame(predicted_actual, columns=required_columns)
        predicted_expenses.index = [f"Month {i + 1}" for i in range(len(predicted_expenses))]

        # Display predictions in a table
        st.write("### Predicted Expenses")
        st.dataframe(predicted_expenses)

        # Financial Summary
        total_expenses = predicted_expenses['TotalExpenses'].sum()
        monthly_income = predicted_expenses['MonthlyIncome'].mean()
        savings = monthly_income * len(predicted_expenses) - total_expenses

        st.markdown("### Financial Summary")
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Monthly Income", f"${monthly_income:,.2f}")
        col2.metric("Average Expenses", f"${(total_expenses / 3):,.2f}")
        col3.metric("Savings/Deficit", f"${savings:,.2f}", "positive" if savings >= 0 else "negative")

        # Visualization Dashboard
        st.markdown("### Visualization Dashboard")

        # Buttons for Month Selection
        selected_month = st.radio("Select Month:", ["Month 1", "Month 2", "Month 3"], horizontal=True)

        # Filter data for the selected month
        month_index = int(selected_month.split(" ")[1]) - 1
        month_data = predicted_expenses.iloc[month_index]

        # Display graphs in two columns for the first two charts
        col1, col2 = st.columns(2)

        with col1:
            st.write("#### Pie Chart: Expense Breakdown")
            pie_data = month_data[[col for col in required_columns if col not in ['MonthlyIncome', 'TotalExpenses']]]
            fig = px.pie(values=pie_data, names=pie_data.index, title=f"Expense Breakdown for {selected_month}")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.write("#### Bar Chart: Expense Comparison")
            fig = px.bar(predicted_expenses.iloc[month_index:month_index+1].drop(columns=['MonthlyIncome', 'TotalExpenses']),
                         barmode='group', title=f"Expense Comparison for {selected_month}")
            st.plotly_chart(fig, use_container_width=True)

        # Display the Line Chart and Area Chart on the last row as a block
        st.write("#### Line Chart: Expense Trends")
        fig = px.line(predicted_expenses.drop(columns=['MonthlyIncome', 'TotalExpenses']),
                      title=f"Expense Trends for {selected_month}")
        st.plotly_chart(fig, use_container_width=True)

        st.write("#### Area Chart: Expense Trends")
        fig = px.area(predicted_expenses.drop(columns=['MonthlyIncome', 'TotalExpenses']),
                      title=f"Expense Trends for {selected_month}")
        st.plotly_chart(fig, use_container_width=True)

        st.write("#### Heatmap: Expense Correlation")
        corr = predicted_expenses.corr()
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.index.values,
            y=corr.columns.values,
            colorscale='Viridis'
        ))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"CSV file is missing required columns: {set(required_columns) - set(df.columns)}")
else:
    st.info("Please upload a CSV file to start.")
