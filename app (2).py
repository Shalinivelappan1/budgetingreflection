import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
from pathlib import Path
import matplotlib.pyplot as plt
import tempfile

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Smart Budget & Expense Tracker",
    page_icon="💰",
    layout="centered"
)

st.title("💰 Smart Budget & Expense Tracker")
st.caption("Finance-first learning | Assessment-ready | Unicode-safe PDF")

# --------------------------------------------------
# FONT LOADER (CRITICAL)
# --------------------------------------------------
def load_unicode_fonts(pdf):
    root = Path(__file__).parent
    regular = root / "DejaVuSans.ttf"
    bold = root / "DejaVuSans-Bold.ttf"

    if not regular.exists() or not bold.exists():
        st.error(
            "Unicode font files missing.\n"
            "Ensure BOTH DejaVuSans.ttf and DejaVuSans-Bold.ttf are present "
            "in the app directory."
        )
        st.stop()

    pdf.add_font("DejaVu", "", str(regular), uni=True)
    pdf.add_font("DejaVu", "B", str(bold), uni=True)

# --------------------------------------------------
# PDF HELPERS
# --------------------------------------------------
def add_expense_table(pdf, df):
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 8, "🧾 Expense Breakdown", ln=True)
    pdf.ln(2)

    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(110, 8, "Category", border=1)
    pdf.cell(40, 8, "Amount (₹)", border=1, ln=True)

    pdf.set_font("DejaVu", "", 11)
    for _, row in df.iterrows():
        pdf.cell(110, 8, row["Category"], border=1)
        pdf.cell(40, 8, f"₹{row['Amount (₹)']:,.0f}", border=1, ln=True)

    pdf.ln(4)


def add_expense_chart(pdf, df):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(df["Category"], df["Amount (₹)"])
    ax.set_title("Expense Distribution")
    ax.set_ylabel("Amount (₹)")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        chart_path = tmp.name
        plt.savefig(chart_path, dpi=150)

    plt.close(fig)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 8, "📊 Expense Distribution", ln=True)
    pdf.ln(2)
    pdf.image(chart_path, x=15, w=180)
    pdf.ln(5)


def add_savings_vs_expenses_chart(pdf, df, savings):
    needs_categories = ["Housing (Rent / EMI)", "Food", "Utilities"]
    wants_categories = ["Lifestyle & Entertainment"]

    needs = df[df["Category"].isin(needs_categories)]["Amount (₹)"].sum()
    wants = df[df["Category"].isin(wants_categories)]["Amount (₹)"].sum()
    other = df[~df["Category"].isin(needs_categories + wants_categories)]["Amount (₹)"].sum()

    labels = ["Needs", "Wants", "Other Expenses", "Savings"]
    values = [needs, wants, other, max(savings, 0)]
    colors = ["#d62728", "#ff7f0e", "#7f7f7f", "#2ca02c"]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(labels, values, color=colors)
    ax.set_title("Savings vs Expenses (Needs / Wants)")
    ax.set_ylabel("Amount (₹)")

    for i, v in enumerate(values):
        ax.text(i, v + max(values) * 0.02, f"₹{v:,.0f}", ha="center", fontsize=9)

    plt.tight_layout()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        chart_path = tmp.name
        plt.savefig(chart_path, dpi=150)

    plt.close(fig)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 8, "📊 Savings vs Expenses Overview", ln=True)
    pdf.ln(2)
    pdf.image(chart_path, x=15, w=180)
    pdf.ln(5)

# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1, tab2 = st.tabs(["📊 Budget Dashboard", "🧠 Reflection & Submission"])

# ==================================================
# TAB 1: BUDGET DASHBOARD
# ==================================================
with tab1:
    period = st.radio("Select Budget Period", ["Monthly", "Yearly"], horizontal=True)
    st.divider()

    income = st.number_input(f"{period} Income (₹)", min_value=0, step=1000)
    savings_goal = st.number_input(f"{period} Savings Goal (₹)", min_value=0, step=1000)

    st.divider()
    st.subheader("📊 Expenses")

    categories = [
        "Housing (Rent / EMI)",
        "Food",
        "Transport",
        "Utilities",
        "Lifestyle & Entertainment",
        "Others"
    ]

    expenses = {c: st.number_input(f"{c} (₹)", min_value=0, step=500) for c in categories}
    df = pd.DataFrame({"Category": expenses.keys(), "Amount (₹)": expenses.values()})

    total_expenses = df["Amount (₹)"].sum()
    savings = income - total_expenses
    savings_rate = (savings / income * 100) if income > 0 else 0

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Income", f"₹{income:,.0f}")
    c2.metric("Expenses", f"₹{total_expenses:,.0f}")
    c3.metric("Savings", f"₹{savings:,.0f}")

# ==================================================
# TAB 2: REFLECTION + PDF
# ==================================================
with tab2:
    st.header("🧠 Reflection & Learning Submission")

    student_name = st.text_input("Student Name")
    course = st.text_input("Course / Section")

    r1 = st.text_area("1️⃣ What surprised you most about your spending pattern?")
    r2 = st.text_area("2️⃣ Which expense would you reduce to improve savings? Why?")
    r3 = st.text_area("3️⃣ Did your budget follow the 30–30–20 rule? Explain.")
    r4 = st.text_area("4️⃣ One financial habit you want to change after this exercise.")
    r5 = st.text_area("5️⃣ One-line reflection: “After this activity, I realized that …”")

    if st.button("📄 Generate PDF Submission"):
        if not student_name or not course:
            st.warning("Please enter your name and course.")
            st.stop()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        load_unicode_fonts(pdf)

        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 10, "Budgeting & Expense Tracker – Submission", ln=True)

        pdf.set_font("DejaVu", "", 11)
        pdf.cell(0, 8, f"Name: {student_name}", ln=True)
        pdf.cell(0, 8, f"Course: {course}", ln=True)
        pdf.cell(0, 8, f"Date: {date.today().strftime('%d %B %Y')}", ln=True)

        pdf.ln(4)
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 8, "📊 Budget Summary", ln=True)

        pdf.set_font("DejaVu", "", 11)
        pdf.cell(0, 8, f"Income: ₹{income:,.0f}", ln=True)
        pdf.cell(0, 8, f"Expenses: ₹{total_expenses:,.0f}", ln=True)
        pdf.cell(0, 8, f"Savings: ₹{savings:,.0f}", ln=True)
        pdf.cell(0, 8, f"Savings Rate: {savings_rate:.1f}%", ln=True)

        pdf.ln(4)
        add_expense_table(pdf, df)
        add_expense_chart(pdf, df)
        add_savings_vs_expenses_chart(pdf, df, savings)

        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 8, "🧠 Student Reflection", ln=True)
        pdf.set_font("DejaVu", "", 11)
        pdf.multi_cell(0, 8, f"{r1}\n\n{r2}\n\n{r3}\n\n{r4}\n\n{r5}")

        filename = f"{student_name.replace(' ', '_')}_Budget_Submission.pdf"
        pdf.output(filename)

        with open(filename, "rb") as f:
            st.download_button(
                "⬇️ Download PDF",
                data=f,
                file_name=filename,
                mime="application/pdf"
            )

        st.success("✅ PDF generated successfully!")
