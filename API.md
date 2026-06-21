# Fabaxi REST API

Lokaler HTTP-Server der parallel zum Discord-Bot läuft.  
Startet automatisch beim Bot-Start auf dem in `.env` konfigurierten Port.

---

## Authentifizierung

Alle Endpunkte erfordern einen Bearer-Token im `Authorization`-Header:

```
Authorization: Bearer <API_SECRET>
```

Der `API_SECRET` wird in `.env` gesetzt. Fehlt der Header oder ist der Token falsch, antwortet die API mit `401 Unauthorized`.

---

## Endpunkte

### `POST /api/dm` — DM als Embed senden

Sendet einem Discord-Nutzer eine Direktnachricht als Embed.

**URL**
```
POST http://localhost:62299/api/dm
```

**Headers**
| Header | Wert |
|---|---|
| `Authorization` | `Bearer <API_SECRET>` |
| `Content-Type` | `application/json` |

**Request Body**

```json
{
  "user_id": 327880195476422656,
  "embed": {
    "title": "Dein Titel",
    "description": "Der Haupttext der Nachricht.",
    "color": 1752220,
    "fields": [
      { "name": "Feld 1", "value": "Inhalt 1", "inline": false },
      { "name": "Feld 2", "value": "Inhalt 2", "inline": true }
    ],
    "footer": "Fußzeile",
    "image_url": "https://example.com/bild.png",
    "thumbnail_url": "https://example.com/thumb.png"
  }
}
```

**Felder**

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `user_id` | integer | ✅ | Discord User-ID des Empfängers |
| `embed` | object | ✅ | Das Embed-Objekt |
| `embed.title` | string | ❌ | Titel des Embeds |
| `embed.description` | string | ❌ | Haupttext |
| `embed.color` | integer | ❌ | Farbe als Dezimalzahl (Standard: `0x1abc9c`) |
| `embed.fields` | array | ❌ | Liste von Feldern (name, value, inline) |
| `embed.footer` | string | ❌ | Fußzeile |
| `embed.image_url` | string | ❌ | Großes Bild unten im Embed |
| `embed.thumbnail_url` | string | ❌ | Kleines Bild oben rechts |

> **Hinweis:** `embed.title` oder `embed.description` sollte mindestens eins gesetzt sein, sonst ist das Embed leer.

**Antworten**

| Status | Body | Bedeutung |
|---|---|---|
| `200` | `{"success": true}` | DM erfolgreich gesendet |
| `400` | `{"error": "..."}` | Pflichtfelder fehlen oder kein valides JSON |
| `401` | `{"error": "Unauthorized"}` | Falscher oder fehlender Bearer-Token |
| `403` | `{"error": "Cannot send DM to this user"}` | Nutzer hat DMs deaktiviert |
| `404` | `{"error": "User not found"}` | User-ID existiert nicht |
| `500` | `{"error": "..."}` | Discord-API-Fehler |

---

## Beispiele

### cURL

```bash
curl -X POST http://localhost:62299/api/dm \
  -H "Authorization: Bearer <API_SECRET>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 327880195476422656,
    "embed": {
      "title": "Hallo!",
      "description": "Das ist eine automatische Nachricht.",
      "color": 1752220
    }
  }'
```

### Python (`httpx`)

```python
import httpx

response = httpx.post(
    "http://localhost:62299/api/dm",
    headers={"Authorization": "Bearer <API_SECRET>"},
    json={
        "user_id": 327880195476422656,
        "embed": {
            "title": "Hallo!",
            "description": "Das ist eine automatische Nachricht.",
            "color": 1752220,
            "fields": [
                {"name": "Status", "value": "Aktiv", "inline": True}
            ],
            "footer": "Fabaxi Bot"
        }
    }
)
print(response.json())
```

### JavaScript (`fetch`)

```js
await fetch("http://localhost:62299/api/dm", {
  method: "POST",
  headers: {
    "Authorization": "Bearer <API_SECRET>",
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    user_id: 327880195476422656,
    embed: {
      title: "Hallo!",
      description: "Das ist eine automatische Nachricht.",
      color: 1752220
    }
  })
});
```

---

## Farbwerte (Dezimal)

Discord-Embed-Farben werden als Dezimalzahl übergeben. Umrechnung: `parseInt("1abc9c", 16)`.

| Farbe | Hex | Dezimal |
|---|---|---|
| Türkis (Standard) | `#1abc9c` | `1752220` |
| Blau | `#3498db` | `3447003` |
| Rot | `#e74c3c` | `15158332` |
| Grün | `#2ecc71` | `3066993` |
| Gelb | `#f1c40f` | `15844367` |
| Grau | `#95a5a6` | `9807270` |
