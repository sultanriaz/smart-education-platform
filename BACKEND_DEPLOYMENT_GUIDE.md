# SmartEdu Platform — Backend Deployment Guide

This guide details how to deploy the **SmartEdu Backend Microservices & API Gateway** so your live Vercel frontend (`https://smart-education-platform-teal.vercel.app`) can connect and operate end-to-end.

---

## Deployment Options at a Glance

| Option | Ideal For | Difficulty | Setup Time | Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Option 1: Cloudflare Tunnel / ngrok** | Immediate live testing with Vercel | Very Easy | 2 minutes | **Free** |
| **Option 2: Railway or Render (PaaS)** | Automated cloud hosting with free HTTPS | Easy (1-Click) | 5 minutes | Free tier / $5/mo |
| **Option 3: Linux Cloud VPS (DigitalOcean/AWS/EC2)** | Production hosting with custom domain | Intermediate | 15 minutes | $5–$10/mo |

---

## Option 1: Instant Free HTTPS Tunnel (Recommended for Immediate Testing)

If your backend is running locally on your computer and you want to test your **live Vercel frontend** right now without paying for a cloud server:

### Step 1: Start the Backend Locally
In your project root terminal:
```bash
python run.py
```
*(Starts the API Gateway on port `18080` and all 12 microservices).*

### Step 2: Open a Free HTTPS Tunnel
In a new terminal window, run either:

**Via Cloudflare Tunnel (100% Free, No Account / Login Required):**
```bash
npx cloudflared tunnel --url http://localhost:18080
```
*Cloudflare will print a public HTTPS URL such as `https://random-subdomain.trycloudflare.com`.*

**OR via ngrok:**
```bash
ngrok http 18080
```
*ngrok will output a URL like `https://xxxx.ngrok-free.app`.*

### Step 3: Connect to Vercel
1. Go to your [Vercel Dashboard](https://vercel.com) → Select `smart-education-platform`.
2. Go to **Settings → Environment Variables**.
3. Add or update:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://your-tunnel-subdomain.trycloudflare.com` (your tunnel URL, no trailing slash).
4. Go to **Deployments** → Click **Redeploy**.
5. Refresh your Vercel site — registration, login, and all student features will work end-to-end!

---

## Option 2: 1-Click Cloud Deployment via Railway or Render

You can deploy the backend directly to **Railway** or **Render** using the included root [`Dockerfile`](file:///c:/black_paper/Projects/smart-education-platform/Dockerfile).

### Deploying to Railway (Fastest)

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **New Project → Deploy from GitHub Repo**.
3. Select `smart-education-platform`.
4. Railway will automatically detect the root [`Dockerfile`](file:///c:/black_paper/Projects/smart-education-platform/Dockerfile).
5. Add a **PostgreSQL** database service in the same project:
   - Click **+ New → Database → Add PostgreSQL**.
6. Under your backend service settings:
   - Go to **Networking** → Click **Generate Domain**.
   - Railway will provide an HTTPS URL like `https://smartedu-backend.up.railway.app`.
7. Add this URL to your **Vercel** project:
   - `VITE_API_BASE_URL` = `https://smartedu-backend.up.railway.app`.

### Deploying to Render

1. Go to [render.com](https://render.com) and sign in.
2. Click **New + → Web Service**.
3. Connect your `smart-education-platform` GitHub repository.
4. Set:
   - **Environment**: `Docker`
   - **Dockerfile Path**: `Dockerfile`
   - **Instance Type**: Free or Starter
5. Click **Create Web Service**.
6. Copy the provided Render URL (e.g., `https://smartedu-api.onrender.com`) into Vercel's `VITE_API_BASE_URL`.

---

## Option 3: Linux Cloud VPS (Ubuntu 22.04 / 24.04 on DigitalOcean, AWS, Linode)

For a dedicated server with your own domain (e.g., `https://api.yourdomain.com`):

### Step 1: Install Docker & Git on your VPS
```bash
sudo apt update && sudo apt install -y git docker.io docker-compose
sudo systemctl enable --now docker
```

### Step 2: Clone the Repository
```bash
git clone https://github.com/sultanriaz/smart-education-platform.git
cd smart-education-platform
```

### Step 3: Build and Run the Backend Container
```bash
docker build -t smartedu-backend .
docker run -d --restart always -p 18080:18080 --name smartedu-api smartedu-backend
```

### Step 4: Configure Nginx Reverse Proxy with Free SSL
Install Nginx and Certbot:
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

Create `/etc/nginx/sites-available/api.yourdomain.com`:
```nginx
server {
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:18080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site and obtain SSL:
```bash
sudo ln -s /etc/nginx/sites-available/api.yourdomain.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d api.yourdomain.com
```

### Step 5: Update Vercel
In Vercel **Settings → Environment Variables**:
- `VITE_API_BASE_URL` = `https://api.yourdomain.com`
Redeploy Vercel.
