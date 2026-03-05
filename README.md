# 🛒 SuperMarket Analytics Dashboard — Glassmorphism Edition

Dashboard interactivo en Streamlit para analisis de ventas, comportamiento de clientes y visualizaciones avanzadas, basado en datos reales de supermercados. Incluye KPIs animados, visualizaciones dinamicas, clustering y heatmaps con un diseno **glassmorphism** moderno y profesional.

## ✨ Caracteristicas

### 📊 KPIs Interactivos

Tarjetas con efecto vidrio esmerilado (glassmorphism) y animaciones:

- 💰 Ventas Totales con delta vs periodo anterior
- 🧾 Tickets generados
- 📈 Utilidad total
- 📊 Margen promedio
- 🎫 Ticket promedio
- ⭐ Rating promedio
- 🏪 Sucursales activas

### 📈 Analisis de Ventas

- Tendencia diaria/semanal con opcion de desglose por sucursal
- Ventas acumuladas con area chart
- Filtros interactivos en sidebar

### 🛒 Analisis por Categoria de Producto

- Ventas y utilidad por linea de producto (barras horizontales)
- Ticket promedio por categoria
- Tabla resumen con metricas agregadas

### 👥 Analisis de Clientes

- Ventas por genero y metodo de pago (donut charts)
- Comparacion Miembros vs Normales
- Treemap de distribucion de ventas
- Rating por segmento

### 🤖 Modelos AI

- 🔥 Heatmap avanzado: ventas por hora x dia de la semana (total/promedio)
- 🧩 Clustering K-Means con visualizacion 3D interactiva
- Silhouette Score y grafico del Codo (Elbow)
- Tabla de detalle por cluster

### 📥 Datos

- Visualizacion de datos filtrados en tabla interactiva
- Descarga de datos en formato CSV

## 🎨 Diseno Glassmorphism

El dashboard utiliza un sistema de diseno **glassmorphism** con:

- **Efecto vidrio esmerilado**: `backdrop-filter: blur()` en tarjetas, sidebar, tabs y graficos
- **Fondo con gradient mesh animado**: Gradientes radiales sutiles con animacion pulsante
- **Hero header**: Titulo con gradiente animado y strip de estadisticas rapidas
- **Sidebar premium**: Logo animado con gradiente, secciones estilizadas
- **KPI cards con efectos**: Bordes con gradiente animado, shimmer al hover, elevacion y glow
- **Tabs con glow**: Estilo pill con efecto luminoso en tab activa
- **Charts en contenedores glass**: Cada grafico envuelto en contenedor con efecto vidrio
- **Animaciones CSS**: fadeInUp, shimmer, pulse, glowPulse, gradientShift, borderGlow
- **Footer glass**: Con links estilizados y efecto hover luminoso
- **Responsive**: Ajustes automaticos para pantallas pequenas

### Paleta de Colores

| Color | Hex | Uso |
|-------|-----|-----|
| Indigo | `#6366f1` | Color primario |
| Indigo Light | `#818cf8` | Gradientes y acentos |
| Emerald | `#10b981` | Indicadores positivos |
| Amber | `#f59e0b` | Advertencias |
| Red | `#ef4444` | Indicadores negativos |
| Pink | `#ec4899` | Acentos secundarios |
| Cyan | `#06b6d4` | Graficos |
| Violet | `#8b5cf6` | Bordes glass |

## 🗂️ Estructura del Proyecto

```
supermarket-dashboard/
├── data/
│   └── SuperMarket.csv          # Datos fuente (1,000 registros)
├── database/
│   └── sales.db                 # Base de datos SQLite (generada)
├── src/
│   ├── app.py                   # Dashboard principal Streamlit
│   └── load_data.py             # Script ETL: CSV → SQLite
├── .streamlit/
│   └── config.toml              # Configuracion del tema
├── requirements.txt
├── CLAUDE.md
├── README.md
└── venv/                        # Entorno virtual (opcional)
```

## ⚙️ Instalacion

### 1. Clonar

```bash
git clone https://github.com/lvant/supermarket-dashboard.git
cd supermarket-dashboard
```

### 2. Crear entorno virtual (opcional)

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Cargar datos en SQLite

```bash
python src/load_data.py
```

### 5. Ejecutar

```bash
streamlit run src/app.py
```

## 📦 Base de Datos

El archivo SQLite se genera en `database/sales.db` a partir del CSV fuente.

| Campo | Descripcion |
|-------|-------------|
| Invoice ID | ID del ticket |
| Branch | Sucursal (A, B, C) |
| City | Ciudad |
| Customer type | Miembro o Normal |
| Gender | Genero |
| Product line | Categoria de producto |
| Unit price | Precio unitario |
| Quantity | Cantidad |
| Tax 5% | Impuesto |
| Sales | Valor de venta |
| Date | Fecha |
| Time | Hora |
| Payment | Forma de pago |
| cogs | Costo de bienes |
| gross margin percentage | Margen bruto % |
| gross income | Utilidad bruta |
| Rating | Calificacion (1-10) |

## 🧠 Dependencias

```
streamlit==1.39.0
pandas==2.2.3
numpy==2.1.2
plotly==5.24.1
scikit-learn==1.5.2
```

> Si scikit-learn no esta disponible, la pestana de Modelos muestra un aviso y el resto del dashboard funciona normalmente.

## 🤝 Contribuciones

Pull requests abiertos. Ideas sugeridas:

- Panel de prediccion avanzado (Prophet/series de tiempo)
- Dashboard movil optimizado
- Sistema de alertas con umbrales configurables
- Modo claro/oscuro con toggle

## 📄 Licencia

Este proyecto utiliza la licencia MIT.
