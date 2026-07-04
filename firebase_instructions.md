# Provide Firebase Configuration

To complete the application and test the full end-to-end functionality (Authentication, AI Captioning, and saving straight to Firestore), you need to provide the actual configuration keys for your Firebase Project.

The AI Backend and Frontend are all built and ready! 

## Step 1: Frontend Config (`firebaseConfig`)
Please go to your Firebase Console > Project Settings > General.
Scroll down to "Your apps". If you haven't added a web app yet, click the `</>` icon to add one.
Copy the **`firebaseConfig`** object that looks like this:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyDoX...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdefgh"
};
```
Paste those exact values back to me here so I can inject them into `frontend/js/app.js`.

## Step 2: Backend Admin Key (`serviceAccountKey.json`)
We also need the Admin SDK credentials for the backend to verify the secure tokens and write data.
1. In Firebase Console > Project Settings > **Service accounts** tab
2. Click **Generate new private key** (this downloads a `.json` file)
3. Save that downloaded file directly into `c:\Users\91970\Desktop\MICG PROJECT\backend\` and name it exactly **`serviceAccountKey.json`**.
*(Note: I have already added this filename to your `.gitignore` so it won't be committed).*

## Step 3: Enable Authentication & Firestore
Make sure you've actually enabled these services in the Firebase dashboard:
1. **Authentication:** Go to Auth -> Sign-in method -> Enable **Email/Password**.
2. **Firestore Database:** Click Create Database. Start in **Test Mode** (we will change the rules later).

Let me know when you have generated the `serviceAccountKey.json` in the backend folder and pasted the `firebaseConfig` variables here!