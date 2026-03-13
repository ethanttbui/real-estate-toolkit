import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Buy vs Rent (Japan)", layout="wide")
st.title("🏠 Buy vs Rent 比較ツール (Japanese Market)")
st.caption("Compare the total cost of buying vs renting property in Japan over a given period.")

# ---------------------------------------------------------------------------
# Sidebar – all inputs
# ---------------------------------------------------------------------------
st.sidebar.header("🔧 Parameters")

# --- Evaluation period ---
st.sidebar.subheader("Evaluation Period")
years = st.sidebar.slider("Evaluation period (years)", 1, 35, 10)

# --- Property / Purchase ---
st.sidebar.subheader("🏗 Property & Purchase")
property_price = st.sidebar.number_input(
    "Property price (万円)", value=5000, step=100,
    help="Purchase price in 万円 (10,000 yen units). 5000万円 ≈ 50M yen."
)
down_payment_pct = st.sidebar.slider(
    "Down payment (%)", 0, 100, 20, help="Percentage of property price paid upfront."
)

# Mortgage
st.sidebar.subheader("💰 Mortgage")
mortgage_rate = st.sidebar.number_input(
    "Annual interest rate (%)", value=0.5, step=0.05, format="%.2f",
    help="Typical Japanese variable rate ~0.3-0.6%, fixed 10yr ~1.0-1.5%."
)
mortgage_term = st.sidebar.slider("Mortgage term (years)", 1, 35, 35)

# Taxes & closing costs
st.sidebar.subheader("📋 Buying Costs & Taxes")

closing_cost_pct = st.sidebar.number_input(
    "Closing costs (% of price)", value=7.0, step=0.5, format="%.1f",
    help="Includes 仲介手数料 (agent ~3%), 登録免許税 (registration), 不動産取得税, "
         "stamp duty, judicial scrivener, etc. Typically 6-8% for used, 3-5% new."
)

property_tax_rate = st.sidebar.number_input(
    "Annual property tax (% of assessed value)", value=1.7, step=0.1, format="%.1f",
    help="固定資産税 (1.4%) + 都市計画税 (0.3%) = 1.7% of assessed value."
)
assessed_value_ratio = st.sidebar.number_input(
    "Assessed / market value ratio", value=0.7, step=0.05, format="%.2f",
    help="固定資産税評価額 is typically 60-70% of market value."
)

# Maintenance
st.sidebar.subheader("🔧 Maintenance (Buying)")
monthly_maintenance = st.sidebar.number_input(
    "Monthly management fee (万円)", value=1.5, step=0.1, format="%.1f",
    help="管理費 for mansions (condos). Typically 1-2万円/month."
)
monthly_repair_reserve = st.sidebar.number_input(
    "Monthly repair reserve (万円)", value=1.0, step=0.1, format="%.1f",
    help="修繕積立金. Typically 0.5-1.5万円/month, increases over time."
)
repair_reserve_increase_pct = st.sidebar.number_input(
    "Annual repair reserve increase (%)", value=3.0, step=0.5, format="%.1f",
    help="修繕積立金 often increases ~3-5% per year."
)

# Insurance
annual_insurance = st.sidebar.number_input(
    "Annual fire/earthquake insurance (万円)", value=3.0, step=0.5, format="%.1f",
    help="火災・地震保険. Typically 2-5万円/year."
)

# Tax benefits
st.sidebar.subheader("🏦 Tax Benefits (住宅ローン控除)")
loan_deduction_rate = st.sidebar.number_input(
    "Loan deduction rate (%)", value=0.7, step=0.1, format="%.1f",
    help="住宅ローン控除: tax credit as % of year-end loan balance. "
         "0.7% since 2022 reform (was 1.0% before)."
)
loan_deduction_years = st.sidebar.number_input(
    "Deduction period (years)", value=13, step=1, min_value=0, max_value=13,
    help="13 years for new properties, 10 years for used (中古). Set 0 to disable."
)
loan_deduction_balance_cap = st.sidebar.number_input(
    "Loan balance cap for deduction (万円)", value=3000, step=500,
    help="Upper limit on eligible loan balance. New general: 3000万円, "
         "ZEH/低炭素: 3500-5000万円. Used: 2000万円."
)
annual_income_tax_cap = st.sidebar.number_input(
    "Annual income tax + resident tax cap (万円)", value=40.0, step=5.0, format="%.1f",
    help="Your actual annual tax liability (所得税+住民税) that the deduction can offset. "
         "The deduction cannot exceed your tax bill."
)

