Select * from [Ecomerce_Sales].[dbo].Customer
Select * from [Ecomerce_Sales].[dbo].[Order]
Select * from [Ecomerce_Sales].[dbo].OrderItem
Select * from [Ecomerce_Sales].[dbo].PriceHistory
Select * from [Ecomerce_Sales].[dbo].Product
Select * from [Ecomerce_Sales].[dbo].Variant
Select * from [Ecomerce_Sales].[dbo].Sales


--Q1
WITH Last6MonthsOrders AS (
    SELECT 
        O.CustomerID,
        O.TotalAmount
    FROM 
        [Order] O
    WHERE 
        O.OrderDate >= DATEADD(MONTH, -6, GETDATE())
),
CustomerAvgOrderAmount AS (
    SELECT 
        CustomerID,
        AVG(TotalAmount) AS AvgOrderAmount
    FROM 
        Last6MonthsOrders
    GROUP BY 
        CustomerID
)
SELECT TOP 5
    C.Name,
    C.Email,
    CAOA.AvgOrderAmount
FROM 
    CustomerAvgOrderAmount CAOA
JOIN 
    Customer C ON C.CustomerID = CAOA.CustomerID
ORDER BY 
    CAOA.AvgOrderAmount DESC;



--Q2
WITH OrderValue AS (
    SELECT 
        CustomerID,
        YEAR(OrderDate) AS OrderYear,
        SUM(TotalAmount) AS TotalOrderValue
    FROM 
        [Order]
    GROUP BY 
        CustomerID, YEAR(OrderDate)
),
CurrentYear AS (
    SELECT 
        CustomerID,
        TotalOrderValue AS CurrentYearValue
    FROM 
        OrderValue
    WHERE 
        OrderYear = YEAR(GETDATE())
),
PreviousYear AS (
    SELECT 
        CustomerID,
        TotalOrderValue AS PreviousYearValue
    FROM 
        OrderValue
    WHERE 
        OrderYear = YEAR(GETDATE()) - 1
)
SELECT 
    C.Name,
    C.Email,
    CY.CurrentYearValue,
    PY.PreviousYearValue
FROM 
    CurrentYear CY
JOIN 
    PreviousYear PY ON CY.CustomerID = PY.CustomerID
JOIN 
    Customer C ON CY.CustomerID = C.CustomerID
WHERE 
    CY.CurrentYearValue < PY.PreviousYearValue;



--Q3
WITH CustomerPurchases AS (
    SELECT
        o.CustomerID,
        p.ProductCategory,
        SUM(oi.Quantity * oi.Price) AS TotalAmount
    FROM
        [Order] o
        JOIN OrderItem oi ON o.OrderID = oi.OrderID
        JOIN Variant v ON oi.VariantID = v.VariantID
        JOIN Product p ON v.ProductID = p.ProductID
    GROUP BY
        o.CustomerID,
        p.ProductCategory
)
SELECT
    c.CustomerID,
    c.Name,
    c.Email,
    cp.ProductCategory,
    cp.TotalAmount
FROM
    Customer c
    JOIN CustomerPurchases cp ON c.CustomerID = cp.CustomerID
ORDER BY
    c.CustomerID,
    cp.ProductCategory;



--Q4
WITH TopSellingProducts AS (
    SELECT TOP 5
        v.ProductID,
        p.ProductName,
        SUM(oi.Quantity) AS TotalQuantitySold
    FROM
        OrderItem oi
        JOIN Variant v ON oi.VariantID = v.VariantID
        JOIN Product p ON v.ProductID = p.ProductID
    GROUP BY
        v.ProductID,
        p.ProductName
    ORDER BY
        TotalQuantitySold DESC
)
SELECT
    tsp.ProductID,
    tsp.ProductName,
    v.VariantName,
    SUM(oi.Quantity) AS VariantQuantitySold
FROM
    TopSellingProducts tsp
    JOIN Variant v ON tsp.ProductID = v.ProductID
    JOIN OrderItem oi ON v.VariantID = oi.VariantID
GROUP BY
    tsp.ProductID,
    tsp.ProductName,
    v.VariantName
ORDER BY
    tsp.ProductID,
    VariantQuantitySold DESC;
