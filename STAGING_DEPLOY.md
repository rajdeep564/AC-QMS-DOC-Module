# Staging deploy — AC-QMS DOC-Module (branch: staging)

Deploy this service from **`staging` only**. Use the included **Dockerfile** (LibreOffice installed) so PDF conversion works.

## Render (Docker)

1. New Web Service → connect this repo
2. **Branch:** `staging`
3. **Runtime:** Docker
4. Env:

```env
API_KEY=<shared-with-gateway-DOC_MODULE_API_KEY>
DEBUG=false
LIBREOFFICE_PATH=soffice
```

5. After deploy, set Gateway `DOC_MODULE_URL` to this service URL.

See `AC-QMS-API-Gateway/STAGING_DEPLOY.md` for the full stack checklist.
