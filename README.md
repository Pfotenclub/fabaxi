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
- Fun Commands such as
  - 8ball
  - hug
  - pat

### You have some tasks for me?

Go ahead and ask @DiniskaWolfiii! He will then prepare everything so I can assist you better ^w^

---

## Deployment (Single-File Docker Compose)

Fabaxi is published as a pre-built container image to the GitHub Container Registry (`ghcr.io/pfotenclub/fabaxi:latest`).

You can deploy the entire stack using only the [docker-compose.yml](file:///e:/fabaxi/docker-compose.yml) file:

```bash
# 1. Start the bot
docker compose up -d

# 2. View logs
docker compose logs -f

# 3. Pull updates and restart
docker compose pull && docker compose up -d
```

All credentials, database connection parameters, and bot configuration options are documented and directly editable inside `docker-compose.yml`.
