# Security Policy

## Product boundary

This application is intentionally signal-only. Do not add exchange order, withdrawal, transfer, or private-account credentials without a separate threat model and explicit project decision.

## Secrets

- Store secrets only in `.env` or a production secrets manager.
- Never commit `.env`, Telegram tokens, database passwords, Django secret keys, backups, or model datasets containing personal data.
- Rotate a token immediately if it appears in logs, screenshots, commits, chat, or tickets.

## Deployment

- Set `DEBUG=false` and a random `SECRET_KEY` of at least 50 characters.
- Use HTTPS and keep PostgreSQL and Redis on private networks.
- Create a dedicated non-superuser database account.
- Restrict Django admin to the owner and enable MFA at the reverse proxy or identity layer.
- Back up the database and test restoration.
- Patch dependencies regularly and rerun the full test suite.

## Reporting

For private use, record security findings in the project issue tracker without including secrets. Revoke affected credentials before investigating further.
