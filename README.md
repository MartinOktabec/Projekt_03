# Election Scraper - Projekt 3 do Engeto Python Akademie

Tento skript slouží k automatickému stahování (scrapování) výsledků voleb do Poslanecké sněmovny Parlamentu České republiky z roku 2017 z oficiálního webu [volby.gov.cz](https://volby.gov.cz). Skript automaticky vyhledá zadaný územní celek (okres) a výsledky uloží do formátu `.csv`.

## Instalace a nastavení

Pro spuštění projektu doporučuji vytvořit a aktivovat izolované virtuální prostředí (`venv`). Následně nainstalujte všechny potřebné knihovny třetích stran pomocí připraveného souboru `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Spuštění projektu

Skript se spouští z terminálu (příkazové řádky) a vyžaduje **přesně 2 spouštěcí argumenty**:
1. **Název okresu** – Přesný název územního celku s diakritikou (např. `"Benešov"` nebo `"Praha"`). Seznam všech platných názvů okresů naleznete na [hlavním rozcestníku voleb 2017](https://volby.gov.czpls/ps2017nss/ps3?xjazyk=CZ).
2. **Název výstupního souboru** – Jméno souboru, do kterého se uloží výsledná data (musí mít příponu `.csv`).

### Příklad spuštění v terminálu:

```bash
python main.py "Benešov" vysledky_benesov.csv
```

## Ukázka průběhu stahování

Po spuštění programu uvidíte v terminálu výpis o postupném zpracování jednotlivých obcí:

```text
Scraping Benešov ...
Scraping Bernartice ...
Scraping Bílkovice ...
...
Done. Wrote 114 rows to vysledky_benesov.csv.
```

## Ukázka výstupních dat (CSV)

Výsledný soubor obsahuje strukturovaná data s absolutními počty hlasů pro jednotlivé strany. Zde je zkrácená ukázka vygenerovaného souboru:

```text
kod,obec,volici_v_seznamu,vydane_obalky,platne_hlasy,Občanská demokratická strana,Řád národa - Vlastenecká unie,CESTA ODPOVĚDNÉ SPOLEČNOSTI
529303,Benešov,13104,8485,8437,1052,10,2
532568,Bernartice,191,148,148,4,0,0
530743,Bílkovice,170,121,118,7,0,0
532380,Blažejovice,96,80,77,6,0,0
532096,Borovnice,73,54,53,2,0,0
```