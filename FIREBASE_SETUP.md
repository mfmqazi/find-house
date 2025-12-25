# Firebase Security Setup Instructions

To implement real username/password security, we will use **Firebase Authentication** (by Google). It is free and works perfectly with GitHub Pages.

## Step 1: Create a Firebase Project
1. Go to [console.firebase.google.com](https://console.firebase.google.com/).
2. Click **Add project**.
3. Name it `find-house-auth` (or similar) and click **Continue** -> **Create Project**.

## Step 2: Enable Authentication
1. On the left menu, click **Build** -> **Authentication**.
2. Click **Get Started**.
3. In the "Sign-in method" tab, click **Email/Password**.
4. **Enable** the "Email/Password" toggle and click **Save**.

## Step 3: Create Users
1. Go to the **Users** tab (still in Authentication).
2. Click **Add user**.
3. Create accounts for your allowed users:
   - `mfmqazi@gmail.com` (Set a password)
   - `qazi.fatima@gmail.com` (Set a password)

## Step 4: Get Web Configuration
1. Click the **Project Settings** (Gear icon ⚙️ next to "Project Overview" at the top left).
2. Scroll down to the "Your apps" section.
3. Click the **</> (Web)** icon.
4. Give it a nickname (e.g., "HouseFinder") and click **Register app**.
5. You will see a code block: `const firebaseConfig = { ... }`.

**Please COPY that `firebaseConfig` object and paste it here.**
It looks like this:
```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "...",
  projectId: "...",
  storageBucket: "...",
  messagingSenderId: "...",
  appId: "..."
};
```
