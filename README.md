# Fabaxi

Hi! I'm Fabaxi, your Pfotenclub Companion 😊
I will assist you in the Pfotenclub Discord Server with various features and fun activities. I'm here to make your experience more enjoyable and engaging!

## What do I do?

See me as the assistant of Pfotenclub.
You wanna know who's the most active on the server? I'll tell you.
When's the next birthday of someone? I gotcha!
You wanna play minigames because you're bored? I have you covered 😉

### Explicit, I have following features (More to come)

- Birthday List and announcements with a Birthday kid role given for the day.
- Karma leaderboard which tracks your activity (Tracks messages, Voice Activity and Reactions).
- Choosable Chat color via Reaction Roles.
- Temporary Voice Channels with custom Interface.
- Autoroles on Member join.
- Nightclub Approval.
- Minigames
  - Counting
  - Guess the Number
- Fun Commands such as
  - 8ball
  - hug
  - pat

### You have some tasks for me?

Go ahead and ask @DiniskaWolfiii! He will then prepare everything so I can assist you better ^w^

---

## Cloud-Native Architecture & GitOps Deployment

Fabaxi is completely **stateless** (all runtime state is persisted in MySQL/MariaDB, running as non-root `UID 10001` with `readOnlyRootFilesystem: true`) and published to the GitHub Container Registry (`ghcr.io/pfotenclub/fabaxi`).

Following Cloud-Native & GitOps best practices, application code and production configuration are strictly separated:
- **Public Code Repository (`pfotenclub/fabaxi`):** Contains the bot source code, `Dockerfile`, CI/CD pipeline, and a neutral [`config.example.toml`](config.example.toml) template.
- **Private GitOps Repository (`pfotenclub/fabaxi-gitops`):** Contains the Kubernetes Kustomize manifests (`base/` and `overlays/prod/`) and the production `config.toml` monitored by **ArgoCD**.

---

## Local Development & Testing

### Option 1: Direct Python / Virtual Environment
1. Copy [`config.example.toml`](config.example.toml) to `config.toml` (gitignored) and fill in your test server/channel IDs.
2. Configure your development token and database credentials in `.env` (`ENVIRONMENT=DEV`).
3. Start the bot:
   ```bash
   python fabaxi.py
   ```

### Option 2: Local 1-Command Container & MariaDB Test Stack
[`docker-compose.yml`](docker-compose.yml) spins up a local MariaDB container and builds Fabaxi locally with Kubernetes-identical security constraints (`read_only: true`, non-root user):

```bash
cp config.example.toml config.toml
docker compose up --build
```
Health and readiness probes can be inspected at `http://localhost:62299/healthz` and `http://localhost:62299/readyz`.
