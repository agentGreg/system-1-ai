# Domain: it_security (IT helpdesk and security). Hand-written items, all names / domains fictional.
# The company domain in all items is przyklad-firma.example (fictional).
_PHISH_Q = ("Czy ten e-mail jest phishingiem, czyli próbą oszustwa, w której nadawca podszywa się pod zaufaną osobę "
            "lub instytucję, aby wyłudzić dane logowania lub płatnicze, skłonić do przelewu pieniędzy albo do "
            "otwarcia złośliwego linku lub załącznika? Firmowa domena to przyklad-firma.example.")

_CAT_OPTS = ["Dostęp - konta, hasła, uprawnienia do systemów i folderów",
             "Sprzęt - fizyczne urządzenia (komputer, monitor, drukarka, telefon): awaria lub wymiana",
             "Oprogramowanie - instalacja, aktualizacja lub błędy działania aplikacji",
             "Sieć - brak połączenia z internetem, Wi-Fi, VPN, wolne łącze",
             "Bezpieczeństwo - podejrzenie incydentu: kliknięty podejrzany link, podane hasło oszustowi, złośliwe oprogramowanie, utrata urządzenia, podejrzana aktywność konta"]
_CAT_KEYS = ["dostep", "sprzet", "oprogramowanie", "siec", "bezpieczenstwo"]
_CAT_Q = ("Do której kategorii należy zgłoszenie? Jeżeli w zgłoszeniu występuje podejrzenie incydentu "
          "bezpieczeństwa, kategoria 'Bezpieczeństwo' ma pierwszeństwo przed pozostałymi.")

_PRIO_Q = ("Jaki priorytet ma incydent? Poziomy: P4 = niski (prośba, pytanie lub drobna usterka, która nikomu nie "
           "blokuje pracy); P3 = średni (jeden użytkownik nie może wykonywać swojej pracy); P2 = wysoki (cały dział "
           "lub co najmniej 10 osób nie może pracować, albo podejrzenie incydentu bezpieczeństwa dotyczącego jednego "
           "konta lub urządzenia); P1 = krytyczny (cała firma nie może pracować, albo trwający incydent "
           "bezpieczeństwa obejmujący wiele urządzeń).")
_PRIO_OPTS = ["P4 - niski", "P3 - średni", "P2 - wysoki", "P1 - krytyczny"]
_PRIO_KEYS = ["p4_niski", "p3_sredni", "p2_wysoki", "p1_krytyczny"]

