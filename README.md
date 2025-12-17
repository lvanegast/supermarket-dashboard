🛒 SuperMarket Analytics Dashboard — Dark Pro Edition

Dashboard interactivo en Streamlit para análisis de ventas, comportamiento de clientes y visualizaciones avanzadas, basado en datos reales de supermercados. Incluye KPIs, visualizaciones dinámicas, clustering y heatmaps.

✨ Características
📊 KPIs Interactivos

Tarjetas animadas con:

💰 Ventas Totales

🧾 Tickets generados

📈 Utilidad total

📊 Margen promedio

📈 Análisis de Ventas

Gráfico de ventas por día

Filtros por ciudad

Mapa de calor: ventas por hora del día vs día de la semana

🛒 Análisis por Categoría de Producto

Ventas por “Product Line”

Barras interactivas con Plotly

👥 Análisis de Clientes

Ventas por género

Ventas por método de pago

Segmentación de clientes con K-Means

🤖 Modelos AI

🔥 Heatmap avanzado (hora × día)

🧩 Clustering inteligente RFM-like
(el módulo de forecast Prophet es opcional y puede activarse si instalas Prophet)

🗂️ Estructura del Proyecto
supermarket-dashboard/
│
├── database/
│   └── sales.db               # Base de datos SQLite
│
├── src/
│   └── app.py                 # Código principal Streamlit
│
├── requirements.txt
├── README.md
└── venv/                      # Opcional

⚙️ Instalación
1. Clonar
git clone https://github.com/lvant/supermarket-dashboard.git
cd supermarket-dashboard

2. Crear entorno virtual (opcional)
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. Instalar dependencias
pip install -r requirements.txt

4. Ejecutar
streamlit run src/app.py

📦 Base de Datos

El archivo SQLite debe estar en:

database/sales.db


Columnas esperadas:

Campo	Descripción
Invoice ID	ID del ticket
Date	Fecha
Time	Hora
City	Ciudad
Product line	Categoría
Payment	Forma de pago
Quantity	Cantidad
Sales	Valor de venta
cogs	Costo
gross income	Utilidad
Rating	Calificación
🎨 Diseño

Tema Dark Pro:

Fondo gris carbón

Tarjetas animadas

Plotly Dark Theme

Tabs estilizadas

KPI cards suaves con hover

📊 Visualizaciones Incluidas

Línea temporal de ventas

Barras comparativas

Pie charts

Clustering K-Means

Heatmap día × hora

Tabla de clientes segmentados

🧠 Dependencias

Archivo requirements.txt:

streamlit
pandas
numpy
plotly
scikit-learn
matplotlib


Si Prophet da error al instalar, se puede comentar.

🤝 Contribuciones

¡Pull requests abiertos!
Ideas sugeridas:

Panel de predicción avanzado

Dashboard móvil

Sistema de alertas

📄 Licencia

Este proyecto utiliza la licencia MIT.