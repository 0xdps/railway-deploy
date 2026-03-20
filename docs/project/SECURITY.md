# Security Policy

## Reporting a vulnerability

Please do not open a public issue for security problems.

Report privately to the repository maintainers with:
- affected version/commit
- impact summary
- reproduction steps
- suggested mitigation (if known)

We will acknowledge reports quickly and coordinate a fix and disclosure timeline.

## Secret handling

- Never commit real credentials.
- `.env.*` files are ignored by `.gitignore`.
- The CLI masks common secret-like keys in output.