ITEMS = [
    # ---------------- noul ----------------
    dict(id="ITS01", type="noul", rule_based=True, tricky=True,
         state="Dziś jest czwartek, 2026-10-15.\n"
               "Wniosek o dostęp do systemu kadrowego.\n"
               "Wnioskodawca: Anna Przykładowa, stanowisko: Specjalista HR.\n"
               "Akceptacja bezpośredniego przełożonego: tak (2026-10-14).\n"
               "Szkolenie z ochrony danych osobowych: ukończone 2025-10-15.",
         question="Czy wniosek o dostęp można zatwierdzić? Reguła: można, jeżeli łącznie: (1) wniosek zaakceptował "
                  "bezpośredni przełożony; (2) data ukończenia szkolenia z ochrony danych nie jest wcześniejsza niż "
                  "data dzisiejsza pomniejszona o 365 dni; (3) stanowisko wnioskodawcy to 'Specjalista HR' lub "
                  "'Kierownik HR'.",
         options=["Tak, można zatwierdzić", "Nie, nie można zatwierdzić"], gold=0),
    dict(id="ITS02", type="noul", rule_based=True, tricky=False,
         state="Dziś jest czwartek, 2026-10-01.\n"
               "Wniosek o uprawnienia administratora lokalnego na laptopie LAP-0000-22.\n"
               "Wnioskodawca: Marek Fikcyjny, kontraktor zewnętrzny, aktywna umowa NDA do 2027-06-30.\n"
               "Akceptacje: przełożony - tak; zespół bezpieczeństwa - tak.\n"
               "Wnioskowany termin wygaśnięcia uprawnienia: 2026-11-05.",
         question="Czy uprawnienia administratora lokalnego można nadać? Reguła: można, jeżeli łącznie: (1) wniosek "
                  "zaakceptował przełożony oraz zespół bezpieczeństwa; (2) uprawnienie wygasa najpóźniej 30 dni po "
                  "dniu dzisiejszym; (3) wnioskodawca jest pracownikiem etatowym, chyba że jest kontraktorem z "
                  "aktywną umową NDA.",
         options=["Tak, można nadać", "Nie, nie można nadać"], gold=1),
    dict(id="ITS03", type="noul", rule_based=True, tricky=False,
         state="Dziś jest czwartek, 2026-11-12.\n"
               "Wniosek o dostęp VPN. Pracownik: Jan Testowy.\n"
               "Urządzenie: laptop LAP-0000-31, szyfrowanie dysku: włączone.\n"
               "Szkolenie 'Bezpieczna praca zdalna': ukończone 2026-08-13.\n"
               "Akceptacja przełożonego: tak.",
         question="Czy dostęp VPN można zatwierdzić? Reguła: można, jeżeli łącznie: (1) urządzenie ma włączone "
                  "szyfrowanie dysku; (2) data ukończenia szkolenia 'Bezpieczna praca zdalna' nie jest wcześniejsza "
                  "niż data dzisiejsza pomniejszona o 90 dni; (3) wniosek zaakceptował przełożony.",
         options=["Tak, można zatwierdzić", "Nie, nie można zatwierdzić"], gold=1),
    dict(id="ITS04", type="noul", rule_based=True, tricky=False,
         state="Dziś jest piątek, 2026-11-20.\n"
               "Raport kont nieaktywnych, konto: ewa.testowa@przyklad-firma.example.\n"
               "Ostatnie logowanie: 2026-09-10. Status w systemie HR: 'aktywny'.",
         question="Czy konto należy wyłączyć? Reguła: konto wyłącza się, jeżeli od ostatniego logowania minęło "
                  "ponad 60 dni, chyba że użytkownik ma w systemie HR status 'urlop długoterminowy'.",
         options=["Tak, wyłączyć konto", "Nie, nie wyłączać konta"], gold=0),
    dict(id="ITS05", type="noul", rule_based=True, tricky=False,
         state="Zgłoszenie do helpdesku:\n"
               "Proszę o instalację programu 'Konwerter-Demo' do zamiany plików PDF na obrazy. Program jest "
               "darmowy, ale ma zamknięty kod źródłowy; instaluje się bez uprawnień administratora. "
               "Karol Przykładowy, dział marketingu.",
         question="Czy instalację można zatwierdzić bez przeglądu bezpieczeństwa? Reguła: można, jeżeli program jest "
                  "na liście zatwierdzonej (Edytor-Przykład, PDF-Test, Arkusz-Fikcja) albo jeżeli spełnia łącznie trzy "
                  "warunki: jest darmowy, ma otwarty kod źródłowy i nie wymaga uprawnień administratora.",
         options=["Tak, bez przeglądu bezpieczeństwa", "Nie, wymaga przeglądu bezpieczeństwa"], gold=1),
    dict(id="ITS06", type="noul", rule_based=False, tricky=True,
         state="Od: IT Helpdesk <it-helpdesk@przyklad-firma.example>\n"
               "Temat: PILNE: przerwa w działaniu poczty w sobotę\n"
               "W sobotę 2026-10-17 w godz. 22:00-02:00 poczta firmowa będzie niedostępna z powodu prac "
               "serwisowych. Nie musicie nic robić, nie klikajcie żadnych linków w sprawie tej przerwy i nigdy nie "
               "podawajcie nikomu hasła - IT nigdy o nie nie prosi. Pytania: telefon wewnętrzny 1234.\n"
               "[Nagłówki: SPF pass, DKIM pass; brak linków i załączników]",
         question=_PHISH_Q,
         options=["Tak, to phishing", "Nie, to nie jest phishing"], gold=1),
    dict(id="ITS07", type="noul", rule_based=False, tricky=True,
         state="Od: Anna Przykładowa <anna.przykladowa@przyklad-hurt-pl.test>\n"
               "Temat: Re: faktura FV-0000-12\n"
               "Dzień dobry Panie Marku, w nawiązaniu do naszej rozmowy uprzejmie informuję, że zmieniliśmy bank. "
               "Bardzo proszę o wpisanie w systemie nowego numeru rachunku 00 0000 0000 0000 0000 0000 0000 przed "
               "piątkowym przelewem za fakturę FV-0000-12. Dziękuję za pomoc i serdecznie pozdrawiam.\n"
               "[Anna Przykładowa jest stałą kontrahentką firmy (hurtownia Przykład-Hurt); dotąd zawsze pisała z "
               "adresu w domenie przyklad-hurt.example, a zmiana rachunku nie była wcześniej omawiana telefonicznie]",
         question=_PHISH_Q,
         options=["Tak, to phishing", "Nie, to nie jest phishing"], gold=0),
    dict(id="ITS08", type="noul", rule_based=False, tricky=False,
         state="Od: Dział Bezpieczeństwa <security@przyklad-firma-weryfikacja.test>\n"
               "Temat: Twoje hasło wygasa dziś!\n"
               "Twoje hasło do poczty firmowej wygaśnie o 23:59. Aby nie stracić dostępu, zaloguj się natychmiast "
               "i potwierdź dane: http://przyklad-firma.login-weryfikacja.example/konto\n"
               "Zespół IT",
         question=_PHISH_Q,
         options=["Tak, to phishing", "Nie, to nie jest phishing"], gold=0),
    # ---------------- choice ----------------
    dict(id="ITS09", type="choice", rule_based=False, tricky=True,
         state="Zgłoszenie do helpdesku:\n"
               "Rano dostałem maila o 'zaległej fakturze', kliknąłem link i wpisałem tam login i hasło do poczty, "
               "bo strona wyglądała jak nasza. Od godziny nie mogę się zalogować - pisze, że hasło jest "
               "nieprawidłowe. Proszę o reset hasła. Tomasz Testowy",
         question=_CAT_Q, options=_CAT_OPTS, keys=_CAT_KEYS, gold=4),
    dict(id="ITS10", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie do helpdesku:\n"
               "W sali konferencyjnej na 2. piętrze laptopy nie łapią Wi-Fi, a w pokojach obok działa normalnie. "
               "Sprawdzaliśmy na trzech różnych laptopach, wszędzie to samo. Monika Fikcyjna",
         question=_CAT_Q, options=_CAT_OPTS, keys=_CAT_KEYS, gold=3),
    dict(id="ITS11", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie do helpdesku:\n"
               "Od wczorajszej aktualizacji arkusz kalkulacyjny zawiesza się przy otwieraniu większych plików "
               "(powyżej 20 MB). Małe pliki otwierają się normalnie, komputer poza tym działa sprawnie.",
         question=_CAT_Q, options=_CAT_OPTS, keys=_CAT_KEYS, gold=2),
    dict(id="ITS12", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie od kierownika działu księgowości:\n"
               "Od poniedziałku pracuje u nas Alicja Przykładowa. Proszę o nadanie jej uprawnień odczytu i zapisu "
               "do folderu sieciowego 'Księgowość-2026'. Akceptuję ten wniosek. Jerzy Testowy",
         question=_CAT_Q, options=_CAT_OPTS, keys=_CAT_KEYS, gold=0),
    dict(id="ITS13", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie do helpdesku:\n"
               "Monitor mi zgas i juz nie wstal, nic nie swieci, nawet ta lampka z przodu. Kabel zasilania "
               "przepinalem do innego gniazdka i nic. Komputer chodzi, bo slychac wentylator.",
         question=_CAT_Q, options=_CAT_OPTS, keys=_CAT_KEYS, gold=1),
    # ---------------- score ----------------
    dict(id="ITS14", type="score", rule_based=False, tricky=True,
         state="Zgłoszenie do helpdesku:\n"
               "PILNE!!! Potrzebuję drugiego monitora najlepiej na jutro, bo przy jednym ekranie praca nad "
               "raportami idzie mi dużo wolniej. Obecny monitor i komputer działają bez zarzutu. Piotr Przykładowy",
         question=_PRIO_Q, options=_PRIO_OPTS, keys=_PRIO_KEYS, gold=0),
    dict(id="ITS15", type="score", rule_based=False, tricky=False,
         state="Zgłoszenie od kierownika sprzedaży:\n"
               "Cały dział sprzedaży (14 osób) od 9:00 nie może zalogować się do systemu CRM, komunikat 'błąd "
               "serwera'. Inne działy korzystają z CRM normalnie, poczta i reszta systemów działają.",
         question=_PRIO_Q, options=_PRIO_OPTS, keys=_PRIO_KEYS, gold=2),
    dict(id="ITS16", type="score", rule_based=False, tricky=False,
         state="Zgłoszenie telefoniczne:\n"
               "Pracownica księgowości po powrocie z urlopu nie może zalogować się do komputera - konto "
               "zablokowane po kilku próbach wpisania starego hasła. Bez tego nie może zacząć pracy. Nie było "
               "żadnych podejrzanych wiadomości ani nietypowych logowań.",
         question=_PRIO_Q, options=_PRIO_OPTS, keys=_PRIO_KEYS, gold=1),
    dict(id="ITS17", type="score", rule_based=False, tricky=False,
         state="Zgłoszenia z ostatnich 20 minut:\n"
               "Na kilkunastu komputerach w działach finansów, logistyki i HR pliki zmieniają rozszerzenie na "
               ".locked, a na pulpicie pojawia się plik z żądaniem okupu. Liczba zgłoszeń ciągle rośnie.",
         question=_PRIO_Q, options=_PRIO_OPTS, keys=_PRIO_KEYS, gold=3),
]
