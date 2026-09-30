# Domain: wspólnota mieszkaniowa / nieruchomości (housing community). Hand-written items, fictional people.

_CAT_Q = ("Do której kategorii należy zgłoszenie? Kategorie: hydraulika = instalacja wodna, kanalizacyjna, "
          "grzewcza (rury, piony, grzejniki, krany); elektryka = instalacja elektryczna, zasilanie, bezpieczniki, "
          "oświetlenie (także na klatce); winda = dźwig osobowy; dach = pokrycie dachu, obróbki, rynny, przecieki "
          "przez dach; części wspólne = elementy budowlane wspólne: drzwi, zamki, okna na klatce, schody, poręcze, "
          "skrzynki pocztowe; sprawa sąsiedzka = konflikt z sąsiadem (hałas, zachowanie, parkowanie) bez usterki "
          "technicznej.")
_CAT_OPTS = ["Hydraulika", "Elektryka", "Winda", "Dach", "Części wspólne", "Sprawa sąsiedzka"]
_CAT_KEYS = ["hydraulika", "elektryka", "winda", "dach", "czesci_wspolne", "sprawa_sasiedzka"]

_URG_Q = ("Jaka jest pilność zgłoszenia? Poziomy: 1 = kosmetyczne (odrapana farba, rysa, graffiti, bez wpływu na "
          "korzystanie z budynku); 2 = zwykła usterka (dotyczy jednego lokalu albo drobnego elementu części "
          "wspólnej, bez zagrożenia i bez szkody w mieniu); 3 = poważna awaria (wyłączone z użytku urządzenie lub "
          "instalacja dla wielu lokali, bez bezpośredniego zagrożenia, np. niedziałająca winda bez osób w środku, "
          "brak ciepłej wody w całym pionie); 4 = awaria zagrażająca (zapach gazu, zalewanie lokali, brak prądu "
          "w całym budynku, osoba uwięziona w windzie).")
_URG_OPTS = ["1 - kosmetyczne", "2 - zwykła usterka", "3 - poważna awaria", "4 - awaria zagrażająca"]
_URG_KEYS = ["p1_kosmetyczne", "p2_usterka", "p3_awaria", "p4_zagrozenie"]

