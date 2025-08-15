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

## 🏢 Storytelling for Stakeholders
The dashboard tells a **business story**:
- **Growth patterns**: Monthly sales & profit trends reveal seasonal spikes
- **Category performance**: Identify high-performing categories vs. underperformers
- **Regional focus**: Heatmaps uncover strong/weak regional sales areas
- **Profit discipline**: Highlight products with low margins for pricing or discount strategy reviews

This enables **data-driven decision-making** for sales, marketing, and operations teams.


---

## **📂 Project Structure**
```
superstore_etl/
├─ data/
│  ├─ raw/                     # Put raw superstore.csv here (or use cloud ingestion)
│  └─ curated/                 # Cleaned/enriched data + marts written here
├─ artifacts/
│  └─ plots/                   # Saved Matplotlib figures (e.g., outlier visuals)
├─ src/
│  ├─ config.py                # Paths & constants
│  ├─ main.py                  # CLI entrypoint: run ETL or Dashboard
│  ├─ utils/
│  │  ├─ io.py                 # CSV I/O helpers
│  │  └─ dates.py              # Date parsing & helpers
│  ├─ ingest/
│  │  └─ readers.py            # Local/Cloud ingestion (S3/Azure/GCS/Kaggle)
│  ├─ transform/
│  │  ├─ cleaning.py           # Data cleaning rules
│  │  ├─ enrich.py             # Derived fields (profit margin, order month)
│  │  ├─ outliers.py           # IQR flags + Matplotlib outlier plots
│  │  └─ features.py           # KPI aggregates used by marts & viz
│  ├─ model/
│  │  └─ marts.py              # Build curated marts (fact/dim/monthly)
│  ├─ sql/
│  │  └─ duckdb_utils.py       # Query curated CSVs with DuckDB
│  └─ viz/
│     ├─ charts_matplotlib.py  # Reusable static charts (export)
│     └─ dashboard.py          # Plotly Dash single-page app
├─ requirements.txt
└─ README.md
```

---

## **🚀 Features**
- **ETL Pipeline** with modular functions (no notebooks, production style).
- **Cloud-Ready Ingestion**:
  - AWS S3 via `boto3`
  - Azure Blob Storage via `azure-storage-blob`
  - Google Cloud Storage via `google-cloud-storage`
  - Kaggle API integration
- **Data Cleaning & Enrichment**:
  - Handle missing/duplicate values
  - Profit Margin calculation
  - Monthly sales aggregation
- **Outlier Detection**:
  - IQR method with boxplot visuals
- **Interactive Dashboard**:
  - Filters: Date range, Region, Category, Segment
  - KPIs: Total Sales, Profit, Orders
  - Charts: Time series, category bars, Region×Category heatmap, top products
- **SQL Access** to curated marts via DuckDB

---

## **🛠 Installation**
```bash
# Clone the repository
git clone https://github.com/sahil095/Superstore-etl.git
cd Superstore-etl

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # For Linux/Mac
# .venv\Scripts\activate   # For Windows

# Install dependencies
pip install -r requirements.txt
```

📥 Data Ingestion
Local CSV (default)

Place your SuperStore dataset in:
```bash
data/raw/superstore.csv
```
Cloud ingestion examples (commented in ingestion.py):
# From AWS S3
```bash
s3_client.download_file('bucket-name', 'path/to/file.csv', 'data/raw/superstore.csv')
```
# From Azure Blob Storage
```bash
blob_client.download_blob().readinto(open('data/raw/superstore.csv', 'wb'))
```
# From Google Cloud Storage
```bash
bucket.blob('path/to/file.csv').download_to_filename('data/raw/superstore.csv')
```
# From Kaggle
```bash
!kaggle datasets download -d <dataset-identifier> -p data/raw --unzip
```
▶ Running the Pipeline

Run the ETL process:
```bash
python -m src.main --run etl
```

Run the dashboard:
```bash
python -m src.main --run dash
```
📊 Dashboard Preview

KPIs – Total Sales, Profit, Orders

Filters – Date, Region, Category, Segment

Charts:

Monthly Sales & Profit Trend

Sales by Category

Region × Category Heatmap

Top Products by Sales

Responsive Design – Works on desktop & tablet

📈 Outlier Detection

Generate and save outlier plots:
```bash
python -m src.main --run outliers
```

Plots are stored in:

plots/outliers/


📜 License

This project is licensed under the MIT License – see the LICENSE file for details.

🤝 Contributing

Pull requests are welcome!
For major changes, please open an issue first to discuss what you would like to change.

📧 Contact

GitHub: https://github.com/sahil095

---

## **LICENSE** (MIT License)
```text
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all  
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
SOFTWARE.