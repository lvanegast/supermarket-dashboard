# 🛒 SuperMarket Analytics Pro v2.0 — Enterprise Retail Intelligence

[![CI Pipeline](https://github.com/lvant/supermarket-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/lvant/supermarket-dashboard/actions/workflows/ci.yml)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io)
[![DuckDB](https://img.shields.io/badge/DuckDB-OLAP%20Engine-FFF000.svg)](https://duckdb.org)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

Plataforma integral de analítica comercial, inteligencia de retail y pronósticos de demanda con Machine Learning, impulsada por **Streamlit Multi-Page**, un motor **OLAP columnar con DuckDB** y una interfaz moderna con diseño ejecutivo **Executive Dark Glassmorphism**.

---

## 🚀 Nuevas Funcionalidades & Módulos de I+D (v2.0)

### 1. 📊 Panel Ejecutivo (Executive Overview)
- **KPIs en tiempo real con deltas porcentuales** calculados contra el período anterior equivalente.
- Diagnósticos dinámicos automatizados sobre la sucursal y categoría líderes.
- Visualización de tendencias temporales (diarias/semanales) y descomposición por sucursal.
- Mapas de calor comerciales de intensidad horaria por día de la semana.

### 2. 📈 Pronóstico Predictivo & Control de Stock (Demand Forecasting)
- Modelado de series de tiempo con **Holt-Winters / Exponential Smoothing** con estacionalidad semanal.
- Intervalos de confianza ajustables (90% y 95%).
- **Matriz de Stock de Seguridad & Puntos de Reorden (ROP):** Cálculo estocástico de inventario de seguridad basado en la desviación de la demanda y el *lead time* del proveedor para prevenir quiebres de stock.

### 3. 🛒 Rendimiento de Productos & Market Basket Analysis
- Matriz de posicionamiento por categoría: volumen de facturación vs margen porcentual.
- **Minería de Reglas de Asociación (Cross-Selling):** Cálculo de Soporte, Confianza y Elevación (*Lift*) para descubrir patrones de co-compra.
- Recomendador dinámico de *Packs Promocionales* y combos para incrementar el ticket promedio.

### 4. 👥 Inteligencia de Clientes & Segmentación RFM
- Segmentación conductual avanzada con **K-Means y Silhouette Score**.
- Identificación de segmentos clave: *Clientes VIP / Alto Valor*, *Compradores Frecuentes*, *En Riesgo*, *Ocasionales*.
- Visualizador interactivo 3D (Recencia vs Gasto Monetario vs Calificación).
- Comparativa profunda de hábitos: *Miembros* vs *Clientes Regulares*.

### 5. 🤖 Retail AI Copilot
- Asistente analítico conversacional para responder preguntas comerciales en lenguaje natural.
- Sugerencias rápidas ("chips") para consultas frecuentes: márgenes, horas pico, medios de pago.
- Respuestas instantáneas calculadas directamente sobre los datos en memoria.

### 6. ⚡ Simulador de Escenarios Comerciales ("What-If")
- Simulación financiera de impacto antes de lanzar promociones:
  - Variación porcentual de descuento.
  - Factor de elasticidad precio-demanda.
  - Inflación o incremento en el costo de la mercancía (COGS).
- Comparativa visual de ventas base vs ventas proyectadas y alertas de destrucción de margen.

### 7. 📥 Explorador de Datos & Consola SQL DuckDB
- Explorador interactivo con soporte de configuración avanzada de columnas (`st.column_config`).
- **Consola SQL en vivo:** Permite a analistas y directores ejecutar consultas analíticas directas sobre DuckDB.
- Exportación en formatos CSV y **Apache Parquet columnar**.

---

## 🏗️ Arquitectura Modular del Proyecto

```
supermarket-dashboard/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Pipeline CI con tests automáticos
│       └── deploy.yml             # Despliegue en producción
├── assets/
│   └── css/
│       └── glassmorphism.css      # Sistema de diseño Executive Dark Glassmorphism
├── data/
│   └── SuperMarket.csv            # Dataset POS (1,000 registros transaccionales)
├── database/
│   ├── sales.duckdb               # Base de datos OLAP columnar
│   └── sales.db                   # Base de datos SQLite
├── src/
│   ├── components/                # Componentes UI reutilizables
│   │   ├── charts.py              # Visualizaciones estandarizadas en Plotly
│   │   ├── filters.py             # Sidebar de filtrado interactivo
│   │   └── kpi_card.py            # Tarjetas de métricas con indicadores delta
│   ├── core/                      # Configuración y temas
│   │   ├── config.py              # Paletas de color, constantes y rutas
│   │   └── theme.py               # Inyector de CSS y estilos de gráficos
│   ├── data/                      # Capa de persistencia y acceso a datos
│   │   └── db.py                  # Motor DuckDB / SQLite y cálculos de KPIs
│   ├── models/                    # Algoritmos de Machine Learning y Analítica
│   │   ├── basket_analysis.py     # Reglas de asociación y canasta de compra
│   │   ├── forecasting.py         # Pronóstico de series de tiempo y stock ROP
│   │   └── rfm_clustering.py      # Segmentación conductual RFM
│   ├── pages/                     # Páginas nativas de Streamlit Multi-Page
│   │   ├── 1_📊_Overview.py
│   │   ├── 2_📈_Forecast.py
│   │   ├── 3_🛒_Products_Basket.py
│   │   ├── 4_👥_Customers_RFM.py
│   │   ├── 5_🤖_AI_Copilot.py
│   │   ├── 6_⚡_What_If_Simulator.py
│   │   └── 7_📥_Data_Explorer.py
│   ├── app.py                     # Entrypoint orquestador con st.navigation
│   └── load_data.py               # Script ETL DuckDB + SQLite
├── tests/                         # Suite de pruebas automatizadas
│   ├── test_data_db.py
│   └── test_models.py
├── Dockerfile                     # Contenedorización multi-stage
├── docker-compose.yml             # Orquestación de contenedores
├── requirements.txt               # Dependencias del proyecto
└── README.md
```

---

## ⚡ Instalación y Puesta en Marcha

### Opción A: Entorno Virtual Local (Recomendado para Desarrollo)

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/lvant/supermarket-dashboard.git
   cd supermarket-dashboard
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Cargar la base de datos (DuckDB y SQLite):**
   ```bash
   python src/load_data.py
   ```

5. **Iniciar el dashboard:**
   ```bash
   streamlit run src/app.py
   ```

---

### Opción B: Ejecución con Docker

1. **Construir y levantar el contenedor:**
   ```bash
   docker compose up --build -d
   ```

2. Accede a tu navegador en: `http://localhost:8501`.

---

## 🧪 Pruebas Automatizadas

Para ejecutar la suite de pruebas unitarias con `pytest`:
```bash
pytest tests/ -v
```

---

## 📄 Licencia

Este proyecto se encuentra bajo la licencia MIT.
