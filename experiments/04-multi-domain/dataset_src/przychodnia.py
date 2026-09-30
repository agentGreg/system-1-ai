# Domain: przychodnia - wyłącznie administracja (rejestracja, skierowania, dokumenty, pilność wg protokołu).
# No medical advice, no diagnosis questions. Hand-written items, all data fictional.
_SKIER_RULE = ("(1) zawiera imię i nazwisko pacjenta, PESEL, kod rozpoznania ICD-10 oraz dane lekarza kierującego "
               "(imię, nazwisko, numer prawa wykonywania zawodu)")

_ALARM = ("ból w klatce piersiowej, duszność, utrata przytomności, nagły niedowład lub nagłe zaburzenia mowy, "
          "silne krwawienie")

_KIER_Q = "Gdzie należy skierować rozmówcę w przychodni?"
_KIER = ["Rejestracja POZ - wizyta u lekarza rodzinnego, bez skierowania",
         "Poradnia specjalistyczna - wizyta u specjalisty na skierowanie",
         "Gabinet zabiegowy - zastrzyki, pobrania krwi, opatrunki na zlecenie lekarza",
         "Punkt szczepień - zapisy na szczepienia",
         "Dział dokumentacji medycznej - kopie dokumentacji, zaświadczenia, wydruki wyników",
         "Pracownia diagnostyki obrazowej - RTG, USG na skierowanie"]
_KIER_KEYS = ["poz", "specjalista", "zabiegowy", "szczepienia", "dokumentacja", "diagnostyka_obrazowa"]

_PIL_Q = ("Jaki poziom pilności administracyjnej ma zgłoszenie według protokołu rejestracji? Wybierz najwyższy "
          "pasujący poziom. "
          "4 = alarmowy: rozmówca opisuje u kogoś objaw z listy alarmowej (" + _ALARM + ") - rejestratorka "
          "instruuje, aby natychmiast zadzwonić na 112; "
          "3 = pilny: gorączka co najmniej 39°C lub nowa dolegliwość, która pojawiła się w ciągu ostatnich 48 godzin - "
          "wizyta tego samego dnia; "
          "2 = planowy: wizyta kontrolna albo dolegliwość trwająca dłużej niż 48 godzin - termin w ciągu 14 dni; "
          "1 = administracyjny: sprawa niezwiązana z dolegliwościami (dokumenty, zmiana terminu, informacja).")
_PIL_OPT = ["1 - administracyjny", "2 - planowy (termin do 14 dni)", "3 - pilny (wizyta dziś)",
            "4 - alarmowy (zadzwonić na 112)"]
_PIL_KEYS = ["p1_administracyjny", "p2_planowy", "p3_pilny", "p4_alarmowy_112"]

