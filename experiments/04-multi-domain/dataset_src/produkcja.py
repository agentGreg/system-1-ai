# Domain: produkcja / jakość (manufacturing, quality). Hand-written items, fictional firms and people.

_DEFECT_Q = ("Do której kategorii należy opisana niezgodność? Kategorie: wymiarowa = wymiar lub geometria poza "
             "tolerancją rysunku; powierzchniowa = rysy, odpryski, wgniecenia, przebarwienia, wady powłoki bez wpływu "
             "na wymiar; materiałowa = niewłaściwy materiał lub jego właściwości (skład, twardość, porowatość, "
             "pęknięcia w materiale); montażowa = części poprawne, ale źle zmontowane, brakujące lub niedokręcone; "
             "dokumentacyjna = wyrób zgodny, błąd w etykiecie, certyfikacie lub dokumentach towarzyszących.")
_DEFECT_OPTS = ["Wymiarowa", "Powierzchniowa", "Materiałowa", "Montażowa", "Dokumentacyjna"]
_DEFECT_KEYS = ["wymiarowa", "powierzchniowa", "materialowa", "montazowa", "dokumentacyjna"]

_SEV_Q = ("Jaką wagę ma ta niezgodność? Poziomy: 1 = kosmetyczna (niewidoczna dla klienta po montażu, bez wpływu na "
          "funkcję); 2 = mała (widoczna wada wyglądu lub dokumentacji, funkcja zachowana); 3 = poważna (obniża funkcję "
          "lub uniemożliwia montaż u klienta, bez zagrożenia bezpieczeństwa); 4 = krytyczna (może zagrażać "
          "bezpieczeństwu użytkownika lub narusza wymagania prawne).")
_SEV_OPTS = ["1 - kosmetyczna", "2 - mała", "3 - poważna", "4 - krytyczna"]
_SEV_KEYS = ["s1_kosmetyczna", "s2_mala", "s3_powazna", "s4_krytyczna"]

