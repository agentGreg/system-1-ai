# Domain: logistyka (logistics, transport). Hand-written items, all names / numbers fictional.
_TYPE_OPTS = ["Uszkodzenie - przesyłka dotarła, ale zawartość lub opakowanie są uszkodzone",
              "Opóźnienie - przesyłka jest w drodze lub dotarła, ale po obiecanym terminie; jej położenie jest znane",
              "Błędny adres - przesyłki nie da się doręczyć lub trafiła gdzie indziej, bo adres na etykiecie jest błędny lub niepełny",
              "Zaginięcie - przewoźnik nie wie, gdzie jest przesyłka (brak skanów, nie odnaleziono jej w magazynie)",
              "Odmowa przyjęcia - odbiorca nie przyjął przesyłki od kuriera"]
_TYPE_KEYS = ["uszkodzenie", "opoznienie", "bledny_adres", "zaginiecie", "odmowa"]
_TYPE_Q = "Jaki jest typ problemu z przesyłką?"

_PRIO_Q = ("Jaki priorytet ma to zgłoszenie? Poziomy: 1 = niski (pytanie informacyjne, brak problemu z żadną "
           "przesyłką); 2 = normalny (problem z pojedynczą przesyłką o wartości do 1 000 zł, bez towaru "
           "niebezpiecznego i bez wymogu temperatury); 3 = wysoki (problem z przesyłką o wartości powyżej 1 000 zł "
           "albo z więcej niż 10 przesyłkami jednego klienta naraz); 4 = krytyczny (towar niebezpieczny, z którego "
           "coś wycieka lub którego opakowanie jest uszkodzone, albo przesyłka wymagająca chłodzenia, której "
           "temperatura jest przekroczona).")
_PRIO_OPTS = ["1 - niski", "2 - normalny", "3 - wysoki", "4 - krytyczny"]
_PRIO_KEYS = ["niski", "normalny", "wysoki", "krytyczny"]

