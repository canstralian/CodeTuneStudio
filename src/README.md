# Cloudflare Worker Source

This directory contains the Cloudflare Worker implementation for CodeTuneStudio.

## File Structure

```
src/
└── worker.js         # Main worker entry point
```

## worker.js

The main Cloudflare Worker script that provides API endpoints for CodeTuneStudio.

### Key Features

- **CORS Support**: Handles cross-origin requests with proper headers
- **Health Checks**: `/health` endpoint for monitoring
- **API Routing**: Handles `/api/*` routes
- **Error Handling**: Comprehensive error handling and logging
- **Environment Variables**: Secure access to secrets and configuration

### Endpoints

#### Root Endpoint
```
GET /
```
Returns API information and available endpoints.

#### Health Check
```
GET /health
```
Returns worker health status.

#### API Status
```
GET /api/status
```
Returns operational status of all services.

#### Code Analysis
```
POST /api/analyze
Content-Type: application/json

{
  "code": "your code here"
}
```
Analyzes code and returns quality scores and suggestions.

#### Configuration
```
GET /api/config
```
Returns public configuration and feature flags.

#### Training
```
POST /api/training/start
Content-Type: application/json

{
  "model_type": "CodeT5",
  "dataset": "dataset_name"
}
```
Queues a training job.

```
GET /api/training/status?job_id=<id>
```
Returns training job status.

#### Models
```
GET /api/models
```
Returns list of available models.

## Development

### Local Testing

```bash
# Install dependencies
npm install

# Start local development server
npm run dev
# or
wrangler dev
```

The worker will be available at `http://localhost:8787`

### Environment Variables

Required environment variables (set via `wrangler secret put` or `.dev.vars`):

- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key for code analysis
- `ANTHROPIC_API_KEY` - Anthropic API key
- `HF_TOKEN` - HuggingFace token
- `SECRET_KEY` - Secret key for sessions

Optional:
- `ENVIRONMENT` - Deployment environment (production/staging/development)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR)
- `REQUIRE_API_KEY` - Require API key for endpoints (true/false)

### Deployment

```bash
# Deploy to production
npm run deploy:production
# or
wrangler deploy --env production

# Deploy to staging
npm run deploy:staging
# or
wrangler deploy --env staging
```

## Architecture

The worker follows a simple routing pattern:

```
Request → CORS Check → Route Handler → Response + CORS Headers
                           │
                           ├─ Root (/)
                           ├─ Health Check (/health)
                           ├─ Status (/api/status)
                           └─ API Routes (/api/*)
                                  │
                                  ├─ Analyze
                                  ├─ Config
                                  ├─ Training
                                  └─ Models
```

## Adding New Endpoints

To add a new API endpoint:

1. Create a handler function:
```javascript
async function handleMyEndpoint(request, env) {
  // Your logic here
  return jsonResponse({ status: 'success' });
}
```

2. Add routing logic in `handleAPI()`:
```javascript
if (path === '/api/myendpoint') {
  return handleMyEndpoint(request, env);
}
```

3. Update endpoint list in `handleRoot()`.

## Testing

Test endpoints locally:

```bash
# Health check
curl http://localhost:8787/health

# API status
curl http://localhost:8787/api/status

# Code analysis
curl -X POST http://localhost:8787/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"code":"console.log(\"hello\");"}'
```

## Monitoring

View real-time logs:

```bash
# Tail logs
npm run tail
# or
wrangler tail

# Production logs
npm run tail:production
# or
wrangler tail --env production
```

## Documentation

For complete deployment guide, see:
- [Cloudflare Workers Guide](../docs/CLOUDFLARE_WORKERS.md)
- [Quick Start Guide](../docs/CLOUDFLARE_QUICKSTART.md)

## Support

- [GitHub Issues](https://github.com/canstralian/CodeTuneStudio/issues)
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
