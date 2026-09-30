# Domain: administracja publiczna (urząd miasta / gminy). Hand-written items, all data fictional.
_KANAL = ["Skarga - zarzut wobec działania urzędu lub pracownika (przewlekłość, zaniedbanie, niewłaściwe zachowanie)",
          "Wniosek - propozycja usprawnienia pracy urzędu lub lepszego zaspokajania potrzeb mieszkańców",
          "Podanie w sprawie indywidualnej - żądanie załatwienia własnej sprawy (decyzja, zaświadczenie, wpis)",
          "Informacja lub podziękowanie - pismo bez żadnego żądania ani zarzutu"]
_KANAL_KEYS = ["skarga", "wniosek", "podanie", "informacja"]

_PILNOSC_Q = ("Jaki poziom pilności ma sprawa według protokołu kancelarii urzędu? Poziomy: "
              "1 = zapytanie informacyjne bez terminu i bez skutków dla mieszkańca; "
              "2 = własna sprawa mieszkańca lub firmy do załatwienia w zwykłym trybie, której termin (jeżeli jest) wypada "
              "później niż 7 dni od dziś; "
              "3 = termin mieszkańca (urzędowy, szkolny, wyjazd, utrata uprawnienia) upływa w ciągu najbliższych "
              "7 dni od dziś; "
              "4 = bieżące zagrożenie życia, zdrowia lub mienia wymagające reakcji tego samego dnia.")
_PILNOSC_OPT = ["1 - informacyjna", "2 - zwykły tryb", "3 - termin w ciągu 7 dni", "4 - zagrożenie, reakcja dziś"]
_PILNOSC_KEYS = ["p1_informacyjna", "p2_zwykla", "p3_termin_7_dni", "p4_zagrozenie"]

