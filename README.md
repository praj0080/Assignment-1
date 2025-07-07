# Flask Auth0 App - Logging, Monitoring & Alerting

In this project we will display a secure Flask web application based on Auth0 auth, hosted on Azure, with a logging solution based on Application Insights, detection capabilities based on KQL, and monitoring based on Azure Alerts.

---

## 🔧 Setup Instructions

### 1. Auth0 Setup

1. Go to [Auth0 Dashboard](https://flask-auth0-app.azurewebsites.net/dashboard))
2.Make a new **Regular Web Application**
3. On the tab **Settings**:
- Enter your own callback URL (i.e. `https://flask-auth0-app.azurewebsites.net/callback`)
- Add your logout URL (`https://flask-auth0-app.azurewebsites.net`)
- Allowed web origins are set to: `http://localhost:5000`, etc.
4. In the settings of the app, acquire the following credentials:
- `AUTH0_CLIENT_ID`
- `AUTH0_CLIENT_SECRET`
- `AUTH0_DOMAIN`

### 2. Azure Setup
1. An **Azure App Service** (Linux) is created with Python 3.10 runtime.
2. Make an instance of Application Insights and connect it with your App Service.
3. Use GitHub or Azure CLI to deploy your Flask.
4. Turn on logging in **App Service App Service Monitoring Application Insights**.

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

- Ensure that you have connected Application Insights correctly.
- Make sure having a clear user_id in a well-organized form in your Flask logs.
- Test by sending several requests to `/protected` as if it was a group of users.
- Alerts assist in noticing suspicious actions of abnormality or brute-force efforts.

## Demo Vedio Link
