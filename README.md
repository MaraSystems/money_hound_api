# MoneyHound API Documentation

MoneyHound is a comprehensive financial simulation and analysis platform that helps users understand their financial behaviors through AI-powered insights and transaction simulations.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Features](#features)
- [Response Format](#response-format)
- [Error Handling](#error-handling)

## Overview

MoneyHound provides a FastAPI-based REST API with JWT Bearer authentication. The platform offers:

- 🔐 Secure user authentication with OTP verification
- 💬 AI-powered chatbot for financial guidance
- 📊 Financial transaction simulations
- 📈 Advanced analytics and insights
- 👥 Role-based access control
- 🔔 Real-time notifications

**Base URL**: `https://api.moneyhound.com` (replace with your actual domain)

**API Version**: 1.0.0

**OpenAPI Specification**: Available at `/openapi.json`

## Getting Started

### Prerequisites

- API access credentials
- HTTP client (cURL, Postman, or any programming language)
- JWT token for authenticated requests

### Quick Start

1. **Register a new account**
```bash
curl -X POST https://api.moneyhound.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securePassword123",
    "name": "John Doe"
  }'
```

2. **Request OTP for verification**
```bash
curl -X GET https://api.moneyhound.com/auth/request?email=user@example.com
```

3. **Verify OTP and get access token**
```bash
curl -X POST https://api.moneyhound.com/auth/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp": "123456"
  }'
```

4. **Use the token for authenticated requests**
```bash
curl -X GET https://api.moneyhound.com/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Authentication

MoneyHound uses JWT (JSON Web Token) Bearer authentication. Include the token in the Authorization header for all authenticated endpoints.

### Endpoints

#### Register User
```http
POST /auth/register
```

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe"
}
```

#### Request OTP
```http
GET /auth/request?email=user@example.com
```

Request an OTP for email verification or login.

#### Verify OTP
```http
POST /auth/verify
```

Verify OTP and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response:**
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

#### Get User Profile
```http
GET /auth/profile
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Update User Profile
```http
PATCH /auth/profile
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body:**
```json
{
  "name": "Jane Doe",
  "preferences": {}
}
```

#### Delete User Profile
```http
DELETE /auth/profile
Authorization: Bearer YOUR_JWT_TOKEN
```

## API Endpoints

### Users

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/users` | Fetch all users | ✅ |
| GET | `/users/{id}` | Get specific user | ✅ |

### Roles & Permissions

Manage role-based access control for your application.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/roles/domains` | List available role domains | ✅ |
| POST | `/roles` | Create a new role | ✅ |
| GET | `/roles` | List all roles | ✅ |
| GET | `/roles/{id}` | Get specific role | ✅ |
| PATCH | `/roles/{id}` | Update role | ✅ |
| DELETE | `/roles/{id}` | Delete role | ✅ |
| POST | `/roles/{id}/assign/{user_id}` | Assign role to user | ✅ |
| DELETE | `/roles/{id}/unassign/{user_id}` | Unassign role from user | ✅ |

### Notifications

Real-time notification management system.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/notifications` | Create notification | ✅ |
| GET | `/notifications` | List all notifications | ✅ |
| GET | `/notifications/{id}` | Get specific notification | ✅ |
| PUT | `/notifications/{id}` | Mark notification as read | ✅ |

### Chat Bot

AI-powered financial assistant for personalized guidance.

#### Chat with Bot
```http
POST /bot/chat
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body:**
```json
{
  "message": "How can I save more money?",
  "session_id": "optional-session-id"
}
```

#### Get Chat History
```http
GET /bot/chat/{session_id}
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Sync Chat Data
```http
POST /bot/sync
Authorization: Bearer YOUR_JWT_TOKEN
```

### Simulations

Create and manage financial simulations to test different scenarios.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/simulations` | Create new simulation | ✅ |
| GET | `/simulations` | List all simulations | ✅ |
| GET | `/simulations/{id}` | Get specific simulation | ✅ |
| PATCH | `/simulations/{id}` | Update simulation | ✅ |
| DELETE | `/simulations/{id}` | Delete simulation | ✅ |
| GET | `/simulations/{id}/analyze` | Analyze simulation results | ✅ |

**Example: Create Simulation**
```json
{
  "name": "6-Month Budget Plan",
  "description": "Testing savings strategy",
  "start_date": "2025-01-01",
  "end_date": "2025-06-30"
}
```

### Simulation Transactions

Manage transactions within simulations.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/simulation_transactions` | Create transaction | ✅ |
| GET | `/simulation_transactions` | List transactions | ✅ |
| GET | `/simulation_transactions/{id}` | Get specific transaction | ✅ |

**Example: Create Transaction**
```json
{
  "simulation_id": "sim_123",
  "amount": 150.00,
  "category": "groceries",
  "date": "2025-01-15",
  "description": "Weekly groceries"
}
```

### Simulation Profiles

Define financial profiles for different scenarios.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/simulation_profiles` | Create profile | ✅ |
| GET | `/simulation_profiles` | List profiles | ✅ |
| GET | `/simulation_profiles/{id}` | Get specific profile | ✅ |
| GET | `/simulation_profiles/{id}/analyze` | Analyze profile | ✅ |

### Simulation Accounts

Manage financial accounts within simulations.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/simulation_accounts` | Create account | ✅ |
| GET | `/simulation_accounts` | List accounts | ✅ |
| GET | `/simulation_accounts/{id}` | Get specific account | ✅ |
| GET | `/simulation_accounts/{id}/analyze` | Analyze account | ✅ |

### Simulation Bank Devices

Track banking devices and connections.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/simulation_bank_devices` | List bank devices | ✅ |
| GET | `/simulation_bank_devices/{id}` | Get specific device | ✅ |

## Features

### 1. Financial Simulations
Create hypothetical financial scenarios to test different spending and saving strategies before implementing them in real life.

### 2. AI-Powered Chat Assistant
Get personalized financial advice and insights through natural conversations with the MoneyHound chatbot.

### 3. Transaction Analysis
Advanced analytics to understand spending patterns, identify trends, and optimize financial decisions.

### 4. Role-Based Access
Granular permission system to manage team access and collaboration on financial planning.

### 5. Real-Time Notifications
Stay updated with important financial events, insights, and recommendations.

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "data": {
    // Response data
  },
  "message": "Success",
  "status": "success"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "status": "error"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Error Handling

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error |

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Standard tier**: 100 requests per minute
- **Premium tier**: 1000 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## SDK & Client Libraries

Official SDKs are available for:

- **Python**: `pip install moneyhound-sdk`
- **JavaScript/Node.js**: `npm install moneyhound-sdk`
- **Go**: `go get github.com/moneyhound/moneyhound-go`

## Support

- **Documentation**: https://docs.moneyhound.com
- **Email**: support@moneyhound.com
- **Community**: https://community.moneyhound.com
- **Status Page**: https://status.moneyhound.com

## License

MoneyHound API is proprietary software. Usage is subject to the terms of service available at https://moneyhound.com/terms

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**Maintained by**: MoneyHound Team