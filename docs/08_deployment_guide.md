# Deployment Guide

Want to share your interactive dashboard online so anyone can open it in their browser? Here are three easy ways, starting with the **free, zero-server option**.

---

## Option 1: Streamlit Community Cloud (Recommended — Free)

**Streamlit Community Cloud** hosts Streamlit apps directly from your GitHub repository for free.

1. **Push your code to GitHub** (make sure `data/raw/netflix_titles.csv` and `.env` are **not** committed—`.gitignore` handles this).
2. Visit [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
3. Click **New app** and select:
   - **Repository**: `<your-username>/netflix-data-analysis`
   - **Branch**: `master` (or `main`)
   - **Main file path**: `app/streamlit_app.py`
4. *(Optional)* Click **Advanced settings** -> **Secrets** if you want the cloud app to download the full Kaggle dataset automatically:
   ```toml
   KAGGLE_USERNAME = "your_username"
   KAGGLE_KEY = "your_api_key"
   ```
   *(If you skip this, the app automatically runs on the 300-row sample dataset with a clear banner!)*
5. Click **Deploy!** Your app will be live in 1–2 minutes.

- **Cost**: **$0 / Free** for public GitHub repositories.

---

## Option 2: Docker (Run Anywhere)

A **Docker container** packages Python, all dependencies, and your app into one portable box that runs identically on any laptop or cloud server.

### Build and Run Locally
```bash
docker build -t netflix-explorer .
docker run -p 8501:8501 netflix-explorer
```
Open **`http://localhost:8501`** in your browser.

*(To pass optional Kaggle credentials into the container without baking them into the image: `docker run -p 8501:8501 -e KAGGLE_USERNAME=... -e KAGGLE_KEY=... netflix-explorer`.)*

---

## Option 3: Render or Railway (Cloud Containers)

Both **Render** and **Railway** can deploy directly from the included `Dockerfile`:

1. Create a new **Web Service** connected to your GitHub repo.
2. Choose **Docker** as the runtime/environment (it automatically detects `Dockerfile`).
3. Set the port to **`8501`** (if prompted).
4. *(Optional)* Add `KAGGLE_USERNAME` and `KAGGLE_KEY` in the dashboard's **Environment Variables** section.
5. Deploy!

- **Cost Notes**: Render offers a free tier (spins down after inactivity); Railway offers a low-cost usage-based plan with a trial credit.
