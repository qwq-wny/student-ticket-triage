# Where the data comes from

Both datasets are synthetic and are made by `ml/scripts/build_dataset.py` with random seed `42`. No real customer data is used.

Columns: `ticket_id`, `text`, `customer_tier`, `monthly_revenue`, and `priority`.

## v1

- 150 rows
- DVC hash: `9c49d6adf6e96819fb5626bcb6a261ce`
- Commit: `bffc61a3d544a5a003d60b33fdb706f2e9bea3da`
- Class counts: about 30 urgent, 40 high, 55 normal, 25 low
- It includes some noisy labels on purpose.

## v2

- 240 rows
- DVC hash: `a1640c8c6041889f71eb384b8585853f`
- Commit: `dc01217f059b08a6dc2242e57b72eb8c51e5442a`
- Every class has 60 rows
- Noisy labels were corrected
- More text variations were added

## Commands

```bash
dvc pull
# or recreate the toy files:
python ml/scripts/build_dataset.py v1
python ml/scripts/build_dataset.py v2
```
