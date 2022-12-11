# Codice per la risoluzione del problema dell'ospedale

Il progetto contiene, oltre ai file delle classi utilzzate, gli script:

- `generateInstance.py` che, se eseguito crea delle istanze di esempio in formato JSON,
- `solve.py` che risolve le istanze.

Lo script di generazione può accettare differenti parametri a riga di comando, visualizzati con

```python generateInstance.py --help```

Lo script di risoluzione può accettare il path del file JSON di istanza con la flag `--file`:

```python solve.py --file [FILE.json]```
