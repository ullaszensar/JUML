# JUML Deployment Guide

This document provides detailed instructions for deploying the JUML application in various environments.

## Deployment on Replit

JUML is optimized for easy deployment on Replit. Follow these steps:

1. **Fork the project on Replit**:
   - Go to the original JUML project on Replit
   - Click the "Fork" button to create your own copy

2. **Run the application**:
   - Click the "Run" button in Replit
   - Replit will automatically install the required dependencies and start the application
   - The application will be served at the URL provided by Replit

3. **Make the application public**:
   - Go to your project settings
   - Under "Privacy", select "Public" to make your application accessible to others

4. **Share your application**:
   - Use the provided Replit URL to share your JUML instance with others

## Deployment on a Server

For deploying JUML on your own server or cloud infrastructure:

1. **Clone the repository**:
   ```
   git clone https://github.com/yourusername/juml.git
   cd juml
   ```

2. **Set up a Python environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```
   pip install streamlit graphviz pydantic
   ```

4. **Running with Streamlit**:
   ```
   streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
   ```

5. **Production deployment with Docker** (recommended):

   Create a `Dockerfile`:
   ```
   FROM python:3.10-slim

   WORKDIR /app

   RUN apt-get update && apt-get install -y \
       graphviz \
       && rm -rf /var/lib/apt/lists/*

   COPY . .
   RUN pip install --no-cache-dir streamlit graphviz pydantic

   EXPOSE 5000

   CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0", "--server.headless=true"]
   ```

   Build and run the Docker container:
   ```
   docker build -t juml .
   docker run -p 5000:5000 juml
   ```

## Serving Behind a Reverse Proxy

For production deployments, it's recommended to serve JUML behind a reverse proxy like Nginx:

```
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Environment Variables

JUML doesn't require any environment variables for basic operation, but you can configure Streamlit behavior using environment variables. See the [Streamlit documentation](https://docs.streamlit.io/library/advanced-features/configuration) for details.

## Troubleshooting

- **Graphviz Errors**: Ensure that Graphviz is installed on your system
- **Port Conflicts**: If port 5000 is in use, change the port in the `.streamlit/config.toml` file or use the `--server.port` parameter
- **Memory Issues**: For large Java projects, you might need to increase memory limits (Docker: `--memory=2g`)