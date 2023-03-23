# odoo-16
Odoo 16 repository

## Git Commit hooks/linting
```pip install pre-commit
/opt/odoo/.local/bin/pre-commit install
/opt/odoo/.local/bin/pre-commit run --all-files
```

## Missing requirements so far

1. pdfminer (core apparently)
2. redis (oak_redis_session)
3. hiredis (oak_redis_session)
4. plotly (mrp_shop_floor_control)