# FleetTrack - Render Deployment Guide

This guide will help you deploy FleetTrack on Render.

## Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **MongoDB Atlas Account** - Sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)

---

## Step 1: Set Up MongoDB Atlas

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) and create an account
2. Create a **New Cluster** (free M0 tier is sufficient)
3. Wait for cluster creation (2-3 minutes)
4. Click **Database Access** → **Add New Database User**:
   - Username: `fleettrack_user`
   - Password: Generate a secure password (save it!)
   - Role: `Atlas Admin` or `Read and write to any database`
5. Click **Network Access** → **Add IP Address**:
   - Click **Allow Access from Anywhere**
   - IP: `0.0.0.0/0`
   - Confirm
6. Click **Database** → **Connect** → **Connect your application**
7. Copy the connection string:
   ```
   mongodb+srv://fleettrack_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
8. Replace `<password>` with your actual password

---

## Step 2: Push Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - FleetTrack app"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/fleettrack.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy Backend on Render

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub account and select your repository
4. Configure the service:

   **Basic Settings:**
   - **Name**: `fleettrack-backend`
   - **Region**: Choose closest to your location
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`

   **Build & Deploy:**
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     uvicorn server:app --host 0.0.0.0 --port $PORT
     ```

5. Click **Advanced** → **Add Environment Variable**:

   | Key | Value |
   |-----|-------|
   | `MONGO_URL` | Your MongoDB connection string from Step 1 |
   | `DB_NAME` | `fleettrack_db` |
   | `SECRET_KEY` | Generate a random string (e.g., `openssl rand -hex 32`) |
   | `CORS_ORIGINS` | `*` |

6. Click **Create Web Service**
7. Wait for deployment (3-5 minutes)
8. **Copy your backend URL** (e.g., `https://fleettrack-backend.onrender.com`)

---

## Step 4: Deploy Frontend on Render

1. In Render Dashboard, click **New +** → **Static Site**
2. Select your GitHub repository
3. Configure the static site:

   **Basic Settings:**
   - **Name**: `fleettrack-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`

   **Build & Deploy:**
   - **Build Command**: 
     ```bash
     npm install --legacy-peer-deps && npm run build
     ```
     OR if using Yarn:
     ```bash
     yarn install && yarn build
     ```
   - **Publish Directory**: `build`

4. Click **Advanced** → **Add Environment Variable**:

   | Key | Value |
   |-----|-------|
   | `REACT_APP_BACKEND_URL` | Your backend URL from Step 3 |

5. Click **Create Static Site**
6. Wait for deployment (2-4 minutes)
7. **Copy your frontend URL** (e.g., `https://fleettrack-frontend.onrender.com`)

---

## Step 5: Update CORS (Important!)

1. Go back to your **Backend Service** in Render
2. Click **Environment**
3. Update `CORS_ORIGINS` to your frontend URL:
   ```
   https://fleettrack-frontend.onrender.com
   ```
4. Click **Save Changes** (this will trigger a redeploy)

---

## Step 6: Test Your Application

1. Visit your frontend URL
2. **Register a new account**:
   - Username: `admin`
   - Password: `admin123`
   - Role: `Admin`
3. **Test features**:
   - Login with credentials
   - Create driver/helper accounts
   - Update deliveries
   - Check commission calculations
   - Test monthly reset

---

## Troubleshooting

### Backend not starting?
- Check **Logs** in Render dashboard
- Verify MongoDB connection string is correct
- Ensure all environment variables are set

### Frontend can't connect to backend?
- Verify `REACT_APP_BACKEND_URL` is correct
- Check CORS settings in backend
- Open browser console for error messages

### Database connection errors?
- Verify MongoDB Atlas IP whitelist includes `0.0.0.0/0`
- Check database user permissions
- Test connection string format

---

## Custom Domain (Optional)

1. In Render dashboard, go to your service
2. Click **Settings** → **Custom Domains**
3. Add your domain (e.g., `fleettrack.com`)
4. Update DNS records as instructed
5. Update `REACT_APP_BACKEND_URL` and `CORS_ORIGINS` with new domain

---

## Automatic Deployments

Render automatically deploys when you push to your `main` branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render will detect changes and redeploy automatically!

---

## Cost Estimation

**Free Tier:**
- Backend: Free (spins down after inactivity)
- Frontend: Free
- MongoDB: Free (M0 cluster, 512MB)

**Paid Tier (if needed):**
- Backend: $7/month (always on)
- Frontend: Free
- MongoDB: $9/month (M2 cluster, 2GB)

---

## Support

If you encounter issues:
- Check Render [documentation](https://render.com/docs)
- Join Render [community](https://community.render.com)
- MongoDB Atlas [support](https://www.mongodb.com/docs/atlas/)

---

**Congratulations! Your FleetTrack app is now live! 🎉**