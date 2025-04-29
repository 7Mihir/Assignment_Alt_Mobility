--1. Order & Sales Analysis
-- Order‐status distribution
SELECT
  order_status,
  COUNT(*) AS order_count
FROM customer_orders
GROUP BY order_status
ORDER BY order_count DESC;

--Monthly total revenue & order volume

SELECT
  FORMAT(DATEFROMPARTS(YEAR(order_date), MONTH(order_date), 1), 'yyyy-MM') AS month,
  COUNT(*) AS total_orders,
  SUM(order_amount) AS total_revenue
FROM customer_orders
GROUP BY 
  FORMAT(DATEFROMPARTS(YEAR(order_date), MONTH(order_date), 1), 'yyyy-MM')
ORDER BY 
  FORMAT(DATEFROMPARTS(YEAR(order_date), MONTH(order_date), 1), 'yyyy-MM');

  -- Revenue by order status
SELECT
  order_status,
  SUM(order_amount) AS revenue
FROM customer_orders
GROUP BY order_status
ORDER BY revenue DESC;

-----2.Customer Analysis-------------------------------------------------------------------------------------------------------------

--  Orders & spend per customer
SELECT Top 20 -- top 20 customers by order count
  customer_id,
  COUNT(*)      AS num_orders,
  SUM(order_amount) AS total_spent
FROM customer_orders
GROUP BY customer_id
ORDER BY num_orders DESC;  

-- Segment customers by frequency
WITH cust_counts AS (
  SELECT customer_id, COUNT(*) AS num_orders
  FROM customer_orders
  GROUP BY customer_id
)
SELECT
  CASE
    WHEN num_orders = 1 THEN 'One-time'
    WHEN num_orders BETWEEN 2 AND 4 THEN 'Occasional'
    ELSE 'Frequent'
  END AS segment,
  COUNT(*) AS num_customers,
  ROUND(AVG(CAST(num_orders AS FLOAT)), 2) AS avg_orders
FROM cust_counts
GROUP BY
  CASE
    WHEN num_orders = 1 THEN 'One-time'
    WHEN num_orders BETWEEN 2 AND 4 THEN 'Occasional'
    ELSE 'Frequent'
  END
ORDER BY num_customers DESC;

--- Monthly new vs. returning customers
WITH first_order AS (
  SELECT
    customer_id,
    DATEFROMPARTS(YEAR(MIN(order_date)), MONTH(MIN(order_date)), 1) AS first_month
  FROM customer_orders
  GROUP BY customer_id
),
monthly AS (
  SELECT
    customer_id,
    DATEFROMPARTS(YEAR(order_date), MONTH(order_date), 1) AS month
  FROM customer_orders
)
SELECT
  m.month,
  COUNT(DISTINCT CASE WHEN f.first_month = m.month THEN m.customer_id END) AS new_customers,
  COUNT(DISTINCT CASE WHEN f.first_month <  m.month THEN m.customer_id END) AS returning_customers
FROM monthly m
JOIN first_order f ON m.customer_id = f.customer_id
GROUP BY m.month
ORDER BY m.month;

---3.Payment Status Analysis----------------------------------------------------------------------------
-- Overall success vs. failure
SELECT
  payment_status,
  COUNT(*)             AS count,
  ROUND(AVG(payment_amount),2) AS avg_amount
FROM payments
GROUP BY payment_status;

--Failure & success rates by method
SELECT
  payment_method,
  COUNT(*) AS total_txns,
  ROUND(SUM(CASE WHEN payment_status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate,
  ROUND(SUM(CASE WHEN payment_status = 'failed' THEN 1 ELSE 0 END) / COUNT(*), 2) AS failure_rate
FROM payments
GROUP BY payment_method
ORDER BY failure_rate DESC;

----- Monthly failed vs. successful payments
SELECT
  FORMAT(payment_date, 'yyyy-MM') AS month,
  SUM(CASE WHEN payment_status = 'failed' THEN 1 ELSE 0 END) AS failed_count,
  SUM(CASE WHEN payment_status = 'completed' THEN 1 ELSE 0 END) AS success_count
FROM payments
GROUP BY FORMAT(payment_date, 'yyyy-MM')
ORDER BY month;

----4. Order Details Report---------

-- One‐row-per-order with payment details
SELECT Top 100
  o.order_id,
  o.customer_id,
  o.order_date,
  o.order_amount,
  o.shipping_address,
  o.order_status,
  p.payment_id,
  p.payment_date,
  p.payment_amount,
  p.payment_method,
  p.payment_status
FROM customer_orders o
LEFT JOIN payments p
  ON o.order_id = p.order_id
ORDER BY o.order_date DESC;

-----  Aggregate paid vs. amount due per order
SELECT
  o.order_id,
  o.order_amount,
  COALESCE(SUM(p.payment_amount),0)     AS total_paid,
  o.order_amount - COALESCE(SUM(p.payment_amount),0) AS balance_due
FROM customer_orders o
LEFT JOIN payments p
  ON o.order_id = p.order_id
GROUP BY o.order_id, o.order_amount
HAVING SUM(p.payment_amount) IS NULL
   OR SUM(p.payment_amount) <> o.order_amount
ORDER BY balance_due DESC;

---Customer Rentention Analysis

-- Step 1: Create temporary table of orders grouped by month
SELECT
    customer_id,
    DATEFROMPARTS(YEAR(order_date), MONTH(order_date), 1) AS order_month
INTO #customer_orders_with_month
FROM customer_orders;

-- Step 2: Find first purchase month (cohort) per customer
SELECT
    customer_id,
    MIN(order_month) AS cohort_month
INTO #customer_cohorts
FROM #customer_orders_with_month
GROUP BY customer_id;

-- Step 3: Join cohort data and calculate months since cohort
SELECT
    o.customer_id,
    c.cohort_month,
    o.order_month,
    DATEDIFF(MONTH, c.cohort_month, o.order_month) AS months_since_cohort
INTO #cohort_orders
FROM #customer_orders_with_month o
JOIN #customer_cohorts c ON o.customer_id = c.customer_id;

-- Step 4: Count unique customers by cohort and month offset
SELECT
    cohort_month,
    months_since_cohort,
    COUNT(DISTINCT customer_id) AS customer_count
FROM #cohort_orders
GROUP BY cohort_month, months_since_cohort
ORDER BY cohort_month, months_since_cohort;
