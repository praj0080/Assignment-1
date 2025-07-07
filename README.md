# Flask Auth0 App - Logging, Monitoring & Alerting

This project demonstrates a secure Flask web application using Auth0 for authentication, deployed on Azure, with Application Insights for logging, KQL for detection, and Azure Alerts for monitoring.

---

## 🔧 Setup Instructions

### 1. Auth0 Setup
## 🔧 Setup Instructions

### 1. ⚙️ Auth0 Setup

1. Go to [Auth0 Dashboard](https://manage.auth0.com/)
2. Create a new **Regular Web Application**
3. Under the **Settings** tab:
   - Add your callback URL (e.g., `https://flask-auth0-app.azurewebsites.net/callback`)
   - Add your logout URL (e.g., `https://flask-auth0-app.azurewebsites.net`)
   - Set allowed web origins: `http://localhost:5000`, etc.
4. Get the following credentials from the app settings:
   - `AUTH0_CLIENT_ID`
   - `AUTH0_CLIENT_SECRET`
   - `AUTH0_DOMAIN`

### 2. Azure Setup
1. Create an **Azure App Service** (Linux) using Python 3.10 runtime.
2. Create an **Application Insights** instance and link it to your App Service.
3. Deploy your Flask app via GitHub or Azure CLI.
4. Enable logging under **App Service → Monitoring → Application Insights**.

### 3. Create `.env` File

Create a `.env` file in the root of your Flask app with:

```env
AUTH0_CLIENT_ID=your_auth0_client_id
AUTH0_CLIENT_SECRET=your_auth0_client_secret
AUTH0_DOMAIN=your_auth0_domain
AUTH0_CALLBACK_URL=https://flask-auth0-app.azurewebsites.net/callback
APP_SECRET_KEY=your_flask_secret_key
```

You can generate a secret key with:
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

---

---

## 📜 Logging Explanation

The Flask app logs:
- Successful Auth0 logins
- Access to `/protected` route
- Unauthorized attempts

These logs are captured by **Azure Application Insights** via built-in instrumentation.

Example log format for `/protected` access:
```
user_id=12345678abcd accessed /protected at 2025-07-06T11:00Z
```

## 🔍 Detection Logic with KQL

To identify potential misuse of the `/protected` route, we use this **Kusto Query Language (KQL)**:

```
requests
| where name has "/protected"
| where timestamp > ago(15m)
| extend user_info = tostring(customDimensions.user_id)
| summarize access_count = count(), last_access = max(timestamp) by user_info
| where access_count > 10
| project user_info, last_access, access_count
```

This query checks if any user accessed the protected route more than **10 times in the last 15 minutes**.

---

## 🚨 Alert Logic


**Alert Rule Setup:**

- **Query Source**: Application Insights → Logs
- **Query**: Use the KQL above
- **Threshold**: If `access_count` > 10 in 15 minutes
- **Evaluation Frequency**: Every 5 minutes
- **Severity**: 3 (Low)

### 📧 Action Group

- Create an **Action Group**
- Select **Email** as the notification method
- Add your email address to receive alert notifications

---

## ✅ Final Notes

- Make sure Application Insights is properly linked.
- Ensure your Flask logs include a clear `user_id` in a structured format.
- Simulate multiple accesses to `/protected` for testing.
- Alerts help identify abnormal behavior or brute-force attempts.

## Demo Vedio Link
