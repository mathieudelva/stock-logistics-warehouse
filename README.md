# odoo-16
Odoo 16 repository

## Git Commit hooks/linting
```pip install pre-commit
/opt/odoo/.local/bin/pre-commit install
/opt/odoo/.local/bin/pre-commit run --all-files
```

## Git Aggregator
```pip install git-aggregator
/opt/odoo/.local/bin/gitaggregate -c repos.yml
/opt/odoo/.local/bin/gitaggregate -c repos.yml -p
/opt/odoo/.local/bin/gitaggregate -c repos.yml -d ./oca/manufacture
```
```
export GITHUB_TOKEN="xxxx"
/opt/odoo/.local/bin/gitaggregate -c repos.yml show-all-prs
```

## Missing python lib requirements so far

1. pdfminer (core apparently)
2. redis (oak_redis_session)
3. hiredis (oak_redis_session)
4. plotly (mrp_shop_floor_control)
5. xmltodict (partner_usps_address_validation)