# Depreciation & appreciation
st.sidebar.subheader("📉 Property Value Changes")
annual_appreciation_pct = st.sidebar.number_input(
    "Annual property appreciation (%)", value=-1.0, step=0.5, format="%.1f",
    help="Japanese properties often depreciate. Wood structures: ~-2 to -4%/yr, "
         "RC mansions: ~0 to -2%/yr. Central Tokyo may appreciate."
)

# Exit strategy
st.sidebar.subheader("🚪 Exit Strategy (End of Period)")
exit_strategy = st.sidebar.radio(
    "At end of evaluation period:", ["Sell the property", "Rent it out"]
)

if exit_strategy == "Sell the property":
    selling_cost_pct = st.sidebar.number_input(
        "Selling costs (% of sale price)", value=4.0, step=0.5, format="%.1f",
        help="仲介手数料 ~3% + misc ~1%."
    )
else:
    rental_income_monthly = st.sidebar.number_input(
        "Expected monthly rental income (万円)", value=15.0, step=1.0, format="%.1f",
        help="Gross monthly rent you could charge."
    )
    rental_vacancy_pct = st.sidebar.number_input(
        "Vacancy rate (%)", value=5.0, step=1.0, format="%.1f"
    )
    rental_mgmt_fee_pct = st.sidebar.number_input(
        "Property management fee (%)", value=5.0, step=1.0, format="%.1f",
        help="管理委託料, typically 3-5% of rent."
    )
    rental_eval_years = st.sidebar.slider(
        "Rental evaluation period (years)", 1, 30, 10,
        help="How many years you plan to rent it out after the evaluation period."
    )
    rental_mortgage_rate = st.sidebar.number_input(
        "Rental mortgage rate (%)", value=1.5, step=0.1, format="%.2f",
        help="Investment property loans typically 1.5-3.0%."
    )

# --- Renting ---
st.sidebar.subheader("🏢 Renting")
monthly_rent = st.sidebar.number_input(
    "Monthly rent (万円)", value=15.0, step=1.0, format="%.1f",
    help="Current monthly rent."
)
rent_inflation_pct = st.sidebar.number_input(
    "Annual rent increase (%)", value=1.0, step=0.5, format="%.1f",
    help="Rent inflation. Japan is low: 0-2%/yr."
)

st.sidebar.subheader("📋 Renting Costs")
reikin_months = st.sidebar.number_input(
    "礼金 Reikin (months of rent)", value=1.0, step=0.5, format="%.1f",
    help="Gift money (non-refundable). Typically 0-2 months."
)
shikikin_months = st.sidebar.number_input(
    "敷金 Shikikin / deposit (months)", value=1.0, step=0.5, format="%.1f",
    help="Security deposit, partially refundable."
)
shikikin_return_pct = st.sidebar.number_input(
    "Deposit return (%)", value=50.0, step=10.0, format="%.1f",
    help="Percentage of shikikin returned when moving out."
)
agency_fee_months = st.sidebar.number_input(
    "Agency fee (months of rent)", value=1.0, step=0.5, format="%.1f",
    help="仲介手数料. Typically 0.5-1 month."
)
renewal_fee_months = st.sidebar.number_input(
    "Renewal fee (months of rent)", value=1.0, step=0.5, format="%.1f",
    help="更新料. Typically 1 month every 2 years."
)
renewal_interval = st.sidebar.slider(
    "Renewal interval (years)", 1, 5, 2,
    help="Lease renewal cycle. Standard is 2 years."
)
renter_insurance_annual = st.sidebar.number_input(
    "Annual renter's insurance (万円)", value=0.5, step=0.1, format="%.1f",
    help="火災保険 for renters. ~0.3-0.7万円/year."
)

# --- Investment return (opportunity cost) ---
st.sidebar.subheader("📈 Opportunity Cost")
investment_return_pct = st.sidebar.number_input(
    "Annual investment return (%)", value=5.0, step=0.5, format="%.1f",
    help="Return on alternative investments if you didn't buy. "
         "Used to compare the opportunity cost of the down payment & savings difference."
)

# ---------------------------------------------------------------------------
# Calculations (all in 万円)
# ---------------------------------------------------------------------------

# --- BUY side ---
down_payment = property_price * down_payment_pct / 100.0
loan_amount = property_price - down_payment
closing_costs = property_price * closing_cost_pct / 100.0

# Monthly mortgage payment (fixed rate for simplicity)
monthly_rate = (mortgage_rate / 100.0) / 12.0
n_payments = mortgage_term * 12
if monthly_rate > 0 and loan_amount > 0:
    monthly_mortgage = loan_amount * monthly_rate * (1 + monthly_rate) ** n_payments / (
        (1 + monthly_rate) ** n_payments - 1
    )
