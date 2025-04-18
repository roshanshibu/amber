# Amber

A self-hosted music steaming server.

![Project Status](https://img.shields.io/badge/status-alpha-orange)


### Installation

## 🐳 Running with Docker

You can run this project as a Docker container with HTTPS support out of the box.

### Requirements

- Docker installed
- Your own HTTPS certificate and key (`server.crt`, `server.key`)
- Your music and staging folders

### Installation steps

1. **Create a folder** on your host machine to hold the certificate and key files:
   ```
   mkdir -p ~/amber-docker/certs
   ```

2. **Place your certificate and key files** into that folder:
   ```
   ~/amber-docker/certs/server.crt
   ~/amber-docker/certs/server.key
   ```

3. **Prepare your directory structure**, for example:
   ```
   ~/amber-docker/
   ├── Music/           # Files processed by the server placed here
   ├── Staging/         # All music files waiting to be processed
   └── certs/
       ├── server.crt
       └── server.key
   ```

4. Place all your music files in the supported formats inside the `Staging` folder

5. **Create a `docker-compose.yml` file** inside `~/amber-docker/` with the following content:

   ```yaml
   services:
     amber:
       image: roshanshibu/amber:alpha
       ports:
         - "7000:443"
       restart: always
       volumes:
         - ./Music:/amber/Music
         - ./Staging:/amber/Staging
         - ./certs/server.crt:/certs/server.crt:ro
         - ./certs/server.key:/certs/server.key:ro
       environment:
         - AMBER_DUMMY_TOKEN=your_dummy_token_here
         - ACOUSTID_API_KEY=your_acoustid_api_key_here
   ```

6. **Run the container** from inside the project directory:
   ```bash
   docker compose up -d
   ```

7. Amber server is now accesible at:
   ```
   https://<your-hostname>:7000/
   ```

8. Acces your library through the amber web app: https://amber-web-client.vercel.app/  
   Use the `AMBER_DUMMY_TOKEN` from the docker-compose and your server url to connect.

---
