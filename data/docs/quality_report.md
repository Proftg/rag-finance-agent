---
type: Report
title: Data quality report
description: Business-rule checks and full column profile for the 30k-client risk database.
tags: [data-quality, profiling, referential-integrity, sqlite]
timestamp: 2026-06-22T00:00:00Z
domain: finance
---

# Data quality report

Run against the relational database `outputs/risk.sqlite`.

## 1. Business rules

| Check | Value | Status |
|---|---|---|
| Total client volume | 30,000 | OK |
| Duplicate identifiers | 0 | OK |
| Ages out of range (18-100) | 0 | OK |
| Credit limits <= 0 | 0 | OK |
| Orphan EDUCATION codes (referential integrity) | 0 | OK |
| Null values in LIMIT_BAL | 0 | OK |

## 2. Column profile

| column | dtype | nulls | distinct | min | mean | max |
|---|---|---|---|---|---|---|
| ID | int64 | 0 | 30000 | 1.0 | 15000.5 | 30000.0 |
| LIMIT_BAL | int64 | 0 | 81 | 10000.0 | 167484.3 | 1000000.0 |
| SEX | int64 | 0 | 2 | 1.0 | 1.6 | 2.0 |
| EDUCATION | int64 | 0 | 5 | 0.0 | 1.8 | 4.0 |
| MARRIAGE | int64 | 0 | 4 | 0.0 | 1.6 | 3.0 |
| AGE | int64 | 0 | 56 | 21.0 | 35.5 | 79.0 |
| PAY_1 | int64 | 0 | 11 | -2.0 | -0.0 | 8.0 |
| PAY_2 | int64 | 0 | 11 | -2.0 | -0.1 | 8.0 |
| PAY_3 | int64 | 0 | 11 | -2.0 | -0.2 | 8.0 |
| PAY_4 | int64 | 0 | 11 | -2.0 | -0.2 | 8.0 |
| PAY_5 | int64 | 0 | 10 | -2.0 | -0.3 | 8.0 |
| PAY_6 | int64 | 0 | 10 | -2.0 | -0.3 | 8.0 |
| BILL_AMT1 | int64 | 0 | 22723 | -165580.0 | 51223.3 | 964511.0 |
| BILL_AMT2 | int64 | 0 | 22346 | -69777.0 | 49179.1 | 983931.0 |
| BILL_AMT3 | int64 | 0 | 22026 | -157264.0 | 47013.2 | 1664089.0 |
| BILL_AMT4 | int64 | 0 | 21548 | -170000.0 | 43262.9 | 891586.0 |
| BILL_AMT5 | int64 | 0 | 21010 | -81334.0 | 40311.4 | 927171.0 |
| BILL_AMT6 | int64 | 0 | 20604 | -339603.0 | 38871.8 | 961664.0 |
| PAY_AMT1 | int64 | 0 | 7943 | 0.0 | 5663.6 | 873552.0 |
| PAY_AMT2 | int64 | 0 | 7899 | 0.0 | 5921.2 | 1684259.0 |
| PAY_AMT3 | int64 | 0 | 7518 | 0.0 | 5225.7 | 896040.0 |
| PAY_AMT4 | int64 | 0 | 6937 | 0.0 | 4826.1 | 621000.0 |
| PAY_AMT5 | int64 | 0 | 6897 | 0.0 | 4799.4 | 426529.0 |
| PAY_AMT6 | int64 | 0 | 6939 | 0.0 | 5215.5 | 528666.0 |
| default_flag | int64 | 0 | 2 | 0.0 | 0.2 | 1.0 |
| education_label | object | 0 | 5 |  |  |  |
| marriage_label | object | 0 | 4 |  |  |  |
| sex_label | object | 0 | 2 |  |  |  |
| age_band | object | 0 | 5 |  |  |  |
| limit_bal_eur | float64 | 0 | 81 | 276.0 | 4616.9 | 27567.0 |
