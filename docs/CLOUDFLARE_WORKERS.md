# Deploying CodeTuneStudio to Cloudflare Workers

This guide provides comprehensive instructions for deploying CodeTuneStudio to Cloudflare Workers with custom domain configuration, environment variables, and observability setup.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Custom Domain Configuration](#custom-domain-configuration)
4. [Environment Variables and Secrets](#environment-variables-and-secrets)
5. [Worker Configuration](#worker-configuration)
6. [Deployment](#deployment)
7. [Observability and Monitoring](#observability-and-monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying to Cloudflare Workers, ensure you have:

- **Cloudflare Account**: Sign up at [cloudflare.com](https://cloudflare.com)
- **Wrangler CLI**: Install via `npm install -g wrangler`
- **Node.js**: Version 16.x or higher
- **Domain**: A domain managed in Cloudflare (for custom domain setup)
- **Database**: PostgreSQL instance (recommended: Cloudflare D1 or external provider)

---

## Initial Setup

### 1. Install Wrangler CLI

```bash
npm install -g wrangler
```

### 2. Authenticate with Cloudflare

```bash
wrangler login
```

This will open a browser window for authentication.

### 3. Create a New Worker Project

```bash
# Navigate to your project directory
cd /path/to/CodeTuneStudio

# Initialize Wrangler configuration (if not exists)
wrangler init
```

---

## Custom Domain Configuration

### Setting Up `api.promptcrafting.net`

#### Step 1: Add Custom Domain in Cloudflare Dashboard

1. Navigate to **Cloudflare Dashboard → Workers & Pages**
2. Select your Worker
3. Go to **Triggers** tab
4. Click **Add Custom Domain**
5. Enter: `api.promptcrafting.net`
6. Click **Add Custom Domain**

#### Step 2: Configure DNS

Cloudflare automatically creates the necessary DNS records when you add a custom domain. Verify:

1. Go to **DNS** section in your domain dashboard
2. Confirm a **CNAME record** exists:
   - **Name**: `api`
   - **Target**: `<your-worker-name>.<your-subdomain>.workers.dev`
   - **Proxy status**: Proxied (orange cloud)

#### Step 3: Verify SSL/TLS

Cloudflare automatically provisions SSL certificates for custom domains:

1. Navigate to **SSL/TLS** → **Edge Certificates**
2. Verify **Universal SSL** is active
3. Set **SSL/TLS encryption mode** to **Full** or **Full (strict)**

#### Step 4: Test Your Custom Domain

```bash
curl https://api.promptcrafting.net/
```

Expected response: Your worker endpoint output.

---

## Environment Variables and Secrets

Cloudflare Workers support two types of configuration:

1. **Environment Variables**: Non-sensitive configuration (visible in dashboard)
2. **Secrets**: Sensitive data (encrypted, not visible after creation)

### Setting Environment Variables

#### Via Wrangler CLI

```bash
# Set environment variable
wrangler secret put DATABASE_URL

# You'll be prompted to enter the value securely
```

#### Via Cloudflare Dashboard

1. Go to **Workers & Pages** → Select your worker
2. Navigate to **Settings** → **Variables**
3. Click **Add variable**
4. Enter key-value pairs:

**Required Variables:**

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/dbname

# API Keys (as secrets)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
HF_TOKEN=hf_...

# Application Configuration
HOST=0.0.0.0
PORT=8787  # Cloudflare Workers default
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-random-secret-key-here

# Cloudflare-specific
ENVIRONMENT=production
WORKER_NAME=codetune-studio
```

### Setting Secrets (Sensitive Data)

**IMPORTANT**: Use secrets for all sensitive information like API keys, database credentials, and tokens.

```bash
# Set secrets via CLI
wrangler secret put OPENAI_API_KEY
wrangler secret put ANTHROPIC_API_KEY
wrangler secret put HF_TOKEN
wrangler secret put DATABASE_URL
wrangler secret put SECRET_KEY

# Verify secrets are set (values won't be shown)
wrangler secret list
```

### Accessing Variables in Worker Code

```javascript
// In your worker script
export default {
  async fetch(request, env) {
    const databaseUrl = env.DATABASE_URL;
    const apiKey = env.OPENAI_API_KEY;
    
    // Use environment variables
    console.log('Environment:', env.ENVIRONMENT);
    
    // Your application logic
    return new Response('Hello from CodeTuneStudio!');
  }
};
```

---

## Worker Configuration

### `wrangler.toml` Configuration

Create or update `wrangler.toml` in your project root:

```toml
# Wrangler Configuration for CodeTuneStudio
name = "codetune-studio"
main = "src/worker.js"
compatibility_date = "2024-01-01"
account_id = "your-account-id"  # Get from Cloudflare dashboard

# Worker settings
workers_dev = true
route = ""
zone_id = ""

# Custom domains (managed via dashboard)
# Note: Custom domains are configured in Cloudflare Dashboard → Triggers

# Environment variables (non-sensitive)
[env.production.vars]
ENVIRONMENT = "production"
LOG_LEVEL = "INFO"
HOST = "0.0.0.0"
PORT = "8787"

[env.staging.vars]
ENVIRONMENT = "staging"
LOG_LEVEL = "DEBUG"

# Build configuration
[build]
command = "npm run build"

# Service bindings (if using other Cloudflare services)
# [[services]]
# binding = "MY_SERVICE"
# service = "my-service-name"

# KV Namespaces (for caching/session storage)
# [[kv_namespaces]]
# binding = "KV"
# id = "your-kv-namespace-id"

# D1 Databases (Cloudflare's SQL database)
# [[d1_databases]]
# binding = "DB"
# database_name = "codetune-studio-db"
# database_id = "your-database-id"

# Durable Objects (for stateful coordination)
# [[durable_objects.bindings]]
# name = "SESSIONS"
# class_name = "SessionManager"

# Analytics Engine (for custom analytics)
# [analytics_engine_datasets]
# binding = "ANALYTICS"

# Limits and performance
[limits]
cpu_ms = 50  # CPU time limit per request (max 50ms for free tier)

# Triggers (routes are managed in dashboard)
# Use custom domains via dashboard instead of routes for better management
```

### Worker Script Example

Create `src/worker.js`:

```javascript
/**
 * CodeTuneStudio Cloudflare Worker
 * Handles API requests and routes to appropriate handlers
 */

// Import your application logic
// Note: For Python applications, you'll need to compile to WebAssembly
// or create a Node.js wrapper

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // Health check endpoint
    if (url.pathname === '/health') {
      return new Response(
        JSON.stringify({ 
          status: 'healthy',
          timestamp: new Date().toISOString(),
          environment: env.ENVIRONMENT 
        }),
        { 
          headers: { 
            ...corsHeaders,
            'Content-Type': 'application/json' 
          } 
        }
      );
    }
    
    // API routes
    if (url.pathname.startsWith('/api/')) {
      return handleApiRequest(request, env, ctx);
    }
    
    // Default response
    return new Response(
      JSON.stringify({ 
        message: 'CodeTuneStudio API',
        version: '0.2.0',
        endpoints: ['/health', '/api/*']
      }),
      { 
        headers: { 
          ...corsHeaders,
          'Content-Type': 'application/json' 
        } 
      }
    );
  }
};

/**
 * Handle API requests
 */
async function handleApiRequest(request, env, ctx) {
  const url = new URL(request.url);
  
  // Example: Database query using environment variable
  try {
    // Your API logic here
    // Access secrets via env.DATABASE_URL, env.OPENAI_API_KEY, etc.
    
    const response = {
      status: 'success',
      path: url.pathname,
      method: request.method
    };
    
    return new Response(JSON.stringify(response), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    return new Response(
      JSON.stringify({ 
        status: 'error', 
        message: error.message 
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}
```

---

## Deployment

### Deploy to Cloudflare Workers

#### Using Wrangler CLI

```bash
# Deploy to production
wrangler deploy

# Deploy to specific environment
wrangler deploy --env production

# Deploy with verbose output
wrangler deploy --verbose
```

#### Deployment Workflow

```bash
# 1. Test locally first
wrangler dev

# 2. Run pre-deployment checks
npm run test  # If you have tests
npm run lint

# 3. Deploy to staging
wrangler deploy --env staging

# 4. Test staging endpoint
curl https://staging.api.promptcrafting.net/health

# 5. Deploy to production
wrangler deploy --env production

# 6. Verify production
curl https://api.promptcrafting.net/health
```

### Continuous Deployment with GitHub Actions

Create `.github/workflows/deploy-cloudflare.yml`:

```yaml
name: Deploy to Cloudflare Workers

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    name: Deploy to Cloudflare Workers
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Deploy to Cloudflare Workers
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: deploy --env production
      
      - name: Test deployment
        run: |
          sleep 5
          curl -f https://api.promptcrafting.net/health || exit 1
```

**Required GitHub Secrets:**
- `CLOUDFLARE_API_TOKEN`: API token from Cloudflare dashboard
- `CLOUDFLARE_ACCOUNT_ID`: Account ID from Cloudflare dashboard

---

## Observability and Monitoring

### 1. Cloudflare Analytics

Access built-in analytics:

1. Navigate to **Workers & Pages** → Select your worker
2. Click **Metrics** tab
3. View:
   - Request count
   - Error rate
   - CPU time usage
   - Request duration

### 2. Real-Time Logs

#### Via Wrangler CLI

```bash
# Tail production logs
wrangler tail

# Tail with filters
wrangler tail --format pretty
wrangler tail --status error  # Only errors

# Tail specific environment
wrangler tail --env production
```

#### Via Cloudflare Dashboard

1. Go to **Workers & Pages** → Select your worker
2. Click **Logs** tab (requires Logpush setup)

### 3. Logpush Configuration

Send logs to external services for analysis:

```bash
# Configure Logpush to S3
wrangler logpush create \
  --destination-conf "s3://bucket-name/path?region=us-east-1" \
  --dataset "workers_trace_events"

# Configure Logpush to HTTP endpoint
wrangler logpush create \
  --destination-conf "https://logs.example.com/endpoint" \
  --dataset "workers_trace_events"
```

### 4. Custom Logging in Worker

```javascript
export default {
  async fetch(request, env, ctx) {
    const startTime = Date.now();
    
    try {
      // Your application logic
      const response = await handleRequest(request, env);
      
      // Log successful request
      console.log(JSON.stringify({
        timestamp: new Date().toISOString(),
        method: request.method,
        url: request.url,
        status: response.status,
        duration: Date.now() - startTime,
        environment: env.ENVIRONMENT
      }));
      
      return response;
    } catch (error) {
      // Log error
      console.error(JSON.stringify({
        timestamp: new Date().toISOString(),
        error: error.message,
        stack: error.stack,
        url: request.url,
        method: request.method
      }));
      
      throw error;
    }
  }
};
```

### 5. Health Checks and Uptime Monitoring

Set up external monitoring:

```bash
# Use services like:
# - Cloudflare Health Checks
# - UptimeRobot
# - Pingdom
# - StatusCake

# Example health check endpoint
GET https://api.promptcrafting.net/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "environment": "production"
}
```

### 6. Error Tracking Integration

Integrate with error tracking services:

```javascript
// Example: Sentry integration
import * as Sentry from '@sentry/browser';

Sentry.init({
  dsn: env.SENTRY_DSN,
  environment: env.ENVIRONMENT,
  tracesSampleRate: 1.0,
});

export default {
  async fetch(request, env, ctx) {
    try {
      return await handleRequest(request, env);
    } catch (error) {
      Sentry.captureException(error);
      throw error;
    }
  }
};
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Custom Domain Not Working

**Symptoms**: `api.promptcrafting.net` returns 404 or connection error

**Solutions**:
1. Verify DNS propagation: `nslookup api.promptcrafting.net`
2. Check CNAME record in Cloudflare DNS dashboard
3. Ensure custom domain is added in **Workers → Triggers → Custom Domains**
4. Wait 5-10 minutes for DNS propagation

#### Issue 2: Environment Variables Not Accessible

**Symptoms**: `env.DATABASE_URL` is undefined

**Solutions**:
1. Verify variables are set: `wrangler secret list`
2. Redeploy after setting secrets: `wrangler deploy`
3. Check variable names match exactly (case-sensitive)
4. For local dev, create `.dev.vars` file:
   ```
   DATABASE_URL=postgresql://localhost/db
   OPENAI_API_KEY=sk-test
   ```

#### Issue 3: CPU Time Limit Exceeded

**Symptoms**: `Error: Worker exceeded CPU time limit`

**Solutions**:
1. Optimize expensive operations (database queries, API calls)
2. Use `ctx.waitUntil()` for non-blocking operations
3. Consider upgrading to Workers Paid plan for higher limits
4. Implement caching with KV storage

#### Issue 4: Database Connection Errors

**Symptoms**: Cannot connect to PostgreSQL from worker

**Solutions**:
1. Ensure database allows connections from Cloudflare IPs
2. Use Cloudflare D1 for better integration
3. Consider connection pooling services (e.g., PgBouncer)
4. Verify DATABASE_URL format: `postgresql://user:pass@host:port/db`

#### Issue 5: CORS Errors

**Symptoms**: Browser shows CORS policy errors

**Solutions**:
1. Add CORS headers to all responses
2. Handle OPTIONS preflight requests
3. Set appropriate `Access-Control-Allow-Origin`
4. Example fix in [Worker Script Example](#worker-script-example)

### Debug Mode

Enable verbose logging:

```bash
# Local development with debug logs
wrangler dev --log-level debug

# Tail logs with detailed output
wrangler tail --format pretty --debug
```

### Get Help

- **Cloudflare Community**: [community.cloudflare.com](https://community.cloudflare.com)
- **Cloudflare Discord**: [discord.gg/cloudflaredev](https://discord.gg/cloudflaredev)
- **Documentation**: [developers.cloudflare.com/workers](https://developers.cloudflare.com/workers)
- **Support Portal**: [dash.cloudflare.com/support](https://dash.cloudflare.com/support)

---

## Additional Resources

### Official Documentation

- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/wrangler/)
- [Custom Domains Guide](https://developers.cloudflare.com/workers/platform/triggers/custom-domains/)
- [Environment Variables](https://developers.cloudflare.com/workers/platform/environment-variables/)

### Best Practices

1. **Security**:
   - Always use secrets for sensitive data
   - Enable SSL/TLS Full (strict) mode
   - Implement rate limiting
   - Validate all inputs

2. **Performance**:
   - Use KV for caching frequently accessed data
   - Minimize CPU time per request
   - Leverage Cloudflare CDN for static assets
   - Use `ctx.waitUntil()` for background tasks

3. **Reliability**:
   - Implement proper error handling
   - Set up health check endpoints
   - Use staging environments for testing
   - Monitor error rates and performance metrics

4. **Cost Optimization**:
   - Start with free tier (100,000 requests/day)
   - Monitor usage in dashboard
   - Optimize request patterns
   - Use caching to reduce compute

---

## Summary

You now have:

✅ Custom domain configured: `api.promptcrafting.net`  
✅ Environment variables and secrets properly set  
✅ Worker deployed and accessible  
✅ Observability and monitoring in place  
✅ Troubleshooting knowledge for common issues  

**Next Steps**:

1. Test all endpoints: `curl https://api.promptcrafting.net/health`
2. Monitor metrics in Cloudflare dashboard
3. Set up continuous deployment via GitHub Actions
4. Configure external monitoring/alerting
5. Review and optimize based on usage patterns

---

*Last Updated: 2024-02-09*  
*For questions or issues, please open a GitHub issue or contact the maintainers.*
