# Bank Operations Optimization: A Monte Carlo Queueing Simulation

This project models and optimizes bank branch staffing levels using a Discrete Event Simulation (DES) approach based on Queueing Theory. By balancing customer experience (waiting times and abandonment rates) against operational costs (teller salaries), the model identifies the most profitable staffing level for a bank day.

##  Project Overview
Bank branches face a classic operational trade-off: hiring too many tellers increases fixed operating costs, while hiring too few leads to long queues, customer dissatisfaction, and revenue loss from customer abandonment (reneging).

This repository simulates 1,000 bank days for various staffing levels ($n = 2, 3, 4, 5$ tellers) to find the exact point where net profit is maximized.

---

##  Simulation Logic & Architecture
The model simulates a 480-minute bank day utilizing stochastic processes to recreate realistic customer behavior:
* **Arrivals:** Modeled via a Non-Homogeneous Poisson Process where inter-arrival times follow an exponential distribution $X \sim \text{Exp}(\lambda)$ that varies depending on peak hours.
* **Service Times:** Modeled using an exponential distribution based on historical average service times.
* **Customer Reneging (Abandonment):** If a customer's virtual wait time exceeds 15 minutes, there is a 60% probability they will leave the queue, forfeiting the potential revenue.

Here is the exact algorithmic workflow of the simulation:

```mermaid
graph TD
    A([Start of Bank Day]) --> B[Generate Stochastic Arrivals via Non-Homogeneous Poisson Process]
    B --> C[Assign Exponential Service Times to Customers]
    C --> D[Iterate by Customer]
    D --> E{Is Virtual Wait Time > 15 min?}
    E -- Yes <br> 60% Probability --> F[Customer Abandons / Record Renége]
    E -- No / Customer Stays --> G[Assign to Teller with Earliest Available Time]
    G --> H[Calculate Exact Wait & Update Teller Next Available Time]
    F --> I{Are There More Customers?}
    H --> I
    I -- Yes --> D
    I -- No --> J[Compute Final KPIs: Profit, Revenue, Utilization, P95 Wait]
    J --> K([End of Simulation])