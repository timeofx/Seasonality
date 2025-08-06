# 🚀 Deployment Guide - Seasonality Trading Tool

## 📋 Schritt-für-Schritt Anleitung

### 🔧 1. Vorbereitung (Einmalig)

#### Python & Dependencies installieren:
```bash
# 1. Python 3.12+ installiert? Prüfen:
python --version

# 2. Requirements installieren:
pip install -r requirements.txt
```

#### Firewall konfigurieren (Windows):
1. **Windows-Taste** → "Windows Defender Firewall"
2. **"Erweiterte Einstellungen"**
3. **"Eingehende Regeln"** → **"Neue Regel"**
4. **Port** → **TCP** → **Bestimmte lokale Ports: 8501**
5. **Verbindung zulassen** → **Name: "Seasonality Tool"**

### 🌐 2. Server starten

#### **Option A: Lokaler Zugriff (nur dein PC)**
```bash
# Einfacher Start für nur lokalen Zugriff
python start_seasonality_tool.py
# ODER
streamlit run app/main.py
```
**Zugriff:** http://localhost:8501

#### **Option B: Remote-Zugriff (Team-Sharing)**
```bash
# Windows (Doppelklick):
start_secure_server.bat

# Oder manuell:
python start_secure_server.py
```

**Ausgabe zeigt dir:**
```
🌍 Local Access:  http://localhost:8501
🌐 Remote Access: http://192.168.178.159:8501  # ← Diese IP an Team weitergeben
```

### 🔑 3. Login-Credentials

| Rolle | Username | Passwort | Zugriff |
|-------|----------|----------|---------|
| **👑 Admin** | `admin` | `#Cassian42!` | Vollzugriff |
| **📈 Trader** | `trader` | `#Derek42!` | Trading-Analyse |
| **📊 Analyst** | `analyst` | `market2024` | Research |

### 🤝 4. Team-Zugriff einrichten

#### Für deinen Kollegen:
1. **Du startest:** `start_secure_server.bat`
2. **Du teilst:** Die angezeigte IP-Adresse (z.B. `http://192.168.178.159:8501`)
3. **Er öffnet:** Diese URL in seinem Browser
4. **Er loggt sich ein:** Mit einem der Login-Credentials
5. **Fertig!** Er hat vollen Zugriff auf das Tool

#### Router-Konfiguration (für externes Internet):
Falls dein Kollege **nicht im gleichen Netzwerk** ist:
1. **Router-Admin** öffnen (meist http://192.168.1.1)
2. **Port-Weiterleitung** einrichten:
   - **Externe Port:** 8501
   - **Interne Port:** 8501
   - **IP-Adresse:** Deine PC-IP (wird angezeigt)
3. **Externe IP** deines Routers an Kollegen weitergeben

### ⚠️ 5. Troubleshooting

#### "Port already in use" Fehler:
```bash
# Alle Python-Prozesse beenden:
taskkill /f /im python.exe
taskkill /f /im pythonw.exe

# Dann neu starten
python start_secure_server.py
```

#### "streamlit command not found":
```bash
# Verwende stattdessen:
python -m streamlit run app/main.py
```

#### Kollege kann nicht zugreifen:
1. **Firewall prüfen** (Windows Defender)
2. **Router-Einstellungen** prüfen
3. **Antivirus-Software** temporär deaktivieren
4. **Alternative Ports** verwenden (8502, 8503...)

#### Login funktioniert nicht:
- **Groß-/Kleinschreibung** beachten
- **Sonderzeichen** exakt eingeben (`#Cassian42!`)
- **Browser-Cache** leeren

### 🔐 6. Sicherheitshinweise

#### Passwörter ändern (Produktion):
```python
# In app/auth.py neue Hashes generieren:
python -c "
import hashlib
password = 'dein_neues_passwort'
hash_val = hashlib.sha256(password.encode()).hexdigest()
print(f'Hash für \"{password}\": {hash_val}')
"
```

#### Sichere Produktion:
- ✅ **Starke Passwörter** verwenden
- ✅ **HTTPS** implementieren (für Internet-Zugriff)
- ✅ **VPN** verwenden (für Remote-Team)
- ✅ **Regelmäßige Updates** der Dependencies

### 🎯 7. Schnellstart-Kommandos

```bash
# Lokaler Start (nur du):
python start_seasonality_tool.py

# Remote-Start (Team-Sharing):
python start_secure_server.py

# Prozesse beenden:
taskkill /f /im python.exe

# Requirements aktualisieren:
pip install -r requirements.txt --upgrade
```

### 📞 Support
Bei Problemen die Logs prüfen oder das Terminal-Output kopieren und weitergeben.

**Das Tool ist jetzt production-ready mit sicherer Authentifizierung! 🚀🔐**