ITEMS = [
    # ---------------- noul ----------------
    dict(id="LOG01", type="noul", rule_based=True, tricky=True,
         state="Reklamacja z dnia 2026-11-16.\n"
               "Przesyłka ekspresowa EXP-0000-101 nadana we wtorek 2026-11-10, doręczona w piątek 2026-11-13 o 11:20.\n"
               "Klient: 'Zapłaciłem za ekspres, a paczka szła trzy dni! Żądam odszkodowania za opóźnienie.'",
         question="Czy klientowi przysługuje odszkodowanie za opóźnienie? Reguła: odszkodowanie przysługuje, jeżeli "
                  "przesyłkę ekspresową doręczono później niż 2. dnia roboczego po dniu nadania (dni robocze to "
                  "poniedziałek - piątek z wyjątkiem dni ustawowo wolnych od pracy; 2026-11-11 jest dniem ustawowo "
                  "wolnym), a reklamację złożono w ciągu 14 dni od doręczenia.",
         options=["Tak, odszkodowanie przysługuje", "Nie, odszkodowanie nie przysługuje"], gold=1),
    dict(id="LOG02", type="noul", rule_based=True, tricky=True,
         state="Dziś jest piątek, 2026-10-23.\n"
               "Przesyłka PAC-0000-202, waga 34 kg. Zadeklarowane okno doręczenia: 2026-10-19, 8:00-18:00.\n"
               "Log kuriera: próba doręczenia 2026-10-19 o 21:10, 'nikt nie otworzył'.\n"
               "Odbiorca Jan Testowy prosi dziś o ponowne doręczenie. Przesyłka nie była wcześniej doręczana ponownie.",
         question="Czy odbiorcy przysługuje bezpłatne ponowne doręczenie? Reguła: przysługuje, gdy spełnione są "
                  "łącznie warunki: (1) przesyłka waży nie więcej niż 30 kg; (2) prośbę złożono w ciągu 5 dni "
                  "kalendarzowych od nieudanej próby, licząc od dnia następującego po dniu próby; (3) jest to pierwsze "
                  "ponowne doręczenie tej przesyłki. Jeżeli nieudana próba nastąpiła poza zadeklarowanym oknem "
                  "doręczenia, warunek (1) nie obowiązuje.",
         options=["Tak, bezpłatne ponowne doręczenie przysługuje", "Nie, nie przysługuje"], gold=0),
    dict(id="LOG03", type="noul", rule_based=True, tricky=False,
         state="Przewóz zaplanowany na wtorek 2026-10-27.\n"
               "Ładunek: farba rozpuszczalnikowa, UN 1263, klasa 3, grupa pakowania II.\n"
               "List przewozowy: numer UN, prawidłowa nazwa przewozowa, klasa i grupa pakowania - wpisane.\n"
               "Instrukcje pisemne dla kierowcy: w kabinie. Kierowca Marek Fikcyjny, zaświadczenie ADR ważne do 2026-10-26.",
         question="Czy dokumentacja przewozu towaru niebezpiecznego jest kompletna? Reguła: jest kompletna, jeżeli "
                  "(1) list przewozowy zawiera numer UN, prawidłową nazwę przewozową, klasę i grupę pakowania; "
                  "(2) kierowca ma przy sobie instrukcje pisemne; (3) kierowca ma zaświadczenie ADR, którego data "
                  "ważności nie jest wcześniejsza niż dzień przewozu.",
         options=["Tak, dokumentacja jest kompletna", "Nie, dokumentacja nie jest kompletna"], gold=1),
    dict(id="LOG04", type="noul", rule_based=True, tricky=False,
         state="Zgłoszenie szkody z dnia 2026-10-09.\n"
               "Przesyłka PAC-0000-404 (ekspres do kawy), zadeklarowana wartość 1 200 zł, doręczona 2026-10-02.\n"
               "Odbiorca Anna Przykładowa dołączyła zdjęcia rozbitej obudowy i opakowania. Magazyn potwierdził, że "
               "opakowanie nadawcy spełniało wymogi regulaminu. Żądana kwota: 1 150 zł.",
         question="Czy klientce przysługuje odszkodowanie za uszkodzenie? Reguła: przysługuje, jeżeli łącznie: "
                  "(1) uszkodzenie zgłoszono najpóźniej 7. dnia po doręczeniu, licząc od dnia następującego po dniu "
                  "doręczenia; (2) dołączono protokół szkody lub zdjęcia uszkodzeń; (3) opakowanie spełniało wymogi "
                  "regulaminu; (4) żądana kwota nie przekracza zadeklarowanej wartości przesyłki.",
         options=["Tak, odszkodowanie przysługuje", "Nie, odszkodowanie nie przysługuje"], gold=0),
    dict(id="LOG05", type="noul", rule_based=True, tricky=False,
         state="Dziś jest środa, 2026-11-04.\n"
               "Przesyłka PAC-0000-505, ostatni skan: czwartek 2026-10-29, 'przyjęto w sortowni Testowo'. Od tamtej "
               "pory brak nowych skanów. Status: 'w transporcie'. Nadawca pisze, że paczka 'na pewno zaginęła'.",
         question="Czy należy uruchomić procedurę poszukiwawczą dla zaginionej przesyłki? Reguła: procedurę "
                  "uruchamia się, gdy przesyłka nie ma statusu 'oczekuje w punkcie odbioru' i od ostatniego skanu "
                  "minęło co najmniej 5 dni roboczych bez nowego skanu; dni roboczych liczy się od dnia następującego "
                  "po dniu ostatniego skanu do dnia dzisiejszego włącznie (dni robocze: poniedziałek - piątek poza "
                  "dniami ustawowo wolnymi od pracy).",
         options=["Tak, uruchomić procedurę", "Nie, jeszcze nie uruchamiać"], gold=1),
    dict(id="LOG06", type="noul", rule_based=False, tricky=False,
         state="Raport kuriera, przesyłka PAC-0000-606:\n"
               "Odbiorca obejrzał karton przy drzwiach, powiedział: 'Nie biorę tego, jest cały zgnieciony', "
               "i podpisał na terminalu odmowę przyjęcia. Przesyłka wraca do oddziału.",
         question="Czy odbiorca odmówił przyjęcia przesyłki, czyli świadomie nie przyjął jej od kuriera?",
         options=["Tak, odmówił przyjęcia", "Nie, nie odmówił przyjęcia"], gold=0),
    dict(id="LOG07", type="noul", rule_based=False, tricky=True,
         state="E-mail do obsługi klienta:\n"
               "Dzień dobry, przesyłka PAC-0000-707 jest dziś w drodze, a mnie niestety nie będzie w domu do piątku. "
               "Czy byłaby możliwość, żeby kurier zostawił ją w moim biurze przy ul. Przykładowej 5, 00-000 Testowo, "
               "zamiast pod adresem domowym? Będę bardzo wdzięczna. Pozdrawiam, Ewa Testowa",
         question="Czy klientka żąda zmiany adresu doręczenia przesyłki, czyli prosi o doręczenie jej pod inny "
                  "adres niż ten podany w zleceniu?",
         options=["Tak, prosi o zmianę adresu", "Nie, nie prosi o zmianę adresu"], gold=0),
    dict(id="LOG08", type="noul", rule_based=False, tricky=True,
         state="Wiadomość od odbiorcy:\n"
               "Karton z serwisem obiadowym przyszedł mocno zgnieciony z jednego boku, wyglądał strasznie. Ale "
               "w środku wszystko całe, sprawdziłem każdy talerz i filiżankę. Piszę tylko, żebyście wiedzieli, "
               "niczego nie oczekuję. Karol Testowy",
         question="Czy zgłoszenie dotyczy uszkodzenia zawartości przesyłki, czyli czy uszkodzony jest przewożony "
                  "towar (a nie samo opakowanie)?",
         options=["Tak, zawartość jest uszkodzona", "Nie, zawartość nie jest uszkodzona"], gold=1),
    # ---------------- choice ----------------
    dict(id="LOG09", type="choice", rule_based=False, tricky=False,
         state="Notatka kuriera, przesyłka PAC-0000-909:\n"
               "Na etykiecie: 'Przykład-Bud sp. z o.o., ul. Przykładowa 12'. Pod numerem 12 jest szkoła, nikt nie "
               "zna firmy. Dzwoniłem do odbiorcy: firma mieści się pod numerem 21, nadawca pomylił cyfry.",
         question=_TYPE_Q, options=_TYPE_OPTS, keys=_TYPE_KEYS, gold=2),
    dict(id="LOG10", type="choice", rule_based=False, tricky=False,
         state="Czat:\n"
               "Paczka miała być we wtorek, dziś czwartek i nadal jej nie ma. W śledzeniu od wczoraj rana widzę "
               "status 'wydana do doręczenia, kurier w drodze', więc chyba jest już w mieście. Kiedy wreszcie dotrze?",
         question=_TYPE_Q, options=_TYPE_OPTS, keys=_TYPE_KEYS, gold=1),
    dict(id="LOG11", type="choice", rule_based=False, tricky=True,
         state="Sprawa PAC-0000-111:\n"
               "Klient: 'Znowu opóźnienie, ile można czekać na tę paczkę?!'\n"
               "Notatka magazynu: ostatni skan 9 dni temu w sortowni Testowo; przeszukanie sortowni i "
               "inwentaryzacja nie odnalazły przesyłki; brak skanu w innych oddziałach.",
         question=_TYPE_Q, options=_TYPE_OPTS, keys=_TYPE_KEYS, gold=3),
    dict(id="LOG12", type="choice", rule_based=False, tricky=False,
         state="Protokół przyjęcia palety PAL-0000-012:\n"
               "Paleta dotarła w terminie. Folia rozcięta z boku, dwa kartony z ekspresami ciśnieniowymi "
               "przemoczone, w jednym pęknięta obudowa urządzenia. Odbiorca przyjął paletę z adnotacją o szkodzie.",
         question=_TYPE_Q, options=_TYPE_OPTS, keys=_TYPE_KEYS, gold=0),
    dict(id="LOG13", type="choice", rule_based=False, tricky=False,
         state="Raport kuriera, przesyłka PAC-0000-013 (za pobraniem 89 zł):\n"
               "Adres i nazwisko zgodne. Odbiorca Jerzy Fikcyjny powiedział: 'Nic nie zamawiałem i nie będę za to "
               "płacił', po czym zamknął drzwi. Przesyłka wraca do nadawcy.",
         question=_TYPE_Q, options=_TYPE_OPTS, keys=_TYPE_KEYS, gold=4),
    # ---------------- score ----------------
    dict(id="LOG14", type="score", rule_based=False, tricky=False,
         state="E-mail od stałego klienta biznesowego:\n"
               "Dzień dobry, od grudnia planujemy nadawać paczki także w soboty. Do której godziny kurier może "
               "odebrać przesyłki z magazynu w sobotę i czy trzeba to zgłaszać dzień wcześniej?",
         question=_PRIO_Q, options=_PRIO_OPTS, keys=_PRIO_KEYS, gold=0),
    dict(id="LOG15", type="score", rule_based=False, tricky=False,
         state="Zgłoszenie od sklepu internetowego Przykład-Moda:\n"
               "15 naszych paczek do różnych klientów (każda o wartości 80 - 250 zł, odzież) od 3 dni stoi w "
               "sortowni Testowo bez żadnego ruchu. Klienci piszą do nas z pretensjami.",
         question=_PRIO_Q, options=_PRIO_OPTS, keys=_PRIO_KEYS, gold=2),
    dict(id="LOG16", type="score", rule_based=False, tricky=False,
         state="Czat:\n"
               "Zamówiłem książki za 180 zł, paczka miała być wczoraj, a według śledzenia będzie jutro. Nic się "
               "nie pali, ale proszę o informację, czy termin jest pewny.",
         question=_PRIO_Q, options=_PRIO_OPTS, keys=_PRIO_KEYS, gold=1),
    dict(id="LOG17", type="score", rule_based=False, tricky=False,
         state="Wiadomość od kierowcy z trasy:\n"
               "Na postoju zauważyłem, że z palety z kanistrami oznaczonymi klasą 8 (materiały żrące) coś kapie "
               "na podłogę naczepy, jest mała kałuża. Poza tym wszystko ok, mogę jechać dalej?",
         question=_PRIO_Q, options=_PRIO_OPTS, keys=_PRIO_KEYS, gold=3),
]
