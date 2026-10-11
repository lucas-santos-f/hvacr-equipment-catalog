# Workflow: pre-release check

Run before tagging or before pointing a deployment at a new commit.

```bash
make lint
make test
make spec && git diff --exit-code openapi.yaml
make audit
docker compose up -d --build
curl -fs localhost:8000/health
curl -fs 'localhost:8000/equipment?limit=1' | grep '"total":90'
curl -fs localhost:8080 > /dev/null
docker compose down -v
```

Then read the diff since the last release with one question in mind: **does anything
here change the API contract?** If yes, the frontend needs rebuilding, because
`VITE_API_URL` and the response shapes are baked in at build time.

Check `security/scan-findings.md` is still accurate. A finding that was accepted three
months ago may not be acceptable now.
