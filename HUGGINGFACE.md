# Deploying to HuggingFace Spaces

This guide explains how to deploy the ML Fine-tuning Platform to HuggingFace Spaces.

## Prerequisites

1. A HuggingFace account
2. Git installed on your local machine
3. The HuggingFace CLI installed (`pip install huggingface_hub`)

## Configuration Files

### requirements.txt

Ensure your `requirements.txt` includes all necessary dependencies:

```txt
streamlit==1.26.0
torch>=2.2.0
transformers==4.33.0
plotly==5.17.0
sqlalchemy==2.0.22
psycopg2-binary==2.9.7
flask-sqlalchemy==3.0.5
flask-migrate==4.0.4
numpy==1.25.2
datasets==2.14.5
evaluate==0.5.1
accelerate==0.23.0
flask==3.0.0
```

### Dockerfile

Create a `Dockerfile` in your project root:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]
```

## Deployment Steps

1. Create a new Space on HuggingFace:

   - Go to [HuggingFace Spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Choose "Streamlit" as the SDK
   - Name your space and set it to Public/Private

2. Clone your Space:

```bash
git clone https://huggingface.co/spaces/your-username/your-space-name
```

3. Copy your project files to the cloned directory

4. Push to HuggingFace:

```bash
cd your-space-name
git add .
git commit -m "Initial commit"
git push
```

## Environment Variables

Configure the following environment variables in your HuggingFace Space settings:

- `DATABASE_URL`: Your PostgreSQL database URL
- Any other sensitive configuration values

## Monitoring

After deployment:

1. Monitor your Space's logs for any issues
2. Check the Space's "Factory" tab for build status
3. Visit your Space's URL to verify the application is running correctly

## Updating Your Space

To update your deployed application:

1. Make changes to your local code
2. Commit and push to the Space repository:

```bash
git add .
git commit -m "Update description"
git push
```

The Space will automatically rebuild and deploy your changes.

## Troubleshooting

Common issues and solutions:

1. **Build Failures**

   - Check logs in the "Factory" tab
   - Verify all dependencies are in `requirements.txt`
   - Check for Python version compatibility

2. **Runtime Errors**

   - Check the application logs
   - Verify environment variables are set correctly
   - Check database connectivity

3. **Performance Issues**
   - Monitor resource usage in the Space settings
   - Consider optimizing model loading and inference