ITEMS = [
    dict(id="ADM01", type="noul", rule_based=True, tricky=True,
         state="Dziś jest poniedziałek, 2026-11-16.\n"
               "Odwołanie od decyzji w sprawie dodatku mieszkaniowego, wnioskodawca: Jan Testowy. "
               "Decyzję doręczono stronie w środę 2026-10-28 (potwierdzenie odbioru w aktach). "
               "Odwołanie nadano w placówce pocztowej w czwartek 2026-11-12, do urzędu wpłynęło 2026-11-16.",
         question="Czy odwołanie zostało wniesione w terminie? Reguła: odwołanie wnosi się w terminie 14 dni; "
                  "termin liczy się od dnia następującego po doręczeniu decyzji; jeżeli ostatni dzień terminu "
                  "przypada w sobotę lub dzień ustawowo wolny od pracy (w tym 11 listopada), termin upływa "
                  "następnego dnia roboczego; o zachowaniu terminu decyduje data nadania w placówce pocztowej.",
         options=["Tak, w terminie", "Nie, po terminie"], gold=0),
    dict(id="ADM02", type="noul", rule_based=True, tricky=False,
         state="Wniosek złożony przez ePUAP:\n"
               "Wnioskodawczyni: Anna Przykładowa, ul. Przykładowa 1/4, 00-000 Testowo. "
               "Treść: Proszę o wydanie zaświadczenia o zameldowaniu na pobyt stały. Zaświadczenie jest mi potrzebne "
               "do ośrodka pomocy społecznej w sprawie zasiłku celowego. "
               "Wniosek podpisany profilem zaufanym. Brak załączników.",
         question="Czy wniosek jest kompletny? Reguła: wniosek o zaświadczenie jest kompletny, jeżeli zawiera "
                  "(1) podpis wnioskodawcy (odręczny lub elektroniczny), (2) dowód zapłaty opłaty skarbowej 17 zł, "
                  "chyba że zaświadczenie jest potrzebne w sprawie z zakresu pomocy społecznej, oraz "
                  "(3) pełnomocnictwo, ale tylko wtedy, gdy wniosek składa pełnomocnik.",
         options=["Tak, wniosek jest kompletny", "Nie, wniosek wymaga uzupełnienia"], gold=0),
    dict(id="ADM03", type="noul", rule_based=True, tricky=False,
         state="Dziś jest środa, 2026-10-14.\n"
               "Wniosek o przywrócenie terminu do złożenia odwołania, wnioskodawca: Marek Fikcyjny. "
               "Uzasadnienie: przebywałem w szpitalu, wypis nastąpił w poniedziałek 2026-10-05 (karta wypisowa w "
               "załączeniu). Wniosek złożony osobiście w biurze podawczym we wtorek 2026-10-13.",
         question="Czy wniosek o przywrócenie terminu złożono w terminie? Reguła: wniosek składa się w ciągu 7 dni "
                  "od ustania przyczyny uchybienia (tu: od dnia wypisu ze szpitala); termin liczy się od dnia "
                  "następującego po tym dniu; jeżeli ostatni dzień przypada w sobotę lub dzień ustawowo wolny od "
                  "pracy, termin upływa następnego dnia roboczego.",
         options=["Tak, w terminie", "Nie, po terminie"], gold=1),
    dict(id="ADM04", type="noul", rule_based=True, tricky=False,
         state="Dziś jest czwartek, 2026-10-08.\n"
               "Wniosek o rozłożenie na raty zaległości w podatku od nieruchomości. Podatnik: Ewa Testowa. "
               "Kwota zaległości: 3 000,00 zł. Proponowana liczba rat: 6. "
               "Z rejestru: w marcu 2026 r. odmówiono podatniczce rozłożenia na raty wyłącznie z powodu braku "
               "podpisu na wniosku; innych odmów nie było.",
         question="Czy wniosek kwalifikuje się do trybu uproszczonego? Reguła: tryb uproszczony stosuje się, "
                  "jeżeli (a) zaległość nie przekracza 3 000 zł, (b) liczba rat nie jest większa niż 6 oraz "
                  "(c) w ciągu ostatnich 12 miesięcy podatnikowi nie odmówiono rozłożenia na raty, chyba że odmowa "
                  "wynikała wyłącznie z braków formalnych wniosku.",
         options=["Tak, tryb uproszczony", "Nie, tryb zwykły"], gold=0),
    dict(id="ADM05", type="noul", rule_based=False, tricky=True,
         state="E-mail do sekretariatu:\n"
               "Na podstawie ustawy o dostępie do informacji publicznej wnoszę o udostępnienie informacji, jaka jest "
               "wysokość mojej zaległości w podatku od nieruchomości za lokal przy ul. Przykładowej 1/2 oraz od kiedy "
               "naliczane są mi odsetki. Proszę o odpowiedź na ten adres e-mail. Piotr Testowy",
         question="Czy pismo jest wnioskiem o udostępnienie informacji publicznej, czyli czy autor prosi o informację "
                  "o działalności urzędu lub gminy (np. umowy, wydatki, uchwały), a nie o dane dotyczące jego własnej "
                  "sprawy lub własnego konta podatkowego?",
         options=["Tak, to wniosek o informację publiczną", "Nie, to sprawa własna wnioskodawcy"], gold=1),
    dict(id="ADM06", type="noul", rule_based=False, tricky=False,
         state="Zgłoszenie z formularza kontaktowego, godz. 06:52:\n"
               "Na ul. Testowej przy przystanku autobusowym leży złamane drzewo, zajmuje połowę jezdni. Samochody "
               "omijają je, wjeżdżając na chodnik, a zaraz ludzie będą szli do szkoły.",
         question="Czy zgłoszenie należy natychmiast przekazać dyżurnemu zarządzania kryzysowego, czyli czy opisuje "
                  "bieżące zagrożenie dla ludzi lub mienia w przestrzeni publicznej (np. przeszkoda na jezdni, "
                  "zerwana linia, zalanie)?",
         options=["Tak, przekazać dyżurnemu", "Nie, zwykły tryb"], gold=0),
    dict(id="ADM07", type="noul", rule_based=False, tricky=True,
         state="Pismo w sprawie OŚ.0000.12.2026:\n"
               "Dzień dobry, w nawiązaniu do wniosku o zezwolenie na usunięcie drzewa chciałbym coś wyjaśnić: nie "
               "wycofuję wniosku. Proszę jedynie o przesunięcie oględzin z 2026-10-21 na dowolny dzień w listopadzie, "
               "bo w październiku będę za granicą. Z poważaniem, Tomasz Przykładowy",
         question="Czy pismo jest wycofaniem wniosku, czyli czy wnioskodawca jednoznacznie rezygnuje z dalszego "
                  "prowadzenia sprawy?",
         options=["Tak, wycofanie wniosku", "Nie, sprawa toczy się dalej"], gold=1),
    dict(id="ADM08", type="noul", rule_based=False, tricky=False,
         state="Wniosek o lokalizację zjazdu z drogi gminnej, złożony przez ePUAP.\n"
               "Treść: ... W załączeniu przesyłam: 1) mapę z zaznaczonym zjazdem, 2) pisemną zgodę współwłaściciela "
               "działki nr 0/00.\n"
               "Załączniki w systemie: mapa_zjazd.pdf",
         question="Czy do pisma dołączono wszystkie załączniki wymienione w jego treści?",
         options=["Tak, wszystkie załączniki są", "Nie, brakuje załącznika"], gold=1),
    dict(id="ADM09", type="choice", rule_based=False, tricky=False,
         state="Pytanie z czatu na stronie urzędu:\n"
               "Dzień dobry, kupiłem używane auto sprowadzone z zagranicy. Co muszę złożyć i gdzie, żeby dostać "
               "polskie tablice i dowód rejestracyjny?",
         question="Do którego wydziału należy skierować sprawę?",
         options=["Wydział Spraw Obywatelskich - dowody osobiste, zameldowanie i wymeldowanie",
                  "Urząd Stanu Cywilnego - akty urodzenia, małżeństwa i zgonu, śluby cywilne",
                  "Wydział Komunikacji - rejestracja pojazdów, prawa jazdy",
                  "Wydział Podatków i Opłat Lokalnych - podatek od nieruchomości, opłata za odpady",
                  "Wydział Architektury i Budownictwa - pozwolenia na budowę, zgłoszenia robót"],
         keys=["spraw_obywatelskich", "usc", "komunikacji", "podatkow", "architektury"], gold=2),
    dict(id="ADM10", type="choice", rule_based=False, tricky=True,
         state="Szanowni Państwo, z najwyższym szacunkiem dla ciężkiej pracy urzędników pozwalam sobie uprzejmie "
               "zauważyć, że mój wniosek o dodatek mieszkaniowy, złożony 2026-06-15, od ponad trzech miesięcy "
               "pozostaje bez odpowiedzi, a pani prowadząca sprawę nie odbiera telefonu i nie odpisuje na e-maile. "
               "Będę wdzięczna za wyjaśnienie, dlaczego to tak długo trwa i kto za to odpowiada. Z wyrazami "
               "szacunku, Maria Testowa",
         question="Jaki charakter ma pismo? Jeżeli pismo porusza kilka wątków, wybierz ten, który stanowi jego "
                  "główną treść.",
         options=_KANAL, keys=_KANAL_KEYS, gold=0),
    dict(id="ADM11", type="choice", rule_based=False, tricky=False,
         state="Uwagi do urzędu, formularz papierowy:\n"
               "Proponuję, żeby w czwartki kasa urzędu była czynna do 18:00, bo osoby pracujące do 16:00 nie mają "
               "kiedy zapłacić. Przydałaby się też możliwość płacenia kartą w Wydziale Komunikacji. Jan Przykładowy",
         question="Jaki charakter ma pismo?",
         options=_KANAL, keys=_KANAL_KEYS, gold=1),
    dict(id="ADM12", type="choice", rule_based=True, tricky=False,
         state="Wniosek o zajęcie pasa drogowego, wnioskodawca: Przykład-Bud sp. z o.o.\n"
               "Cel: ustawienie rusztowania przy remoncie elewacji budynku przy ul. Przykładowej 7. "
               "Powierzchnia zajęcia: 20 m². Okres: od 2026-10-19 do 2026-10-25 włącznie. "
               "Roboty nie są związane z żadną awarią sieci.",
         question="W jakim trybie należy rozpatrzyć wniosek? Reguła: tryb awaryjny stosuje się zawsze, gdy zajęcie "
                  "jest związane z usuwaniem awarii sieci (niezależnie od powierzchni i czasu); w pozostałych "
                  "przypadkach zgłoszenie uproszczone stosuje się, jeżeli zajęcie trwa nie dłużej niż 7 dni "
                  "kalendarzowych (licząc pierwszy i ostatni dzień) i obejmuje nie więcej niż 20 m²; w każdym innym "
                  "przypadku wymagane jest zezwolenie standardowe.",
         options=["Zezwolenie standardowe", "Tryb awaryjny", "Zgłoszenie uproszczone"],
         keys=["zezwolenie_standardowe", "tryb_awaryjny", "zgloszenie_uproszczone"], gold=2),
    dict(id="ADM13", type="choice", rule_based=False, tricky=True,
         state="Zgłoszenie telefoniczne, notatka dosłowna:\n"
               "Pod mojim blokiym na Przykładowej je tako dziura w asfalcie, że już dwa razy mi koło w aucie siadło. "
               "Straż miejsko ino mandaty dowo, a tego nikt nie naprawio. Kto to mo zrobić?",
         question="Do której jednostki należy przekazać zgłoszenie?",
         options=["Straż Miejska - porządek publiczny, nieprawidłowe parkowanie, interwencje",
                  "Referat Gospodarki Odpadami - odbiór śmieci, deklaracje odpadowe",
                  "Referat Zieleni Miejskiej - drzewa, parki, trawniki",
                  "Zarząd Dróg Miejskich - nawierzchnia ulic i chodników, oznakowanie, sygnalizacja"],
         keys=["straz_miejska", "odpady", "zielen", "zarzad_drog"], gold=3),
    dict(id="ADM14", type="choice", rule_based=False, tricky=False,
         state="E-mail do Urzędu Stanu Cywilnego:\n"
               "Dzień dobry, razem z narzeczoną planujemy ślub cywilny w maju 2027 r. w tutejszym urzędzie. Jakie "
               "dokumenty musimy złożyć i z jakim wyprzedzeniem? Paweł Testowy",
         question="Jakiego rodzaju sprawy dotyczy e-mail?",
         options=["Wydanie odpisu aktu stanu cywilnego",
                  "Rejestracja urodzenia dziecka",
                  "Rejestracja zgonu",
                  "Zmiana imienia lub nazwiska w trybie administracyjnym",
                  "Przygotowanie zawarcia małżeństwa (ślub cywilny)"],
         keys=["odpis_aktu", "urodzenie", "zgon", "zmiana_nazwiska", "slub"], gold=4),
    dict(id="ADM15", type="score", rule_based=False, tricky=False,
         state="Dziś jest czwartek, 2026-10-01.\n"
               "Wniosek: Proszę o zaświadczenie o niezaleganiu w podatkach lokalnych. Będzie mi potrzebne do "
               "przetargu, którego termin składania ofert to 2026-12-07. Firma Fikcyjny-Serwis, Marek Fikcyjny",
         question=_PILNOSC_Q, options=_PILNOSC_OPT, keys=_PILNOSC_KEYS, gold=1),
    dict(id="ADM16", type="score", rule_based=False, tricky=False,
         state="Dziś jest poniedziałek, 2026-10-19.\n"
               "Dzień dobry, szkoła wymaga ode mnie zaświadczenia o zameldowaniu syna, bez niego nie przyjmą go do "
               "świetlicy. Muszę je donieść najpóźniej w czwartek 2026-10-22. Anna Testowa",
         question=_PILNOSC_Q, options=_PILNOSC_OPT, keys=_PILNOSC_KEYS, gold=2),
    dict(id="ADM17", type="score", rule_based=False, tricky=False,
         state="Zgłoszenie od lokatora budynku komunalnego przy ul. Testowej 3:\n"
               "Po nocnej wichurze na klatce schodowej częściowo zawalił się sufit, na schodach leży gruz, a z góry "
               "dalej coś się sypie. Lokatorzy muszą tamtędy przechodzić, bo innego wyjścia nie ma.",
         question=_PILNOSC_Q, options=_PILNOSC_OPT, keys=_PILNOSC_KEYS, gold=3),
]
