
from pathlib import Path
from datetime import date, timedelta
import json

import pandas as pd
import streamlit as st
import plotly.express as px


# ==================================================
# PERSONAL EXPENSE ANALYSIS AND PREDICTION
# GROUP #11
# ==================================================

st.set_page_config(
    page_title="ExpensePro | Smart Finance",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path("expenses.csv")
DEMO_FILE = Path("demo_expenses.csv")

REAL_BUDGET_FILE = Path("real_budget.json")
DEMO_BUDGET_FILE = Path("demo_budget.json")

COLUMNS = ["Date", "Category", "Description", "Amount"]

CATEGORIES = [
    "Food", "Travel", "Shopping", "Education",
    "Bills", "Health", "Entertainment", "Other"
]

GOLD = "#D4AF37"
GREEN = "#10B981"
RED = "#EF4444"


# ---------------- LUXURY DESIGN ----------------

st.markdown(
    """
    <style>
    
/* Choose Data dropdown text: dark green */
[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #006400 !important;
    -webkit-text-fill-color: #006400 !important;
}

/* White dropdown background */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- DEMO DATA ----------------



       


def create_demo_data():
    if not DEMO_FILE.exists() or DEMO_FILE.stat().st_size == 0:
        empty_df = pd.DataFrame(columns=COLUMNS)
        empty_df.to_csv(DEMO_FILE, index=False)


# ---------------- DATA FUNCTIONS ----------------

def load_data(file_path):
    if not file_path.exists():
        return pd.DataFrame(columns=COLUMNS)

    try:
        data = pd.read_csv(file_path)

        if not all(col in data.columns for col in COLUMNS):
            return pd.DataFrame(columns=COLUMNS)

        data = data[COLUMNS].copy()
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
        data["Category"] = data["Category"].fillna("Other").astype(str)
        data["Description"] = data["Description"].fillna("").astype(str)

        data = data.dropna(subset=["Date", "Amount"])
        data = data[data["Amount"] >= 0]

        return data.reset_index(drop=True)

    except Exception as error:
        st.error(f"Data file read nahi ho payi: {error}")
        return pd.DataFrame(columns=COLUMNS)


def save_data(data, file_path):
    output = data[COLUMNS].copy()
    output["Date"] = pd.to_datetime(
        output["Date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    output.to_csv(file_path, index=False)


def load_budget(file_path):
    try:
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as file:
                result = json.load(file)
                return max(1.0, float(result.get("monthly_budget", 10000)))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass

    return 10000.0


def save_budget(value, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump({"monthly_budget": float(value)}, file)


def money(value):
    return f"₹{value:,.2f}"


def current_month_expenses(data):
    if data.empty:
        return data.copy()

    today = pd.Timestamp(date.today())

    return data[
        (data["Date"].dt.year == today.year)
        & (data["Date"].dt.month == today.month)
    ].copy()


def show_empty():
    st.info(
        "Abhi expense record nahi hai. "
        "Add Expense page se apna pehla expense add karo."
    )


# ---------------- SIDEBAR NAVIGATION ----------------

with st.sidebar:
    st.markdown("# 💎 ExpensePro")
    st.caption("PREMIUM PERSONAL FINANCE")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "🏠 Dashboard",
            "➕ Add Expense",
            "📊 Analytics",
            "🔮 Prediction",
            "🎓 Project Info",
        ],
    )

    st.divider()

    data_mode = st.selectbox(
        "📂 Choose Data",
        ["Real Expenses", "Demo Data"],
    )

    st.caption("Real aur demo records alag files mein save hote hain.")

    st.divider()

    st.markdown("### 👥 Our Team")
    st.markdown("**01. Yashjeet Yadav**")
    st.caption("Project Developer")
    st.markdown("**02. Saurabh Gond**")
    st.caption("Team Member")
    st.markdown("**03. Nihal Yadav**")
    st.caption("Team Member")

    st.divider()
    st.caption("College Mini Project | Group #11")
    st.caption("groupproject01@gmail.com")


# ---------------- SELECT DATA FILE ----------------

if data_mode == "Demo Data":
    create_demo_data()
    active_file = DEMO_FILE
    budget_file = DEMO_BUDGET_FILE
else:
    active_file = DATA_FILE
    budget_file = REAL_BUDGET_FILE

df = load_data(active_file)
month_df = current_month_expenses(df)

monthly_spent = (
    float(month_df["Amount"].sum()) if not month_df.empty else 0.0
)


# ---------------- MONTHLY BUDGET ----------------

saved_budget = load_budget(budget_file)

with st.sidebar:
    st.markdown("### 🎯 Monthly Budget")

    monthly_budget = st.number_input(
        "Set your monthly limit (₹)",
        min_value=100.0,
        max_value=100000000.0,
        value=float(saved_budget),
        step=500.0,
        key=f"budget_input_{data_mode}",
    )

    if float(monthly_budget) != float(saved_budget):
        try:
            save_budget(monthly_budget, budget_file)
        except OSError as error:
            st.error(f"Budget save nahi hua: {error}")

    spent_percent = (monthly_spent / monthly_budget) * 100

    st.progress(min(spent_percent / 100, 1.0))
    st.caption(f"Is month used: {spent_percent:.1f}%")

    if monthly_spent >= monthly_budget:
        st.error("🚨 BUDGET LIMIT CROSSED!")
        st.caption("Kharch control karein.")
    elif spent_percent >= 80:
        st.warning("⚠️ Budget ka 80% use ho gaya!")
        st.caption("Ab unnecessary expenses se bachein.")
    else:
        st.success("✅ Budget ke andar ho.")


# ---------------- HEADER ----------------

st.markdown(
    '<div class="main-title">💎 ExpensePro</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="sub-title">'
    'Personal Expense Analysis and Prediction | Smart Finance Dashboard'
    '</div>',
    unsafe_allow_html=True,
)

st.write("")


# ==================================================
# DASHBOARD
# ==================================================

if page == "🏠 Dashboard":

    st.subheader("✨ Your Financial Overview")

    if data_mode == "Demo Data":
        st.info(
            "Demo Mode: sample data dikhaya ja raha hai. "
            "Ye aapke real expenses nahi hain."
        )

    total = float(df["Amount"].sum()) if not df.empty else 0.0
    average = float(df["Amount"].mean()) if not df.empty else 0.0
    highest = float(df["Amount"].max()) if not df.empty else 0.0
    remaining = max(float(monthly_budget) - monthly_spent, 0.0)

    a, b, c, d = st.columns(4)
    a.metric("💰 All-Time Spending", money(total))
    b.metric("📅 This Month", money(monthly_spent))
    c.metric("🎯 Budget Remaining", money(remaining))
    d.metric("🧾 Expense Records", len(df))

    st.write("")

    if monthly_spent >= monthly_budget:
        st.error(
            f"🚨 Spending Alert: Is month aapne {money(monthly_spent)} "
            f"kharch kiye hain, jo {money(monthly_budget)} ke budget "
            "ke barabar ya usse zyada hai."
        )
    elif monthly_spent >= monthly_budget * 0.8:
        st.warning(
            f"⚠️ Budget Alert: Aapne monthly budget ka "
            f"{spent_percent:.1f}% use kar liya hai."
        )
    else:
        st.success(
            f"✅ Aapka kharch budget ke andar hai. "
            f"{money(remaining)} budget remaining hai."
        )

    st.progress(min(spent_percent / 100, 1.0))

    st.divider()

    if df.empty:
        show_empty()

    else:
        left, right = st.columns(2)

        with left:
            st.markdown("#### 🥧 Category Breakdown")

            category_data = (
                df.groupby("Category", as_index=False)["Amount"]
                .sum()
                .sort_values("Amount", ascending=False)
            )

            fig = px.pie(
                category_data,
                names="Category",
                values="Amount",
                hole=0.55,
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#F8FAFC",
                margin=dict(t=20, b=20, l=10, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.markdown("#### 📈 Daily Spending Trend")

            daily = df.copy()
            daily["Date"] = daily["Date"].dt.date
            daily = daily.groupby("Date", as_index=False)["Amount"].sum()

            fig = px.bar(
                daily,
                x="Date",
                y="Amount",
                color="Amount",
                color_continuous_scale=["#10B981", "#D4AF37", "#EF4444"],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#F8FAFC",
                xaxis_title="Date",
                yaxis_title="Amount (₹)",
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 📋 Recent Transactions")

        recent = df.sort_values("Date", ascending=False).head(10).copy()
        recent["Date"] = recent["Date"].dt.strftime("%d %b %Y")
        recent["Amount"] = recent["Amount"].map(money)

        st.dataframe(recent, use_container_width=True, hide_index=True)


# ==================================================
# ADD EXPENSE
# ==================================================

# ==================================================
# ADD EXPENSE
# ==================================================

elif page == "➕ Add Expense":

    st.subheader("➕ Add New Transaction")
    st.caption("Expense save hote hi selected data file aur dashboard update honge.")

    with st.form("expense_form", clear_on_submit=True):

        expense_date = st.date_input("📅 Date", value=date.today())

        category = st.selectbox("📂 Category", CATEGORIES)

        description = st.text_input(
            "📝 Description",
            placeholder="Example: Lunch, books, bus fare",
        )

        amount = st.number_input(
            "💰 Amount (₹)",
            min_value=0.01,
            value=100.0,
            step=10.0,
        )

        submitted = st.form_submit_button(
            "💾 Save Expense",
            use_container_width=True,
        )

    if submitted:
        try:
            new_row = pd.DataFrame(
                [{
                    "Date": pd.Timestamp(expense_date),
                    "Category": category,
                    "Description": description.strip() or category,
                    "Amount": float(amount),
                }]
            )

            updated = pd.concat([df, new_row], ignore_index=True)

            save_data(updated, active_file)

            df = updated

            st.success(
                f"✅ Expense Saved Successfully! "
                f"Amount: {money(float(amount))}"
            )

            st.toast(
                f"Expense saved: {money(float(amount))}",
                icon="✅",
            )

        except Exception as error:
            st.error(f"Expense save nahi ho paya: {error}")

    st.divider()
    st.markdown("#### 📋 Saved Expenses")

    if df.empty:
        show_empty()

    else:
        records = df.sort_values("Date", ascending=False).copy()
        records["Date"] = records["Date"].dt.strftime("%d %b %Y")
        records["Amount"] = records["Amount"].map(money)

        st.dataframe(
            records,
            use_container_width=True,
            hide_index=True,
        )
# ==================================================
# ANALYTICS
# ==================================================

elif page == "📊 Analytics":

    st.subheader("📊 Advanced Expense Analytics")

    if df.empty:
        show_empty()

    else:
        cat = (
            df.groupby("Category", as_index=False)["Amount"]
            .sum()
            .sort_values("Amount", ascending=False)
        )

        st.markdown("#### Category-wise Comparison")

        fig = px.bar(
            cat,
            x="Category",
            y="Amount",
            color="Category",
            text="Amount",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#F8FAFC",
            showlegend=False,
            yaxis_title="Amount (₹)",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Monthly Spending History")

        monthly = df.copy()
        monthly["Month"] = monthly["Date"].dt.to_period("M").astype(str)

        monthly = (
            monthly.groupby("Month", as_index=False)["Amount"]
            .sum()
            .sort_values("Month")
        )

        fig = px.line(
            monthly,
            x="Month",
            y="Amount",
            markers=True,
        )
        fig.update_traces(
            line_color=GOLD,
            line_width=4,
            marker_color=GREEN,
            marker_size=9,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#F8FAFC",
            yaxis_title="Amount (₹)",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Category Summary")
        cat["Amount"] = cat["Amount"].map(money)
        st.dataframe(cat, use_container_width=True, hide_index=True)


# ==================================================
# PREDICTION
# ==================================================

elif page == "🔮 Prediction":

    st.subheader("🔮 Smart Spending Prediction")

    st.write(
        "Ye educational estimate pichhle 30 din ke kharch par based hai."
    )

    if df.empty:
        show_empty()

    else:
        today = pd.Timestamp(date.today())
        start = today - pd.Timedelta(days=29)

        recent = df[
            (df["Date"] >= start)
            & (df["Date"] < today + pd.Timedelta(days=1))
        ]

        last_30_days = float(recent["Amount"].sum())
        daily_average = last_30_days / 30
        predicted = daily_average * 30

        p1, p2, p3 = st.columns(3)
        p1.metric("Last 30 Days", money(last_30_days))
        p2.metric("Daily Average", money(daily_average))
        p3.metric("Next 30 Days Estimate", money(predicted))

        prediction = pd.DataFrame({
            "Period": ["Past 30 Days", "Next 30 Days Estimate"],
            "Amount": [last_30_days, predicted],
        })

        fig = px.bar(
            prediction,
            x="Period",
            y="Amount",
            color="Period",
            text="Amount",
            color_discrete_sequence=[GREEN, GOLD],
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#F8FAFC",
            showlegend=False,
            yaxis_title="Amount (₹)",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info(
            "Prediction historical average par based hai. "
            "Actual future spending alag ho sakti hai."
        )


# ==================================================
# PROJECT INFORMATION
# ==================================================

elif page == "🎓 Project Info":

    st.subheader("🎓 Project Information")

    st.markdown("### Personal Expense Analysis and Prediction")
    st.write(
        "Is project ka objective personal expenses ko record karna, "
        "spending patterns ko graphs se samajhna, monthly budget track "
        "karna aur past spending se future expenses ka estimate dena hai."
    )

    st.divider()

    st.markdown("### ✨ Key Features")
    st.markdown(
        """
        - Personal expense entry and CSV storage
        - Real Expenses and Demo Data modes
        - Luxury financial dashboard
        - Category-wise and monthly analytics
        - Monthly budget and spending alerts
        - Historical-average-based prediction
        """
    )

    st.divider()

    st.markdown("### 🛠️ Technologies Used")
    t1, t2, t3 = st.columns(3)
    t1.info("🐍 Python")
    t2.info("📊 Pandas & Plotly")
    t3.info("🌐 Streamlit")

    st.divider()

    st.markdown("### 👥 Project Team — Group #11")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown("#### 01. Yashjeet Yadav")
        st.success("Project Developer")

    with m2:
        st.markdown("#### 02. Saurabh Gond")
        st.info("Team Member")

    with m3:
        st.markdown("#### 03. Nihal Yadav")
        st.info("Team Member")

    st.divider()

    st.markdown("### 📧 Contact")
    st.markdown("**groupproject01@gmail.com**")


# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    """
    <div class="project-footer">
        <b>💎 ExpensePro — Personal Expense Analysis and Prediction</b><br>
        College Mini Project | Group #11<br>
        Yashjeet Yadav · Saurabh Gond · Nihal Yadav<br>
        Contact: groupproject01@gmail.com
    </div>
    """,
    unsafe_allow_html=True,
)