else:
    monthly_mortgage = loan_amount / max(n_payments, 1)

# Build year-by-year schedule
buy_yearly = []
remaining_loan = loan_amount
property_value = property_price
cumulative_buy_cost = down_payment + closing_costs
repair_reserve = monthly_repair_reserve

for yr in range(1, years + 1):
    # Mortgage payments for the year
    interest_paid = 0.0
    principal_paid = 0.0
    for _ in range(12):
        if remaining_loan <= 0:
            break
        interest = remaining_loan * monthly_rate
        principal = min(monthly_mortgage - interest, remaining_loan)
        interest_paid += interest
        principal_paid += principal
        remaining_loan -= principal

    # Property tax
    assessed_value = property_value * assessed_value_ratio
    prop_tax = assessed_value * property_tax_rate / 100.0

    # Maintenance
    annual_maintenance = monthly_maintenance * 12
    annual_repair = repair_reserve * 12
    repair_reserve *= (1 + repair_reserve_increase_pct / 100.0)

    # Insurance
    ins = annual_insurance

    # Housing loan tax deduction (住宅ローン控除)
    tax_deduction = 0.0
    if yr <= loan_deduction_years:
        eligible_balance = min(max(remaining_loan, 0), loan_deduction_balance_cap)
        raw_deduction = eligible_balance * loan_deduction_rate / 100.0
        tax_deduction = min(raw_deduction, annual_income_tax_cap)

    # Total annual buy cost (cash outflows excluding principal, which builds equity)
    annual_cost = interest_paid + prop_tax + annual_maintenance + annual_repair + ins
    total_cash_out = principal_paid + annual_cost - tax_deduction  # net after tax credit
    cumulative_buy_cost += total_cash_out

    # Property value change
    property_value *= (1 + annual_appreciation_pct / 100.0)

    buy_yearly.append({
        "Year": yr,
        "Mortgage (Interest)": round(interest_paid, 1),
        "Mortgage (Principal)": round(principal_paid, 1),
        "Property Tax": round(prop_tax, 1),
        "Maintenance": round(annual_maintenance, 1),
        "Repair Reserve": round(annual_repair, 1),
        "Insurance": round(ins, 1),
        "Tax Deduction": round(tax_deduction, 1),
        "Annual Cash Out": round(total_cash_out, 1),
        "Cumulative Cash Out": round(cumulative_buy_cost, 1),
        "Remaining Loan": round(max(remaining_loan, 0), 1),
        "Property Value": round(property_value, 1),
    })

# Equity at end of evaluation period
final_property_value = property_value
equity = final_property_value - max(remaining_loan, 0)

if exit_strategy == "Sell the property":
    sell_costs = final_property_value * selling_cost_pct / 100.0
    net_sale_proceeds = final_property_value - max(remaining_loan, 0) - sell_costs
    buy_net_cost = cumulative_buy_cost - net_sale_proceeds
    exit_summary = {
        "Property value at sale": round(final_property_value, 1),
        "Remaining loan": round(max(remaining_loan, 0), 1),
        "Selling costs": round(sell_costs, 1),
        "Net sale proceeds": round(net_sale_proceeds, 1),
    }
