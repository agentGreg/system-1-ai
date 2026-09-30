# Domain: HR i rekrutacja. Hand-written items, all data fictional.
_KAT_Q = "Do której kategorii należy zgłoszenie pracownika w systemie HR?"
_KAT = ["Urlop - wnioski i pytania o urlop wypoczynkowy, okolicznościowy lub na żądanie",
        "Wynagrodzenie - wypłata, dodatki, premie, potrącenia, PIT",
        "BHP - warunki bezpieczeństwa i higieny pracy, środki ochrony, wypadki",
        "Mobbing lub dyskryminacja - zgłoszenie nękania, dyskryminacji lub molestowania",
        "Sprzęt i dostępy - laptop, telefon, konta w systemach, karta wejściowa",
        "Benefity - karta sportowa, pakiet medyczny, świadczenia socjalne"]
_KAT_KEYS = ["urlop", "wynagrodzenie", "bhp", "mobbing", "sprzet", "benefity"]

_PRI_Q = ("Jaki priorytet ma zgłoszenie w kolejce HR? Poziomy: "
          "1 = pytanie informacyjne bez terminu i bez skutków dla pracownika; "
          "2 = standardowa sprawa kadrowa (zaświadczenie, wniosek, zmiana danych), a jeżeli dokument ma termin, to "
          "później niż za 3 dni robocze; "
          "3 = problem z wypłatą wynagrodzenia (brak lub błędna kwota) albo dokument potrzebny w ciągu najbliższych "
          "3 dni roboczych; "
          "4 = groźba przemocy, molestowanie lub bezpośrednie zagrożenie zdrowia albo bezpieczeństwa pracownika.")
_PRI_OPT = ["1 - informacyjny", "2 - standardowy", "3 - wysoki (wypłata lub termin do 3 dni)",
            "4 - krytyczny (przemoc lub zagrożenie)"]
_PRI_KEYS = ["p1_informacyjny", "p2_standardowy", "p3_wysoki", "p4_krytyczny"]

