# Frontend Testing Interface

A comprehensive, modern web interface for testing all India Entry Project backend APIs.

## Features

✨ **Premium UI Design**
- Modern glassmorphism effects
- Smooth animations and transitions
- Gradient backgrounds and buttons
- Responsive design for all screen sizes

🔐 **Authentication**
- Email/Password signup and login for both Client and Service Provider
- Google OAuth integration
- Microsoft OAuth integration
- Automatic token management
- User type detection and tab visibility control

👤 **Client APIs**
- Get profile with completion percentage
- Update personal details
- Update company information
- Update contact preferences
- Update billing information

💼 **Service Provider APIs**
- Get profile with completion percentage
- Update professional information
- Add portfolio projects
- Add work experience
- Add education
- Add certifications
- Upload KYC documents

🎯 **Smart UI**
- Tabs are hidden until authenticated
- Only relevant tab (Client or Service Provider) is shown based on login type
- Real-time API response display
- Success/error notifications
- Token copy functionality

## How to Use

### 1. Start the Backend Server

Make sure your backend is running:

```bash
cd e:\India-entry-backend\india-entry-project
uvicorn app.main:app --reload
```

The backend should be running at `http://localhost:8000`

### 2. Open the Frontend

**Option A: Direct File Open**
- Simply open `index.html` in your web browser
- Navigate to: `e:\India-entry-backend\india-entry-project\frontend\index.html`

**Option B: Using a Local Server (Recommended for OAuth)**
```bash
cd e:\India-entry-backend\india-entry-project\frontend
python -m http.server 8080
```
Then open: `http://localhost:8080`

### 3. Test Authentication

1. **Sign Up**: Create a new account as Client or Service Provider
2. **Login**: Login with email/password
3. **OAuth**: Use Google or Microsoft login buttons

After successful authentication:
- Your access token will be displayed at the top
- The relevant tab (Client or Service Provider) will automatically show
- You can now test all profile APIs

### 4. Test APIs

**For Clients:**
- Click "Get Profile" to fetch your profile
- Fill out forms to update personal details, company info, contact preferences, or billing info
- See real-time responses in the API Response section

**For Service Providers:**
- Click "Get Profile" to fetch your profile
- Update professional information
- Add portfolio projects, work experience, education, certifications
- Upload KYC documents
- See real-time responses in the API Response section

## API Endpoints

### Authentication
- `POST /api/v1/signup/client` - Client signup
- `POST /api/v1/login/client` - Client login
- `POST /api/v1/signup/service-provider` - Service Provider signup
- `POST /api/v1/login/service-provider` - Service Provider login
- `POST /api/v1/login/google/{user_type}` - Google OAuth
- `POST /api/v1/login/microsoft/{user_type}` - Microsoft OAuth

### Client APIs (Requires Authentication)
- `GET /api/v1/client/profile` - Get client profile
- `PUT /api/v1/client/personal-details` - Update personal details
- `PUT /api/v1/client/company-info` - Update company info
- `PUT /api/v1/client/contact-preferences` - Update contact preferences
- `PUT /api/v1/client/billing-info` - Update billing info

### Service Provider APIs (Requires Authentication)
- `GET /api/v1/service-provider/profile` - Get service provider profile
- `PUT /api/v1/service-provider/professional-info` - Update professional info
- `POST /api/v1/service-provider/portfolio` - Add portfolio project
- `POST /api/v1/service-provider/experience` - Add work experience
- `POST /api/v1/service-provider/education` - Add education
- `POST /api/v1/service-provider/certification` - Add certification
- `POST /api/v1/service-provider/kyc` - Upload KYC document

## OAuth Setup

### Google OAuth
- Client ID is already configured in `app.js`
- Make sure your Google Cloud Console has the correct redirect URIs

### Microsoft OAuth
- Client ID and Tenant ID are already configured in `app.js`
- Make sure your Azure Portal has the correct redirect URIs

## Troubleshooting

**CORS Errors:**
- Make sure your backend has CORS enabled for `http://localhost:8080` or `file://`

**OAuth Not Working:**
- Check that OAuth credentials in `app.js` match your `.env` file
- Verify redirect URIs in Google/Microsoft consoles

**Token Not Persisting:**
- Token is stored in localStorage
- Clear browser cache if experiencing issues

**APIs Returning 401:**
- Make sure you're logged in
- Check that the token is displayed at the top
- Try logging in again

## Files

- `index.html` - Main HTML structure
- `style.css` - Premium styling with animations
- `app.js` - JavaScript with API integration
- `README.md` - This file

## Technologies Used

- HTML5
- CSS3 (Glassmorphism, Gradients, Animations)
- Vanilla JavaScript
- Google Sign-In SDK
- Microsoft Authentication Library (MSAL)
- Inter Font (Google Fonts)

---

Built with ❤️ for India Entry Project
