# Domain: bank_aml (banking, credit, AML). Hand-written items, all names / numbers fictional.
_VERIF_RULE = ("Reguła: przelew wymaga dodatkowej weryfikacji, jeżeli spełniony jest co najmniej jeden warunek: "
               "(1) kwota tego przelewu wynosi co najmniej 20 000 zł; (2) odbiorca został dodany w ciągu ostatnich "
               "24 godzin i kwota przekracza 5 000 zł; (3) bank odbiorcy ma siedzibę w kraju z listy podwyższonego "
               "ryzyka: Fikcjonia, Testlandia, Wyspy Przykładowe; (4) suma przelewów do tego samego odbiorcy w oknie "
               "7 dni kalendarzowych kończącym się dniem bieżącego przelewu (np. dla przelewu z 2026-11-20 okno "
               "obejmuje dni od 2026-11-14 do 2026-11-20), łącznie z bieżącym przelewem, wynosi co najmniej 20 000 zł.")

_ROUTING_OPTS = ["Karty - wydanie, blokada, zastrzeżenie, limity, PIN, wznowienie karty",
                 "Kredyty - wnioski kredytowe, raty, harmonogram, wcześniejsza spłata",
                 "Reklamacje transakcji - kwestionowanie konkretnej transakcji (podwójne obciążenie, zła kwota, nieautoryzowana, niezrealizowana usługa)",
                 "Konto - otwarcie i zamknięcie rachunku, opłaty za prowadzenie, wyciągi, pełnomocnictwa",
                 "Bankowość elektroniczna - logowanie, aplikacja mobilna, hasła, autoryzacja w aplikacji, powiadomienia"]
_ROUTING_KEYS = ["karty", "kredyty", "reklamacje", "konto", "bankowosc_el"]
_ROUTING_Q = "Do którego działu należy skierować sprawę klienta?"

_RISK_Q = ("Jaki poziom ryzyka AML ma klient? Poziomy: 1 = niski (transakcje zgodne z zadeklarowanym profilem "
           "klienta); 2 = średni (pojedyncze duże odstępstwo od profilu, ale z udokumentowanym uzasadnieniem, np. "
           "wpływ ze sprzedaży nieruchomości potwierdzony aktem notarialnym); 3 = podwyższony (powtarzające się "
           "odstępstwa od profilu bez udokumentowanego uzasadnienia lub regularne transakcje z krajem z listy wysokiego "
           "ryzyka: Fikcjonia, Testlandia, Wyspy Przykładowe); 4 = wysoki (klient na liście sankcyjnej, odmowa "
           "wskazania źródła środków przy dużych wpłatach gotówkowych albo posługiwanie się cudzymi lub podrobionymi "
           "dokumentami).")
_RISK_OPTS = ["1 - niski", "2 - średni", "3 - podwyższony", "4 - wysoki"]
_RISK_KEYS = ["niski", "sredni", "podwyzszony", "wysoki"]