ITEMS = [
    dict(id="MED01", type="noul", rule_based=True, tricky=True,
         state="Dziś jest wtorek, 2026-10-20.\n"
               "Pacjentka zgłasza się na wizytę w poradni endokrynologicznej. E-skierowanie: Anna Testowa, PESEL "
               "00000000000, rozpoznanie E04.1, lekarz kierujący: lek. Marek Fikcyjny, nr PWZ 0000000, data "
               "wystawienia 2026-07-15. W systemie: pacjentkę wpisano na listę oczekujących tej poradni "
               "2026-08-03, termin wizyty wyznaczono na dziś.",
         question="Czy skierowanie jest ważne na dzisiejszą wizytę? Reguła: skierowanie jest ważne, jeżeli "
                  + _SKIER_RULE + " oraz (2) od daty wystawienia do dnia wizyty minęło nie więcej niż 90 dni, "
                  "chyba że pacjenta wpisano na listę oczekujących tej poradni w ciągu 90 dni od daty wystawienia - "
                  "wtedy skierowanie zachowuje ważność do dnia wyznaczonej wizyty.",
         options=["Tak, skierowanie jest ważne", "Nie, skierowanie jest nieważne"], gold=0),
    dict(id="MED02", type="noul", rule_based=True, tricky=False,
         state="Dziś jest poniedziałek, 2026-10-19.\n"
               "Pacjent chce się dziś wpisać na listę oczekujących do poradni okulistycznej. Skierowanie papierowe: "
               "Jan Przykładowy, PESEL 00000000000, rozpoznanie H52.1, lekarz kierujący: lek. Ewa Testowa, nr PWZ "
               "0000000, data wystawienia 2026-07-20. Pacjent nie był wcześniej wpisany na żadną listę tej poradni.",
         question="Czy skierowanie można przyjąć przy dzisiejszym wpisie na listę oczekujących? Reguła: skierowanie "
                  "można przyjąć, jeżeli " + _SKIER_RULE + " oraz (2) od daty wystawienia do dnia wpisu na listę "
                  "minęło nie więcej niż 90 dni (liczy się różnicę dat kalendarzowych).",
         options=["Tak, można przyjąć", "Nie, nie można przyjąć"], gold=1),
    dict(id="MED03", type="noul", rule_based=True, tricky=True,
         state="Dziś jest wtorek, 2026-10-20.\n"
               "Przy okienku: Pani Ewa Przykładowa prosi o kopię dokumentacji medycznej swojego syna, Kacpra "
               "Przykładowego (data urodzenia 2008-03-10), bo chce ją zawieźć do innego lekarza. W systemie brak "
               "jakichkolwiek upoważnień udzielonych przez Kacpra Przykładowego.",
         question="Czy rejestracja może wydać kopię dokumentacji tej osobie? Reguła: kopię dokumentacji wydaje się "
                  "(a) pacjentowi, (b) osobie upoważnionej przez pacjenta pisemnie lub w systemie albo (c) rodzicowi "
                  "pacjenta, ale tylko wtedy, gdy pacjent w dniu wniosku nie ukończył 18 lat.",
         options=["Tak, można wydać", "Nie, nie można wydać"], gold=1),
    dict(id="MED04", type="noul", rule_based=True, tricky=False,
         state="Dziś jest wtorek, 2026-10-20.\n"
               "Telefon: Pan Adam Testowy chce umówić teleporadę u swojego lekarza rodzinnego w celu omówienia "
               "wyników badań krwi, które zrobił w zeszłym tygodniu. W systemie: ostatnia wizyta osobista w tej "
               "przychodni 2025-11-04, pacjent jest pod opieką tej poradni POZ od 2019 r.",
         question="Czy pacjenta można zarejestrować na teleporadę? Reguła: teleporada jest możliwa, jeżeli "
                  "(a) pacjent był w tej przychodni na wizycie osobistej w ciągu ostatnich 12 miesięcy, "
                  "(b) celem jest przedłużenie recepty na lek przyjmowany stale lub omówienie wyników badań oraz "
                  "(c) nie jest to pierwsza wizyta pacjenta w danej poradni.",
         options=["Tak, można zarejestrować na teleporadę", "Nie, wymagana wizyta osobista"], gold=0),
    dict(id="MED05", type="noul", rule_based=False, tricky=False,
         state="Telefon do rejestracji:\n"
               "Dzień dobry, mam zapisaną wizytę u okulisty na ten czwartek na 10:30, ale nie dam rady przyjść. "
               "Czy można ją przełożyć na jakiś dzień w przyszłym tygodniu? Jan Fikcyjny",
         question="Czy rozmówca prosi o zmianę terminu istniejącej wizyty, czyli przeniesienie już umówionej wizyty "
                  "na inny dzień (a nie o nową rejestrację ani samo odwołanie wizyty)?",
         options=["Tak, zmiana terminu", "Nie, inna sprawa"], gold=0),
    dict(id="MED06", type="noul", rule_based=False, tricky=True,
         state="Telefon do rejestracji:\n"
               "Dzień dobry, dzwonię w sprawie mamy. Rok temu miała zawał i kardiolog zalecił, żeby co roku "
               "przychodziła na kontrolę. Teraz czuje się dobrze, nic jej nie dolega, chciałabym ją tylko zapisać na "
               "tę coroczną kontrolę. Beata Testowa",
         question="Czy zgłoszenie należy obsłużyć jako alarmowe według protokołu, czyli czy rozmówca opisuje, że ktoś "
                  "ma teraz objaw z listy alarmowej (" + _ALARM + ")?",
         options=["Tak, zgłoszenie alarmowe", "Nie, zgłoszenie niealarmowe"], gold=1),
    dict(id="MED07", type="noul", rule_based=False, tricky=True,
         state="Wiadomość przez portal pacjenta:\n"
               "Dzień dobry, czy muszę się zapisywać, żeby odebrać wydruk wyników morfologii z zeszłego tygodnia? "
               "Nie potrzebuję wizyty u lekarza, chodzi mi tylko o sam papier z wynikami. Marta Przykładowa",
         question="Czy prośba dotyczy wydania dokumentu (wydruku wyników, zaświadczenia, kopii dokumentacji), a nie "
                  "umówienia wizyty u lekarza?",
         options=["Tak, wydanie dokumentu", "Nie, umówienie wizyty"], gold=0),
    dict(id="MED08", type="noul", rule_based=False, tricky=False,
         state="Przy okienku rejestracji poradni dermatologicznej:\n"
               "Pani Zofia Fikcyjna okazuje dowód osobisty. Mówi, że lekarz rodzinny wystawił jej skierowanie "
               "papierowe, ale nie zdążyła go odebrać i zostało w gabinecie lekarza. Nie ma e-skierowania.",
         question="Czy pacjentka ma przy sobie wszystkie dokumenty wymagane do rejestracji do poradni "
                  "specjalistycznej, czyli dokument tożsamości oraz skierowanie (papierowe lub kod e-skierowania)?",
         options=["Tak, ma komplet dokumentów", "Nie, brakuje dokumentu"], gold=1),
    dict(id="MED09", type="choice", rule_based=False, tricky=False,
         state="Telefon:\n"
               "Dzień dobry, lekarz rodzinny przepisał mi serię zastrzyków i dał zlecenie. Gdzie mam się zgłosić, "
               "żeby mi je robiono? Piotr Przykładowy",
         question=_KIER_Q, options=_KIER, keys=_KIER_KEYS, gold=2),
    dict(id="MED10", type="choice", rule_based=False, tricky=True,
         state="Telefon, notatka dosłowna:\n"
               "Dziołszka mo w listopadzie terminy na szczepiynie, jo bych jom chciała zapisać. Kaj mom zadzwonić, "
               "bo w rejestracji do doktora pedzieli, że to niy u nich?",
         question=_KIER_Q, options=_KIER, keys=_KIER_KEYS, gold=3),
    dict(id="MED11", type="choice", rule_based=False, tricky=False,
         state="Wiadomość przez portal pacjenta:\n"
               "Mam e-skierowanie do dermatologa od lekarza rodzinnego. Chciałbym się zapisać na pierwszą wizytę. "
               "Tomasz Testowy",
         question=_KIER_Q, options=_KIER, keys=_KIER_KEYS, gold=1),
    dict(id="MED12", type="choice", rule_based=False, tricky=False,
         state="E-mail:\n"
               "Proszę o przygotowanie kopii mojej dokumentacji medycznej z ostatnich 3 lat, potrzebuję jej do "
               "sprawy w sądzie. Odbiorę osobiście. Krzysztof Przykładowy",
         question=_KIER_Q, options=_KIER, keys=_KIER_KEYS, gold=4),
    dict(id="MED13", type="choice", rule_based=True, tricky=False,
         state="Rejestracja do poradni kardiologicznej:\n"
               "E-skierowanie dla Jana Testowego z oznaczeniem PILNE, wszystkie wymagane dane kompletne. Pacjent "
               "okazuje w oryginale ważną legitymację uprawniającą do przyjęcia poza kolejnością.",
         question="Na jaką listę wpisać pacjenta? Reguła: przyjęcie poza kolejnością, jeżeli pacjent okaże w "
                  "oryginale ważny dokument uprawniający do przyjęcia poza kolejnością - niezależnie od oznaczenia "
                  "skierowania; lista pilna, jeżeli skierowanie ma oznaczenie PILNE, a pacjent nie ma takiego "
                  "uprawnienia; lista stabilna w pozostałych przypadkach.",
         options=["Lista stabilna", "Przyjęcie poza kolejnością", "Lista pilna"],
         keys=["stabilna", "poza_kolejnoscia", "pilna"], gold=1),
    dict(id="MED14", type="choice", rule_based=False, tricky=False,
         state="Telefon:\n"
               "Dzień dobry, od wczoraj mam katar, kaszel i 38 stopni gorączki. Chciałbym dziś albo jutro zapisać się "
               "do swojego lekarza rodzinnego. Skierowania nie mam. Marek Testowy",
         question=_KIER_Q, options=_KIER, keys=_KIER_KEYS, gold=0),
    dict(id="MED15", type="score", rule_based=False, tricky=False,
         state="Telefon:\n"
               "Chciałabym zapisać tatę na wizytę kontrolną ciśnienia, lekarz kazał przyjść po trzech miesiącach. "
               "Tata czuje się dobrze, pomiary w domu ma w normie. Anna Fikcyjna",
         question=_PIL_Q, options=_PIL_OPT, keys=_PIL_KEYS, gold=1),
    dict(id="MED16", type="score", rule_based=False, tricky=False,
         state="Telefon:\n"
               "Syn (7 lat) od dzisiejszego rana ma 39,4°C gorączki. Poza tym je, pije i się bawi. Czy jest dziś "
               "wolny termin u pediatry? Katarzyna Przykładowa",
         question=_PIL_Q, options=_PIL_OPT, keys=_PIL_KEYS, gold=2),
    dict(id="MED17", type="score", rule_based=False, tricky=False,
         state="Telefon:\n"
               "Dzień dobry, chciałabym zapytać, czy jest dziś wolny termin u lekarza rodzinnego dla męża. Od jakichś "
               "20 minut mówi niewyraźnie, jakby bełkotał, i nie może podnieść prawej ręki. Może być nawet po "
               "południu, nie ma pośpiechu. Ewa Testowa",
         question=_PIL_Q, options=_PIL_OPT, keys=_PIL_KEYS, gold=3),
]
