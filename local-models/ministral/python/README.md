# Lokale Python-Umgebung

Der Python-Interpreter liegt unter:

```text
%USERPROFILE%\.venvs\all\Scripts\python.exe
```

Hardwarebericht anzeigen:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\hardware_check.py
```

Hardwarebericht als JSON speichern:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\hardware_check.py --output .\hardware-report.json
```

Die eigentliche Modellinferenz soll später über `llama.cpp` laufen. Dadurch benötigt
dieses Python-Projekt weder PyTorch noch CUDA-Python-Pakete.

Ministral herunterladen:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\download_mistral.py
```

Lokalen Ministral-Server starten:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\start_mistral.py
```

Alternativ im Hintergrund starten und stoppen:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\start_mistral.py --background
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\start_mistral.py --stop
```

Beim ersten Start wird automatisch ein lokaler API-Schlüssel unter
`C:\LLMs\config\api_key.txt` erzeugt. `chat_test.py` liest diesen Schlüssel selbst ein.

Installation und Zugriffsschutz prüfen:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\verify_server.py
```

In einem zweiten Terminal testen:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\chat_test.py
```
