# Astro Project (Astro Grimoire)

## Project Overview
A full-stack astronomical calculation application ("Astro Grimoire") that provides real-time data on sun/moon cycles, moon phases, and solstices based on user location.

### Technology Stack
*   **Backend:** Python (FastAPI), `ephem` for astronomy calculations, `geopy`/`requests` for geocoding (Nominatim).
*   **Frontend:** Vue.js 3, Vite, Tailwind CSS.
*   **Infrastructure:** Docker Compose.

## Architecture
The application consists of two main services orchestrated by Docker Compose:
*   **Backend (`/backend`):** A FastAPI service exposing endpoints for geocoding (`/search-location`, `/reverse-geocode`) and astronomical data (`/astro-data`). It uses the `ephem` library for precise celestial calculations.
*   **Frontend (`/frontend`):** A Vue 3 Single Page Application (SPA) that consumes the backend API. It features a "Glassmorphism" UI design with a "Wicca/Mystic" theme.

## Getting Started

### Using Docker (Recommended)
To run the entire stack:
```bash
docker-compose up --build
```
*   **Frontend:** Access at `http://localhost:5173`
*   **Backend API Docs:** Access at `http://localhost:8000/docs`

### Local Development

#### Backend
1.  Navigate to the backend directory: `cd backend`
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the server (with hot-reload):
    ```bash
    uvicorn app.main:app --reload
    ```
    *   The API will be available at `http://localhost:8000`.

#### Frontend
1.  Navigate to the frontend directory: `cd frontend`
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    *   The app will be available at `http://localhost:5173`.

## Key Files & Directories
*   `docker-compose.yml`: Orchestrates the backend and frontend services.
*   `backend/app/main.py`: Main entry point for the FastAPI application. Contains all API routes and core astronomy logic.
*   `backend/requirements.txt`: Python dependencies.
*   `frontend/src/App.vue`: Main Vue component containing the UI layout, state logic, and mystical effects.
*   `frontend/src/assets/background.webp`: Tiled mystical background texture.
*   `frontend/vite.config.js`: Vite configuration for the frontend build.

## Mystical UI Features
The application includes several visual effects to enhance the "Wicca" aesthetic:
*   **Tiled Background:** A subtle, low-opacity mystical texture that covers the entire viewport.
*   **Mouse Parallax:** The background shifts gracefully in response to mouse movements (Desktop).
*   **Cursor Aura:** A trailing, glowing emerald aura that follows the mouse cursor with a smooth lag.
*   **Mobile Parallax:** On devices with motion sensors, the background shifts based on the phone's tilt (Gyroscope).

## Development Conventions
*   **Backend:**
    *   Uses Pydantic models (`BaseModel`) for request/response validation.
    *   Follows standard FastAPI patterns.
    *   `ephem` objects are converted to ISO strings for JSON serialization.
*   **Frontend:**
    *   Uses Vue 3 Composition API (`<script setup>`).
    *   Styling is handled via Tailwind CSS utility classes.
    *   Lucide-vue-next is used for icons.
