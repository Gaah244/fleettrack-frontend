# FleetTrack - Commission Monitoring System

A modern web application for monitoring driver and helper commissions based on delivery counts across different truck types.

## Features

### User Features
- ✅ User registration & login (driver/helper/admin roles)
- ✅ Personal dashboard showing total deliveries and commission
- ✅ Breakdown by truck type with automatic commission calculation
- ✅ Secure JWT-based authentication

### Admin Features
- ✅ Admin panel to view all users and their statistics
- ✅ Update delivery counts for each user and truck type
- ✅ Monthly reset button to clear all deliveries
- ✅ View total commission and deliveries for each user

### Commission Rates
- **BKO, PYW, NYC**: R$ 3.50 per delivery
- **GKY, GSD**: R$ 7.50 per delivery
- **AUA**: R$ 10.00 per delivery

## Tech Stack

- **Frontend**: React, Tailwind CSS, Shadcn/UI components
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Authentication**: JWT with bcrypt password hashing

## Local Development

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB (local or Atlas)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB connection
uvicorn server:app --reload --port 8001
```

### Frontend Setup
```bash
cd frontend
yarn install
cp .env.example .env
# Edit .env with your backend URL
yarn start
```

Visit `http://localhost:3000` to see the app.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to Render.

### Quick Deploy with Render Blueprint

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click the button above
2. Fill in environment variables
3. Deploy!

## Project Structure

```
fleettrack/
├── backend/
│   ├── server.py           # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── pages/          # Page components
│   │   └── components/     # Reusable UI components
│   ├── package.json        # Node dependencies
│   └── .env.example        # Environment variables template
├── render.yaml             # Render deployment configuration
└── DEPLOYMENT.md           # Deployment guide
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Deliveries
- `GET /api/deliveries/my` - Get personal deliveries
- `POST /api/deliveries/update` - Update deliveries (admin)
- `GET /api/deliveries/all-users` - Get all users (admin)
- `POST /api/deliveries/reset-month` - Reset monthly deliveries (admin)

## License

MIT License - feel free to use this project for your own purposes.

## Support

For issues or questions, please open an issue on GitHub.