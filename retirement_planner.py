import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_retirement_plan(monthly_expense_retired, years_after_retirement, 
                            years_to_retirement, current_savings, monthly_contribution, 
                            expected_return):
    # Convert annual return to monthly
    monthly_return = (1 + expected_return) ** (1/12) - 1
    
    # Calculate total months
    total_months = (years_to_retirement + years_after_retirement) * 12
    months_to_retirement = years_to_retirement * 12
    
    # Initialize arrays to store data
    savings = np.zeros(total_months + 1)
    monthly_cashflow = np.zeros(total_months + 1)  # New array to track cash flow
    savings[0] = current_savings
    
    # Calculate monthly progress
    for i in range(1, total_months + 1):
        if i <= months_to_retirement:
            # During accumulation phase - contributing and growing
            savings[i] = (savings[i-1] * (1 + monthly_return)) + monthly_contribution
            monthly_cashflow[i] = monthly_contribution
        else:
            # During retirement phase - only withdrawing and growing
            savings[i] = (savings[i-1] * (1 + monthly_return)) - monthly_expense_retired
            monthly_cashflow[i] = -monthly_expense_retired
            
    return savings, monthly_cashflow

def main():
    st.title("Retirement Planning Calculator")
    st.write("""
    This calculator helps you plan your retirement savings and visualize your financial journey.
    The calculator assumes:
    - Monthly contributions occur only during working years
    - No additional income during retirement years
    - Consistent investment returns
    - Inflation-adjusted values
    """)
    
    # Input parameters
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_expense_retired = st.number_input(
            "Expected Monthly Expenses in Retirement ($)",
            min_value=0,
            value=5000,
            step=100,
            help="How much you expect to spend each month during retirement (in today's dollars)"
        )
        
        years_after_retirement = st.number_input(
            "Expected Years in Retirement",
            min_value=0,
            value=30,
            step=1,
            help="How many years you expect to live after retiring"
        )
        
        years_to_retirement = st.number_input(
            "Years until Retirement",
            min_value=0,
            value=25,
            step=1,
            help="Number of years until you plan to retire"
        )
    
    with col2:
        current_savings = st.number_input(
            "Current Savings ($)",
            min_value=0,
            value=100000,
            step=1000,
            help="Your current retirement savings balance"
        )
        
        monthly_contribution = st.number_input(
            "Monthly Contribution ($)",
            min_value=0,
            value=1000,
            step=100,
            help="How much you can save each month during working years"
        )
        
        expected_return = st.slider(
            "Expected Annual Return (%)",
            min_value=0.0,
            max_value=15.0,
            value=7.0,
            step=0.1,
            help="Expected annual return on investments (inflation-adjusted)"
        ) / 100

    # Calculate retirement plan
    savings, monthly_cashflow = calculate_retirement_plan(
        monthly_expense_retired,
        years_after_retirement,
        years_to_retirement,
        current_savings,
        monthly_contribution,
        expected_return
    )

    # Create time points for plotting
    total_years = years_to_retirement + years_after_retirement
    years = np.linspace(0, total_years, len(savings))
    
    # Create the plot
    fig = make_subplots(rows=2, cols=1, subplot_titles=('Savings Balance Over Time', 'Monthly Cash Flow'))
    
    # Add savings trace
    fig.add_trace(
        go.Scatter(x=years, y=savings, name="Savings Balance", line=dict(color='blue')),
        row=1, col=1
    )

    # Add cash flow trace
    fig.add_trace(
        go.Scatter(x=years, y=monthly_cashflow, name="Monthly Cash Flow", line=dict(color='green')),
        row=2, col=1
    )

    # Add vertical line at retirement
    fig.add_vline(x=years_to_retirement, line_dash="dash", line_color="red",
                  annotation_text="Retirement Date")

    # Update layout
    fig.update_layout(
        height=800,
        title="Retirement Planning Projection",
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_xaxes(title_text="Years", row=2, col=1)
    fig.update_yaxes(title_text="Balance ($)", row=1, col=1)
    fig.update_yaxes(title_text="Monthly Cash Flow ($)", row=2, col=1)

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

    # Display key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Peak Savings",
            f"${max(savings):,.2f}"
        )
    
    with col2:
        retirement_savings = savings[years_to_retirement * 12]
        st.metric(
            "Savings at Retirement",
            f"${retirement_savings:,.2f}"
        )
    
    with col3:
        final_savings = savings[-1]
        st.metric(
            "Final Savings",
            f"${final_savings:,.2f}",
            delta=f"${final_savings-retirement_savings:,.2f}"
        )

    # Analysis and recommendations
    st.subheader("Analysis")
    
    monthly_income_needed = monthly_expense_retired
    total_retirement_needs = monthly_income_needed * 12 * years_after_retirement
    
    if final_savings > 0:
        st.success(f"""
        ✅ Your retirement plan appears to be sustainable! 
        You'll have approximately ${final_savings:,.2f} remaining at the end of your planned retirement period.
        """)
    else:
        shortfall = abs(final_savings)
        additional_monthly_needed = (shortfall / (years_to_retirement * 12)) * (1 / (1 + expected_return/12) ** (years_to_retirement * 12))
        
        st.error(f"""
        ⚠️ Warning: Your savings will be depleted before the end of your planned retirement period.
        - Projected shortfall: ${abs(final_savings):,.2f}
        - To make up this shortfall, consider increasing your monthly contribution by approximately ${additional_monthly_needed:,.2f}
        
        Other options:
        - Reduce planned retirement expenses
        - Work longer before retirement
        - Seek higher investment returns (but be cautious of increased risk)
        """)

    # Detailed breakdown
    st.subheader("Financial Overview")
    st.write(f"""
    💰 Working Years ({years_to_retirement} years):
    - Monthly contribution: ${monthly_contribution:,.2f}
    - Total contributions: ${(monthly_contribution * 12 * years_to_retirement):,.2f}
    
    🏡 Retirement Years ({years_after_retirement} years):
    - Monthly expenses: ${monthly_expense_retired:,.2f}
    - Total needed: ${total_retirement_needs:,.2f}
    
    📈 Investment Details:
    - Expected annual return: {expected_return*100:.1f}%
    - Starting savings: ${current_savings:,.2f}
    """)

if __name__ == "__main__":
    main()