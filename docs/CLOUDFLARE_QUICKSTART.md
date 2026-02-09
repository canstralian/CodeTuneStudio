# Cloudflare Workers Quick Start Guide

Get CodeTuneStudio running on Cloudflare Workers in 5 minutes.

## Prerequisites

- Cloudflare account ([Sign up free](https://dash.cloudflare.com/sign-up))
- Node.js 16+ installed
- npm or yarn package manager

## Step-by-Step Setup

### 1. Install Wrangler CLI

```bash
npm install -g wrangler
```

### 2. Authenticate with Cloudflare

```bash
wrangler login
```

This opens a browser window for authentication.

### 3. Configure Your Worker

Edit `wrangler.toml` and add your account ID:

```toml
account_id = "your-account-id-here"  # Get from Cloudflare dashboard
```

**Find your account ID:**
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Click on "Workers & Pages"
3. Your Account ID is shown in the right sidebar

### 4. Set Environment Secrets

```bash
# Database connection
wrangler secret put DATABASE_URL

# API keys
wrangler secret put OPENAI_API_KEY
wrangler secret put ANTHROPIC_API_KEY
wrangler secret put HF_TOKEN

# Security
wrangler secret put SECRET_KEY
```

When prompted, enter each secret value.

### 5. Test Locally

```bash
# Copy example environment variables
cp .dev.vars.example .dev.vars

# Edit .dev.vars with your local test values
nano .dev.vars  # or use your preferred editor

# Start local development server
wrangler dev
```

Visit http://localhost:8787 to test locally.

### 6. Deploy to Production

```bash
# Deploy to Cloudflare Workers
wrangler deploy --env production
```

Your worker is now live at: `https://codetune-studio.your-subdomain.workers.dev`

### 7. Add Custom Domain (Optional)

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **Workers & Pages** → Select your worker
3. Click **Triggers** tab
4. Click **Add Custom Domain**
5. Enter your domain (e.g., `api.promptcrafting.net`)
6. Click **Add Custom Domain**

SSL certificate is automatically provisioned!

Test your custom domain:
```bash
curl https://api.promptcrafting.net/health
```

## Verify Deployment

Check that your deployment is working:

```bash
# Health check
curl https://your-worker.workers.dev/health

# API status
curl https://your-worker.workers.dev/api/status
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-02-09T08:00:00.000Z",
  "environment": "production",
  "worker": "codetune-studio"
}
```

## View Logs

```bash
# Tail production logs
wrangler tail --env production

# Filter for errors only
wrangler tail --status error
```

## Update Deployment

```bash
# Make code changes, then redeploy
wrangler deploy --env production
```

## Troubleshooting

### Issue: "Error: Missing account_id"
**Solution:** Add your account ID to `wrangler.toml`

### Issue: "Error: Authentication failed"
**Solution:** Run `wrangler login` again

### Issue: Custom domain not working
**Solution:** 
1. Check DNS propagation: `nslookup your-domain.com`
2. Wait 5-10 minutes for DNS to propagate
3. Verify domain is added in Workers dashboard

### Issue: Environment variables undefined
**Solution:**
1. Set secrets: `wrangler secret put VARIABLE_NAME`
2. Redeploy: `wrangler deploy`

## Next Steps

- 📖 Read full documentation: [docs/CLOUDFLARE_WORKERS.md](./CLOUDFLARE_WORKERS.md)
- 🔧 Configure monitoring and observability
- 🚀 Set up CI/CD with GitHub Actions
- 📊 Review analytics in Cloudflare Dashboard

## Resources

- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/wrangler/)
- [CodeTuneStudio GitHub](https://github.com/canstralian/CodeTuneStudio)

## Support

Having issues? 
- Open an issue: [GitHub Issues](https://github.com/canstralian/CodeTuneStudio/issues)
- Cloudflare Community: [community.cloudflare.com](https://community.cloudflare.com)
