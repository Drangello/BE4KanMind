# Kanban Board REST API

Eine robuste, kollaborative Kanban-Board-API, entwickelt mit Django REST Framework (DRF).

## 🚀 Features
- **Authentifizierung**: Token-basiertes Login mit benutzerdefinierten User-Modellen (Email-Login).
- **Board-Management**: Rollenbasierte Zugriffskontrolle (Owner vs. Member).
- **Task-Management**: Status-Tracking, Priorisierung und Zuweisungen.
- **Threaded Comments**: Verschachtelte Kommentarfunktion für Aufgaben.
- **Sicherheit**: Objekt-Level-Berechtigungen gegen IDOR-Schwachstellen.

---

## 🛠️ Voraussetzungen
- Python 3.10+
- `pip` (Python Paket-Manager)

## 🚀 Setup & Installation

1. **Repository klonen**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Virtuelle Umgebung erstellen & aktivieren**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Abhängigkeiten installieren**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Umgebungsvariablen konfigurieren**:
   Erstelle eine `.env` Datei im Hauptverzeichnis (basierend auf `.env.example`) und hinterlege deine `SECRET_KEY` und `DEBUG` Einstellungen.

5. **Datenbank-Migrationen ausführen**:
   ```bash
   python manage.py migrate
   ```

6. **Server starten**:
   ```bash
   python manage.py runserver
   ```
   Die API ist unter `http://127.0.0.1:8000/` verfügbar.

---

## 🧪 Testing

Führe die Test-Suite aus, um die Integrität der API sicherzustellen:
```bash
python manage.py test
```

---

## 🏗️ Architektur & Module

Das System ist modular in drei Apps unterteilt:
- **`auth_app`**: Identity & Access Management (Custom User, Token Auth).
- **`boards_app`**: Board-Logik (Besitzverhältnisse, Einladungen).
- **`tasks_app`**: Aufgaben-Management & Kommentar-Thread-Struktur.

---

## 🔐 Security & Permissions

- **Authentifizierung**: Erfordert `Authorization: Token <key>` im Header.
- **Visibility**: Striktes Object-Level-Permission-Handling (User sehen nur Boards, denen sie zugeordnet sind).
- **Role Actions**:
  - *Owner*: Board-Löschung möglich.
  - *Creator/Owner*: Task-Löschung möglich.
  - *Author*: Kommentar-Löschung möglich.

---

## 🗄️ Datenhaltung & Beziehungen

- **Cascading Deletes**:
  - Board gelöscht → Alle Tasks werden entfernt.
  - Task gelöscht → Alle zugehörigen Kommentare werden entfernt.
- **Data Preservation**: Beim Löschen eines Users bleiben Tasks/Kommentare erhalten; die User-Referenz wird auf `NULL` gesetzt, um die Historie zu wahren.