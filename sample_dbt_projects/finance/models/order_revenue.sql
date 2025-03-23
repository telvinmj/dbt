WITH transactions AS (
    SELECT
        transaction_id,
        order_id,
        transaction_date,
        payment_method,
        amount,
        status
    FROM raw_data.finance.transactions
    WHERE status = 'completed'
),

-- Cross-project reference
ecommerce_orders AS (
    SELECT * FROM {{ ref('customer_orders', 'ecommerce') }}
),

order_revenue AS (
    SELECT
        t.order_id,
        eo.customer_id,
        eo.first_order_date AS order_date,
        t.transaction_date,
        SUM(t.amount) AS revenue,
        COUNT(t.transaction_id) AS transaction_count,
        MAX(t.payment_method) AS payment_method
    FROM transactions t
    JOIN ecommerce_orders eo ON t.order_id = eo.customer_id
    GROUP BY 1, 2, 3, 4
)

SELECT * FROM order_revenue 