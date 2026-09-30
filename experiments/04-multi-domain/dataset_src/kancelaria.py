# Domain: kancelaria prawna (intake nowych spraw). Hand-written items, all data fictional.
_KAT_Q = ("Do której kategorii należy sprawa? Jeżeli wiadomość dotyczy kilku kwestii, wybierz kategorię "
          "głównego żądania klienta.")
_KAT = ["Rodzinna - rozwód, separacja, alimenty, kontakty z dzieckiem, władza rodzicielska",
        "Pracownicza - spór pracownika z pracodawcą wynikający ze stosunku pracy",
        "Gospodarcza - spór między przedsiębiorcami związany z ich działalnością",
        "Karna - postępowanie karne lub wykroczeniowe (klient podejrzany, oskarżony lub pokrzywdzony)",
        "Nieruchomości - własność, granice działek, służebności, zasiedzenie, obrót nieruchomościami",
        "Spadkowa - nabycie spadku, testament, zachowek, dział spadku"]
_KAT_KEYS = ["rodzinna", "pracownicza", "gospodarcza", "karna", "nieruchomosci", "spadkowa"]

_PIL_Q = ("Jaki poziom pilności nadać sprawie przy przyjęciu? Poziomy: "
          "1 = brak jakiegokolwiek terminu, pytanie ogólne; "
          "2 = najbliższy termin (procesowy lub inny wskazany przez klienta) upływa za więcej niż 14 dni od dziś; "
          "3 = najbliższy termin upływa za 3 do 14 dni od dziś; "
          "4 = termin upływa dziś lub w ciągu 2 dni od dziś albo klient lub osoba mu bliska jest zatrzymana.")
_PIL_OPT = ["1 - brak terminu", "2 - termin za ponad 14 dni", "3 - termin za 3-14 dni",
            "4 - termin do 2 dni lub zatrzymanie"]
_PIL_KEYS = ["p1_brak_terminu", "p2_ponad_14_dni", "p3_3_14_dni", "p4_do_2_dni"]

