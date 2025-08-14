# SuperStore Analytics – ETL & Interactive Dashboard

An **end-to-end data analytics project** built in Python that takes the famous **SuperStore Sales dataset** from raw CSV to a fully interactive dashboard.  
The solution demonstrates best practices in **ETL pipeline design**, **data cleaning**, **curated marts creation**, and **dashboarding** using Plotly/Dash with dynamic filters.

---

## **📖 Project Overview**
This project simulates a production-grade analytics workflow:
1. **Ingestion** – Load SuperStore data from CSV (with cloud ingestion stubs for AWS S3, Azure Blob, Google Cloud Storage, Kaggle).
2. **Transformation** – Clean, enrich, and calculate key KPIs such as Profit Margin, Monthly Sales, and Customer Segmentation.
3. **Storage** – Save cleaned data into a curated CSV mart and query-ready DuckDB database.
4. **Visualization** – Generate:
   - Interactive dashboards with Plotly/Dash
   - Static outlier detection plots using Matplotlib

---