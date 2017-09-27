# script-web



## Getting Started

In das Projektverzeichnis wechseln:
```python
cd script_web
```

### Virtual Environment
Für Pakete/Services sollten grundsätzlich Virtual Environments verwendet werden.
Ein neues environment anlegen:
```python
python3 -m venv .venv
source .venv/bin/activate
```

### Requirements

Paketquellen aus requirements.txt installieren
```
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

### Lokale Installation des Projekt-Pakets

Paket mit Abhängigkeiten für Tests im aktuellen Verzeichnis bereitstellen:
```shell
pip install -e ".[testing]"
```

### Ausführen der Tests

```shell
python setup.py test
```

Hilfe, was setup.py noch alles kann:
```shell
python setup.py --help-commands
```

### Ausführen des Services

```shell
gunicorn --paste development.ini
```

## Paketierung

### Requirements

Die aktuellen Paketversionen im Virtual Environment als requirements.txt ablegen:
```shell
pip freeze > requirements.txt
```

Paketkonfiguration prüfen und bauen
```shell
python setup.py check
python setup.py build
```