ITEMS = [
    dict(id="RE01", type="noul", rule_based=True, tricky=True,
         state="Protokół głosowania nad uchwałą nr 0/2026 w sprawie wymiany domofonów, Wspólnota Mieszkaniowa "
               "ul. Przykładowa 1, 00-000 Testowo.\nZa: 48,20% udziałów. Przeciw: 20,00% udziałów. Wstrzymali się: "
               "5,00% udziałów. Nie głosowało: 26,80% udziałów.",
         question="Czy uchwała została przyjęta? Reguła: uchwała jest przyjęta, gdy za jej przyjęciem opowiedzieli "
                  "się właściciele reprezentujący więcej niż 50% wszystkich udziałów w nieruchomości wspólnej "
                  "(nie tylko udziałów osób głosujących).",
         options=["Tak, uchwała przyjęta", "Nie, uchwała nieprzyjęta"], gold=1),
    dict(id="RE02", type="noul", rule_based=True, tricky=False,
         state="Zebranie wspólnoty ul. Testowa 5 odbyło się we wtorek, 2026-10-06. Uchwała o remoncie elewacji.\n"
               "Głosy za oddane na zebraniu: 31,40% udziałów.\nGłosy za zebrane indywidualnie przez zarząd: "
               "12,05% udziałów w dniach 2026-10-09 do 2026-10-15 oraz 7,10% udziałów w dniu 2026-10-20.\n"
               "Głosów przeciw nie zebrano.",
         question="Czy uchwała została przyjęta? Reguła: sumuje się udziały za oddane na zebraniu i zebrane "
                  "indywidualnie; głosy zebrane indywidualnie są ważne tylko wtedy, gdy oddano je w ciągu 14 dni od "
                  "dnia zebrania (termin liczy się od dnia następującego po zebraniu, dni kalendarzowe). Uchwała jest "
                  "przyjęta, gdy ważne głosy za stanowią więcej niż 50% wszystkich udziałów.",
         options=["Tak, uchwała przyjęta", "Nie, uchwała nieprzyjęta"], gold=0),
    dict(id="RE03", type="noul", rule_based=True, tricky=False,
         state="Zgłoszenie do administratora, lokal nr 12, ul. Przykładowa 1:\nPękł wężyk łączący baterię "
               "zlewozmywakową z zaworem pod zlewem w kuchni. Hydraulik wymienił wężyk, faktura 180 zł. Pion i zawór "
               "odcinający w lokalu są sprawne.",
         question="Czy koszt naprawy pokrywa wspólnota? Reguła: wspólnota pokrywa naprawy instalacji wodnej od pionu "
                  "do zaworu odcinającego w lokalu włącznie; instalacja za zaworem odcinającym (w kierunku baterii i "
                  "innych punktów poboru) należy do właściciela lokalu, który sam pokrywa koszt jej naprawy.",
         options=["Tak, pokrywa wspólnota", "Nie, pokrywa właściciel lokalu"], gold=1),
    dict(id="RE04", type="noul", rule_based=True, tricky=True,
         state="Pismo właścicielki lokalu nr 7, Anny Przykładowej:\nPodczas montażu rusztowań przez firmę "
               "Przykład-Bud sp. z o.o., która na zlecenie wspólnoty wykonuje docieplenie budynku, pracownik "
               "uderzył rurą w moje okno i pękła szyba. Kierownik budowy potwierdził zdarzenie wpisem do dziennika. "
               "Wymiana szyby: 640 zł.",
         question="Czy koszt wymiany szyby pokrywa wspólnota? Reguła: okna w lokalach są częścią lokalu i koszt ich "
                  "naprawy pokrywa właściciel lokalu, chyba że uszkodzenie spowodowały prace zlecone przez wspólnotę; "
                  "wtedy koszt pokrywa wspólnota.",
         options=["Tak, pokrywa wspólnota", "Nie, pokrywa właścicielka lokalu"], gold=0),
    dict(id="RE05", type="noul", rule_based=True, tricky=False,
         state="Dziś jest czwartek, 2026-11-12.\nWłaściciel lokalu nr 3, Jan Testowy, składa dziś pisemne "
               "zastrzeżenia do rocznego rozliczenia wody. Rozliczenie doręczono mu w poniedziałek, 2026-10-12.",
         question="Czy zastrzeżenia złożono w terminie? Reguła: zastrzeżenia do rozliczenia składa się w ciągu "
                  "30 dni od doręczenia; termin liczy się od dnia następującego po doręczeniu; jeżeli ostatni dzień "
                  "przypada w sobotę, niedzielę lub dzień ustawowo wolny od pracy (m.in. 2026-11-11), termin upływa "
                  "następnego dnia roboczego.",
         options=["Tak, w terminie", "Nie, po terminie"], gold=0),
    dict(id="RE06", type="noul", rule_based=False, tricky=False,
         state="Zgłoszenie z aplikacji mieszkańca, lokal nr 20:\nZ kratki wentylacyjnej w łazience czuć spaleniznę "
               "i dym, jak z grilla. Sąsiad z dołu chyba znowu grilluje na balkonie węglem drzewnym. Budynek nie ma "
               "instalacji gazowej.",
         question="Czy zgłaszający opisuje zapach gazu lub wyciek gazu?",
         options=["Tak, opisuje zapach lub wyciek gazu", "Nie, nie opisuje zapachu ani wycieku gazu"], gold=1),
    dict(id="RE07", type="noul", rule_based=False, tricky=True,
         state="E-mail do zarządu:\nGratuluję, domofon działa od tygodnia wprost rewelacyjnie: nikt nie może się do "
               "mnie dodzwonić, a kurier trzeci raz odjechał z paczką. Naprawdę świetna robota. Marek Fikcyjny, "
               "lokal 15.",
         question="Czy wiadomość jest zgłoszeniem usterki, czyli opisuje uszkodzenie lub nieprawidłowe działanie "
                  "urządzenia albo elementu budynku?",
         options=["Tak, to zgłoszenie usterki", "Nie, to nie jest zgłoszenie usterki"], gold=0),
    dict(id="RE08", type="noul", rule_based=False, tricky=False,
         state="Wiadomość do administratora:\nDzień dobry, zamek w drzwiach do komórek lokatorskich się zacinał, "
               "więc go wczoraj sam wymieniłem, klucze zostawiłem w skrzynce zarządu. Nie oczekuję zwrotu za zamek, "
               "daję znać tylko dla porządku. Piotr Testowy, lokal 2.",
         question="Czy właściciel wnosi o zwrot kosztów, czyli wprost domaga się, by wspólnota oddała mu pieniądze?",
         options=["Tak, wnosi o zwrot kosztów", "Nie, nie wnosi o zwrot kosztów"], gold=1),
    dict(id="RE09", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie, lokal nr 41 (ostatnie piętro):\nPo każdym większym deszczu z sufitu w pokoju kapie woda "
               "i robi się mokra plama. Hydraulik sprawdził: w lokalu i nad nim nie ma żadnych rur, instalacja "
               "sucha. Na strychu widać przetartą papę nad moim pokojem.",
         question=_CAT_Q, options=_CAT_OPTS, keys=_CAT_KEYS, gold=3),
    dict(id="RE10", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie, lokal nr 8:\nSąsiad z lokalu 12 od miesiąca codziennie po 22:00 wierci i puszcza głośno "
               "muzykę. Rozmowa nie pomogła. Proszę zarząd o interwencję.",
         question=_CAT_Q, options=_CAT_OPTS, keys=_CAT_KEYS, gold=5),
    dict(id="RE11", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie, klatka B:\nNa 3. piętrze nie świeci lampa na korytarzu. Wymieniłem żarówkę na nową, "
               "nadal nic, a przy włączaniu wybija bezpiecznik oświetlenia klatki.",
         question=_CAT_Q, options=_CAT_OPTS, keys=_CAT_KEYS, gold=1),
    dict(id="RE12", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie, klatka A:\nSamozamykacz przy drzwiach wejściowych do budynku jest zepsuty, drzwi "
               "trzaskają z hukiem albo zostają otwarte na oścież.",
         question=_CAT_Q, options=_CAT_OPTS, keys=_CAT_KEYS, gold=4),
    dict(id="RE13", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie, lokal nr 5:\nGrzejnik w łazience jest zimny, pozostałe w mieszkaniu grzeją normalnie. "
               "Odpowietrzałem go dwa razy, zawór termostatyczny odkręcony.",
         question=_CAT_Q, options=_CAT_OPTS, keys=_CAT_KEYS, gold=0),
    dict(id="RE14", type="score", rule_based=False, tricky=True,
         state="SMS do administratora: siema, nie chcę robić paniki, pewnie nic takiego, ale od rana przy zejściu do "
               "piwnic na klatce C mocno czuć gaz. Może ktoś coś gotuje, haha. Pozdro, Kamil z 3.",
         question=_URG_Q, options=_URG_OPTS, keys=_URG_KEYS, gold=3),
    dict(id="RE15", type="score", rule_based=False, tricky=False,
         state="Zgłoszenie telefoniczne, godz. 8:10:\nWinda w budynku 9-piętrowym stoi od rana na parterze z "
               "otwartymi drzwiami i nie reaguje na przyciski. Nikogo nie ma w środku. Mieszkańcy chodzą schodami.",
         question=_URG_Q, options=_URG_OPTS, keys=_URG_KEYS, gold=2),
    dict(id="RE16", type="score", rule_based=False, tricky=False,
         state="Zgłoszenie z aplikacji: na poręczy schodów między 1. a 2. piętrem odrapana farba na długości około "
               "30 cm. Poręcz stabilna.",
         question=_URG_Q, options=_URG_OPTS, keys=_URG_KEYS, gold=0),
    dict(id="RE17", type="score", rule_based=False, tricky=True,
         state="E-mail z tematem: PILNE!!! AWARIA!!! NATYCHMIAST!!!\nW pralni na parterze kapie kran przy zlewie, "
               "kropla co kilka sekund, woda spływa do odpływu. Podłoga sucha. Proszę o hydraulika. Ewa Fikcyjna.",
         question=_URG_Q, options=_URG_OPTS, keys=_URG_KEYS, gold=1),
]
