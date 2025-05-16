# Usage Guide

This guide explains how to use the AIC-HCMUS Fragment Segmentation application, from setup to making predictions.

---

## 1. Prerequisites

- Docker and Docker Compose installed
- Modern web browser (for frontend)
- (Optional) Python 3.10+ and Node.js (for manual setup)

---

## 2. Running the Application

### Using Docker Compose

1. Clone the repository:
   ```sh
   git clone https://github.com/magnusdtd/AIC-HCMUS-Fragment-Segmentation.git
   cd AIC-HCMUS-Fragment-Segmentation
   ```

2. Start all services:
   ```sh
   docker-compose up --build
   ```

3. Access the frontend at [http://localhost:5173](http://localhost:5173)  
   The backend API runs at [http://localhost:8000](http://localhost:8000)

---

## 3. Manual Setup (Development)

### Backend

1. Install dependencies:
   ```sh
   cd backend
   pip install -r requirements.txt
   ```

2. Start the FastAPI server:
   ```sh
   uvicorn app.main:app --reload
   ```

### Frontend

1. Install dependencies:
   ```sh
   cd frontend
   npm install
   ```

2. Start the development server:
   ```sh
   npm run dev
   ```

---

## 4. User Workflow

### 1. Register and Login

- Open the web app.
- Register a new account or log in with existing credentials.

### 2. Upload an Image

- Navigate to the prediction page.
- Upload an image file (e.g., a fragment image).
- Submit to receive segmentation results.

### 3. View Results

- Segmentation results are displayed on the page.
- You can view your uploaded images and results in your user dashboard.

---

## 5. API Usage

- See [API Documentation](api.md) for details on available endpoints and request formats.

---

## 6. Troubleshooting

- Ensure Docker containers are running (`docker ps`).
- Check logs for errors (`docker-compose logs`).
- For manual setup, verify all dependencies are installed.

---

For further help, see the [About](about.md) page or open an issue on GitHub.