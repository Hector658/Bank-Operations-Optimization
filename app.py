import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Bank Operations Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- NOTEBOOK

def get_interarrival_mean(time):
    if time < 120:
        return 6
    elif time < 300:
        return 2
    elif time < 420:
        return 3
    return 5

def simulate_bank_day(sim_time=480, n_tellers=3, mean_service=5):
    arrivals = []
    current_time = 0

    revenue_per_customer = 0.75
    teller_cost = 8.50  

    while current_time < sim_time:
        mean_interarrival = get_interarrival_mean(current_time)
        interarrival = np.random.exponential(mean_interarrival)
        current_time += interarrival
        if current_time <= sim_time:
            arrivals.append(current_time)

    total_arrivals = len(arrivals)
    if total_arrivals == 0:
        return {
            "customers": 0, "served_customers": 0, "abandoned_customers": 0,
            "abandonment_rate": 0, "avg_wait": 0, "max_wait": 0,
            "pct_waiting": 0, "pct_wait_over_10": 0, "avg_utilization": 0,
            "revenue": 0, "operating_cost": n_tellers * teller_cost, "profit": -n_tellers * teller_cost
        }

    service_times = np.random.exponential(mean_service, total_arrivals)
    
    tellers = [0.0] * n_tellers
    busy_time = [0.0] * n_tellers
    served_waiting_times = []
    abandoned_count = 0
    total_waited = 0

    for arrival, service in zip(arrivals, service_times):
        teller_idx = np.argmin(tellers)
        available_at = tellers[teller_idx]
        virtual_wait = max(0.0, available_at - arrival)

        if virtual_wait > 0:
            total_waited += 1

        if virtual_wait > 15 and np.random.rand() < 0.6:
            abandoned_count += 1
            continue 

        start_service = max(arrival, available_at)
        wait = start_service - arrival
        end_service = start_service + service

        tellers[teller_idx] = end_service
        busy_time[teller_idx] += service
        served_waiting_times.append(wait)

    served_waiting_times = np.array(served_waiting_times)
    served_customers = len(served_waiting_times)

    abandonment_rate = (abandoned_count / total_arrivals * 100) if total_arrivals > 0 else 0
    utilization = [min(busy / sim_time, 1.0) for busy in busy_time]
    avg_utilization = np.mean(utilization)

    revenue = served_customers * revenue_per_customer
    operating_cost = n_tellers * teller_cost
    profit = revenue - operating_cost

    pct_wait_over_10 = (served_waiting_times > 10).mean() * 100 if served_customers > 0 else 0
    pct_waiting = (total_waited / total_arrivals * 100) if total_arrivals > 0 else 0

    return {
        "customers": total_arrivals,
        "served_customers": served_customers,
        "abandoned_customers": abandoned_count,
        "abandonment_rate": abandonment_rate,
        "avg_wait": served_waiting_times.mean() if served_customers > 0 else 0,
        "max_wait": served_waiting_times.max() if served_customers > 0 else 0,
        "pct_waiting": pct_waiting,
        "pct_wait_over_10": pct_wait_over_10,
        "avg_utilization": avg_utilization,
        "revenue": revenue,
        "operating_cost": operating_cost,
        "profit": profit
    }

# --- DASHBOARD DESIGN ---

st.title("🏦 Bank Operations & Staffing Optimizer")
st.markdown("""
This dashboard uses a **Discrete Event Monte Carlo Simulation** to evaluate staffing levels.
It helps balance fixed operating costs against operational risk and financial losses due to customer churn.
""")

# Interactive parameters in the sidebar
st.sidebar.header("Simulation Configuration")
sim_time = st.sidebar.slider("Duration of the banking day(Minutes)", 60, 480, 480, step=60)
mean_service = st.sidebar.slider("Mean Service Time (Minutes)", 1, 15, 5)
iterations = st.sidebar.slider("Monte Carlo Runs (Simulaciones)", 100, 1000, 500, step=100)

st.sidebar.markdown("---")
st.sidebar.caption("Portfolio Project - Data Science Applied to Operations.")

# Executer Button
if st.button("Run Dynamic Simulation"):
    
    with st.spinner("Processing mathematical simulations in the background... Please wait."):
        scenarios = [2, 3, 4, 5]
        all_runs = []
        summary = []
        
        # Main Bucle
        for t in scenarios:
            results = [simulate_bank_day(sim_time, t, mean_service) for _ in range(iterations)]
            df_temp = pd.DataFrame(results)
            df_temp['tellers'] = t
            all_runs.append(df_temp)
            
            summary.append({
                "tellers": t,
                "avg_wait": df_temp["avg_wait"].mean(),
                "p95_wait": df_temp["max_wait"].quantile(0.95),
                "profit": df_temp["profit"].mean()
            })
            
        df_all_runs = pd.concat(all_runs, ignore_index=True)
        df_summary = pd.DataFrame(summary)
        
    st.success("Simulation completed successfully!")
    
    # --- DISPLAY BEST RESULTS ON CARDS (KPIs) ---
    st.header("Strategic Business Decisions")
    
    # Identify the optimal gain point
    best_row = df_summary.loc[df_summary['profit'].idxmax()]
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Recommended staff", f"{int(best_row['tellers'])} Tellers")
    kpi2.metric("Expected Net Profit", f"${best_row['profit']:.2f} / day")
    kpi3.metric("Average Waiting Time", f"{best_row['avg_wait']:.2f} min")
    
    # --- DISPLAY PANELS ---
    st.header("Statistical Analysis and Behavior Curves")
    
    tab1, tab2 = st.tabs(["Tail Risk Analysis", "Volatility of Earnings (Violin)"])
    
    with tab1:
        fig1, ax1 = plt.subplots(figsize=(10, 4.5))
        sns.lineplot(data=df_summary, x='tellers', y='avg_wait', marker='o', label='Average Waiting', ax=ax1)
        sns.lineplot(data=df_summary, x='tellers', y='p95_wait', marker='s', label='Tail Risk (Pct 95)', color='crimson', linestyle='--', ax=ax1)
        ax1.set_ylabel("Waiting Time (Minutes)")
        ax1.set_xlabel("Number of Tellers")
        ax1.set_xticks(scenarios)
        ax1.grid(True, linestyle=':', alpha=0.6)
        st.pyplot(fig1)
        st.caption("Notice how the Queue Risk (P95) increases non-linearly when staffing is reduced below 3 cashiers.")
        
    with tab2:
        fig2, ax2 = plt.subplots(figsize=(10, 4.5))
        sns.violinplot(data=df_all_runs, x='tellers', y='profit', inner='quartile', palette="muted", ax=ax2)
        ax2.set_ylabel("Daily Earnings ($)")
        ax2.set_xlabel("Number of Tellers")
        ax2.grid(True, linestyle=':', alpha=0.4)
        st.pyplot(fig2)
        st.caption("The width of the violins describes the financial uncertainty and operational variability in each scenario.")