ITEMS = [
    dict(id="MFG01", type="noul", rule_based=True, tricky=True,
         state="Protokół kontroli odbiorczej, Przykład-Metal sp. z o.o.\nPartia: tuleje TUL-0000-12, 2 000 szt.\n"
               "Pobrano próbę 125 szt. zgodnie z planem. Wyroby niezgodne w próbie: 3 szt. (zadziory na krawędzi).\n"
               "Kontroler: Jan Testowy.",
         question="Czy partię należy wstrzymać? Reguła: dla partii od 1 201 do 3 200 szt. próba liczy 125 szt., liczba "
                  "akceptacji Ac = 3. Partię wstrzymuje się tylko wtedy, gdy liczba wyrobów niezgodnych w próbie jest "
                  "większa niż Ac; w przeciwnym razie partię się zwalnia.",
         options=["Tak, partię należy wstrzymać", "Nie, partię należy zwolnić"], gold=1),
    dict(id="MFG02", type="noul", rule_based=True, tricky=True,
         state="Raport pomiarowy, wałki WAL-0000-7, próba 20 szt., wymiar nominalny średnicy 25,00 ± 0,05 mm.\n"
               "Pomiar suwmiarką: 18 szt. w zakresie 24,97-25,03 mm, szt. nr 6 = 24,94 mm, szt. nr 14 = 25,06 mm.\n"
               "Ponowny pomiar na maszynie współrzędnościowej (CMM): szt. nr 6 = 24,94 mm, szt. nr 14 = 25,055 mm.\n"
               "Uwaga technologa Anny Przykładowej: po CMM wygląda lepiej, proponuję zwolnić.",
         question="Czy partię należy wstrzymać? Reguła: wyrób jest niezgodny, gdy średnica leży poza przedziałem "
                  "24,95-25,05 mm. Partię wstrzymuje się, gdy w próbie są co najmniej 2 wyroby niezgodne, chyba że "
                  "ponowny pomiar na CMM wykaże mniej niż 2 wyroby niezgodne; wynik CMM zastępuje pomiar pierwotny.",
         options=["Tak, partię należy wstrzymać", "Nie, partię można zwolnić"], gold=0),
    dict(id="MFG03", type="noul", rule_based=True, tricky=False,
         state="Kontrola przyjęcia dostawy od Fikcja-Gum S.A., dostawa nr DOS-0000-321: 4 000 uszczelek.\n"
               "Stwierdzono 22 szt. z pęknięciami w materiale uszczelki, widocznymi już przy rozpakowaniu, przed "
               "jakąkolwiek obróbką u nas. Wada nie dotyczy bezpieczeństwa.",
         question="Czy należy otworzyć reklamację 8D do dostawcy? Reguła: 8D otwiera się, gdy (1) wada wymiarowa lub "
                  "materiałowa pochodzi z komponentu dostawcy (nie powstała u nas) oraz (2) liczba wadliwych sztuk "
                  "przekracza 0,5% dostawy albo wada dotyczy bezpieczeństwa.",
         options=["Tak, należy otworzyć 8D", "Nie, 8D nie jest wymagane"], gold=0),
    dict(id="MFG04", type="noul", rule_based=True, tricky=False,
         state="Dziś jest poniedziałek, 2026-11-16.\nDostawa profili aluminiowych od Testowo-Alu sp. z o.o. została "
               "przyjęta w piątek, 2026-10-30. Dziś rano dział jakości zakończył badania i chce wysłać reklamację "
               "jeszcze dziś.",
         question="Czy reklamacja wysłana dziś będzie złożona w terminie? Reguła z umowy: reklamację składa się w ciągu "
                  "10 dni roboczych od przyjęcia dostawy. Termin liczy się od dnia następującego po przyjęciu; dniami "
                  "roboczymi są dni od poniedziałku do piątku z wyłączeniem dni ustawowo wolnych od pracy "
                  "(w tym okresie: 2026-11-01 i 2026-11-11).",
         options=["Tak, w terminie", "Nie, po terminie"], gold=0),
    dict(id="MFG05", type="noul", rule_based=True, tricky=True,
         state="Kontrola końcowa, partia obudów OBD-0000-5, 1 500 szt.\nSprawdzono 48 szt., wyrobów niezgodnych: 0.\n"
               "Kontroler Marek Fikcyjny: \"Wszystko idealne, zero wad, można wysyłać.\"",
         question="Czy partię należy wstrzymać? Reguła: próba z kontroli końcowej jest ważna tylko wtedy, gdy obejmuje "
                  "co najmniej 50 szt. Partię z nieważną próbą wstrzymuje się do czasu powtórzenia kontroli, niezależnie "
                  "od liczby wykrytych wad.",
         options=["Tak, partię należy wstrzymać", "Nie, partię można wysłać"], gold=0),
    dict(id="MFG06", type="noul", rule_based=False, tricky=False,
         state="Zgłoszenie operatora, linia 3, zmiana II:\nPrasa hydrauliczna od godziny głośniej pracuje i trochę "
               "stuka przy dojściu stempla. Zmierzyłem co dziesiątą sztukę jak zawsze, wszystkie wymiary w tolerancji, "
               "powierzchnie czyste. Proszę o przegląd przez utrzymanie ruchu.",
         question="Czy zgłoszenie opisuje niezgodność wyrobu, czyli czy wyrób nie spełnia wymagań specyfikacji "
                  "(a nie tylko problem z maszyną bez stwierdzonego wpływu na wyrób)?",
         options=["Tak, niezgodność wyrobu", "Nie, to nie jest niezgodność wyrobu"], gold=1),
    dict(id="MFG07", type="noul", rule_based=False, tricky=False,
         state="E-mail od klienta, Przykład-Maszyny sp. z o.o.:\nDzień dobry, dostawa z zamówienia ZAM-0000-88 "
               "dotarła kompletna i zgodna. Certyfikat 3.1 był w paczce, ale nasz magazyn go zgubił. Czy mogą Państwo "
               "przesłać kopię PDF do naszego archiwum? Pozdrawiam, Anna Przykładowa.",
         question="Czy klient składa reklamację, czyli wskazuje niezgodność dostarczonych wyrobów lub dokumentów "
                  "z zamówieniem albo specyfikacją?",
         options=["Tak, to reklamacja", "Nie, to nie jest reklamacja"], gold=1),
    dict(id="MFG08", type="noul", rule_based=False, tricky=False,
         state="Karta pomiarowa: kołnierz KOL-0000-3, wymiar A = 40,00 mm, tolerancja +0,10 / -0,00 mm.\n"
               "Wynik pomiaru szt. nr 1: 39,98 mm.",
         question="Czy wynik pomiaru szt. nr 1 mieści się w tolerancji, czyli leży w przedziale od 40,00 do 40,10 mm?",
         options=["Tak, mieści się w tolerancji", "Nie, jest poza tolerancją"], gold=1),
    dict(id="MFG09", type="choice", rule_based=False, tricky=False,
         state="Raport niezgodności RN-0000-41: obudowy lakierowane, 30 szt. z odpryskami lakieru na krawędzi "
               "frontowej. Wymiary sprawdzone, wszystkie zgodne z rysunkiem.",
         question=_DEFECT_Q, options=_DEFECT_OPTS, keys=_DEFECT_KEYS, gold=1),
    dict(id="MFG10", type="choice", rule_based=False, tricky=False,
         state="Raport niezgodności RN-0000-42: 200 szt. wsporników wykonano i sprawdzono zgodnie z obowiązującym "
               "rysunkiem rev. D, wszystkie wymiary i materiał OK. Na etykietach kartonów wydrukowano jednak numer "
               "rysunku rev. C i błędny numer partii.",
         question=_DEFECT_Q, options=_DEFECT_OPTS, keys=_DEFECT_KEYS, gold=4),
    dict(id="MFG11", type="choice", rule_based=False, tricky=False,
         state="Audyt stanowiska montażu: w 12 zespołach zawiasów śruby M8 dokręcono momentem 12 Nm zamiast "
               "wymaganych 25 Nm. Śruby i zawiasy zgodne ze specyfikacją.",
         question=_DEFECT_Q, options=_DEFECT_OPTS, keys=_DEFECT_KEYS, gold=3),
    dict(id="MFG12", type="choice", rule_based=False, tricky=True,
         state="Zgłoszenie z montażu: wałki pękają przy wciskaniu łożysk na prasie, montażysta twierdzi, że "
               "\"to wina montażu, za mocno dociskamy\". Laboratorium: siła wciskania zgodna z instrukcją, wymiary "
               "wałków zgodne z rysunkiem, twardość 38 HRC przy wymaganych 55-60 HRC.",
         question=_DEFECT_Q, options=_DEFECT_OPTS, keys=_DEFECT_KEYS, gold=2),
    dict(id="MFG13", type="choice", rule_based=False, tricky=False,
         state="Kontrola międzyoperacyjna: otwór fi 10H7 w płycie PLY-0000-9. Sprawdzian tłoczkowy nieprzechodni "
               "wchodzi w otwór, czyli otwór jest za duży. Powierzchnia otworu gładka, bez zadziorów.",
         question=_DEFECT_Q, options=_DEFECT_OPTS, keys=_DEFECT_KEYS, gold=0),
    dict(id="MFG14", type="score", rule_based=False, tricky=False,
         state="Raport niezgodności RN-0000-51: rysa długości 5 mm na wewnętrznej ściance obudowy sterownika. "
               "Po montażu ścianka jest całkowicie zakryta płytą elektroniki, funkcja bez zmian.",
         question=_SEV_Q, options=_SEV_OPTS, keys=_SEV_KEYS, gold=0),
    dict(id="MFG15", type="score", rule_based=False, tricky=False,
         state="Raport niezgodności RN-0000-52: na froncie panelu sterującego, widocznym dla użytkownika, rysa "
               "długości 2 cm. Przyciski i wyświetlacz działają poprawnie.",
         question=_SEV_Q, options=_SEV_OPTS, keys=_SEV_KEYS, gold=1),
    dict(id="MFG16", type="score", rule_based=False, tricky=False,
         state="Reklamacja od klienta Testowo-Meble: w 40 szt. płyt bocznych otwory montażowe przesunięte o 2 mm, "
               "nie da się ich przykręcić do stelaża. Brak zagrożenia dla użytkowników, meble nie wyszły z fabryki "
               "klienta.",
         question=_SEV_Q, options=_SEV_OPTS, keys=_SEV_KEYS, gold=2),
    dict(id="MFG17", type="score", rule_based=False, tricky=True,
         state="Notatka brygadzisty: drobna sprawa, nic wielkiego - w 5 grzejnikach elektrycznych z dzisiejszej "
               "zmiany nie podłączono przewodu ochronnego (uziemienia) do obudowy. Grzeją normalnie, klient nie "
               "zauważy, wygląd bez zarzutu.",
         question=_SEV_Q, options=_SEV_OPTS, keys=_SEV_KEYS, gold=3),
]
