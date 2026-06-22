"""Local Streamlit dashboard for NexCart.

Run from the repository root:
    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
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
from app.recommender import (  # noqa: E402
    get_customer_detail,
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
        "Use the sidebar to check database row counts, generate recommendations, "
        "view analytics, inspect performance results, and refresh precomputed "
        "recommendation scores."
    )

elif page == "Database Summary":
    st.subheader("Database Summary")
    if ok:
        counts = get_row_counts()
        st.dataframe(counts, use_container_width=True, hide_index=True)
        st.bar_chart(counts.set_index("table_name"))
    else:
        st.warning("Fix the database connection before viewing row counts.")

elif page == "Recommendation Engine":
    st.subheader("Top-N Product Recommendations")
    st.write(
        "Select a customer ID and generate recommendations. The main query uses "
        "CTEs and SQL window functions to rank products bought by similar customers."
    )

    if ok:
        sample_ids = get_sample_customer_ids(200)
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_customer = st.selectbox("Select customer_id", sample_ids)
            custom_customer = st.text_input("Or paste another customer_id", value="")
            customer_id = custom_customer.strip() or selected_customer
        with col2:
            top_n = st.slider("Number of recommendations", min_value=3, max_value=20, value=10)

        detail = get_customer_detail(customer_id)
        st.write("Customer details")
        st.dataframe(detail, use_container_width=True, hide_index=True)

        if st.button("Generate Recommendations", type="primary"):
            with st.spinner("Running recommendation query..."):
                recs, note = get_recommendations(customer_id, top_n)
            st.success(note)
            st.dataframe(recs, use_container_width=True, hide_index=True)
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
            st.dataframe(state_df, use_container_width=True, hide_index=True)
            st.bar_chart(state_df.set_index("customer_state"))
        with c2:
            review_df = get_review_summary()
            st.write("Review score distribution")
            st.dataframe(review_df, use_container_width=True, hide_index=True)
            st.bar_chart(review_df.set_index("review_score"))

        category_df = get_category_sales(15)
        st.write("Top product categories")
        st.dataframe(category_df, use_container_width=True, hide_index=True)
        st.bar_chart(category_df.set_index("product_category_name")[["total_items_sold"]])

        payment_df = get_payment_summary()
        st.write("Payment method summary")
        st.dataframe(payment_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Fix the database connection before viewing analytics.")

elif page == "Performance Evidence":
    st.subheader("Performance Evidence")
    st.write(
        "The performance script benchmarks selected queries before and after index creation. "
        "The values shown here come from the local PostgreSQL run captured in performance_output.txt."
    )

    perf = PERFORMANCE_SUMMARY.copy()
    st.dataframe(perf, use_container_width=True, hide_index=True)

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
        "The performance SQL file creates `product_recommendation_scores` and the stored "
        "procedure `refresh_product_recommendation_scores()`. Use this page to refresh and "
        "display the precomputed scores."
    )

    if ok:
        if st.button("Refresh recommendation scores", type="primary"):
            try:
                refresh_recommendation_scores()
                st.success("Stored procedure executed successfully.")
            except Exception as exc:
                st.error(f"Could not run the stored procedure: {exc}")
                st.info("Run queries/performance.sql once before using this page.")

        try:
            scores = get_precomputed_scores(10)
            st.dataframe(scores, use_container_width=True, hide_index=True)
            if not scores.empty:
                st.bar_chart(scores.set_index("product_id")[["recommendation_score"]])
        except Exception as exc:
            st.warning(f"Score table not available yet: {exc}")
            st.info("Run queries/performance.sql first to create the score table and procedure.")
    else:
        st.warning("Fix the database connection before running stored procedure demo.")
