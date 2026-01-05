import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
from pathlib import Path
import requests

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Smart Budget & Expense Tracker",
    page_icon="💰",
    layout="centered"
)

st.title("💰 Smart Budget & Expense Tracker")
st.caption("Finance-first learning | No AI | Unicode-safe PDFs")

# --------------------------------------------------
# Helper: Auto-download Unicode font
# --------------------------------------------------
def load_unicode_font():
    font_path = Path("DejaVuSans.ttf")
    if not font_path.exists():
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            st.error("Unable to load Unicode font. Please refresh and try again.")
            st.stop()
        with open(font_path, "wb") as f:
            f.write(response.content)
    return font_path

# --------------------------------------------------
# Tabs
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

    expenses = {}
    for cat in categories:
        expenses[cat] = st.number_input(f"{cat} (₹)", min_value=0, step=500)

    df = pd.DataFrame({
        "Category": expenses.keys(),
        "Amount (₹)": expenses.values()
    })

    total_expenses = df["Amount (₹)"].sum()
    savings = income - total_expenses
    savings_rate = (savings / income * 100) if income > 0 else 0
    expense_ratio = (total_expenses / income * 100) if income > 0 else 0

    st.divider()
    st.subheader("📈 Budget Summary")

    c1, c2, c3 = st.columns(3)
    c1.metric("Income", f"₹{income:,.0f}")
    c2.metric("Expenses", f"₹{total_expenses:,.0f}")
    c3.metric("Savings", f"₹{savings:,.0f}")

    st.subheader("📉 Expense-to-Income Ratio")
    st.progress(min(int(expense_ratio), 100))
    st.caption(f"You are spending **{expense_ratio:.1f}%** of your income")

    st.subheader("🎯 Savings Goal Tracker")
    if savings_goal > 0:
        st.progress(max(min(savings / savings_goal, 1.0), 0.0))
        st.caption(f"₹{savings:,.0f} saved out of ₹{savings_goal:,.0f}")
    else:
        st.info("Set a savings goal to track progress.")

    st.divider()
    st.subheader("🧾 Expense Breakdown")
    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.set_index("Category"))

    st.divider()
    st.subheader("🧠 Smart Budget Insights")

    if income == 0:
        st.warning("Enter income to activate insights.")
    else:
        if savings < 0:
            st.error("⚠️ You are spending more than your income.")
        elif savings_rate < 20:
            st.warning("⚠️ Savings are below the recommended 20%.")
        else:
            st.success("✅ Your savings behavior looks healthy.")

        for _, row in df.iterrows():
            share = (row["Amount (₹)"] / income * 100) if income > 0 else 0
            if row["Category"].startswith("Housing") and share > 30:
                st.write(f"🏠 **{row['Category']}** is high ({share:.1f}%). Ideal ≤ 30%.")
            elif row["Category"] == "Lifestyle & Entertainment" and share > 20:
                st.write(f"🎉 **{row['Category']}** is high ({share:.1f}%).")
            elif share > 25:
                st.write(f"📌 **{row['Category']}** is relatively high ({share:.1f}%).")

    st.divider()
    st.subheader("🇮🇳 30–30–20 Rule Check")

    needs = df.loc[df["Category"].isin(
        ["Housing (Rent / EMI)", "Food", "Utilities"]), "Amount (₹)"].sum()
    wants = df.loc[df["Category"] == "Lifestyle & Entertainment", "Amount (₹)"].sum()

    needs_pct = (needs / income * 100) if income > 0 else 0
    wants_pct = (wants / income * 100) if income > 0 else 0

    st.write(f"**Needs:** {needs_pct:.1f}% (Target ≤ 30%)")
    st.write(f"**Wants:** {wants_pct:.1f}% (Target ≤ 30%)")
    st.write(f"**Savings:** {savings_rate:.1f}% (Target ≥ 20%)")

# ==================================================
# TAB 2: REFLECTION + PDF
# ==================================================
with tab2:

    st.header("🧠 Reflection & Learning Submission")
    st.caption("One-click PDF with budget summary + reflection.")

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

        font_path = load_unicode_font()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font("DejaVu", "", str(font_path), uni=True)

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
        pdf.cell(0, 8, f"Period: {period}", ln=True)
        pdf.cell(0, 8, f"Income: ₹{income:,.0f}", ln=True)
        pdf.cell(0, 8, f"Expenses: ₹{total_expenses:,.0f}", ln=True)
        pdf.cell(0, 8, f"Savings: ₹{savings:,.0f}", ln=True)
        pdf.cell(0, 8, f"Savings Rate: {savings_rate:.1f}%", ln=True)
        pdf.cell(0, 8, f"Expense-to-Income Ratio: {expense_ratio:.1f}%", ln=True)

        pdf.ln(4)
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 8, "🧠 Student Reflection", ln=True)

        pdf.set_font("DejaVu", "", 11)
        pdf.multi_cell(0, 8, f"1. {r1}\n")
        pdf.multi_cell(0, 8, f"2. {r2}\n")
        pdf.multi_cell(0, 8, f"3. {r3}\n")
        pdf.multi_cell(0, 8, f"4. {r4}\n")
        pdf.multi_cell(0, 8, f"5. {r5}\n")

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
