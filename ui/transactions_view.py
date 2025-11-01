import streamlit as st
import pandas as pd

from datetime import datetime, date
from core.accounts import get_accounts
from core.utils import MONTHS
from core.transactions import add_transaction, fetch_transactions, update_transaction_by_uuid, delete_transaction_by_uuid
from core.balances import get_opening

def show_transactions_view(user):
    s1, s2 = st.columns(2)
    with s1:st.header("Transactions")
    with s2:
        current_month_index = datetime.now().month - 1
        selected_month = st.selectbox("Select Month", MONTHS, index=current_month_index, key="global_month_select")
    
    accounts = get_accounts(user["id"])
    account_names = [a['name'] for a in accounts]

    # ------------- Metrics -------------
    metrics_bar = st.empty()

    # ------------- Add Transaction -------------

    with st.expander("➕ Add Transaction", expanded=False):
        with st.form("add_tx"):
            t_date = st.date_input("Date", value=date.today())
            if account_names:
                acc_choice = st.selectbox("Account", account_names)
            else:
                st.warning("No accounts — add one first.")
                acc_choice = None
            t_category = st.selectbox(
                "Category",
                [
                    "Food", "Transport", "Bills", "Shopping", "Rent", "Salary",
                    "Payment", "Investment", "Entertainment", "Health",
                    "Education", "Other"
                ],
            )
            t_description = st.text_input("Description", "")
            t_type = st.radio("Type", ["Expense", "Income"], horizontal=True)
            t_amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
            if st.form_submit_button("Add"):
                if not acc_choice:
                    st.error("Please add an account first.")
                elif t_amount <= 0:
                    st.error("Amount must be > 0")
                else:
                    aid = next((a['id'] for a in accounts if a['name'] == acc_choice), None)
                    add_transaction(t_date, aid, t_category, t_description, t_type, t_amount, user['id'])
                    st.success("Transaction added")
                    st.rerun()
    
    # ------------- Filter Transactions -------------

    with st.expander("🔍 Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            default_start = date(datetime.now().year, current_month_index + 1, 1)
            min_date = st.date_input("Start date", value=default_start)
        with col2:
            default_end = date.today()
            max_date = st.date_input("End date", value=default_end)
        with col3:
            account_options = ["All"] + account_names
            account_filter = st.multiselect("Account", account_options, default=["All"])
            type_filter = st.multiselect("Type", ["All", "Expense", "Income"], default=["All"])

    account_ids = None
    if account_filter and "All" not in account_filter:
        account_ids = [a['id'] for a in accounts if a['name'] in account_filter]
    types = None
    if type_filter and "All" not in type_filter:
        types = [t for t in type_filter if t != "All"]

    tx_df = fetch_transactions(
        month_filter=selected_month,
        start_date=min_date,
        end_date=max_date,
        account_ids=account_ids,
        types=types,
        user_id=user["id"],
    )

    # ------------- SHOW Transactions -------------

    st.write(f"Showing {len(tx_df)} transactions")
    if not tx_df.empty:
        # Convert Date column to datetime.date
        if 'Date' in tx_df.columns:
            tx_df['Date'] = pd.to_datetime(tx_df['Date'], errors='coerce').dt.date
        if "Transaction_ID" in tx_df.columns:
            tx_df = tx_df.set_index("Transaction_ID", drop=False)
            
        st.write("User ID:", user['id'])
        st.write("Selected Month:", selected_month)
        st.write("Rows fetched:", len(tx_df))

        edited = st.data_editor(
            tx_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "Account": st.column_config.Column("Account", disabled=True),
                "Category": st.column_config.TextColumn("Category"),
                "Description": st.column_config.TextColumn("Description"),
                "Type": st.column_config.SelectboxColumn("Type", options=["Expense", "Income"]),
                "Amount": st.column_config.NumberColumn("Amount", min_value=0.0, format="%.2f"),
                "Transaction_ID": st.column_config.Column("Transaction_ID", disabled=True),
            },
            key="tx_editor",
        )
        # Save edits
        if st.button("💾 Save edits"):
            try:
                new_ids = set(edited["Transaction_ID"].astype(str).tolist())
                old_ids = set(tx_df["Transaction_ID"].astype(str).tolist())
                deleted = old_ids - new_ids
                for did in deleted:
                    delete_transaction_by_uuid(did)

                for _, row in edited.iterrows():
                    txid = str(row.get("Transaction_ID", "") or "")
                    if not txid:
                        acc_name = row.get("Account")
                        aid = next((a['id'] for a in accounts if a['name'] == acc_name), None)
                        add_transaction(
                            pd.to_datetime(row["Date"]).date(),
                            aid,
                            row.get("Category", ""),
                            row.get("Description", ""),
                            row.get("Type", "Expense"),
                            float(row.get("Amount", 0.0)),
                            user['id'],
                        )
                    else:
                        updates = {
                            "date": pd.to_datetime(row["Date"]).date().isoformat(),
                            "amount": float(row.get("Amount", 0.0)),
                            "category": row.get("Category", ""),
                            "description": row.get("Description", ""),
                            "type": row.get("Type", "Expense"),
                        }
                        update_transaction_by_uuid(txid, updates)
                st.success("Saved changes")
                st.rerun()
            except Exception as e:
                st.error(str(e))

        # --- Account summary and visuals ---
        st.markdown("---")
        st.subheader(f"Account Summary for {selected_month}")
        top_balance_viewer = st.empty()
        # Rebuild monthly data to include balances
        summary_rows = []
        debit_opening, credit_opening = 0.0, 0.0
        total_income_summary, total_spent_summary = 0.0, 0.0

        # Ensure we have the right columns
        if not tx_df.empty and "Account" in tx_df.columns and "Type" in tx_df.columns:
            for a in accounts:
                acc = a["name"]
                acc_type = a["type"]
                opening = get_opening(selected_month, a["id"], user["id"])
                acc_data = tx_df[tx_df["Account"] == acc]

                # Compute totals
                income = float(acc_data[acc_data["Type"] == "Income"]["Amount"].sum()) if not acc_data.empty else 0.0
                expense = float(acc_data[acc_data["Type"] == "Expense"]["Amount"].sum()) if not acc_data.empty else 0.0

                if acc_type == "Debit":
                    remaining = opening + income - expense
                    debit_opening += opening
                else:  # Credit
                    remaining = opening + expense - income
                    credit_opening += opening

                summary_rows.append({
                    "Account": acc,
                    "Type": acc_type,
                    "Opening Balance": opening,
                    "Total Incoming (Payments)": income,
                    "Total Spent": expense,
                    "Remaining Balance": remaining
                })
                total_income_summary += income
                total_spent_summary += expense

        # Totals
        total_opening = debit_opening - credit_opening
        total_remaining = total_opening + total_income_summary - total_spent_summary
        try:
            summary_df = pd.DataFrame(summary_rows)
            debit_df = summary_df[summary_df["Type"] == "Debit"]
            credit_df = summary_df[summary_df["Type"] == "Credit"]

            # --- Debit section ---
            st.markdown("#### Debit Accounts")
            if not debit_df.empty:
                st.dataframe(
                    debit_df[
                        ["Account", "Type", "Opening Balance", "Total Incoming (Payments)", "Total Spent", "Remaining Balance"]
                    ],
                    use_container_width=True,
                )
            else:
                st.info("No debit accounts configured for this month.")

            total_debit_opening = float(debit_df["Opening Balance"].sum()) if not debit_df.empty else 0.0
            total_debit_remaining = float(debit_df["Remaining Balance"].sum()) if not debit_df.empty else 0.0
            total_debit_spent = float(debit_df["Total Spent"].sum()) if not debit_df.empty else 0.0
            total_debit_incoming = float(debit_df["Total Incoming (Payments)"].sum()) if not debit_df.empty else 0.0
            st.write(f"**Total Remaining Balance (Debit accounts):** ₹{total_debit_remaining:,.2f}")

            # --- Credit section ---
            st.markdown("#### Credit Cards")
            if not credit_df.empty:
                st.dataframe(
                    credit_df[
                        ["Account", "Type", "Opening Balance", "Total Incoming (Payments)", "Total Spent", "Remaining Balance"]
                    ],
                    use_container_width=True,
                )
            else:
                st.info("No credit accounts configured for this month.")

            total_credit_opening = float(credit_df["Opening Balance"].sum()) if not credit_df.empty else 0.0
            total_credit_remaining = float(credit_df["Remaining Balance"].sum()) if not credit_df.empty else 0.0
            total_credit_spent = float(credit_df["Total Spent"].sum()) if not credit_df.empty else 0.0
            total_credit_incoming = float(credit_df["Total Incoming (Payments)"].sum()) if not credit_df.empty else 0.0
            st.write(f"**Total Spent (Credit accounts):** ₹{total_credit_spent:,.2f}")

            # --- Overall Totals ---
            st.markdown(f"#### Total (All Accounts) for {selected_month}")
            total_row = pd.DataFrame([
                {
                    "Account": "Total (All Accounts)",
                    "Opening Balance": total_opening,
                    "Total Spent": total_spent_summary,
                    "Total Incoming (Payments)": total_income_summary,
                    "Remaining Balance": total_remaining,
                },
                {
                    "Account": "Debit Summary",
                    "Opening Balance": total_debit_opening,
                    "Total Spent": total_debit_spent,
                    "Total Incoming (Payments)": total_debit_incoming,
                    "Remaining Balance": total_debit_remaining,
                },
                {
                    "Account": "Credit Summary",
                    "Opening Balance": total_credit_opening,
                    "Total Spent": total_credit_spent,
                    "Total Incoming (Payments)": total_credit_incoming,
                    "Remaining Balance": total_credit_remaining,
                },
            ])
            st.dataframe(total_row, use_container_width=True)

            # --- Top-line balance display ---
            with metrics_bar:
                st.write(f"💰 Available Balance ({selected_month}): :green[₹{total_remaining:,.2f}]")
        except Exception as e:
            st.info("Please Add Transactions")
    
    # ------------- Monthly ----------------------------

    st.markdown("---")
    st.subheader("Monthly Metrics")

    if not tx_df.empty and "Type" in tx_df.columns:
        total_income = tx_df[tx_df["Type"] == "Income"]["Amount"].sum()
        total_expense = tx_df[tx_df["Type"] == "Expense"]["Amount"].sum()
        net_flow = total_income - total_expense
        total_transactions = int(tx_df.shape[0])
        col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
        with col_metrics1:
            st.metric("Total Debit Spending", f'₹{total_debit_spent:,.2f}')
            st.metric("Total Income", f"₹{total_income:,.2f}")
        with col_metrics2:
            st.metric("Total Credit Outstanding", f'₹{total_credit_remaining:,.2f}')
            st.metric("Total Expenses", f"₹{total_expense:,.2f}")
        with col_metrics3:
            st.metric("Total Debit Balance", f'₹{total_debit_remaining:,.2f}')
            st.metric("Net Flow", f"₹{net_flow:,.2f}", delta=net_flow, delta_color="normal" if net_flow >= 0 else "inverse")
        with col_metrics4:
            st.metric("Total Remaining Balance", f'₹{total_remaining:,.2f}')
            st.metric("Total Transactions", total_transactions)
    else:
        st.info("No transaction data to display monthly metrics.")

    import plotly.express as px
    import plotly.graph_objects as go

    # ------------------------------------
    # --- 📊 INTERACTIVE VISUAL INSIGHTS ---
    # ------------------------------------
    st.markdown("---")
    st.subheader(f"📈 Visual Insights for {selected_month}")

    if not tx_df.empty:
        # --- 1️⃣ Daily Expenses Trend (Line Chart) ---
        st.markdown("#### 1️⃣ Daily Expenses Trend")
        daily_expenses = (
            tx_df[tx_df["Type"] == "Expense"]
            .groupby("Date")["Amount"]
            .sum()
            .reset_index()
            .sort_values("Date")
        )
        if not daily_expenses.empty:
            fig1 = px.line(
                daily_expenses,
                x="Date",
                y="Amount",
                title=f"Daily Expenses - {selected_month}",
                markers=True,
                labels={"Amount": "Amount (₹)", "Date": "Date"},
            )
            fig1.update_traces(line=dict(width=3))
            fig1.update_layout(hovermode="x unified", xaxis_title=None)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No expenses recorded for this month.")

        # --- 2️⃣ Category-wise Spending (Pie Chart) ---
        st.markdown("#### 2️⃣ Category-wise Spending Distribution")
        category_spend = (
            tx_df[tx_df["Type"] == "Expense"]
            .groupby("Category")["Amount"]
            .sum()
            .reset_index()
            .sort_values("Amount", ascending=False)
        )
        if not category_spend.empty:
            fig2 = px.pie(
                category_spend,
                names="Category",
                values="Amount",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3,
                title="Spending by Category",
            )
            fig2.update_traces(textinfo="percent+label", pull=[0.05] * len(category_spend))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No category data available for expenses.")

        # --- 3️⃣ Account-wise Income vs Expense (Grouped Bar) ---
        st.markdown("#### 3️⃣ Income vs Expense by Account")

        account_summary = (
            tx_df.groupby(["Account", "Type"])["Amount"]
            .sum()
            .reset_index()
            .pivot(index="Account", columns="Type", values="Amount")
            .fillna(0)
            .reset_index()
        )

        # ✅ Ensure both Income & Expense columns exist
        for col in ["Income", "Expense"]:
            if col not in account_summary.columns:
                account_summary[col] = 0.0

        if not account_summary.empty:
            melted = account_summary.melt(
                id_vars="Account",
                value_vars=["Income", "Expense"],
                var_name="Type",
                value_name="Amount",
            )

            fig3 = px.bar(
                melted,
                x="Account",
                y="Amount",
                color="Type",
                barmode="group",
                text_auto=".2s",
                title="Income vs Expense per Account",
                labels={"Amount": "Amount (₹)", "Account": "Account"},
                color_discrete_map={"Expense": "#EF553B", "Income": "#00CC96"},
            )
            fig3.update_layout(hovermode="x unified")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No account data available for income/expense comparison.")


        # --- 4️⃣ Cumulative Spending Over Time (Line) ---
        st.markdown("#### 4️⃣ Cumulative Spending Over the Month")
        if not daily_expenses.empty:
            daily_expenses["Cumulative"] = daily_expenses["Amount"].cumsum()
            fig4 = px.line(
                daily_expenses,
                x="Date",
                y="Cumulative",
                title="Cumulative Expenses Over the Month",
                markers=True,
                labels={"Cumulative": "Cumulative Spent (₹)"},
            )
            fig4.update_traces(line_color="#EF553B", line_width=3)
            fig4.update_layout(hovermode="x unified")
            st.plotly_chart(fig4, use_container_width=True)

        # --- 5️⃣ Spending vs Income Ratio (Gauge / Indicator) ---
        st.markdown("#### 5️⃣ Spending vs Income Ratio")
        total_income = tx_df[tx_df["Type"] == "Income"]["Amount"].sum()
        total_expense = tx_df[tx_df["Type"] == "Expense"]["Amount"].sum()
        ratio = (total_expense / total_income * 100) if total_income > 0 else 0

        fig5 = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=ratio,
                title={"text": "Spending-to-Income Ratio (%)"},
                delta={"reference": 100, "increasing": {"color": "red"}},
                gauge={
                    "axis": {"range": [0, 200]},
                    "bar": {"color": "darkred" if ratio > 100 else "green"},
                    "steps": [
                        {"range": [0, 80], "color": "lightgreen"},
                        {"range": [80, 100], "color": "gold"},
                        {"range": [100, 200], "color": "#EF553B"},
                    ],
                    "threshold": {
                        "line": {"color": "black", "width": 4},
                        "thickness": 0.75,
                        "value": ratio,
                    },
                },
            )
        )
        fig5.update_layout(height=250, margin=dict(t=50, b=30))
        st.plotly_chart(fig5, use_container_width=True)

    else:
        st.info("No data available to show visualizations.")
