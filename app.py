
import streamlit as st
import pandas as pd
import textwrap

from utils.database import run_query

from utils.ai import (
    generate_sql,
    clean_sql_query,
    generate_business_insight
)

from utils.charts import generate_chart
from utils.security import validate_sql_query


# =========================================
# PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="AI SQL Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================
# STREAMLIT SECRETS
# =========================================

groq_api_key = st.secrets.get("GROQ_API_KEY")

database_path = st.secrets.get(
    "DATABASE_PATH",
    "data/business_sales.db"
)


# =========================================
# SESSION STATE
# =========================================

if "query_history" not in st.session_state:
    st.session_state.query_history = []


# =========================================
# QUERY HISTORY SIDEBAR
# =========================================

with st.sidebar:

    st.markdown("## 🕘 Query History")

    if st.session_state.query_history:

        for item in reversed(st.session_state.query_history[-10:]):

            st.markdown(f"""
            <div style="
            background:rgba(15,23,42,0.85);
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
            border:1px solid rgba(255,255,255,0.06);
            color:#d1d5db;
            font-size:14px;
            ">
            {item}
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("No queries yet.")


# =========================================
# CUSTOM CSS
# =========================================

st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    max-width: 1500px;
    margin: auto;
}

html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
    background-color: #020817;
    color: white;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1rem;
    color: white;
}

.glass-card {
    background: rgba(15, 23, 42, 0.88);
    backdrop-filter: blur(14px);
    padding: 1.2rem;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1rem;
    color: #d1d5db;
}

.insight-box {

    background:
        linear-gradient(
            135deg,
            rgba(30,41,59,0.96),
            rgba(49,46,129,0.92)
        );

    padding: 2rem 2.2rem;

    border-radius: 24px;

    border: 1px solid rgba(139,92,246,0.22);

    color: #e5e7eb;

    font-size: 1rem;

    line-height: 1.95;

    margin-top: 1rem;

    box-shadow:
        0 10px 40px rgba(0,0,0,0.35),
        0 0 40px rgba(139,92,246,0.06);

    backdrop-filter: blur(14px);
}


/* Headings */

.insight-box h1,
.insight-box h2,
.insight-box h3 {
    color: white;
    margin-top: 1.4rem;
    margin-bottom: 1rem;
    font-weight: 700;
}


/* Bold text */

.insight-box strong {
    color: #ffffff;
    font-weight: 700;
}


/* Paragraph spacing */

.insight-box p {
    margin-bottom: 1rem;
    color: #dbe4ff;
}


/* Lists */

.insight-box ul,
.insight-box ol {
    padding-left: 1.4rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
}

.insight-box li {
    margin-bottom: 1rem;
    color: #dbe4ff;
}


/* Inline highlighted values */

.insight-box code {

    background: rgba(15,23,42,0.95);

    padding: 4px 8px;

    border-radius: 8px;

    color: #a78bfa;

    font-size: 0.95rem;

    border: 1px solid rgba(139,92,246,0.18);
}


/* Optional subtle divider */

.insight-divider {

    height: 1px;

    background: rgba(255,255,255,0.08);

    margin: 1.5rem 0;
}

div[data-testid="metric-container"] {
    background: rgba(15,23,42,0.88);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 1rem;
    border-radius: 18px;
}

div.stButton > button {
    background: linear-gradient(
        135deg,
        #2563eb,
        #7c3aed
    );

    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.7rem 1.4rem;
    font-weight: 600;
}

div.stButton > button:hover {
    opacity: 0.92;
}

.footer-text {
    text-align: center;
    color: #9ca3af;
    margin-top: 4rem;
    font-size: 0.9rem;
}

.loader {
    width: 18px;
    height: 18px;
    border: 3px solid rgba(255,255,255,0.2);
    border-top: 3px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    100% {
        transform: rotate(360deg);
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================
# HERO SECTION
# =========================================

hero_html = textwrap.dedent("""
<div style="
padding:24px 30px;
border-radius:24px;
background:linear-gradient(135deg,#0f172a,#1e293b);
border:1px solid rgba(255,255,255,0.08);
margin-bottom:24px;
box-shadow:0 0 40px rgba(59,130,246,0.08);
">

<h1 style="
color:white;
font-size:46px;
font-weight:800;
margin-bottom:10px;
">
📊 AI-Powered SQL Analytics Platform
</h1>

<p style="
color:#94a3b8;
font-size:18px;
line-height:1.5;
max-width:1200px;
margin:0;
">
Convert natural language business questions into SQL queries, visual analytics, and AI-generated business insights.
</p>

</div>
""")

st.markdown(hero_html, unsafe_allow_html=True)


# =========================================
# DATABASE + KPI SECTION
# =========================================

try:

    records_query = """
    SELECT COUNT(*) AS total_records
    FROM sales
    """

    sales_query = """
    SELECT ROUND(SUM(sales), 2) AS total_sales
    FROM sales
    """

    profit_query = """
    SELECT ROUND(SUM(profit), 2) AS total_profit
    FROM sales
    """

    records_df = run_query(records_query, database_path)
    sales_df = run_query(sales_query, database_path)
    profit_df = run_query(profit_query, database_path)

    total_records = records_df["total_records"][0]
    total_sales = sales_df["total_sales"][0]
    total_profit = profit_df["total_profit"][0]

    dashboard_tab, ai_tab = st.tabs([
        "📊 Dashboard",
        "🤖 AI Analytics"
    ])

    with dashboard_tab:

        st.markdown(
            '<div class="section-title">Business KPIs</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        def kpi_card(title, value):

            st.markdown(f"""
            <div style="
            background:linear-gradient(145deg,#0f172a,#111827);
            padding:16px 18px;
            border-radius:20px;
            border:1px solid rgba(255,255,255,0.06);
            box-shadow:0 6px 24px rgba(0,0,0,0.25);
            min-height:88px;
            ">

            <div style="
            font-size:14px;
            color:#94a3b8;
            margin-bottom:14px;
            ">
            {title}
            </div>

            <div style="
            font-size:24px;
            font-weight:800;
            color:white;
            ">
            {value}
            </div>

            </div>
            """, unsafe_allow_html=True)

        st.markdown(
            '<div class="section-title">Sample Business Data</div>',
            unsafe_allow_html=True
        )

        preview_query = """
        SELECT *
        FROM sales
        LIMIT 10
        """

        preview_df = run_query(preview_query, database_path)

        st.dataframe(preview_df, use_container_width=True)

        with col1:
            kpi_card(
                "Total Records",
                f"{total_records:,}"
            )

        with col2:
            kpi_card(
                "Total Revenue",
                f"${total_sales:,.0f}"
            )

        with col3:
            kpi_card(
                "Total Profit",
                f"${total_profit:,.0f}"
            )

    with ai_tab:

        st.markdown(
            '<div class="section-title">AI SQL Generator</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="glass-card">
            Ask business questions in natural language.
            The AI generates SQL queries, executes analytics,
            creates charts, and summarizes insights automatically.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("""
            <div style="
            font-size:28px;
            font-weight:700;
            margin-bottom:18px;
            color:white;
            ">
            Suggested Questions
            </div>
            """, unsafe_allow_html=True)       

        q1, q2, q3 = st.columns(3)

        with q1:
            if st.button("Top 5 products by profit"):
                st.session_state["question"] = (
                    "Top 5 products by profit"
                )

        with q2:
            if st.button("Monthly sales trend"):
                st.session_state["question"] = (
                    "Monthly sales trend"
                )

        with q3:
            if st.button("Best performing region"):
                st.session_state["question"] = (
                    "Best performing region"
                )

        user_question = st.text_area(
            "Ask a business question",
            value=st.session_state.get("question", ""),
            placeholder="Example: Show top 5 products by profit",
            height=120
        )

        if st.button("Generate Analytics"):

            if user_question.strip() == "":

                st.warning(
                    "Please enter a business question."
                )

            else:

                st.session_state.query_history.append(
                    user_question
                )

                loading_placeholder = st.empty()

                loading_placeholder.markdown("""
                <div style="
                background:rgba(15,23,42,0.9);
                padding:18px;
                border-radius:16px;
                border:1px solid rgba(255,255,255,0.08);
                margin-top:10px;
                margin-bottom:20px;
                ">

                <div style="
                display:flex;
                align-items:center;
                gap:12px;
                color:white;
                font-weight:600;
                font-size:16px;
                ">

                <div class="loader"></div>

                Generating AI-powered analytics...

                </div>
                </div>
                """, unsafe_allow_html=True)

                generated_sql = generate_sql(
                    user_question,
                    groq_api_key
                )

                generated_sql = clean_sql_query(
                    generated_sql
                )

                is_safe, validation_message = (
                    validate_sql_query(
                        generated_sql
                    )
                )

                loading_placeholder.empty()

                if not is_safe:

                    st.error(validation_message)

                    st.stop()

                st.markdown("""
                <div style="
                font-size:28px;
                font-weight:700;
                margin-bottom:18px;
                color:white;
                ">
                Generated SQL
                </div>
                """, unsafe_allow_html=True)

                st.code(
                    generated_sql.strip(),
                    language="sql"
                )

                try:

                    raw_result = run_query(
                        generated_sql,
                        database_path
                    )

                    query_result = raw_result.copy()

                    st.success("Analytics generated successfully.")

                    st.markdown("""
                    <div style="
                    font-size:28px;
                    font-weight:700;
                    margin-bottom:18px;
                    color:white;
                    ">
                    Analytics Results
                    </div>
                    """, unsafe_allow_html=True)

                    query_result.columns = [
                        col.replace("_", " ").title()
                        for col in query_result.columns
                    ]

                    for col in query_result.columns:

                        if (
                            "Sales" in col
                            or "Profit" in col
                            or "Revenue" in col
                        ):

                            query_result[col] = query_result[col].apply(
                                lambda x: f"${x:,.2f}"
                                if pd.notnull(x)
                                else x
                            )

                    st.dataframe(
                        query_result,
                        use_container_width=True
                    )

                    csv = query_result.to_csv(index=False)

                    download_col1, download_col2 = st.columns([1, 5])

                    with download_col1:

                        st.download_button(
                            label="📥 Export CSV",
                            data=csv,
                            file_name="analytics_results.csv",
                            mime="text/csv"
                        )

                    st.divider()

                    st.markdown("""
                    <div style="
                    font-size:28px;
                    font-weight:700;
                    margin-bottom:18px;
                    color:white;
                    ">
                    Visual Analytics
                    </div>
                    """, unsafe_allow_html=True)

                    generate_chart(raw_result)

                    st.divider()

                    st.markdown("""
                    <div style="
                    font-size:28px;
                    font-weight:700;
                    margin-bottom:18px;
                    color:white;
                    ">
                    AI Business Insights
                    </div>
                    """, unsafe_allow_html=True)

                    with st.spinner(
                        "Generating business insights..."
                    ):

                        insight = generate_business_insight(
                            user_question,
                            raw_result,
                            groq_api_key
                        )

                    st.markdown(
                        f"""
                        <div class="insight-box">
                            {insight}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                except Exception as sql_error:

                    st.error(
                        "The AI generated an invalid SQL query. "
                        "Please try rephrasing your question."
                    )

                    st.code(str(sql_error))

except Exception as e:

    st.error(
        f"Database connection failed: {e}"
    )


# =========================================
# FOOTER
# =========================================

st.markdown(
    """
    <div class="footer-text">
        Built using Python, Streamlit, SQLite,
        Llama 3, Groq API, Pandas, and Plotly.
    </div>
    """,
    unsafe_allow_html=True
)
