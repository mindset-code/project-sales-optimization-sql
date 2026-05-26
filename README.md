# Sales Optimization SQL — Business Intelligence Portfolio

> **BI / RevOps Portfolio Project** · SQL · Sales Performance · Profitability
> **Status:** Finished · Portfolio showcase (2026-04)

[![Portfolio](https://img.shields.io/badge/Portfolio-proyectos--personales.web.app-60a5fa?style=for-the-badge&logo=firebase&logoColor=white)](https://proyectos-personales.web.app)
[![SQL](https://img.shields.io/badge/Language-SQL-4479A1?style=for-the-badge&logo=postgresql&logoColor=white)](.)
[![Wiki](https://img.shields.io/badge/Wiki-Documentación-38bdf8?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mindset-code/project-sales-optimization-sql/wiki)

---

## Project Status

| Phase | Status |
|---|---|
| Synthetic dataset (10,000 sales records) | Done |
| 5 analytical SQL queries | Done |
| Business findings documentation | Done |
| Ready for Power BI / Tableau connection | Done |

**Current phase:** portfolio showcase — listo para reutilizar en dashboards BI.

---

## Project Overview

Análisis de rendimiento de ventas y rentabilidad usando **SQL** puro y principios de **Business Intelligence** para generar *insights* de negocio. Alineado con experiencia previa en **SalesOps / RevOps**: identifica regiones rentables, vendedores estrella, estacionalidades y productos con bajo margen.

Las consultas están diseñadas para conectarse directamente a **Power BI** o **Tableau** como fuente de un dashboard comercial.

---

## Skills Demostradas

- **SQL Avanzado:** agregaciones (`SUM`, `AVG`), agrupamiento (`GROUP BY`) y filtrado (`HAVING`)
- **Business Intelligence:** definición de métricas clave (Ingreso Total, Margen de Beneficio, Rendimiento por Vendedor)
- **Análisis de Rentabilidad:** identificación de áreas de alto y bajo rendimiento
- **Data Storytelling:** preparación de datos para visualización en Power BI / Tableau
- **RevOps mindset:** conectar métricas técnicas a decisiones de negocio

---

## Hallazgos Clave

1. **Regiones más rentables** y su margen de beneficio
2. **Vendedores de alto rendimiento** que merecen reconocimiento o replicación de sus estrategias
3. **Tendencia de ventas** a lo largo del tiempo y patrones de estacionalidad
4. **Productos o categorías con bajo margen** que requieren revisión de precios o costos

---

## Tech Stack

| Layer | Technology |
|---|---|
| Query language | SQL (portable: SQLite, PostgreSQL, MySQL) |
| Data generation | Python 3.12, Pandas |
| BI target | Power BI · Tableau |

---

## Repository Structure

```
project-sales-optimization-sql/
├── sales_data.csv           # 10,000 registros sintéticos de ventas
├── generate_data.py         # generador del dataset
└── sales_analysis.sql       # 5 queries de análisis y rentabilidad
```

---

## How to Run

```bash
# 1. Clonar el repositorio
git clone https://github.com/mindset-code/project-sales-optimization-sql.git
cd project-sales-optimization-sql

# 2. Cargar el CSV en SQLite / PostgreSQL / MySQL
# (ejemplo con SQLite)
sqlite3 sales.db
.mode csv
.import sales_data.csv sales

# 3. Ejecutar las queries
.read sales_analysis.sql

# 4. (Opcional) Conectar la DB a Power BI o Tableau
```

---

## Links

- **Wiki:** [Documentación técnica](https://github.com/mindset-code/project-sales-optimization-sql/wiki)
- **Portfolio:** [proyectos-personales.web.app](https://proyectos-personales.web.app)
- **LinkedIn:** [Mindset & Code](https://www.linkedin.com/company/mindset-code)
- **Email:** contacto@mindset-code.com

---

*Built by [Mindset & Code](https://github.com/mindset-code) · Data & BI Analyst · MBA · ISC2 CC*
