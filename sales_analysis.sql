-- 📊 Proyecto 3: Análisis de Rendimiento de Ventas (SQL & BI)
-- Este archivo contiene consultas SQL clave para el análisis de los datos de ventas.

-- 1. Cálculo del Ingreso Total y Margen de Beneficio por Región
SELECT
    Region,
    SUM(Revenue) AS Total_Revenue,
    SUM(Profit) AS Total_Profit,
    (SUM(Profit) * 100.0 / SUM(Revenue)) AS Profit_Margin_Percentage
FROM
    sales_data
GROUP BY
    Region
ORDER BY
    Total_Profit DESC;

-- 2. Identificación de los 5 Vendedores con Mayor Ingreso
SELECT
    SalesPersonID,
    SUM(Revenue) AS Total_Revenue
FROM
    sales_data
GROUP BY
    SalesPersonID
ORDER BY
    Total_Revenue DESC
LIMIT 5;

-- 3. Análisis de la Distribución de Clientes por Tipo de Producto
SELECT
    ProductCategory,
    CustomerType,
    COUNT(SaleID) AS Number_of_Sales
FROM
    sales_data
GROUP BY
    ProductCategory, CustomerType
ORDER BY
    ProductCategory, Number_of_Sales DESC;

-- 4. Tendencia de Ventas Mensuales (para visualización en BI)
SELECT
    strftime('%Y-%m', SaleDate) AS Sales_Month,
    SUM(Revenue) AS Monthly_Revenue
FROM
    sales_data
GROUP BY
    Sales_Month
ORDER BY
    Sales_Month;

-- 5. Consulta para identificar productos con bajo margen de beneficio
SELECT
    ProductCategory,
    AVG(Revenue) AS Avg_Revenue,
    AVG(Cost) AS Avg_Cost,
    AVG(Profit) AS Avg_Profit
FROM
    sales_data
GROUP BY
    ProductCategory
HAVING
    AVG(Profit) < 1000; -- Asumiendo que un beneficio promedio menor a 1000 es bajo
