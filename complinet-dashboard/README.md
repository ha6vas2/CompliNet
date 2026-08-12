# CompliNet Network Compliance Dashboard

## Overview
CompliNet is a network compliance dashboard designed to help organizations monitor and manage their network devices' compliance status. This application provides a user-friendly interface for viewing compliance data, managing devices, and generating reports.

## Project Structure
The project is divided into two main parts: the backend and the frontend.

### Backend
The backend is built using FastAPI and is responsible for handling API requests, managing data, and implementing business logic. The structure of the backend is as follows:

- `app/`
  - `api/`
    - `routers/`
      - `compliance.py`: API endpoints related to compliance data.
      - `devices.py`: API endpoints for device management.
    - `__init__.py`: Initializes the API module.
  - `core/`
    - `config.py`: Application configuration settings.
    - `security.py`: Security-related functions.
  - `models/`
    - `device.py`: Data model for devices.
  - `schemas/`
    - `compliance.py`: Data schemas for compliance data.
    - `device.py`: Data schemas for device data.
  - `services/`
    - `compliance_service.py`: Business logic for compliance operations.
    - `inventory_service.py`: Business logic for managing device inventory.
  - `main.py`: Entry point of the FastAPI application.

### Frontend
The frontend is built using React with Vite and provides a responsive user interface for interacting with the backend. The structure of the frontend is as follows:

- `public/`
  - `index.html`: Main HTML file for the React application.
- `src/`
  - `assets/`: Static assets such as images and icons.
  - `components/`
    - `ComplianceDashboard.jsx`: Component for displaying compliance status.
    - `DeviceList.jsx`: Component for displaying a list of devices.
  - `pages/`
    - `Home.jsx`: Main dashboard view.
    - `Settings.jsx`: Settings page for user configurations.
  - `services/`
    - `api.js`: Functions for making API calls to the backend.
  - `App.jsx`: Main application component.
  - `main.jsx`: Entry point for the React application.
  - `styles.css`: Styles for the frontend application.

## Setup Instructions

### Backend
1. Navigate to the `backend` directory.
2. Create a virtual environment and activate it.
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables by copying `.env.example` to `.env` and updating the values as needed.
5. Run the FastAPI application:
   ```
   uvicorn app.main:app --reload
   ```

### Frontend
1. Navigate to the `frontend` directory.
2. Install the required dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm run dev
   ```

## Usage
Once both the backend and frontend are running, you can access the CompliNet dashboard by navigating to `http://localhost:3000` in your web browser. From there, you can view compliance data, manage devices, and configure application settings.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.