ITEMS = [
    dict(id="LAW01", type="noul", rule_based=True, tricky=True,
         state="Dziś jest poniedziałek, 2026-10-19.\n"
               "Notatka z rozmowy telefonicznej: Pan Jan Testowy przegrał sprawę przed sądem rejonowym. Wyrok z "
               "uzasadnieniem odebrał na poczcie w sobotę 2026-10-03. Pyta, czy zdążymy z apelacją, jeżeli "
               "złożymy ją w sądzie jeszcze dziś.",
         question="Czy apelacja złożona dziś będzie wniesiona w terminie? Reguła: apelację wnosi się w terminie "
                  "14 dni od doręczenia wyroku z uzasadnieniem; termin liczy się od dnia następującego po "
                  "doręczeniu; jeżeli ostatni dzień terminu przypada w sobotę lub dzień ustawowo wolny od pracy, "
                  "termin upływa następnego dnia roboczego.",
         options=["Tak, w terminie", "Nie, po terminie"], gold=0),
    dict(id="LAW02", type="noul", rule_based=True, tricky=True,
         state="Dziś jest środa, 2026-10-14.\n"
               "Formularz przyjęcia sprawy: Klient Przykład-Serwis sp. z o.o. chce dochodzić zapłaty od "
               "Fikcyjny-Trans sp. z o.o. za usługę serwisową. Faktura FV/0000/2023 była płatna (wymagalna) "
               "2023-03-15. Dłużnik nigdy nie uznał długu, nie było też wcześniejszego pozwu ani ugody.",
         question="Czy roszczenie jest już przedawnione? Reguła: roszczenie przedawnia się z upływem 3 lat od dnia "
                  "wymagalności, przy czym koniec terminu przedawnienia przypada na ostatni dzień roku "
                  "kalendarzowego, w którym upłynęłyby te 3 lata; uznanie długu przez dłużnika przerywa bieg "
                  "przedawnienia.",
         options=["Tak, roszczenie jest przedawnione", "Nie, roszczenie nie jest jeszcze przedawnione"], gold=1),
    dict(id="LAW03", type="noul", rule_based=True, tricky=False,
         state="Dziś jest środa, 2026-10-07.\n"
               "Nowa sprawa: Anna Przykładowa chce pozwać Przykład-Bud sp. z o.o. o usunięcie wad w mieszkaniu. "
               "Wynik sprawdzenia w systemie konfliktów: Przykład-Bud sp. z o.o. była klientem kancelarii w sprawie "
               "windykacyjnej zakończonej 2024-02-28. Brak w aktach jakiejkolwiek zgody Przykład-Bud sp. z o.o. "
               "na prowadzenie spraw przeciwko niej.",
         question="Czy kancelaria może przyjąć sprawę? Reguła: kancelaria nie może przyjąć sprawy, jeżeli "
                  "(a) reprezentuje stronę przeciwną lub reprezentowała ją w jakiejkolwiek sprawie zakończonej w "
                  "ciągu ostatnich 3 lat przed dniem dzisiejszym, albo (b) doradzała obu stronom w tej samej sprawie; "
                  "ograniczenie z pkt (a) nie obowiązuje, jeżeli strona przeciwna wyraziła pisemną zgodę.",
         options=["Tak, może przyjąć", "Nie, nie może przyjąć"], gold=1),
    dict(id="LAW04", type="noul", rule_based=True, tricky=False,
         state="Zlecenie windykacyjne:\n"
               "Klient: Przykład-Handel sp. z o.o. Dłużnik: Fikcyjny-Serwis sp. z o.o. (przedsiębiorca). "
               "Należność główna: 9 800,00 zł (faktura FV/0000/2026). Odsetki za opóźnienie do dziś: 452,17 zł. "
               "Koszty upomnień: 40,00 zł. Razem do zapłaty: 10 292,17 zł.",
         question="Czy sprawa kwalifikuje się do pakietu ryczałtowego? Reguła: pakiet ryczałtowy obejmuje sprawy, w "
                  "których wartość przedmiotu sporu wynosi co najmniej 10 000 zł i nie więcej niż 100 000 zł, a "
                  "dłużnik jest przedsiębiorcą; wartość przedmiotu sporu to wyłącznie należność główna, bez odsetek "
                  "i kosztów.",
         options=["Tak, pakiet ryczałtowy", "Nie, poza pakietem"], gold=1),
    dict(id="LAW05", type="noul", rule_based=False, tricky=False,
         state="Wiadomość z formularza, godz. 07:15:\n"
               "Dzień dobry, mój brat Piotr Testowy został w nocy zatrzymany przez policję i jest na komisariacie. "
               "Nie wiemy, o co dokładnie chodzi, rano mają go przesłuchiwać. Czy ktoś może do niego pojechać?",
         question="Czy sprawa wymaga kontaktu adwokata jeszcze dziś, czyli czy zgłoszenie dotyczy zatrzymania osoby "
                  "przez policję albo terminu procesowego upływającego dziś lub jutro?",
         options=["Tak, kontakt jeszcze dziś", "Nie, zwykły tryb"], gold=0),
    dict(id="LAW06", type="noul", rule_based=False, tricky=True,
         state="E-mail:\n"
               "Dzień dobry, nie chcę na razie nikogo pozywać ani chodzić do sądu. Chciałbym tylko, żeby ktoś z "
               "Państwa przejrzał umowę najmu lokalu użytkowego, zanim podpiszę ją w piątek. Umowę załączam. "
               "Tomasz Przykładowy",
         question="Czy klient zleca reprezentację przed sądem, czyli prowadzenie sprawy sądowej w jego imieniu (a nie "
                  "tylko poradę lub opinię o dokumencie)?",
         options=["Tak, reprezentacja przed sądem", "Nie, porada lub opinia"], gold=1),
    dict(id="LAW07", type="noul", rule_based=False, tricky=False,
         state="Formularz kontaktowy:\n"
               "Nazywam się Marek Fikcyjny. Chcę pozwać mojego byłego wspólnika, Pawła Testowego, o zwrot pożyczki "
               "40 000 zł, której mi nie oddał mimo wezwań. Mam umowę pożyczki i potwierdzenie przelewu.",
         question="Czy zgłoszenie zawiera dane potrzebne do sprawdzenia konfliktu interesów, czyli zarówno imię i "
                  "nazwisko (lub nazwę) klienta, jak i imię i nazwisko (lub nazwę) strony przeciwnej?",
         options=["Tak, dane są kompletne", "Nie, brakuje danych"], gold=0),
    dict(id="LAW08", type="noul", rule_based=False, tricky=True,
         state="Wiadomość:\n"
               "Szef zwolnił mnie dyscyplinarnie po 8 latach pracy w sklepie. Twierdzi, że ukradłam towar z "
               "magazynu, co jest kompletną bzdurą, nikt nie zawiadamiał policji i nie ma żadnego postępowania. "
               "Chcę się odwołać od tego zwolnienia. Ewa Testowa",
         question="Czy sprawa jest sprawą z zakresu prawa pracy, czyli sporem pracownika z pracodawcą wynikającym ze "
                  "stosunku pracy?",
         options=["Tak, sprawa pracownicza", "Nie, inna kategoria"], gold=0),
    dict(id="LAW09", type="choice", rule_based=False, tricky=False,
         state="E-mail:\n"
               "Miesiąc temu zmarł mój tata. Siostra twierdzi, że ma testament, w którym tata zapisał jej cały dom, "
               "a mnie pominął. Chcę dostać to, co mi się należy, słyszałam o zachowku. Katarzyna Testowa",
         question=_KAT_Q, options=_KAT, keys=_KAT_KEYS, gold=5),
    dict(id="LAW10", type="choice", rule_based=False, tricky=False,
         state="Zapytanie od klienta firmowego:\n"
               "Nasza spółka dostarczyła kontrahentowi, Fikcyjny-Hurt sp. z o.o., trzy partie towaru. Trzy faktury "
               "na łącznie 58 000 zł są nieopłacone od 4 miesięcy, wezwania do zapłaty nic nie dały. Prosimy o "
               "skierowanie sprawy do sądu. Zarząd Przykład-Handel sp. z o.o.",
         question=_KAT_Q, options=_KAT, keys=_KAT_KEYS, gold=2),
    dict(id="LAW11", type="choice", rule_based=False, tricky=False,
         state="Formularz kontaktowy:\n"
               "Chcę rozwodu. Mąż wyprowadził się pół roku temu, na córkę płaci nieregularnie, więc chcę też "
               "zasądzenia alimentów. Mieszkanie mamy wspólne, ale tym zajmiemy się kiedy indziej. Anna Przykładowa",
         question=_KAT_Q, options=_KAT, keys=_KAT_KEYS, gold=0),
    dict(id="LAW12", type="choice", rule_based=False, tricky=False,
         state="SMS przepisany przez recepcję:\n"
               "Dostałem wezwanie na policję na przesłuchanie w charakterze podejrzanego o prowadzenie samochodu w "
               "stanie nietrzeźwości. Termin za 3 tygodnie. Potrzebuję obrońcy. Jan Przykładowy",
         question=_KAT_Q, options=_KAT, keys=_KAT_KEYS, gold=3),
    dict(id="LAW13", type="choice", rule_based=False, tricky=False,
         state="E-mail:\n"
               "Sąsiad postawił nowy płot, który według pomiaru geodety wchodzi na moją działkę na 1,5 metra. "
               "Na rozmowy nie reaguje. Chcę, żeby płot został przesunięty na właściwą granicę. Paweł Fikcyjny",
         question=_KAT_Q, options=_KAT, keys=_KAT_KEYS, gold=4),
    dict(id="LAW14", type="choice", rule_based=True, tricky=True,
         state="Ankieta przyjęcia sprawy:\n"
               "Klientka: Anna Testowa (osoba fizyczna). Sprawa: podwyższenie alimentów od ojca dzieci. "
               "Gospodarstwo domowe: klientka, jej matka i dwoje dzieci (łącznie 4 osoby). Łączny dochód netto "
               "gospodarstwa domowego: 6 000 zł miesięcznie.",
         question="Jaką stawkę przyjąć dla sprawy? Reguła: pro bono, jeżeli klient jest osobą fizyczną, sprawa nie "
                  "jest gospodarcza, a miesięczny dochód netto na osobę w gospodarstwie domowym nie przekracza "
                  "1 500 zł; stawka obniżona, jeżeli klient jest osobą fizyczną, sprawa nie jest gospodarcza, a "
                  "dochód netto na osobę jest wyższy niż 1 500 zł, ale nie przekracza 3 000 zł; stawka standardowa "
                  "we wszystkich pozostałych przypadkach.",
         options=["Stawka standardowa", "Stawka obniżona", "Pro bono"],
         keys=["standardowa", "obnizona", "pro_bono"], gold=2),
    dict(id="LAW15", type="score", rule_based=False, tricky=False,
         state="Dziś jest wtorek, 2026-10-13.\n"
               "E-mail: Dzień dobry, zastanawiam się nad spisaniem testamentu. Co jest lepsze, testament notarialny "
               "czy własnoręczny? Nie spieszy mi się, chcę się po prostu dowiedzieć. Zofia Przykładowa",
         question=_PIL_Q, options=_PIL_OPT, keys=_PIL_KEYS, gold=0),
    dict(id="LAW16", type="score", rule_based=False, tricky=False,
         state="Dziś jest poniedziałek, 2026-10-05.\n"
               "Telefon: Pani Maria Fikcyjna dostała z sądu nakaz zapłaty w sprawie o 12 000 zł za rzekomo "
               "niezapłacony kurs. Według pouczenia termin na sprzeciw mija we wtorek 2026-10-13. Chce złożyć "
               "sprzeciw.",
         question=_PIL_Q, options=_PIL_OPT, keys=_PIL_KEYS, gold=2),
    dict(id="LAW17", type="score", rule_based=False, tricky=False,
         state="Dziś jest środa, 2026-10-07.\n"
               "E-mail: Bardzo się denerwuję, bo pierwszy raz idę do sądu. Rozprawa w mojej sprawie o zapłatę "
               "odbędzie się 2026-11-20 i chciałbym, żeby ktoś mnie reprezentował. Żadnych innych terminów nie mam. "
               "Adam Testowy",
         question=_PIL_Q, options=_PIL_OPT, keys=_PIL_KEYS, gold=1),
]
