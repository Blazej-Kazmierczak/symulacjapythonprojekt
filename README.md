----------------------------------------------------------------------
Symulator Kaskady Przepompowni Ścieków (SCADA)
----------------------------------------------------------------------
1. O projekcie:
   
Projekt jest aplikacją typu SCADA (Supervisory Control and Data Acquisition) napisaną w języku Python przy użyciu biblioteki PyQt5. Symuluje on pracę układu dwóch przepompowni (P1 i P2) działających w kaskadzie, wraz z systemem rurociągów, studni pośrednich oraz logiką sterowania automatycznego.

Celem projektu jest wizualizacja procesów hydraulicznych, testowanie algorytmów sterowania (rotacja pomp, obsługa awarii) oraz monitorowanie stanów alarmowych w czasie rzeczywistym.

2. Struktura Projektu:

Kod został podzielony na moduły zgodnie z wzorcem MVC (Model-View-Controller) w celu zachowania czytelności i łatwości rozbudowy:

run.py: 
Punkt wejściowy aplikacji. Uruchamia pętlę zdarzeń PyQt.

Ui:
scada_app.py: Główne okno aplikacji, panel sterowania (suwaki, przyciski) oraz integracja z silnikiem symulacji.

scene_items.py: Definicje niestandardowych elementów graficznych (zbiorniki, pompy, rury, przepływomierze) renderowanych na scenie QGraphicsScene.

src/sewage_sim/ (Logika Symulacji):
sim.py: Główny silnik fizyki. Oblicza bilans przepływów, poziomy cieczy w czasie (dt) i zarządza stanem całej instalacji.

control.py: Automatyka systemu. Zawiera algorytmy sterowania pompami (start/stop w oparciu o poziomy, rotacja, przełączanie awaryjne).

components.py: Klasy reprezentujące fizyczne obiekty (Pompa, Komora, Przepływomierz).

alarms.py: System obsługi zdarzeń alarmowych i ostrzeżeń.

inflow.py: Generatory dopływu ścieków (model dobowy z szumem oraz stały dopływ).

types.py: Definicje typów danych (dataclasses) dla stanów pomp i zaworów.

3. Kluczowe Funkcjonalności:
   
Symulacja Fizyki Płynów: Obliczanie poziomów w zbiornikach na podstawie bilansu dopływu/odpływu oraz charakterystyki geometrycznej studni.

Automatyka Sterowania:
Histereza załączania pomp (poziomy L_START, L_STOP).

Rotacja pomp: Równomierne zużycie urządzeń poprzez cykliczną zmianę pompy wiodącej.

Redundancja: Automatyczne uruchomienie pompy rezerwowej w przypadku awarii pompy podstawowej.

Wizualizacja SCADA:

Animowane poziomy cieczy w zbiornikach.

Sygnalizacja stanu pracy (zielony) i awarii (czerwony) na schemacie technologicznym.

Wykresy i liczniki przepływu w czasie rzeczywistym.

Interakcja Użytkownika:

Możliwość symulowania awarii pomp (przyciski FAIL).

Ręczne sterowanie zasuwami.

Zmiana parametrów symulacji (wielkość dopływu, prędkość pomp) "w locie".

4. Instrukcja Uruchomienia

Wymagania:

Python 3.8+

Biblioteki: PyQt5, PyYAML

Instalacja zależności:
----------
pip install PyQt5 pyyaml
----------
Uruchomienie: Upewnij się, że w folderze config/ znajduje się plik default.yaml z konfiguracją pomp i zbiorników. Następnie uruchom:
----------
python run.py
----------
5. Plany Rozwoju i Możliwe Usprawnienia:
   
Projekt stanowi solidną bazę do dalszej rozbudowy. W kolejnych wersjach planowane jest wprowadzenie następujących optymalizacji:

- Pełna parametryzacja w pliku YAML:Obecnie progi sterowania (L_START, L_STOP) są zdefiniowane w kodzie (control.py). Docelowo zostaną przeniesione do pliku config/default.yaml, co pozwoli na zmianę logiki działania bez ingerencji w kod źródłowy.
- Zaawansowana fizyka przepływu:
Zastąpienie liniowego modelu wypływu grawitacyjnego wzorem Torricellego
(Q=k*(2gh)^1/2), co zwiększy realizm opróżniania zbiorników przy niskich stanach cieczy. 
- Wielowątkowość (Multithreading):
Przeniesienie pętli obliczeniowej symulacji (sim.step()) do osobnego wątku (QThread). Oddzielenie warstwy obliczeniowej od wątku GUI zapobiegnie potencjalnym przycięciom interfejsu przy bardziej złożonych obliczeniach.
- Archiwizacja danych (Data Logging):Dodanie modułu zapisującego historię pomiarów, stanów pomp oraz wystąpień alarmów do zewnętrznego pliku (CSV) lub bazy danych (SQLite), co pozwoli na późniejszą analizę pracy obiektu.
- Sterowanie PID:
Implementacja regulatora PID dla sterowania prędkością obrotową pomp (falowniki), aby utrzymywać stały poziom ścieków w studni odbiorczej zamiast obecnego sterowania dwustanowego.

