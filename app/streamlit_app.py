"""Local Streamlit dashboard for NexCart.

Run from the repository root:
    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.analytics import (  # noqa: E402
    PERFORMANCE_SUMMARY,
    get_category_sales,
    get_orders_by_state,
    get_payment_summary,
    get_review_summary,
    get_row_counts,
)
from app.db import test_connection  # noqa: E402
from app.display import to_display_df, translate_values  # noqa: E402
from app.recommender import (  # noqa: E402
    get_customer_detail,
    get_demo_customer_ids,
    get_precomputed_scores,
    get_recommendations,
    get_sample_customer_ids,
    refresh_recommendation_scores,
)

st.set_page_config(
    page_title="NexCart Recommendation System",
    page_icon="🛒",
    layout="wide",
)

st.title("🛒 NexCart - E-commerce Recommendation System")
st.caption("Z2004 DBMS Project | PostgreSQL + Streamlit + SQL-based collaborative filtering")

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Choose a section",
        [
            "Home",
            "Database Summary",
            "Recommendation Engine",
            "SQL Analytics",
            "Performance Evidence",
            "Stored Procedure Demo",
        ],
    )
    st.divider()
    ok, message = test_connection()
    if ok:
        st.success("Database connected")
    else:
        st.error("Database connection failed")
    with st.expander("Connection details"):
        st.write(message)


def customer_recommendation_widget(widget_key: str = "main") -> None:
    """Reusable customer-ID recommendation UI."""
    demo_customers = get_demo_customer_ids(15)
    demo_ids = demo_customers["customer_id"].tolist()

    st.write("**15 demo Customer IDs**")
    st.caption("Use any of these during the demo to show that the output changes with the selected customer.")
    st.dataframe(to_display_df(demo_customers), use_container_width=True, hide_index=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_customer = st.selectbox(
            "Select Customer ID",
            demo_ids if demo_ids else get_sample_customer_ids(200),
            key=f"{widget_key}_select_customer",
        )
        custom_customer = st.text_input(
            "Or paste another Customer ID",
            value="",
            key=f"{widget_key}_custom_customer",
        )
        customer_id = custom_customer.strip() or selected_customer
    with col2:
        top_n = st.slider(
            "Number of recommendations",
            min_value=3,
            max_value=20,
            value=10,
            key=f"{widget_key}_top_n",
        )

    detail = get_customer_detail(customer_id)
    st.write("Customer details")
    st.dataframe(to_display_df(detail), use_container_width=True, hide_index=True)

    if st.button("Generate Recommendations", type="primary", key=f"{widget_key}_generate"):
        with st.spinner("Running customer-specific recommendation query..."):
            recs, note = get_recommendations(customer_id, top_n)
        st.success(note)
        st.dataframe(to_display_df(recs), use_container_width=True, hide_index=True)
        st.caption(
            "Rows marked as collaborative filtering come from similar-customer overlap. "
            "Rows marked as popularity fallback are used only when a sparse customer does not produce enough overlap-based candidates."
        )


if page == "Home":
    st.subheader("Project Overview")
    st.write(
        "NexCart is a relational e-commerce recommendation system built on the "
        "Olist marketplace dataset. The database stores customers, sellers, "
        "products, orders, order items, payments, and reviews in PostgreSQL. "
        "The application uses transaction history to recommend products for a "
        "selected customer."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Database", "PostgreSQL")
    c2.metric("App", "Local Streamlit")
    c3.metric("Track", "B - Recommendation Engine")

    st.info(
        "Use the sidebar to check database row counts, generate customer-specific recommendations, "
        "view analytics, inspect performance results, and refresh precomputed recommendation scores."
    )

elif page == "Database Summary":
    st.subheader("Database Summary")
    if ok:
        counts = get_row_counts()
        st.dataframe(to_display_df(counts), use_container_width=True, hide_index=True)
        counts_chart = translate_values(counts)
        st.bar_chart(counts_chart.set_index("table_name"))
    else:
        st.warning("Fix the database connection before viewing row counts.")

elif page == "Recommendation Engine":
    st.subheader("Top-N Product Recommendations")
    st.write(
        "Select a customer ID and generate recommendations. The main query uses "
        "CTEs and SQL window functions to rank products bought by similar customers."
    )

    if ok:
        customer_recommendation_widget("recommendation_page")
    else:
        st.warning("Fix the database connection before generating recommendations.")

elif page == "SQL Analytics":
    st.subheader("SQL Analytics")
    st.write("These charts are generated from SQL queries over the PostgreSQL tables.")

    if ok:
        c1, c2 = st.columns(2)
        with c1:
            state_df = get_orders_by_state(15)
            st.write("Top customer states by order count")
            st.dataframe(to_display_df(state_df), use_container_width=True, hide_index=True)
            st.bar_chart(state_df.set_index("customer_state"))
        with c2:
            review_df = get_review_summary()
            st.write("Review score distribution")
            st.dataframe(to_display_df(review_df), use_container_width=True, hide_index=True)
            st.bar_chart(review_df.set_index("review_score"))

        category_df = get_category_sales(15)
        st.write("Top product categories")
        st.dataframe(to_display_df(category_df), use_container_width=True, hide_index=True)
        category_chart = translate_values(category_df)
        st.bar_chart(category_chart.set_index("product_category_name")[["total_items_sold"]])

        payment_df = get_payment_summary()
        st.write("Payment method summary")
        st.dataframe(to_display_df(payment_df), use_container_width=True, hide_index=True)
    else:
        st.warning("Fix the database connection before viewing analytics.")

elif page == "Performance Evidence":
    st.subheader("Performance Evidence")
    st.write(
        "The performance script benchmarks selected queries before and after index creation. "
        "The values shown here come from the local PostgreSQL run captured in performance_output.txt."
    )

    perf = PERFORMANCE_SUMMARY.copy()
    st.dataframe(to_display_df(perf), use_container_width=True, hide_index=True)

    chart_df = perf.dropna(subset=["before_index_ms", "after_index_ms"])[
        ["query", "before_index_ms", "after_index_ms"]
    ].set_index("query")
    st.bar_chart(chart_df)

    st.markdown(
        "**Interpretation:** Indexing strongly improved the customer-specific lookup because "
        "the plan changed from a sequential scan on `orders` to an index scan on `customer_id`. "
        "The top-selling-products query improved moderately because it still needs to aggregate "
        "all order items. The seller revenue query became slower in this run because it still "
        "processed almost the whole `order_items` table."
    )

elif page == "Stored Procedure Demo":
    st.subheader("Stored Procedure / Recommendation Score Refresh")
    st.write(
        "This page demonstrates the database-side stored procedure and also lets you run "
        "customer-specific recommendations. The stored procedure refreshes global product score data; "
        "the customer-specific generator below uses the collaborative-filtering query."
    )

    if ok:
        if st.button("Refresh global recommendation scores", type="primary"):
            try:
                refresh_recommendation_scores()
                st.success("Stored procedure executed successfully.")
            except Exception as exc:
                st.error(f"Could not run the stored procedure: {exc}")
                st.info("Run queries/performance.sql once before using this page.")

        try:
            st.write("Global precomputed scores from `product_recommendation_scores`")
            scores = get_precomputed_scores(10)
            st.dataframe(to_display_df(scores), use_container_width=True, hide_index=True)
        except Exception as exc:
            st.warning(f"Score table not available yet: {exc}")
            st.info("Run queries/performance.sql first to create the score table and procedure.")

        st.divider()
        st.subheader("Customer-specific recommendation test")
        st.write(
            "Use this section during the demo to prove that the recommendation output changes "
            "when a different Customer ID is selected."
        )
        customer_recommendation_widget("stored_proc_page")
    else:
        st.warning("Fix the database connection before running stored procedure demo.")