else:
    # Simple NPV of rental income stream after evaluation period
    annual_gross_rent = rental_income_monthly * 12
    effective_rent = annual_gross_rent * (1 - rental_vacancy_pct / 100.0) * (1 - rental_mgmt_fee_pct / 100.0)

    # Ongoing costs during rental: property tax, maintenance, repair, insurance, mortgage interest
    # Simplified: use final-year values and project forward
    last_buy = buy_yearly[-1] if buy_yearly else {}
    ongoing_annual_costs = (
        last_buy.get("Property Tax", 0)
        + last_buy.get("Maintenance", 0)
        + last_buy.get("Repair Reserve", 0)
        + last_buy.get("Insurance", 0)
    )

    # Remaining mortgage refinanced at rental rate
    rental_remaining_loan = max(remaining_loan, 0)
    rental_monthly_rate = (rental_mortgage_rate / 100.0) / 12.0
    rental_n_payments = rental_eval_years * 12
    if rental_monthly_rate > 0 and rental_remaining_loan > 0:
        rental_monthly_pmt = (
            rental_remaining_loan
            * rental_monthly_rate
            * (1 + rental_monthly_rate) ** rental_n_payments
            / ((1 + rental_monthly_rate) ** rental_n_payments - 1)
        )
    else:
        rental_monthly_pmt = rental_remaining_loan / max(rental_n_payments, 1)

    rental_annual_mortgage = rental_monthly_pmt * 12
    net_rental_cashflow = effective_rent - ongoing_annual_costs - rental_annual_mortgage

    # NPV of rental cashflows
    disc = investment_return_pct / 100.0
    rental_npv = sum(
        net_rental_cashflow / (1 + disc) ** t for t in range(1, rental_eval_years + 1)
    )

    # Residual property value at end of rental period
    rental_end_value = final_property_value * (1 + annual_appreciation_pct / 100.0) ** rental_eval_years
    # Assume sell at that point
    rental_sell_costs = rental_end_value * 4.0 / 100.0
    rental_loan_at_end = 0  # fully paid if term <= rental_eval_years, else compute
    if rental_eval_years < mortgage_term - years:
        temp_loan = rental_remaining_loan
        for _ in range(rental_eval_years * 12):
            if temp_loan <= 0:
                break
            ri = temp_loan * rental_monthly_rate
            rp = min(rental_monthly_pmt - ri, temp_loan)
            temp_loan -= rp
        rental_loan_at_end = max(temp_loan, 0)

    residual_value = rental_end_value - rental_loan_at_end - rental_sell_costs
    residual_npv = residual_value / (1 + disc) ** rental_eval_years

    total_rental_benefit_npv = rental_npv + residual_npv
    buy_net_cost = cumulative_buy_cost - total_rental_benefit_npv

    exit_summary = {
        "Annual rental income (effective)": round(effective_rent, 1),
        "Annual ongoing costs": round(ongoing_annual_costs, 1),
        "Annual mortgage payment (rental)": round(rental_annual_mortgage, 1),
        "Net annual rental cashflow": round(net_rental_cashflow, 1),
        "NPV of rental cashflows": round(rental_npv, 1),
        "Residual property value (NPV)": round(residual_npv, 1),
        "Total rental benefit (NPV)": round(total_rental_benefit_npv, 1),
    }


# --- RENT side ---
rent_yearly = []
cumulative_rent_cost = 0.0

# Initial fees (paid at move-in, year 0 costs)
initial_rent_fees = (reikin_months + shikikin_months + agency_fee_months) * monthly_rent
cumulative_rent_cost += initial_rent_fees
current_rent = monthly_rent

for yr in range(1, years + 1):
    annual_rent = current_rent * 12

    # Renewal fee
    renewal_cost = 0.0
    if yr > 1 and (yr - 1) % renewal_interval == 0:
        renewal_cost = current_rent * renewal_fee_months

    ins = renter_insurance_annual
    annual_total = annual_rent + renewal_cost + ins
    cumulative_rent_cost += annual_total

    rent_yearly.append({
        "Year": yr,
        "Monthly Rent": round(current_rent, 2),
        "Annual Rent": round(annual_rent, 1),
        "Renewal Fee": round(renewal_cost, 1),
        "Insurance": round(ins, 1),
        "Annual Total": round(annual_total, 1),
        "Deposit Return": 0.0,
        "Cumulative Cost": round(cumulative_rent_cost, 1),
    })

    current_rent *= (1 + rent_inflation_pct / 100.0)

# Deposit return at end
deposit_return = shikikin_months * monthly_rent * shikikin_return_pct / 100.0
cumulative_rent_cost -= deposit_return
if rent_yearly:
    rent_yearly[-1]["Deposit Return"] = round(-deposit_return, 1)
    rent_yearly[-1]["Annual Total"] = round(rent_yearly[-1]["Annual Total"] - deposit_return, 1)
    rent_yearly[-1]["Cumulative Cost"] = round(cumulative_rent_cost, 1)

# --- Opportunity cost of buying capital ---
# The renter can invest down_payment + closing_costs instead
investable_capital = down_payment + closing_costs

# Year-by-year: renter invests the difference in monthly cost
# Compare monthly cash outflows
investment_portfolio = investable_capital
total_principal_invested = investable_capital
investment_portfolio_yearly = []
principal_invested_yearly = []
for yr in range(1, years + 1):
    buy_annual_cash = buy_yearly[yr - 1]["Annual Cash Out"]
    rent_annual_cash = rent_yearly[yr - 1]["Annual Total"]
    monthly_saving = (buy_annual_cash - rent_annual_cash) / 12.0

    # Grow portfolio
    for _ in range(12):
        investment_portfolio *= (1 + investment_return_pct / 100.0 / 12.0)
        if monthly_saving > 0:
            investment_portfolio += monthly_saving
            total_principal_invested += monthly_saving

    investment_portfolio_yearly.append(investment_portfolio)
    principal_invested_yearly.append(total_principal_invested)

