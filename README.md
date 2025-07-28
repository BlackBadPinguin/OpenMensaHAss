# OpenMensa Home Assistant Integration

Eine benutzerdefinierte Integration für [Home Assistant](https://www.home-assistant.io/), die Speisepläne deiner Lieblings-Mensa über die [OpenMensa API](https://openmensa.org/) anzeigt.

## ✨ Features

- **Heutige Mahlzeiten** - Sensor für den aktuellen Tag
- **Wochenansicht** - Sensor für die gesamte Woche (Montag bis Sonntag)
- **Benutzerfreundliche Konfiguration** - Einfacher Setup-Flow zur Auswahl deiner Mensa
- **Detaillierte Informationen** - Vollständige Mahlzeitendetails inklusive Name, Hinweise und Preise
- **Automatische Updates** - Regelmäßige Aktualisierung der Speisepläne

## 🚀 Installation

### Methode 1: Manuelle Installation

1. Kopiere den `openmensa` Ordner in dein `custom_components` Verzeichnis:

```bash
mkdir -p config/custom_components/openmensa
cp -r openmensa/ config/custom_components/
```

2. Starte Home Assistant neu

3. Gehe zu **Einstellungen** → **Geräte & Services** → **Integration hinzufügen**

4. Suche nach "OpenMensa" und folge dem Konfigurationsassistenten

### Methode 2: HACS (empfohlen)

1. Öffne HACS in Home Assistant
2. Gehe zu **Integrationen**
3. Klicke auf die drei Punkte oben rechts und wähle **Benutzerdefinierte Repositories**
4. Füge diese Repository-URL hinzu: `https://github.com/BlackBadPinguin/OpenMensaHAss`
5. Wähle **Integration** als Kategorie
6. Klicke auf **Hinzufügen**
7. Suche nach "OpenMensa" und installiere die Integration
8. Starte Home Assistant neu

## ⚙️ Konfiguration

1. Nach der Installation gehe zu **Einstellungen** → **Geräte & Services**
2. Klicke auf **Integration hinzufügen** und suche nach "OpenMensa"
3. Wähle deine gewünschte Mensa aus der Liste aus
4. Die Integration erstellt automatisch die entsprechenden Sensoren

## 📊 Verfügbare Sensoren

### `sensor.openmensa_today`
Zeigt die heutigen Mahlzeiten an.

**Attribute:**
- `meals`: Liste aller verfügbaren Mahlzeiten
- `mensa_name`: Name der ausgewählten Mensa
- `date`: Datum der Mahlzeiten
- `last_updated`: Zeitstempel der letzten Aktualisierung

### `sensor.openmensa_week`
Zeigt die Mahlzeiten für die gesamte Woche an.

**Attribute:**
- `weekly_meals`: Mahlzeiten organisiert nach Wochentagen
- `mensa_name`: Name der ausgewählten Mensa
- `week_start`: Startdatum der Woche
- `last_updated`: Zeitstempel der letzten Aktualisierung

## 🔧 Mahlzeiten-Details

Jede Mahlzeit enthält folgende Informationen:
- **Name**: Bezeichnung der Mahlzeit
- **Kategorie**: Art der Mahlzeit (z.B. Hauptgericht, Beilage)
- **Preise**: Preise für verschiedene Gruppen (Studierende, Mitarbeiter, Gäste)
- **Hinweise**: Allergene und weitere Informationen
- **Verfügbarkeit**: Status der Mahlzeit

## 🎨 Verwendung in Dashboards

### Lovelace Card Beispiel

```yaml
type: markdown
content: >
  ## 🍽️ Heutige Mahlzeiten

  {% for meal in state_attr('sensor.openmensa_today', 'meals') %}
  **{{ meal.name }}**
  - Kategorie: {{ meal.category }}
  - Preis Studierende: {{ meal.prices.students }}€
  {% if meal.notes %}
  - Hinweise: {{ meal.notes | join(', ') }}
  {% endif %}
  
  {% endfor %}
```

### Automation Beispiel

```yaml
automation:
  - alias: "Mensa Benachrichtigung"
    trigger:
      platform: time
      at: "11:00:00"
    condition:
      condition: template
      value_template: "{{ state_attr('sensor.openmensa_today', 'meals') | length > 0 }}"
    action:
      service: notify.mobile_app_your_phone
      data:
        message: "Heute gibt es {{ states('sensor.openmensa_today') }} Gerichte in der Mensa!"
```

## 🐛 Fehlerbehebung

### Keine Daten werden angezeigt
- Überprüfe, ob die ausgewählte Mensa aktuell geöffnet ist
- Stelle sicher, dass eine Internetverbindung besteht
- Prüfe die Home Assistant Logs auf Fehler

### Integration wird nicht gefunden
- Stelle sicher, dass der Ordner korrekt kopiert wurde
- Überprüfe die Ordnerstruktur: `config/custom_components/openmensa/`
- Starte Home Assistant vollständig neu

### Veraltete Daten
- Die Integration aktualisiert Daten automatisch alle 30 Minuten
- Für sofortige Updates nutze den "Reload" Button in den Integrationseinstellungen

## 🤝 Beitragen

Beiträge sind willkommen! Bitte:

1. Forke das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Pushe den Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📝 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe `LICENSE` Datei für Details.

## 🙏 Danksagungen

- [OpenMensa](https://openmensa.org/) für die bereitgestellte API
- Die Home Assistant Community für die Unterstützung
- Alle Beitragenden zu diesem Projekt

## 📞 Support

Bei Problemen oder Fragen erstelle bitte ein [Issue](https://github.com/BlackBadPinguin/OpenMensaHAss/issues) auf GitHub.

---

**Made with ❤️ for the Home Assistant Community**