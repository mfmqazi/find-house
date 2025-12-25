# Deploying to GitHub and GitHub Pages

## 1. Safety First
I have secured your credentials (API Key, Group ID) in a `.env` file and configured `.gitignore` so they will **never** be uploaded to GitHub.

## 2. Setup GitHub Repository
1. Go to [GitHub.com](https://github.com/new).
2. Create a new repository named `find-house`.
3. Do **NOT** initialize with README/gitignore (we have them).

## 3. Push Code
Run the following commands in your terminal:

```powershell
git init
git add .
git commit -m "Initial commit for House Finder v1"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/find-house.git
git push -u origin main
```

## 4. Enable GitHub Pages
1. Go to your repository **Settings** tab.
2. Click **Pages** on the left menu.
3. Under **Build and deployment**, select **Source** -> `Deploy from a branch`.
4. Select `main` branch and `/ (root)` folder.
5. Click **Save**.

Your visualization will soon be live at:
`https://YOUR_USERNAME.github.io/find-house/`

## 5. Running the Bot (Locally)
Since the bot relies on scraping (Playwright), it is best run locally.
1. Run `python find_houses.py`.
2. It will generate `index.html`.
3. To update the live site, just push the new HTML:
   ```powershell
   git add index.html
   git commit -m "Update listings"
   git push
   ```