rent_total_cost = cumulative_rent_cost
# The renter's net position: cost minus investment gains (not entire portfolio)
renter_investment_gain = investment_portfolio - total_principal_invested
rent_net_cost = rent_total_cost - renter_investment_gain

# ---------------------------------------------------------------------------
# Display results
# ---------------------------------------------------------------------------
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Buy – Net Cost", f"¥{buy_net_cost:,.1f}万")
with col2:
    st.metric("Rent – Net Cost", f"¥{rent_net_cost:,.1f}万")
with col3:
    diff = buy_net_cost - rent_net_cost
    label = "Buy cheaper by" if diff < 0 else "Rent cheaper by"
    st.metric(label, f"¥{abs(diff):,.1f}万")

st.markdown("---")

# --- Summary cards ---
left, right = st.columns(2)

with left:
    st.subheader("🏠 Buy Summary")
    st.write(f"**Property price:** ¥{property_price:,}万")
    st.write(f"**Down payment:** ¥{down_payment:,.1f}万 ({down_payment_pct}%)")
    st.write(f"**Loan amount:** ¥{loan_amount:,.1f}万")
    st.write(f"**Monthly mortgage:** ¥{monthly_mortgage:,.2f}万")
    st.write(f"**Closing costs:** ¥{closing_costs:,.1f}万")
    total_tax_saved = sum(r["Tax Deduction"] for r in buy_yearly)
    st.write(f"**住宅ローン控除 total:** ¥{total_tax_saved:,.1f}万 (over {min(loan_deduction_years, years)}yr)")
    st.write(f"**Total cash out ({years}yr):** ¥{cumulative_buy_cost:,.1f}万 (net of tax deduction)")

    st.markdown("#### Exit Strategy")
    if exit_strategy == "Sell the property":
        for k, v in exit_summary.items():
            st.write(f"**{k}:** ¥{v:,}万")
        st.write(f"**Net cost of buying** (cash out − sale proceeds): **¥{buy_net_cost:,.1f}万**")
    else:
        for k, v in exit_summary.items():
            st.write(f"**{k}:** ¥{v:,}万")
        st.write(f"**Net cost of buying** (cash out − rental NPV): **¥{buy_net_cost:,.1f}万**")

with right:
    st.subheader("🏢 Rent Summary")
    st.write(f"**Monthly rent (initial):** ¥{monthly_rent:,}万")
    st.write(f"**Initial fees:** ¥{initial_rent_fees:,.1f}万 "
             f"(Reikin {reikin_months}mo + Deposit {shikikin_months}mo + Agency {agency_fee_months}mo)")
    st.write(f"**Deposit return:** ¥{deposit_return:,.1f}万")
    st.write(f"**Total rent cost ({years}yr):** ¥{rent_total_cost:,.1f}万")
    st.write(f"**Renter investment gain:** ¥{renter_investment_gain:,.1f}万")
    st.write(f"**Net cost of renting** (cost − investment gain): **¥{rent_net_cost:,.1f}万**")

st.markdown("---")

# --- Charts ---
st.subheader("📊 Net Cost Comparison (Cost − Equity)")
st.caption("Buy: cumulative cash out − property equity. Rent: cumulative cost − investment gains.")

buy_net_by_year = [
    row["Cumulative Cash Out"] - (row["Property Value"] - row["Remaining Loan"])
    for row in buy_yearly
]
rent_net_by_year = [
    rent_yearly[i]["Cumulative Cost"] - (investment_portfolio_yearly[i] - principal_invested_yearly[i])
    for i in range(years)
]

chart_df = pd.DataFrame({
    "Year": [row["Year"] for row in buy_yearly],
    "Buy (Cost − Equity)": buy_net_by_year,
    "Rent (Cost − Investments)": rent_net_by_year,
})
chart_df = chart_df.set_index("Year")
st.line_chart(chart_df, width='stretch')

# --- Detailed tables ---
with st.expander("📋 Buy – Year-by-Year Breakdown"):
    buy_df = pd.DataFrame(buy_yearly)
    st.dataframe(buy_df, width='stretch', hide_index=True)

with st.expander("📋 Rent – Year-by-Year Breakdown"):
    rent_df = pd.DataFrame(rent_yearly)
    st.dataframe(rent_df, width='stretch', hide_index=True)
