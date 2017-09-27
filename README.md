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
```python 
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

### Lokale Installation des Projekt-Pakets

Paket mit Abhängigkeiten für Tests im aktuellen Verzeichnis bereitstellen:
```python
pip install -e ".[testing]"
```

### Ausführen der Tests

```python
python setup.py test
```

Hilfe, was setup.py noch alles kann:
```python
python setup.py --help-commands
```

### Ausführen des Services

```python
gunicorn --paste development.ini
```

## Paketierung

### Requirements

Die aktuellen Paketversionen im Virtual Environment als requirements.txt ablegen:
```python
pip freeze > requirements.txt
```

Paketkonfiguration prüfen und bauen
```python
python setup.py check
python setup.py build
```