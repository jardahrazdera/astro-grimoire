# Astro Grimoire 🌙✨

A mystical, full-stack celestial ephemeris providing real-time data on sun/moon cycles, lunar phases, and solstices with a Wicca-themed UI.

## Tech Stack
- **Frontend:** Vue 3, Tailwind CSS, Vite (Served via Nginx in production)
- **Backend:** FastAPI, Ephem (Astronomy calculations)
- **Infrastructure:** Docker Compose, Traefik (Proxy/SSL)

## Quick Start
```bash
docker-compose up --build
```

- **Production:** Configured for `astro.jaroslav.tech` via Traefik.
- **Development:** Ensure `VITE_API_URL` points to your local backend.

## Features
- **Mystical UI:** Parallax effects, mouse aura, and mobile gyroscope support.
- **Multilingual Search:** Global location support via Nominatim.
- **Real-time Data:** Accurate rise/set times and phase simulations.

---
*Created with the guidance of the Gemini CLI Agent.*
