# 🛒 SuperMarket Analytics Dashboard — Glassmorphism Edition

Interactive Streamlit dashboard for sales analysis, customer behavior, and advanced visualizations using real supermarket data. Includes animated KPIs, dynamic charts, clustering, and heatmaps with a modern, professional glassmorphism design.

## 🎬 Demo

![Dashboard demo](video.gif)

## ✨ Features

### 📊 Interactive KPIs

Glassmorphism cards with animations:

- 💰 Total sales with delta vs previous period
- 🧾 Transactions
- 📈 Total profit
- 📊 Average margin
- 🎫 Average ticket
- ⭐ Average rating
- 🏪 Active branches

### 📈 Sales Analysis

- Daily/weekly trend with optional branch split
- Cumulative sales area chart
- Interactive sidebar filters

### 🛒 Product Category Analysis

- Sales and profit by product line (horizontal bars)
- Average ticket by category
- Summary table with aggregated metrics

### 👥 Customer Analysis

- Sales by gender and payment method (donut charts)
- Members vs Normal comparison
- Sales distribution treemap
- Rating by segment

### 🤖 AI Models

- 🔥 Advanced heatmap: sales by hour x day of week (total/average)
- 🧩 K-Means clustering with interactive 3D visualization
- Silhouette Score and Elbow chart
- Cluster detail table

### 📥 Data

- Filtered data table
- CSV download

## 🎨 Glassmorphism Design

The dashboard uses a **glassmorphism** design system with:

- **Frosted glass effect**: `backdrop-filter: blur()` on cards, sidebar, tabs, and charts
- **Animated gradient mesh background**: subtle radial gradients with pulsing animation
- **Hero header**: animated gradient title and quick stats strip
- **Premium sidebar**: animated logo and styled sections
- **KPI cards with effects**: animated gradient borders, hover shimmer, elevation, and glow
- **Glowing tabs**: pill style with luminous active tab
- **Glass chart containers**: each chart wrapped in a glass container
- **CSS animations**: fadeInUp, shimmer, pulse, glowPulse, gradientShift, borderGlow
- **Glass footer**: styled links with glow hover
- **Responsive**: automatic adjustments for small screens

### Color Palette

| Color | Hex | Use |
|-------|-----|-----|
| Indigo | `#6366f1` | Primary color |
| Indigo Light | `#818cf8` | Gradients and accents |
| Emerald | `#10b981` | Positive indicators |
| Amber | `#f59e0b` | Warnings |
| Red | `#ef4444` | Negative indicators |
| Pink | `#ec4899` | Secondary accents |
| Cyan | `#06b6d4` | Charts |
| Violet | `#8b5cf6` | Glass borders |

## 🗂️ Project Structure

```
supermarket-dashboard/
├── data/
│   └── SuperMarket.csv          # Source data (1,000 records)
├── database/
│   └── sales.db                 # SQLite database (generated)
├── src/
│   ├── app.py                   # Main Streamlit dashboard
│   └── load_data.py             # ETL script: CSV → SQLite
├── .gitignore
├── README.md
├── requirements.txt
├── .venv/                       # Virtual environment (optional, local)
└── .vscode/                     # Editor settings (optional, local)
```

## ⚙️ Installation

### 1. Clone

```bash
git clone https://github.com/lvant/supermarket-dashboard.git
cd supermarket-dashboard
```

### 2. Create a virtual environment (optional)

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Load data into SQLite

```bash
python src/load_data.py
```

### 5. Run

```bash
streamlit run src/app.py
```

## 📦 Database

The SQLite file is generated at `database/sales.db` from the source CSV.

| Field | Description |
|-------|-------------|
| Invoice ID | Receipt ID |
| Branch | Branch (A, B, C) |
| City | City |
| Customer type | Member or Normal |
| Gender | Gender |
| Product line | Product category |
| Unit price | Unit price |
| Quantity | Quantity |
| Tax 5% | Tax |
| Sales | Sales value |
| Date | Date |
| Time | Time |
| Payment | Payment method |
| cogs | Cost of goods sold |
| gross margin percentage | Gross margin % |
| gross income | Gross income |
| Rating | Rating (1-10) |

## 🧠 Dependencies

```
streamlit==1.39.0
pandas==2.2.3
numpy==2.1.2
plotly==5.24.1
scikit-learn==1.5.2
```

> If scikit-learn is not available, the Models tab shows a warning and the rest of the dashboard works normally.
