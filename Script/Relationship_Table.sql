/*
Task 1. Alter Table to be a Primary Key
*/
-- Load Table
ALTER TABLE [autocheck].[loan]
ADD CONSTRAINT PK_load_id PRIMARY KEY (loan_id);

-- Borrow Table
ALTER TABLE [autocheck].[borrow]
ADD CONSTRAINT PK_borrow_id PRIMARY KEY (Borrower_Id);

-- Repayment Table
ALTER TABLE [autocheck].[repayment]
ADD CONSTRAINT PK_payment_id PRIMARY KEY (payment_id);

-- Schedule Table
ALTER TABLE [autocheck].[schedule]
ADD CONSTRAINT PK_schedule_id PRIMARY KEY (schedule_id);


/*
Task 2: Create Foreign Keys Relationships
*/
-- Repayment Table(loan_id_fk) ==Loan Table(loan_id)

ALTER TABLE [autocheck].[repayment]
ADD CONSTRAINT FK_load_id
FOREIGN KEY (loan_id)
REFERENCES [autocheck].[loan] (loan_id);

--
ALTER TABLE [autocheck].[schedule]
ADD CONSTRAINT FK_schedule_id
FOREIGN KEY (loan_id)
REFERENCES [autocheck].[loan] (loan_id);

--
ALTER TABLE [autocheck].[loan]
ADD CONSTRAINT FK_borrow_id
FOREIGN KEY (Borrower_id)
REFERENCES [autocheck].[borrow] (Borrower_id);




