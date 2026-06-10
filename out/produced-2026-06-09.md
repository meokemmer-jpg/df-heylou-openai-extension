# df-heylou-openai-extension — PRODUKTION [CRUX-MK]
*2026-06-09T14:37:46.831149+00:00 | ollama-local/kemmer-14b-ctx8k*

# df-heylou-openai-extension: Produktions-Qualität Dokumentation

## Architekturbeschreibung

Die Dark-Factory `df-heylou-openai-extension` integriert HeyLou-Funktionen in das OpenAI Function Calling Muster. Das System besteht aus mehreren wichtigen Modulen, die für eine effiziente und sichere Funktionsausführung verantwortlich sind.

### Modul: `openai_extension.py`

Dieses Modul enthält die Definition der Funktionen, die von den Anwendern aufgerufen werden können und direkt zu den entsprechenden Backend-Modulen weitergeleitet werden. Ein Beispiel für das Handling einer Function Call ist:

```python
def handle_function_call(function_call):
    function_name = function_call['name']
    
    if function_name == 'search_hotels':
        return search_hotels(**function_call['arguments'])
    
    elif function_name == 'get_rates':
        return get_rates(**function_call['arguments'])
    
    # ähnliche Logik für die anderen Funktionen
```

### Modul: `auth_handler.py`

Dieses Modul verarbeitet Authentifizierungs- und Berechtigungsanfragen, um sicherzustellen, dass nur berechtigte Benutzer auf die API-Zugriff haben. Ein Beispiel dafür ist:

```python
def verify_phronesis_ticket(ticket):
    if ticket == os.getenv('PHRONESIS_TICKET'):
        return True
    else:
        return False
```

### Modul: `audit_logger.py`

Dieses Modul speichert jede Funktionseintrag in einer JSONL-Datei für Audit-Purposes und Sicherheitszwecke. Ein Beispiel dafür ist:

```python
import json

def log_audit(function_call, result):
    audit_entry = {
        'function_name': function_call['name'],
        'arguments': function_call.get('arguments', {}),
        'result': result,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('audit_log.jsonl', 'a') as file:
        json.dump(audit_entry, file)
        file.write('\n')
```

### Modul: `adapter_orchestrator.py`

Dieses Modul ist das Eingangspunkt für die Dark-Factory und startet den LaunchAgent. Ein Beispiel dafür ist:

```python
if __name__ == "__main__":
    # Startet den LaunchAgent mit einem Startinterval von 7200 Sekunden (2 Stunden)
    subprocess.Popen(['launchctl', 'submit', '-l', 'com.kemmer.df-heylou-openai-extension.plist'])
```

## Sandbox-Modus

Die Sandbox-Einstellungen sind durch Umgebungsvariablen gesteuert. Wenn `DF_HEYLOU_OPENAI_EXT_ENABLED` auf `false` gesetzt ist, werden Mock-Responses für die HeyLou Travel-Knowledge-Graph synthetisiert.

```bash
# Sandbox aktiviert
export DF_HEYLOU_OPENAI_EXT_ENABLED=false

# Sandbox deaktiviert und Real Mode aktiviert
export DF_HEYLOU_OPENAI_EXT_ENABLED=true
```

### LaunchAgent-Plist Konfigurationen

Die LaunchAgent-Plist-Konfiguration ist wie folgt aufgebaut:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key><string>com.kemmer.df-heylou-openai-extension</string>
        <!-- weitere Konfigurationen -->
    </dict>
</plist>
```

## Tests

Um die Funktionalität der Dark-Factory zu testen, können Sie folgende Befehle ausführen:

```bash
pytest tests/ -v
```

Dies führt alle im `tests` Verzeichnis definierten Testfälle durch und gibt eine detaillierte Ausgabe.

## Cross-DF-Coupling

Die Dark Factory ist eng mit anderen Backends wie `df-heylou-travel-domain`, `df-pms-mews-adapter`, `df-ota-*` gekoppelt. Diese Couplings werden in den entsprechenden Modulen (z.B. `openai_extension.py`) verwaltet und gesteuert.

### Beispiel für eine Coupling Verwaltung:

```python
def search_hotels(location, dates, preferences):
    # Interne API-Anfrage an df-heylou-travel-domain
    return requests.post('http://localhost:8001/search', json={
        'location': location,
        'dates': dates,
        'preferences': preferences
    }).json()
```

## Kompilierte LaunchAgent-Plist

Die kompilierte LaunchAgent Plist sieht wie folgt aus:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key><string>com.kemmer.df-heylou-openai-extension</string>
        <!-- weitere Konfigurationen -->
    </dict>
</plist>
```

Diese Plist-Konfiguration startet den LaunchAgent und stellt sicher, dass er regelmäßig gestartet wird.

### Startinterval und RunAtLoad

Das `StartInterval` ist auf 7200 Sekunden (2 Stunden) gesetzt. Der `RunAtLoad` ist auf `true`, sodass der Agent beim Systemstart automatisch ausgeführt wird:

```xml
<key>StartInterval</key><integer>7200</integer>
<key>RunAtLoad</key><true/>
```

## Kompilierte API-Definitionen

Die Definition der Funktionen, die vom Modell aufgerufen werden können, sieht wie folgt aus:

```python
tools = [
    {"name": "search_hotels", 
     "description": "Hotel-Search im HeyLou Travel-Knowledge-Graph",
     "parameters_schema": {"type": "object", "properties": {
         "location": {"type": "string"}, 
         "dates": {"type": "array", "items": {"type": "string"}}, 
         "preferences": {"type": "object"}
     }}},
    # ähnliche Definitionen für die anderen Funktionen
]
```

## Schlussfolgerung

Die Dark-Factory `df-heylou-openai-extension` bietet eine effiziente und sichere Methode, um HeyLou-Funktionen im OpenAI Function Calling Framework zu integrieren. Durch die Integration von Authentifizierung, Logging und Cross-DF Coupling bietet sie ein vollständiges Solution für fortgeschrittene Anwendungen.

### Dokumentation der Funktionen

#### `search_hotels(location, dates, preferences)`

Diese Funktion ermöglicht es Benutzern, Hotels im HeyLou Travel-Knowledge Graph zu suchen. Die zurückgegebenen Daten basieren auf den angegebenen Standort, Datumsbereich und Vorlieben.

#### `get_rates(hotel_id, date_range)`

Gibt die Preise für ein spezifisches Hotel über einen bestimmten Zeitraum zurück, basierend auf der Anfrage des Benutzers an das Property Management System (PMS).

#### `compare_otas(hotel_id, dates)`

Vergleicht die OTA-Preise (Booking/Expedia/HRS) für ein spezifisches Hotel über einen bestimmten Zeitraum.

#### `book_direct(hotel_id, room_type, guest, dates)`

Ermöglicht den Direktbuchungsauftrag durch HeyLou ohne Kommission. Der Auftrag wird direkt an das Property Management System weitergeleitet und die Buchungsbestätigung zurückgegeben.

#### `optimize_revenue(hotel_id)`

Enthält einen Revenue-Optimizer Stub, der in Zukunft integriert werden soll, um den Einnahmen für ein Hotel zu maximieren.