ITEMS = [
    # ---------------- noul ----------------
    dict(id="BNK01", type="noul", rule_based=True, tricky=False,
         state="Dziś jest wtorek, 2026-10-13, godz. 10:40.\n"
               "Zlecenie przelewu: klient Jan Testowy, kwota 19 500,00 zł, tytuł: 'zaliczka na kuchnię'.\n"
               "Odbiorca: Przykład-Meble sp. z o.o., rachunek w banku w Polsce, dodany do listy odbiorców 2026-10-10.\n"
               "Inne przelewy do tego odbiorcy w ostatnich 30 dniach: brak.",
         question="Czy przelew wymaga dodatkowej weryfikacji? " + _VERIF_RULE,
         options=["Tak, wymaga weryfikacji", "Nie, nie wymaga weryfikacji"], gold=1),
    dict(id="BNK02", type="noul", rule_based=True, tricky=True,
         state="Dziś jest czwartek, 2026-10-15.\n"
               "Zlecenie przelewu: klientka Anna Przykładowa, kwota 8 000,00 zł do odbiorcy Marek Fikcyjny "
               "(rachunek w Polsce, odbiorca zapisany od 2026-10-01).\n"
               "Historia przelewów do tego odbiorcy: 2026-10-08 - 3 000 zł; 2026-10-09 - 7 000 zł; 2026-10-12 - 5 000 zł.",
         question="Czy przelew wymaga dodatkowej weryfikacji? " + _VERIF_RULE,
         options=["Tak, wymaga weryfikacji", "Nie, nie wymaga weryfikacji"], gold=0),
    dict(id="BNK03", type="noul", rule_based=True, tricky=True,
         state="Wniosek o kredyt gotówkowy złożony 2026-09-28.\n"
               "Wnioskodawca: Piotr Testowy, umowa o pracę na czas nieokreślony u obecnego pracodawcy od 2026-03-16.\n"
               "Dochód netto: 7 500 zł miesięcznie. Obecne raty: kredyt samochodowy 1 200 zł miesięcznie.\n"
               "Wnioskowana rata: 1 800 zł miesięcznie. Rejestr kredytowy: brak zaległości.",
         question="Czy wniosek spełnia kryteria kredytowe? Reguła: (1) DTI, czyli suma miesięcznych rat wszystkich "
                  "zobowiązań łącznie z wnioskowaną ratą podzielona przez miesięczny dochód netto, nie przekracza 40%; "
                  "(2) staż u obecnego pracodawcy wynosi co najmniej 6 miesięcy w dniu złożenia wniosku, a jeżeli "
                  "wnioskodawca prowadzi działalność gospodarczą - co najmniej 12 miesięcy prowadzenia działalności; "
                  "(3) w rejestrze kredytowym brak zaległości dłuższych niż 30 dni.",
         options=["Tak, spełnia kryteria", "Nie, nie spełnia kryteriów"], gold=0),
    dict(id="BNK04", type="noul", rule_based=True, tricky=False,
         state="Wniosek o kredyt gotówkowy złożony 2026-10-20.\n"
               "Wnioskodawczyni: Ewa Przykładowa, jednoosobowa działalność gospodarcza (usługi graficzne) "
               "zarejestrowana 2025-12-01. Wcześniej 5 lat na etacie w agencji reklamowej.\n"
               "Dochód netto z działalności: 9 000 zł miesięcznie. Obecne raty: brak. Wnioskowana rata: 2 250 zł. "
               "Rejestr kredytowy: brak zaległości.",
         question="Czy wniosek spełnia kryteria kredytowe? Reguła: (1) DTI, czyli suma miesięcznych rat wszystkich "
                  "zobowiązań łącznie z wnioskowaną ratą podzielona przez miesięczny dochód netto, nie przekracza 40%; "
                  "(2) staż u obecnego pracodawcy wynosi co najmniej 6 miesięcy w dniu złożenia wniosku, a jeżeli "
                  "wnioskodawca prowadzi działalność gospodarczą - co najmniej 12 miesięcy prowadzenia działalności; "
                  "(3) w rejestrze kredytowym brak zaległości dłuższych niż 30 dni.",
         options=["Tak, spełnia kryteria", "Nie, nie spełnia kryteriów"], gold=1),
    dict(id="BNK05", type="noul", rule_based=True, tricky=False,
         state="Dziś jest wtorek, 2026-10-20.\n"
               "Klient Karol Fikcyjny zgłasza: 2026-09-22 zapłaciłem kartą 1 450 zł w sklepie internetowym "
               "Przykład-Sport za rower, rower nie dotarł. Pisałem do sklepu 2026-10-05, bez odpowiedzi. "
               "Proszę o zwrot pieniędzy przez bank.",
         question="Czy bank może już teraz przyjąć reklamację w trybie chargeback? Reguła: reklamację "
                  "niezrealizowanego zamówienia opłaconego kartą przyjmuje się, jeżeli: (1) od dnia transakcji "
                  "minęło co najmniej 30 dni kalendarzowych (czas na dostawę), (2) od dnia transakcji minęło nie "
                  "więcej niż 120 dni, (3) klient wcześniej kontaktował się ze sprzedawcą.",
         options=["Tak, można przyjąć reklamację", "Nie, jeszcze nie można przyjąć reklamacji"], gold=1),
    dict(id="BNK06", type="noul", rule_based=False, tricky=False,
         state="Czat w aplikacji:\n"
               "Klient: Widzę na historii obciążenie 349,00 zł 'PRZYKLAD-ELEKTRO ONLINE' z wczoraj 23:12. Ja tam nic "
               "nie kupowałem, nikt z rodziny też nie, a karta cały czas leży u mnie w portfelu.",
         question="Czy klient zgłasza transakcję nieautoryzowaną, czyli twierdzi, że transakcji nie wykonał on "
                  "ani osoba przez niego upoważniona?",
         options=["Tak, zgłasza transakcję nieautoryzowaną", "Nie, nie zgłasza transakcji nieautoryzowanej"], gold=0),
    dict(id="BNK07", type="noul", rule_based=False, tricky=True,
         state="Notatka z oddziału:\n"
               "Klientka (lat 78) chce wypłacić wszystkie oszczędności, 86 000 zł, i wpłacić je na wskazany rachunek. "
               "Mówi: 'Nikt mnie do niczego nie namawia, sama decyduję. Pan z działu bezpieczeństwa waszego banku "
               "zadzwonił rano i wytłumaczył, że moje konto jest zagrożone, więc trzeba szybko przenieść pieniądze "
               "na bezpieczne konto techniczne. Prosił, żebym nic nie mówiła w oddziale.'",
         question="Czy występuje sygnał, że klientka może działać pod wpływem oszusta, czyli zleca operację na "
                  "polecenie osoby podającej się za pracownika banku, policji lub doradcy inwestycyjnego?",
         options=["Tak, występuje taki sygnał", "Nie, brak takiego sygnału"], gold=0),
    dict(id="BNK08", type="noul", rule_based=False, tricky=True,
         state="E-mail od klienta:\n"
               "Dzień dobry, wczoraj pisałem, że zgubiłem kartę, ale właśnie się znalazła w kieszeni kurtki. "
               "Proszę jej NIE zastrzegać, chcę jej dalej używać. Przy okazji proszę o obniżenie limitu płatności "
               "zbliżeniowych do 100 zł. Tomasz Testowy",
         question="Czy klient prosi o zastrzeżenie karty, czyli o jej trwałe zablokowanie z powodu utraty lub kradzieży?",
         options=["Tak, prosi o zastrzeżenie", "Nie, nie prosi o zastrzeżenie"], gold=1),
    # ---------------- choice ----------------
    dict(id="BNK09", type="choice", rule_based=False, tricky=True,
         state="Wiadomość z formularza:\n"
               "Po wczorajszej aktualizacji aplikacja wyrzuca mnie zaraz po wpisaniu kodu, pojawia się 'błąd sesji'. "
               "A dziś mija termin raty kredytu hipotecznego i nie mam jak jej zapłacić! Rata jest w porządku, "
               "harmonogram znam, chodzi tylko o to, żebym mógł się zalogować.",
         question=_ROUTING_Q,
         options=_ROUTING_OPTS, keys=_ROUTING_KEYS, gold=4),
    dict(id="BNK10", type="choice", rule_based=False, tricky=False,
         state="Telefon na infolinię (notatka):\n"
               "Klientka zapłaciła kartą na stacji paliw 220,50 zł, a na historii rachunku widzi dwa identyczne "
               "obciążenia po 220,50 zł z tą samą godziną. Chce zwrotu jednego z nich.",
         question=_ROUTING_Q,
         options=_ROUTING_OPTS, keys=_ROUTING_KEYS, gold=2),
    dict(id="BNK11", type="choice", rule_based=False, tricky=False,
         state="E-mail:\n"
               "Dzień dobry, chciałbym w listopadzie spłacić w całości pozostałą część kredytu gotówkowego "
               "nr KRE-0000-321. Proszę o informację, jaka będzie kwota do spłaty i czy bank pobiera prowizję. "
               "Marek Przykładowy",
         question=_ROUTING_Q,
         options=_ROUTING_OPTS, keys=_ROUTING_KEYS, gold=1),
    dict(id="BNK12", type="choice", rule_based=False, tricky=False,
         state="Wizyta w oddziale (notatka):\n"
               "Klient Jerzy Fikcyjny chce ustanowić pełnomocnictwo do swojego rachunku osobistego dla córki, "
               "Alicji Fikcyjnej, tak aby mogła zlecać przelewy i wypłacać gotówkę w jego imieniu.",
         question=_ROUTING_Q,
         options=_ROUTING_OPTS, keys=_ROUTING_KEYS, gold=3),
    dict(id="BNK13", type="choice", rule_based=False, tricky=False,
         state="Czat:\n"
               "Dostałem kurierem nową kartę debetową w miejsce tej, której kończy się ważność, ale nie przyszedł "
               "SMS z PIN-em do niej. Jak mam ustawić PIN, żeby zapłacić w sklepie?",
         question=_ROUTING_Q,
         options=_ROUTING_OPTS, keys=_ROUTING_KEYS, gold=0),
    # ---------------- score ----------------
    dict(id="BNK14", type="score", rule_based=False, tricky=False,
         state="Profil klienta: emeryt, zadeklarowane źródło dochodu: emerytura ok. 3 200 zł miesięcznie.\n"
               "Ostatnie 6 miesięcy: co miesiąc wpływ emerytury, płatności kartą w sklepach spożywczych i aptekach, "
               "opłaty za media, raz w miesiącu wypłata 500 zł z bankomatu. Brak transakcji zagranicznych.",
         question=_RISK_Q, options=_RISK_OPTS, keys=_RISK_KEYS, gold=0),
    dict(id="BNK15", type="score", rule_based=False, tricky=False,
         state="Profil klientki: nauczycielka, dochód z etatu ok. 5 800 zł netto.\n"
               "2026-10-06 na rachunek wpłynęło 480 000 zł przelewem z rachunku notariusza. Klientka na prośbę "
               "banku dostarczyła akt notarialny sprzedaży mieszkania z tą samą kwotą. Poza tym transakcje "
               "zgodne z profilem.",
         question=_RISK_Q, options=_RISK_OPTS, keys=_RISK_KEYS, gold=1),
    dict(id="BNK16", type="score", rule_based=False, tricky=False,
         state="Profil klienta: student, zadeklarowany dochód: stypendium ok. 1 500 zł miesięcznie.\n"
               "Od 3 miesięcy co tydzień przelewy wychodzące po 3 000 - 4 000 zł do tego samego odbiorcy w banku "
               "w Testlandii. Zapytany, klient odpowiedział, że 'pomaga znajomemu', dokumentów nie przedstawił. "
               "Klient nie figuruje na listach sankcyjnych, wpłat gotówkowych brak.",
         question=_RISK_Q, options=_RISK_OPTS, keys=_RISK_KEYS, gold=2),
    dict(id="BNK17", type="score", rule_based=False, tricky=False,
         state="Profil klienta: jednoosobowa działalność, zadeklarowany obrót ok. 20 000 zł miesięcznie.\n"
               "W ciągu tygodnia trzy wpłaty gotówkowe we wpłatomatach po 45 000 zł. Zapytany przez doradcę o "
               "źródło środków klient odpowiedział: 'To nie jest sprawa banku, nie muszę się tłumaczyć'.",
         question=_RISK_Q, options=_RISK_OPTS, keys=_RISK_KEYS, gold=3),
]