ITEMS = [
    dict(id="HR01", type="noul", rule_based=True, tricky=True,
         state="Dziś jest poniedziałek, 2026-10-05.\n"
               "CV: Joanna Testowa. Doświadczenie: Księgowa, Firma Testowa sp. z o.o., 09.2019 - 08.2021; "
               "Starsza księgowa, Przykład-Bud sp. z o.o., 09.2021 - obecnie. Języki: angielski C1. "
               "Certyfikaty: brak. Wykształcenie: magister ekonomii.",
         question="Czy kandydatka spełnia wymagania na stanowisko? Wymagania: (1) co najmniej 3 lata doświadczenia "
                  "na stanowisku księgowym, (2) angielski co najmniej na poziomie B2, (3) certyfikat księgowy, przy "
                  "czym wymóg certyfikatu nie dotyczy kandydatów z co najmniej 5 latami doświadczenia na stanowisku "
                  "księgowym.",
         options=["Tak, spełnia wymagania", "Nie, nie spełnia wymagań"], gold=0),
    dict(id="HR02", type="noul", rule_based=True, tricky=True,
         state="Dziś jest czwartek, 2026-10-01.\n"
               "CV: Michał Przykładowy. Doświadczenie: Stażysta w dziale IT, Fikcyjny-Soft sp. z o.o., 02.2023 - "
               "12.2023; Python Developer, Fikcyjny-Soft sp. z o.o., 01.2024 - obecnie. Umiejętności: Python, SQL, "
               "Docker. Angielski B2.",
         question="Czy kandydat spełnia wymóg doświadczenia, czyli ma co najmniej 3 pełne lata pracy na stanowisku "
                  "programisty? Staże i praktyki nie wliczają się do doświadczenia.",
         options=["Tak, spełnia wymóg", "Nie, nie spełnia wymogu"], gold=1),
    dict(id="HR03", type="noul", rule_based=True, tricky=False,
         state="Czwartek, 2026-10-15, godz. 07:40. E-mail do przełożonego i HR:\n"
               "Dzień dobry, biorę dziś urlop na żądanie. Paweł Testowy.\n"
               "Z systemu: grafik pracownika dziś od 08:00. Urlop na żądanie wykorzystany w 2026 r.: 2 dni w marcu, "
               "1 dzień w czerwcu.",
         question="Czy zgłoszenie spełnia zasady urlopu na żądanie? Zasady: (a) łącznie nie więcej niż 4 dni urlopu "
                  "na żądanie w roku kalendarzowym, wliczając dzień, o który pracownik teraz wnosi, oraz "
                  "(b) zgłoszenie najpóźniej w dniu urlopu, przed godziną rozpoczęcia pracy według grafiku.",
         options=["Tak, spełnia zasady", "Nie, nie spełnia zasad"], gold=0),
    dict(id="HR04", type="noul", rule_based=True, tricky=True,
         state="Wiadomość na czacie HR:\n"
               "Hej, mam pytanie, ile mi zostało urlopu, bo w listopadzie chciałbym wziąć tydzień wolnego. A tak na "
               "marginesie, wczoraj na zmianie poślizgnąłem się na mokrej podłodze w magazynie i skręciłem kostkę, "
               "ale już jest ok, chodzę normalnie. Krzysztof Fikcyjny",
         question="Czy wiadomość należy eskalować do HR Business Partnera? Polityka: eskalacji wymaga wiadomość, "
                  "która zawiera (a) zarzut mobbingu, dyskryminacji lub molestowania, (b) informację o zdarzeniu w "
                  "pracy, w którym pracownik doznał urazu, albo (c) zapowiedź odejścia pracownika oznaczonego jako "
                  "kluczowy; same pytania o saldo urlopu, benefity lub sprzęt nie wymagają eskalacji.",
         options=["Tak, eskalować", "Nie, obsłużyć w zwykłym trybie"], gold=0),
    dict(id="HR05", type="noul", rule_based=False, tricky=True,
         state="E-mail do HR:\n"
               "Szczerze mówiąc, mam już dość tych ciągłych nadgodzin i czasem myślę o odejściu. Na razie chciałabym "
               "jednak po prostu porozmawiać o grafiku na listopad. Kiedy mogłabym się umówić? Magdalena Testowa",
         question="Czy wiadomość jest rezygnacją z pracy, czyli czy pracownik jednoznacznie oświadcza, że składa "
                  "wypowiedzenie lub rozwiązuje umowę?",
         options=["Tak, to rezygnacja", "Nie, to nie jest rezygnacja"], gold=1),
    dict(id="HR06", type="noul", rule_based=False, tricky=False,
         state="Klauzula na końcu CV kandydata Adama Przykładowego:\n"
               "Wyrażam zgodę na przetwarzanie moich danych osobowych przez Przykład-Logistyka sp. z o.o. w celu "
               "realizacji obecnego procesu rekrutacji na stanowisko magazyniera.",
         question="Czy kandydat wyraził zgodę na przetwarzanie danych w przyszłych rekrutacjach, czyli czy klauzula "
                  "wprost obejmuje także inne, przyszłe procesy rekrutacyjne?",
         options=["Tak, zgoda obejmuje przyszłe rekrutacje", "Nie, tylko obecna rekrutacja"], gold=1),
    dict(id="HR07", type="noul", rule_based=False, tricky=False,
         state="Zgłoszenie w portalu pracownika:\n"
               "Mój służbowy laptop wyłącza się po około 10 minutach pracy, a bateria wyraźnie się wybrzuszyła, "
               "obudowa się nie domyka. Pracuję teraz na prywatnym komputerze. Natalia Fikcyjna",
         question="Czy pracownik zgłasza problem ze sprzętem firmowym wymagający interwencji, czyli czy sprzęt nie "
                  "działa prawidłowo, jest uszkodzony lub go brakuje?",
         options=["Tak, problem ze sprzętem", "Nie, to nie jest problem ze sprzętem"], gold=0),
    dict(id="HR08", type="noul", rule_based=False, tricky=True,
         state="Wiadomość do HR:\n"
               "Mój kierownik dziś mnie normalnie zmobbingował, bo kazał mi poprawić raport kwartalny, który "
               "oddałem wczoraj z błędami w tabelach. Wkurzyło mnie to. Poza tym nigdy wcześniej nie miałem z nim "
               "problemów. Łukasz Testowy",
         question="Czy wiadomość zawiera zgłoszenie mobbingu, czyli opis uporczywego i długotrwałego nękania lub "
                  "zastraszania pracownika przez inną osobę w pracy?",
         options=["Tak, zgłoszenie mobbingu", "Nie, to nie jest zgłoszenie mobbingu"], gold=1),
    dict(id="HR09", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie:\n"
               "Dzień dobry, w tym miesiącu nie dostałem dodatku za pracę w nocy, a miałem 6 nocnych zmian. Na pasku "
               "wypłaty w tej pozycji jest 0 zł. Robert Przykładowy",
         question=_KAT_Q, options=_KAT, keys=_KAT_KEYS, gold=1),
    dict(id="HR10", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie:\n"
               "Na hali nr 2 od tygodnia nie działa wyciąg, przy cięciu płyt strasznie się pyli, a masek "
               "przeciwpyłowych nie ma w magazynku od poniedziałku. Brygada z drugiej zmiany",
         question=_KAT_Q, options=_KAT, keys=_KAT_KEYS, gold=2),
    dict(id="HR11", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie:\n"
               "Biorę ślub 14 listopada. Ile dni wolnego z tej okazji mi przysługuje i jak mam je zgłosić? "
               "Karolina Testowa",
         question=_KAT_Q, options=_KAT, keys=_KAT_KEYS, gold=0),
    dict(id="HR12", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie:\n"
               "Hej, mój badge nie działa od rana i nie mogę wejść na open space, a o 10 mam meeting z klientem. "
               "Czy ktoś może go reaktywować? Thanks, Bartek Fikcyjny",
         question=_KAT_Q, options=_KAT, keys=_KAT_KEYS, gold=4),
    dict(id="HR13", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie:\n"
               "Chciałabym dopisać męża do mojego pakietu medycznego od przyszłego miesiąca. Jaki formularz mam "
               "wypełnić i ile wyniesie dopłata? Aleksandra Przykładowa",
         question=_KAT_Q, options=_KAT, keys=_KAT_KEYS, gold=5),
    dict(id="HR14", type="choice", rule_based=True, tricky=False,
         state="Dziś jest wtorek, 2026-10-13.\n"
               "CV: Tomasz Przykładowy. Doświadczenie: Handlowiec B2B, Przykład-Hurt sp. z o.o., 03.2020 - obecnie "
               "(sprzedaż rozwiązań dla firm). Prawo jazdy kat. B od 2015 r. Języki: angielski B2 (certyfikat), "
               "niemiecki A2.",
         question="Na który etap skierować kandydata na stanowisko przedstawiciela handlowego? Reguła: odrzucenie, "
                  "jeżeli kandydat nie spełnia któregokolwiek wymogu obowiązkowego (prawo jazdy kat. B oraz co "
                  "najmniej 2 lata doświadczenia w sprzedaży); rozmowa z dyrektorem (z pominięciem etapu rekrutera), "
                  "jeżeli spełnia wymogi obowiązkowe oraz ma co najmniej 5 lat doświadczenia w sprzedaży B2B i zna "
                  "angielski co najmniej na poziomie B2; rozmowa z rekruterem w pozostałych przypadkach spełnienia "
                  "wymogów obowiązkowych.",
         options=["Rozmowa z rekruterem", "Rozmowa z dyrektorem", "Odrzucenie"],
         keys=["rekruter", "dyrektor", "odrzucenie"], gold=1),
    dict(id="HR15", type="score", rule_based=False, tricky=False,
         state="Zgłoszenie:\n"
               "Poproszę o zaświadczenie o zatrudnieniu i wysokości zarobków do banku. Nie jest pilne, wniosek "
               "kredytowy składamy dopiero w przyszłym miesiącu. Dorota Testowa",
         question=_PRI_Q, options=_PRI_OPT, keys=_PRI_KEYS, gold=1),
    dict(id="HR16", type="score", rule_based=False, tricky=False,
         state="Zgłoszenie:\n"
               "Kolega z mojego działu powiedział mi dziś, że jak jeszcze raz zgłoszę kierownikowi jego spóźnienia, "
               "to „policzy się ze mną po pracy na parkingu”. Boję się wychodzić sama po zmianie. Irena Fikcyjna",
         question=_PRI_Q, options=_PRI_OPT, keys=_PRI_KEYS, gold=3),
    dict(id="HR17", type="score", rule_based=False, tricky=False,
         state="Zgłoszenie:\n"
               "Dzień dobry, wszyscy z mojej zmiany dostali wczoraj wypłatę, a ja nie dostałam nic, na koncie pusto. "
               "Proszę o sprawdzenie. Beata Testowa",
         question=_PRI_Q, options=_PRI_OPT, keys=_PRI_KEYS, gold=2),
]
