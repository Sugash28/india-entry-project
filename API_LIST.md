# India-Entry API Documentation

This document provides a comprehensive list of all backend API endpoints. All routes are prefixed with `/api/v1`.

## 1. Authentication & Identity (`/auth`)

Manage user registration and login for both Clients and Service Providers, including social logins.

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| POST | `/auth/signup/client` | Register as a new Client. | No |
| POST | `/auth/login/client` | Email/Password login for Clients. | No |
| POST | `/auth/signup/service-provider` | Register as a new Service Provider. | No |
| POST | `/auth/login/service-provider` | Email/Password login for Service Providers. | No |
| POST | `/auth/login/google/{user_type}` | Google OAuth Login (`client` or `service_provider`). | No |
| POST | `/auth/login/microsoft/{user_type}` | Microsoft OAuth Login (`client` or `service_provider`). | No |

---

## 2. Client Profile Management (`/client`)

Manage company details, billing info, and preferences for client accounts.

| Method | Endpoint | Description | Role Required |
| :--- | :--- | :--- | :--- |
| GET | `/client/profile` | Get current client profile & completion %. | Client |
| PUT | `/client/personal-details` | Update bio, photo, and location. | Client |
| PUT | `/client/company-info` | Update company name/size/industry. | Client |
| PUT | `/client/contact-preferences` | Update notification/contact settings. | Client |
| PUT | `/client/billing-info` | Update billing address & GST details. | Client |

---

## 3. Service Provider Profile Management (`/service-provider`)

Showcase professional credentials and complete the onboarding process.

| Method | Endpoint | Description | Role Required |
| :--- | :--- | :--- | :--- |
| GET | `/service-provider/profile` | Get provider profile & completion %. | Provider |
| PUT | `/service-provider/professional-info` | Update title, rate, and skills. | Provider |
| POST | `/service-provider/portfolio` | Add past projects to portfolio. | Provider |
| POST | `/service-provider/experience` | Add work history. | Provider |
| POST | `/service-provider/education` | Add education background. | Provider |
| POST | `/service-provider/certification` | Add professional certifications. | Provider |
| POST | `/service-provider/kyc` | Upload digital KYC documentation. | Provider |

---

## 4. Projects & Bidding (`/client/projects`)

The core workflow for posting jobs and submitting proposals.

| Method | Endpoint | Description | Visibility |
| :--- | :--- | :--- | :--- |
| POST | `/client/projects/` | Create a new project. | Client (Owner) |
| GET | `/client/projects/` | List relevant projects. | **Mutual** |
| GET | `/client/projects/{id}` | Get specific project details. | **Mutual** |
| PUT | `/client/projects/{id}/bids/{bid_id}/accept` | Accept a bid (triggrers `pending_contract`). | Client (Owner) |
| POST | `/service-provider/projects/{id}/bid` | Submit a proposal for a project. | Provider |
| GET | `/service-provider/my-bids` | List all bids submitted by provider. | Provider |

---

## 5. Contract & Signature System (`/client/contracts`)

Legally binding agreement flow with photo signatures.

| Method | Endpoint | Description | Visibility |
| :--- | :--- | :--- | :--- |
| POST | `/client/contracts/` | Client signs contract & adds terms. | Client (Owner) |
| GET | `/client/contracts/` | List signed contracts & signatures. | **Mutual** |
| POST | `/client/contracts/{id}/sign/service-provider` | Provider counter-signs contract. | Provider |

---

## 6. Project Lifecycle & Escrow (`/client/projects`)

Post-contract workflow, work submission, and payment release.

| Method | Endpoint | Description | Required State |
| :--- | :--- | :--- | :--- |
| POST | `/client/projects/{id}/submit-work` | Upload PDF and GitHub links. | `IN_PROGRESS` |
| PUT | `/client/projects/{id}/release-funds` | Client releases funds & completes job. | `AWAITING_REVIEW` |

---

## Interactive Documentation

While the server is running, you can access the full interactive API documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
