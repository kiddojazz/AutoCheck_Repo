WITH LatestPayments AS (
    -- Get the latest payment date for each loan
    SELECT loan_id, MAX(Date_paid) AS LastPaymentDate
    FROM [autocheck].[repayment]
    GROUP BY loan_id
),
ExpectedPayments AS (
    -- Get the earliest expected payment date that hasn't been fully paid
    SELECT s.loan_id, MIN(s.Expected_payment_date) AS EarliestExpectedDate,
           SUM(s.Expected_payment_amount) AS TotalExpectedAmount
    FROM [autocheck].[schedule] s
    LEFT JOIN [autocheck].[repayment] r ON s.loan_id = r.loan_id AND s.Expected_payment_date = r.Date_paid
    GROUP BY s.loan_id
    HAVING SUM(s.Expected_payment_amount) > COALESCE(SUM(r.Amount_paid), 0)
)
SELECT 
    l.Borrower_id,
    l.loan_id,
    l.Date_of_release,
    l.Maturity_date,
    ep.EarliestExpectedDate AS FirstMissedPaymentDate,
    DATEDIFF(day, ep.EarliestExpectedDate, GETDATE()) AS PAR_Days,
    ep.TotalExpectedAmount AS Amount_at_Risk,
    COALESCE(lp.LastPaymentDate, l.Date_of_release) AS LastPaymentOrReleaseDate
FROM 
    [autocheck].[loan] l
JOIN ExpectedPayments ep ON l.loan_id = ep.loan_id
LEFT JOIN LatestPayments lp ON l.loan_id = lp.loan_id
WHERE 
    GETDATE() > ep.EarliestExpectedDate
ORDER BY 
    PAR_Days DESC, Amount_at_Risk DESC;