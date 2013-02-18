# MICROTASK

## Konfigurace

* Server je konfigurovan defaultne pomoci souboru settings.cfg
* Je mozne nastaveni v souboru settings.cfg prepsat pomoci souboru zadaneho v
  envvar MICROTASK_SETTINGS
* Nastaveni:
    * DEBUG -- webove vypisy chyb, pro json nanic
    * EXTRANET -- True pokud se jedna o server, ktery tasky pouze rozhazuje
    * HOST -- adresa serveru
    * PORT -- port serveru
    * SLAVES -- seznam adres workeru (format: "ip:port") / pouze u mastera
    * DB -- nazev dbm souboru, slouzi pouze pro zapamatovani idle stavu

## Spusteni serveru

1. Nastaveni konfigurace (viz soubory settings.cfg, settings_slave.cfg a
   settings_slave2.cfg)

    export MICROTASK_SETTINGS=settings_slave.cfg

2. Spusteni prikazem `python microtask.py` anebo deployment na nejaky wsgi server
3. Spusteni vsech instanci stejnym zpusobem

## Spusteni tasku

* Tasky jsou ulozeny jako moduly v tasks/
* V microtask.py jsou tasky rozhazovany k svemu modulu v metode
  `process_task_locally` podle parametru 'action'
* Je tedy treba pridat kod pro zavolani modulu do microtask.py
* Na server musi byt poslan task pomoci metody POST, Content-Type musi byt
  application/json.

### Priklady

#### Hello gcc

* Jako parametr bude poslan zdrojovy kod v C, ten bude zkompilovan a vracena
  bude vysledna binarka zakodovana pomoci base64
* Priklad:

    {"action": "hello", "source_code": "int main() { return 1; }"}

* Pouziti curl:

    $ curl -i -H "Content-Type: application/json" -X POST -d '{"action":
        "hello", "source_code": "int main() { return 1; }"}'
        http://localhost:4000/new-task

#### Wait

* Jako parametr bude poslan pocet sekund, po ktere se vykonavany worker uspi
* Priklad

    {"action": "wait", "seconds": 60}

