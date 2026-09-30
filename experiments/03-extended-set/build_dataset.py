"""Build decisions.jsonl for experiment 03: the 30 items of experiment 01 (ids and text unchanged) plus 170 new ones.

Every new item was written by hand for this experiment. `gold` is the author's label, fixed here before any model
(annotator or system) saw the item. Company and brand names in the new items are fictional.

Categories (id prefix): R reklamacja (noul), D routing (choice, 5 departments), E eskalacja (noul), K kompletnosc
(noul, rule given in the question, rules vary), S sentyment / irytacja (choice, 3 levels), P phishing / oszustwo (noul).
For noul items option 0 is "yes" and option 1 is "no" (as in experiment 01).

usage: python build_dataset.py   (writes decisions.jsonl)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP01 = HERE.parent / "01-basal-vs-thinking" / "decisions.jsonl"

Q_R = ("Czy ta wiadomość jest reklamacją, czyli klient zgłasza wadę lub niezgodność towaru albo usługi z umową i "
       "domaga się z tego powodu naprawy, wymiany, obniżenia ceny lub zwrotu pieniędzy?")
O_R = ["Tak, to reklamacja", "Nie, to nie jest reklamacja"]
Q_D = "Do którego działu skierować tę wiadomość?"
O_D = ["Reklamacje (wady, uszkodzenia, niezgodność towaru z zamówieniem)", "Faktury i płatności",
       "Dostawa i logistyka", "Wsparcie techniczne", "Sprzedaż (oferty, ceny, nowe zamówienia)"]
Q_E = ("Czy tę sprawę należy natychmiast przekazać człowiekowi (konsultantowi) zamiast obsługiwać ją automatycznie? "
       "Eskalujemy, gdy klient grozi krokami prawnymi, jest bardzo zdenerwowany i zapowiada rezygnację, albo gdy chodzi "
       "o osobę w trudnej sytuacji (zdrowie, żałoba, bezradność).")
O_E = ["Tak, eskalować do człowieka", "Nie, można obsłużyć automatycznie"]
O_K = ["Tak, zgłoszenie jest kompletne", "Nie, zgłoszeniu czegoś brakuje"]
Q_S = "Jak bardzo zirytowany jest klient, który napisał tę wiadomość?"
O_S = ["Spokojny (brak irytacji)", "Lekko zirytowany", "Bardzo zirytowany"]
Q_P = ("Czy ta wiadomość jest próbą oszustwa lub phishingu, czyli podszywa się pod kogoś albo próbuje wyłudzić dane, "
       "hasła, kody, dostęp do systemów lub pieniądze od firmy albo jej klienta?")
O_P = ["Tak, to próba oszustwa lub phishingu", "Nie, to zwykła, uczciwa wiadomość"]

RULES = {
    # the 4-part rule of experiment 01 (K01-K05 use exactly this text)
    "A": ("zgłoszenie reklamacyjne jest kompletne, jeśli zawiera (1) numer zamówienia, (2) opis wady, (3) żądanie "
          "klienta (naprawa, wymiana, obniżenie ceny albo zwrot pieniędzy) oraz (4) numer rachunku bankowego, ale "
          "tylko wtedy, gdy klient żąda zwrotu pieniędzy."),
    "B": ("zgłoszenie gwarancyjne jest kompletne, jeśli zawiera (1) numer seryjny urządzenia, (2) datę zakupu oraz "
          "(3) opis usterki."),
    "C": "wniosek o zmianę adresu jest kompletny, jeśli zawiera (1) numer klienta oraz (2) pełny nowy adres z kodem pocztowym.",
    "D": ("zgłoszenie szkody komunikacyjnej jest kompletne, jeśli zawiera (1) numer polisy, (2) datę zdarzenia, "
          "(3) miejsce zdarzenia, (4) opis szkody oraz (5) numer rejestracyjny pojazdu sprawcy, ale tylko wtedy, gdy "
          "szkodę spowodował inny kierowca."),
    "E": ("wniosek o korektę faktury jest kompletny, jeśli zawiera (1) numer faktury, (2) wskazanie, która pozycja lub "
          "które dane są błędne, oraz (3) poprawne dane; jeśli błąd dotyczy numeru NIP, wniosek musi dodatkowo zawierać "
          "(4) dokument potwierdzający poprawny NIP (np. wydruk z CEIDG lub KRS)."),
    "F": ("zgłoszenie odstąpienia od umowy jest kompletne, jeśli zawiera (1) numer zamówienia, (2) listę zwracanych "
          "produktów oraz (3) numer rachunku bankowego do zwrotu, chyba że klient płacił kartą (wtedy zwrot trafia na "
          "kartę i numer rachunku nie jest potrzebny)."),
    "G": ("zgłoszenie awarii jest kompletne, jeśli zawiera (1) nazwę systemu lub aplikacji, (2) opis problemu, "
          "(3) informację, od kiedy problem występuje, oraz (4) treść komunikatu błędu albo zrzut ekranu, ale tylko "
          "wtedy, gdy pojawił się komunikat błędu."),
}
K_HEAD = {"A": "Zgłoszenie reklamacyjne z formularza:", "B": "Zgłoszenie gwarancyjne z formularza serwisu:",
          "C": "Wniosek klienta (operator telekomunikacyjny):", "D": "Zgłoszenie szkody (ubezpieczyciel):",
          "E": "Wiadomość do działu księgowości:", "F": "Zgłoszenie odstąpienia od umowy (sklep internetowy):",
          "G": "Zgłoszenie do helpdesku IT:"}

# (id, context, text, gold, tricky)   gold: 0 = yes / complaint
R = [
    ("R11", "sklep internetowy", "Hej, zamówiłam blender (nr 88213), przyszedł z pękniętym dzbankiem. Poprosze o wymiane albo zwrot kasy.", 0, False),
    ("R12", "operator telekomunikacyjny", "Dzień dobry, chciałbym przejść na wyższy pakiet internetu. Ile to będzie kosztować miesięcznie?", 1, False),
    ("R13", "sklep internetowy", "Nie chcę robić problemu, wiem, że macie teraz dużo pracy. Tylko że te buty po tygodniu mają odklejoną podeszwę... Jeśli to nie kłopot, może dałoby się je naprawić albo wymienić? Z góry dziękuję.", 0, True),
    ("R14", "operator telekomunikacyjny", "Serio? Kolejna podwyżka abonamentu od stycznia? Ogarnijcie się. Jak mogę wypowiedzieć umowę?", 1, True),
    ("R15", "bank", "Bankomat przy ul. Mickiewicza nie wydał mi 500 zł, a kwota zeszła z konta. Proszę o zwrot tych pieniędzy.", 0, False),
    ("R16", "sklep internetowy", "Kiedy wróci do sprzedaży czarny plecak turystyczny 30 l? Czekam od miesiąca.", 1, False),
    ("R17", "sklep z elektroniką", "Hi, laptop, który kupiłem last week, ma dead pixele na ekranie, jakieś 5 sztuk. Chcę replacement, not a repair. Order 45-7781.", 0, False),
    ("R18", "dostawca energii", "Przesyłam odczyt licznika na koniec miesiąca: 12 457 kWh. Pozdrawiam.", 1, False),
    ("R19", "sklep internetowy", "Brawo. Zamówiłem zielony, dostałem różowy. Pewnie uznaliście, że róż bardziej mi pasuje. Proszę o przysłanie tego, co zamówiłem.", 0, True),
    ("R20", "sklep AGD", "Kupiłem u Was pralkę rok temu i działa świetnie. Chciałem tylko zapytać, czy macie do niej zamienny filtr pompy.", 1, False),
    ("R21", "operator telekomunikacyjny", "W fakturze za sierpień naliczyliście mi 89 zł za roaming, a przez cały miesiąc nie wyjeżdżałem z Polski. Proszę o korektę i zwrot tej kwoty.", 0, False),
    ("R22", "ubezpieczyciel", "Chciałabym zgłosić szkodę z OC sprawcy: wczoraj ktoś uderzył w mój zaparkowany samochód. Jakie dokumenty są potrzebne?", 1, True),
    ("R23", "sklep internetowy", "Dzień dobry, kupiłech u wos ekspres do kawy i już po tydniu nie grzeje wody. Chca, coby mi to naprawić abo dać nowy.", 0, False),
    ("R24", "sklep internetowy", "Czy mogę zapłacić za zamówienie przy odbiorze? Nie mam karty.", 1, False),
    ("R25", "firma kurierska", "Paczka doszła zgnieciona, w środku rozbity wazon. Na zdjęciach widać uszkodzony karton. Domagam się odszkodowania za zniszczoną zawartość, 350 zł.", 0, False),
    ("R26", "sklep z porcelaną", "Zamówienie przyszło, jedna z filiżanek ma malutką rysę, ale nic nie szkodzi, nie chcę nic odsyłać ani wymieniać. Chciałem tylko dać znać. Macie może spodki do kompletu?", 1, True),
    ("R27", "klub fitness", "Opłaciłem karnet na cały miesiąc, a basen jest zamknięty od dwóch tygodni z powodu awarii. Uważam, że należy mi się obniżka za ten miesiąc.", 0, False),
    ("R28", "bank", "Proszę o przesłanie zaświadczenia o saldzie kredytu hipotecznego na potrzeby urzędu skarbowego.", 1, False),
    ("R29", "sklep internetowy", "ładowarka nie dziala od nowosci. chce zwrot kasy. zam 55129", 0, False),
    ("R30", "operator telekomunikacyjny", "Zmieniłem numer telefonu kontaktowego, nowy to 601 223 445. Proszę zaktualizować dane w systemie.", 1, False),
    ("R31", "sklep meblowy", "Czy byłaby możliwość obniżenia ceny sofy? Przyszła z przetarciem na oparciu, ale nie chcę jej odsyłać, bo poza tym bardzo nam się podoba.", 0, True),
    ("R32", "sklep internetowy", "Zmieniłem zdanie co do zamówienia 77002, które jeszcze nie zostało wysłane. Czy mogę je anulować?", 1, False),
    ("R33", "serwis rezerwacji hoteli", "Pokój zarezerwowany jako „z widokiem na morze” miał widok na parking i śmietniki. Oczekuję zwrotu różnicy w cenie.", 0, False),
    ("R34", "sklep internetowy", "Wow, dostawa w 12 godzin, jesteście jacyś szaleni :) Dzięki! A tak przy okazji: jak zdobyć kod rabatowy na kolejne zakupy?", 1, True),
    ("R35", "dostawca energii", "Dostałam rachunek za prąd na 1 870 zł, a zwykle płacę około 200 zł. Licznik pokazuje inny stan niż na fakturze (zdjęcie w załączniku). Proszę o korektę faktury.", 0, False),
    ("R36", "sklep internetowy", "Czy wysyłacie też do Niemiec? Brat mieszka w Berlinie i chciałbym mu coś zamówić.", 1, False),
    ("R37", "dostawca oprogramowania (SaaS)", "Hi team, od 3 dni Wasza aplikacja crashes przy eksporcie do PDF. Płacimy za plan Business i to jest core feature. Chcemy credit za ten okres albo fix ASAP.", 0, False),
    ("R38", "bank", "Jaka jest aktualnie oprocentowanie lokaty 6-miesięcznej?", 1, False),
    ("R39", "sklep meblowy", "Chciałbym zamówić jeszcze dwa takie same fotele. Aha, i przy okazji: w tym, który już mam, po miesiącu pękł podłokietnik, więc proszę też o wymianę tej części.", 0, True),
    ("R40", "operator telekomunikacyjny", "Pani na infolinii była wczoraj bardzo niemiła i rzuciła słuchawką. Uważam, że powinni Państwo o tym wiedzieć.", 1, True),
]

# (id, text, gold, tricky)   gold = index into O_D
D = [
    ("D11", "Odkurzacz przestał ssać po dwóch tygodniach. Chcę go oddać na gwarancję.", 0, False),
    ("D12", "Paczka dotarła na czas, dzięki, ale w środku były tylko 3 z 4 zamówionych talerzy, a na fakturze są cztery.", 0, True),
    ("D13", "Kurtka po pierwszym praniu zrobiła się o dwa rozmiary mniejsza, choć prałam zgodnie z metką. I want my money back.", 0, False),
    ("D14", "Genialny produkt, ta lampka. Świeciła aż całe trzy dni. I co teraz?", 0, True),
    ("D15", "Dostałem telefon z porysowanym ekranem, choć był zapakowany w folię. Proszę o wymianę.", 0, False),
    ("D16", "Smartwatch od nowości nie paruje się z telefonem. Próbowałem resetu, aktualizacji, wszystkiego. Jest wadliwy, chcę zwrot pieniędzy.", 0, True),
    ("D17", "Proszę o duplikat faktury za lipiec, oryginał zaginął.", 1, False),
    ("D18", "Karta została obciążona dwa razy za to samo zamówienie 44120.", 1, False),
    ("D19", "Zwrot za oddany towar miał być w 14 dni. Minął miesiąc, a pieniędzy nadal nie ma na koncie.", 1, True),
    ("D20", "Jak mogę zmienić metodę płatności za abonament z karty na przelew?", 1, False),
    ("D21", "Na fakturze jest zła nazwa firmy: powinno być „Nowak Budownictwo”, a jest „Nowak Budowa”. Proszę o korektę.", 1, False),
    ("D22", "halo, płace blikiem i ciągle wywala błąd transakcji, kasa się blokuje a zamówienie nie przechodzi", 1, True),
    ("D23", "Czy mogę zmienić paczkomat odbioru dla zamówienia 90921?", 2, False),
    ("D24", "Kurier miał przyjechać między 8 a 12, jest 16 i nikogo nie ma.", 2, False),
    ("D25", "Status mówi „doręczono”, ale paczki nie ma ani pod drzwiami, ani u sąsiadów.", 2, True),
    ("D26", "Ile trwa wysyłka do Czech?", 2, False),
    ("D27", "Proszę o dostarczenie paczki po 17, wcześniej jestem w pracy.", 2, False),
    ("D28", "Hej, tracking number nie działa na stronie przewoźnika, pisze „not found”. Where is my parcel?", 2, True),
    ("D29", "Nie przychodzi mi SMS z kodem do logowania w aplikacji.", 3, False),
    ("D30", "Jak skonfigurować skrzynkę pocztową w programie pocztowym? Podajecie gdzieś ustawienia serwera?", 3, False),
    ("D31", "Router co godzinę sam się restartuje, a dioda WAN miga na pomarańczowo.", 3, False),
    ("D32", "Zapomniałem hasła do panelu klienta, a link resetujący wygasa, zanim go kliknę.", 3, False),
    ("D33", "Strona wysypuje się przy dodawaniu produktów do koszyka, w każdej przeglądarce. Error 500.", 3, False),
    ("D34", "Przepraszam, że zawracam głowę, pewnie to coś banalnego, ale od aktualizacji telewizor nie widzi Wi-Fi. Mógłby ktoś pomóc?", 3, False),
    ("D35", "Czy macie ten ekspres w wersji srebrnej?", 4, False),
    ("D36", "Chciałbym zamówić 50 koszulek z nadrukiem logo firmy. Jaki jest czas realizacji i cena?", 4, False),
    ("D37", "Mój stary telefon się zepsuł i już go nie naprawiam. Szukam nowego do 1500 zł z dobrym aparatem, co polecacie?", 4, True),
    ("D38", "Czy jest możliwość przedłużenia umowy z nowym telefonem w promocji?", 4, False),
    ("D39", "Mamy u Was konto firmowe. Czy dostaniemy rabat, jeśli przejdziemy na roczną płatność za 30 stanowisk?", 4, True),
    ("D40", "Szukam prezentu dla taty, lubi wędkowanie. Macie jakieś zestawy do 300 zł?", 4, False),
]

# (id, context, text, gold, tricky)   gold: 0 = escalate
E = [
    ("E06", "sklep internetowy", "Jeżeli do końca tygodnia nie oddacie mi pieniędzy, składam pozew do sądu i zgłaszam sprawę do UOKiK.", 0, False),
    ("E07", "operator telekomunikacyjny", "Mam dość. Trzeci miesiąc płacę za usługę, która nie działa. Dzisiaj składam wypowiedzenie i idę do konkurencji, a znajomym powiem, żeby omijali Was szerokim łukiem!!!", 0, False),
    ("E08", "apteka internetowa", "Jestem po operacji, leżę w domu i nie mogę chodzić. Kurier zostawił paczkę z moimi lekami w punkcie odbioru 3 km ode mnie.", 0, False),
    ("E09", "operator telekomunikacyjny", "Moja mama ma demencję i przez telefon podpisała u Was jakąś umowę na trzy lata. Ona nawet nie wie, co to jest.", 0, False),
    ("E10", "sklep internetowy", "Z całym szacunkiem uprzejmie informuję, że mój pełnomocnik przygotował już wezwanie przedsądowe. Liczę jednak, że uda się tę sprawę załatwić polubownie.", 0, True),
    ("E11", "bank", "Ktoś ukradł mi telefon i widzę, że z mojego konta idą przelewy!!! Co mam robić??", 0, True),
    ("E12", "bank", "Właśnie pochowałam męża. Proszę mi powiedzieć, co zrobić z jego kontem, bo nie mam już siły dzwonić w dziesięć miejsc.", 0, False),
    ("E13", "dostawca oprogramowania (SaaS)", "Seriously, to już jest joke. Trzeci raz ta sama awaria. Cancel my subscription NOW albo idę z tym do prawnika.", 0, False),
    ("E14", "operator telekomunikacyjny", "Cudownie. Naprawdę. Czwarty tydzień bez internetu, a Wy mi wysyłacie ankietę satysfakcji. Właśnie szukam innego operatora.", 0, True),
    ("E15", "bank", "Straciłam pracę i nie mam z czego zapłacić raty. Boję się, że zabiorą mi mieszkanie. Proszę o pomoc.", 0, False),
    ("E16", "dostawca energii", "Nie widzę za dobrze, mam 79 lat, a litery w aplikacji są malutkie. Nie umiem zapłacić rachunku i dostałam już upomnienie.", 0, False),
    ("E17", "firma instalacyjna", "Wasz serwisant uszkodził mi ścianę przy montażu. Zgłaszam sprawę na policję i do ubezpieczyciela, a Was pozwę o odszkodowanie.", 0, False),
    ("E18", "operator telekomunikacyjny", "No ja już kurde nie wytrzymie. Pół roku się z Wami użeram, jutro idę do konkurencji i koniec, mom tego dość.", 0, False),
    ("E19", "dostawca energii", "Mój syn jest niepełnosprawny i korzysta w domu z respiratora, a Wy zapowiadacie wyłączenie prądu za zaległość. On bez tego umrze.", 0, False),
    ("E20", "sklep internetowy", "Dzień dobry, proszę o zmianę adresu korespondencyjnego na ul. Lipowa 3, 43-100 Tychy. Przy okazji: jeśli jeszcze raz naliczycie mi karę za nie moje opóźnienie, sprawę przejmie rzecznik konsumentów.", 0, True),
    ("E21", "bank", "Piszę do Was z płaczem. Oszuści podszyli się pod Wasz bank i wyczyścili mi konto, 40 tysięcy, oszczędności całego życia.", 0, False),
    ("E22", "operator telekomunikacyjny", "dość. rezygnuję. wypowiedzenie w załączniku.", 0, True),
    ("E23", "operator telekomunikacyjny", "Czy mogę zmienić termin płatności faktury z 10. na 20. dzień miesiąca?", 1, False),
    ("E24", "sklep internetowy", "Trochę słabo, że paczka spóźnia się już drugi dzień. Dajcie znać, kiedy będzie.", 1, False),
    ("E25", "operator telekomunikacyjny", "Poproszę o przesłanie regulaminu promocji „Jesień z internetem”.", 1, False),
    ("E26", "sklep internetowy", "Haha, jak mi nie przyślecie tego kuponu, to nasyłam na Was mojego prawnika, czyli kota :D A tak serio, gdzie wpisać kod rabatowy?", 1, True),
    ("E27", "operator telekomunikacyjny", "Nie działa mi internet od rana. Zrobiłem restart routera i dalej nic. Możecie sprawdzić?", 1, False),
    ("E28", "bank", "Moja babcia zawsze mówiła, że Wasz bank jest najlepszy, więc po jej śmierci trzy lata temu przeniosłem do Was konto :) Chciałbym teraz otworzyć lokatę.", 1, True),
    ("E29", "sklep internetowy", "Zamówienie przyszło niekompletne, brakuje ładowarki. Proszę o dosłanie.", 1, False),
    ("E30", "bank", "Meh, znowu update aplikacji i znowu muszę się logować od nowa. Kind of annoying. Da się to wyłączyć?", 1, False),
    ("E31", "operator telekomunikacyjny", "Proszę o informację, ile wynosi opłata za wcześniejsze rozwiązanie umowy.", 1, True),
    ("E32", "bank", "Dzień dobry, jestem nowym klientem i nie wiem, gdzie w aplikacji znaleźć numer mojego konta do przelewu.", 1, False),
    ("E33", "operator telekomunikacyjny", "Kiedy będzie dostępna nowa taryfa dla seniorów, o której była mowa w reklamie?", 1, False),
    ("E34", "ubezpieczyciel", "Jestem w ciąży i chciałabym zapytać, czy moje ubezpieczenie zdrowotne obejmuje opiekę okołoporodową.", 1, True),
    ("E35", "dostawca energii", "Faktura jest wyższa o 12 zł niż zwykle. Z czego to wynika?", 1, False),
    ("E36", "sklep internetowy", "Grr, trzeci raz dzwonię i nikt nie odbiera. Proszę o kontakt mailowy.", 1, False),
    ("E37", "bank", "Czy mogę dodać drugą osobę jako pełnomocnika do konta?", 1, False),
    ("E38", "operator telekomunikacyjny", "Mój pies zjadł kabel od routera :) Czy mogę kupić u Was nowy zasilacz?", 1, False),
    ("E39", "dostawca energii", "Proszę o potwierdzenie, że przelew za wrzesień dotarł.", 1, False),
    ("E40", "operator telekomunikacyjny", "Jak przenieść mój numer do Was z innej sieci?", 1, False),
]

# (id, rule, text, gold, tricky)   gold: 0 = complete
K = [
    ("K06", "A", "Zamówienie 70311. Czajnik nie wyłącza się automatycznie po zagotowaniu wody. Proszę o naprawę.", 0, False),
    ("K07", "A", "Zamówienie 70522. Toster przypala chleb nawet na najniższym poziomie. Prosze o zwrot pieniedzy.", 1, True),
    ("K08", "A", "Zamówienie 70688. Kurtka: zamek rozszedł się po tygodniu. Nie chcę zwrotu pieniędzy, wolę wymianę na nową.", 0, True),
    ("K09", "A", "Zamówienie 70901. Proszę o wymianę.", 1, False),
    ("K10", "A", "Numer zamówienia: 71004. Wada: w monitorze nie działa port HDMI. Żądanie: zwrot pieniędzy na rachunek 61 1090 1014 0000 0712 1981 2874.", 0, False),
    ("K11", "A", "Monitor z zamówienia z zeszłego tygodnia ma martwy piksel na środku ekranu. Proszę o wymianę na nowy.", 1, True),
    ("K12", "B", "Numer seryjny: SN-4471-XK-209. Data zakupu: 12.03.2026. Usterka: pralka nie odpompowuje wody, na wyświetlaczu błąd E21.", 0, False),
    ("K13", "B", "Kupiłem zmywarkę 5 maja tego roku, od wczoraj nie grzeje wody. Proszę o przyjęcie na gwarancję.", 1, False),
    ("K14", "B", "SN 88-2210-PL. Lodówka przestała chłodzić zamrażarkę. Proszę o szybki termin serwisu.", 1, False),
    ("K15", "B", "Dzień dobry, piekarnik (nr seryjny z tabliczki: BX7729310), kupiony 28.11.2025, przestał się nagrzewać powyżej 100 stopni.", 0, False),
    ("K16", "B", "Nr seryjny: TV-55-0091823, zakup 02.02.2026. Wszystko opisałem już w poprzednim mailu.", 1, True),
    ("K17", "C", "Numer klienta: 4402198. Nowy adres: ul. Klonowa 8/12, 44-100 Gliwice.", 0, False),
    ("K18", "C", "Numer klienta 4402771. Przeprowadzam się na ul. Brzozową 3 w Rybniku.", 1, True),
    ("K19", "C", "Proszę zmienić mój adres na: al. Jana Pawła II 14/5, 00-828 Warszawa. Z góry dzięki!", 1, False),
    ("K20", "C", "Hi, customer ID 4409930. Moving to: ul. Ogrodowa 22, 58-500 Jelenia Góra. Thanks!", 0, True),
    ("K21", "D", "Polisa OC/AC nr PL-2026-778120. Zdarzenie 14.09.2026 na parkingu przy ul. Zwycięstwa 10 w Gliwicach. Inny kierowca, cofając, uderzył w mój przedni zderzak. Numer rejestracyjny sprawcy: SG 4412K.", 0, False),
    ("K22", "D", "Polisa AC nr PL-2026-551903. 20.09.2026, ok. 18:00, ul. Leśna w Mikołowie. Sam wjechałem w słupek podczas parkowania: pęknięty tylny zderzak i lampa.", 0, True),
    ("K23", "D", "Polisa nr PL-2026-661200. 22.09.2026 na rondzie Ziętka w Katowicach inny samochód wjechał mi w bok i uszkodził przednie drzwi. Sprawca spisał ze mną oświadczenie.", 1, True),
    ("K24", "D", "Nr polisy PL-2026-990011. Zdarzenie 03.09.2026: grad uszkodził maskę i dach auta, jest kilkanaście wgnieceń.", 1, False),
    ("K25", "D", "Polisa PL-2026-114455. Data: 17.09.2026. Miejsce: skrzyżowanie ul. Mickiewicza i Słowackiego w Zabrzu. Opis: kierowca busa nie ustąpił mi pierwszeństwa, mam wgniecione lewe drzwi i błotnik. Sprawca: nr rej. SZ 90021.", 0, False),
    ("K26", "D", "Zdarzenie 11.09.2026, parking przy ul. Wolności 5 w Chorzowie. Ktoś otarł mi bok auta i odjechał, nie znam numeru. Rysa na całych prawych drzwiach.", 1, False),
    ("K27", "E", "Faktura FV/2026/08/0932. Błąd: zła ilość w pozycji 2 (jest 5 szt., powinno być 3 szt.). Proszę o korektę na 3 sztuki.", 0, False),
    ("K28", "E", "Faktura FV/2026/09/1204 ma błędny NIP. Poprawny NIP to 6312345678.", 1, True),
    ("K29", "E", "FV/2026/09/1188: błędny NIP nabywcy, poprawny to 6340198233. W załączniku wydruk z CEIDG.", 0, True),
    ("K30", "E", "Na fakturze jest zła nazwa ulicy: powinno być ul. Graniczna 4, a nie Graniczna 14. Proszę o korektę.", 1, False),
    ("K31", "E", "Faktura FV/2026/07/0555. Coś się nie zgadza z kwotą, proszę sprawdzić.", 1, False),
    ("K32", "E", "Dotyczy faktury FV/2026/09/0077: w danych nabywcy jest błędna nazwa „Kowalska Design”, poprawna to „Kowalska Design Studio Sp. z o.o.”.", 0, False),
    ("K33", "F", "Odstępuję od umowy, zamówienie 81230: sukienka czerwona rozm. 38 i pasek skórzany. Płaciłam kartą.", 0, True),
    ("K34", "F", "Odstępuję od umowy dla zamówienia 81455 (buty sportowe). Płaciłem przelewem.", 1, True),
    ("K35", "F", "Zamówienie 81502. Zwracam: słuchawki XR-200 i etui. Numer konta do zwrotu: 29 1050 1445 1000 0090 3031 2291.", 0, False),
    ("K36", "F", "Chcę zwrócić rzeczy z ostatniego zamówienia. Konto do zwrotu: 11 2490 0005 0000 4500 7654 3210.", 1, False),
    ("K37", "G", "System: CRM. Od poniedziałku rano nie da się zapisać nowego kontaktu: przycisk „Zapisz” nic nie robi i nie pojawia się żaden komunikat.", 0, True),
    ("K38", "G", "Aplikacja: moduł faktur w systemie ERP. Od wczoraj przy wystawianiu faktury wyskakuje błąd i nie da się jej zatwierdzić.", 1, True),
    ("K39", "G", "Program pocztowy od dziś od 9:00 nie wysyła maili, komunikat: „Błąd 0x800CCC0F: połączenie z serwerem zostało przerwane”.", 0, False),
    ("K40", "G", "Nic nie działa!!! Pomóżcie szybko, klienci czekają!", 1, False),
]

# (id, text, gold, tricky)   gold = index into O_S
S = [
    ("S01", "Dzień dobry, chciałabym zapytać o status zamówienia 55410. Dziękuję i pozdrawiam.", 0, False),
    ("S02", "Hej, czy da się zmienić kolor zamówionego kubka na niebieski? Jak nie, to nic nie szkodzi :)", 0, False),
    ("S03", "Paczka jeszcze nie doszła, ale spokojnie, rozumiem, że jest okres świąteczny. Dajcie znać, jak coś będzie wiadomo.", 0, True),
    ("S04", "Proszę o fakturę VAT do zamówienia 33218, dane firmy w załączniku.", 0, False),
    ("S05", "Uprzejmie informuję, że zamówiony produkt nie spełnia moich oczekiwań. Proszę o informację, jak mogę go odesłać.", 0, True),
    ("S06", "Dzięki za szybką odpowiedź! Wszystko już działa.", 0, False),
    ("S07", "Czy w sobotę też realizujecie wysyłki?", 0, False),
    ("S08", "Trochę mnie dziwi, że paczka idzie już piąty dzień, skoro obiecywaliście 48 godzin. Kiedy mogę się jej spodziewać?", 1, False),
    ("S09", "No niestety, znowu to samo: aplikacja sama mnie wylogowuje. Da się coś z tym zrobić?", 1, False),
    ("S10", "Super, że na infolinię można się dodzwonić tylko w godzinach mojej pracy ;) Jest może jakiś czat?", 1, True),
    ("S11", "Drugi raz proszę o tę samą korektę faktury. Liczę, że tym razem się uda.", 1, False),
    ("S12", "Hmm, trochę annoying, że każdy update resetuje mi ustawienia. Możecie to fixnąć?", 1, False),
    ("S13", "Rozumiem, że każdemu zdarzają się pomyłki, ale to już druga źle skompletowana paczka w tym miesiącu. Proszę o dosłanie brakującego produktu.", 1, True),
    ("S14", "Czekam na odpowiedź od tygodnia. Czy ktoś w ogóle czyta te maile?", 1, False),
    ("S15", "TO JUŻ JEST SKANDAL!!! Trzeci tydzień bez internetu i nikt nic nie robi! Mam Was serdecznie dość!", 2, False),
    ("S16", "Gratuluję, naprawdę. Czwarty raz przesuwacie montaż, a ja czwarty raz biorę wolne w pracy. Jesteście mistrzami. Żenada.", 2, True),
    ("S17", "Nie obchodzą mnie Wasze procedury. Oddajcie moje pieniądze, i to natychmiast, bo inaczej zobaczymy się w sądzie.", 2, False),
    ("S18", "This is ridiculous. Płacę za premium i od tygodnia nic nie działa. Absolutnie tragiczna obsługa, WTF.", 2, False),
    ("S19", "Szanowni Państwo, to moja siódma wiadomość w tej sprawie. Moja cierpliwość się skończyła. Oczekuję rozwiązania dzisiaj, w przeciwnym razie rezygnuję z Państwa usług.", 2, True),
    ("S20", "Ludzie, no weźcie się wreszcie ogarnijcie, bo mnie szlag trafi! Który to już raz, co?!", 2, False),
]

P_CO = "Wiadomość, która wpłynęła na skrzynkę firmy:"
P_CU = "Wiadomość, którą klient otrzymał i przekazał do działu bezpieczeństwa do weryfikacji:"
# (id, header, text, gold, tricky)   gold: 0 = scam / phishing
P = [
    ("P01", P_CU, "PaczkaPunkt: Twoja przesyłka została wstrzymana z powodu niedopłaty 1,99 zł. Opłać teraz: paczkapunkt-doplata.info/p/88213", 0, False),
    ("P02", P_CO, "Dzień dobry, tu Marek z działu IT Waszej centrali. Robimy pilną migrację kont, proszę odpisać z loginem i hasłem do panelu administratora do 15:00.", 0, False),
    ("P03", P_CO, "Pani Anno, jestem na spotkaniu i nie mogę rozmawiać. Proszę pilnie zrobić przelew 48 500 zł na nowe konto kontrahenta 12 1140 2004 0000 3102 4455 6677 i nikomu o tym nie mówić, to poufna transakcja. Prezes (wysłane z prywatnego adresu e-mail)", 0, False),
    ("P04", P_CO, "Informujemy, że z dniem dzisiejszym zmieniamy numer rachunku bankowego. Prosimy regulować faktury na nowe konto: 88 1020 1026 0000 0402 0311 5599. Stare konto zostało zamknięte. Dział Księgowości Hurt-Pol (wiadomość z adresu hurtpol.ksiegowosc@gmail.com; dotąd dostawca pisał z domeny hurtpol.pl)", 0, True),
    ("P05", P_CU, "Szanowny Kliencie, wykryliśmy podejrzane logowanie. W celu ochrony środków zaloguj się przez link https://bankpolny-weryfikacja.com i potwierdź dane karty.", 0, False),
    ("P06", P_CU, "Klient opisuje rozmowę telefoniczną: dzwonił „pracownik banku” i poprosił o zainstalowanie aplikacji do zdalnego pulpitu, żeby „zabezpieczyć konto przed hakerami”.", 0, False),
    ("P07", P_CU, "Kupujący z portalu ogłoszeniowego przysłał link „odbierz płatność za przedmiot”. Żeby dostać pieniądze, trzeba podać numer karty, datę ważności i kod CVV.", 0, False),
    ("P08", P_CO, "Hi, your office license expires today. Kliknij tutaj, aby odnowić licencję i uniknąć blokady wszystkich skrzynek: office-renew-license.net/login", 0, False),
    ("P09", P_CO, "Dzień dobry, w załączniku przesyłamy fakturę za wpis Państwa firmy do Centralnego Rejestru Firm i Przedsiębiorców na kwotę 1 290 zł. Prosimy o płatność w ciągu 3 dni.", 0, True),
    ("P10", P_CU, "Gratulacje! Jako lojalny klient sieci wylosowałeś nowy smartfon. Aby odebrać nagrodę, opłać tylko koszt wysyłki 9,99 zł pod linkiem nagroda-dla-ciebie.top", 0, False),
    ("P11", P_CU, "KurierPlus: Twoja paczka 0123456789 zostanie doręczona dziś w godz. 10:00-13:00. Kurier: 600 100 200. Śledzenie przesyłki w aplikacji KurierPlus.", 1, True),
    ("P12", P_CU, "Bank Polny: przypominamy, że nigdy nie prosimy o podanie hasła ani kodów SMS. Zaktualizuj aplikację do wersji 8.2 w oficjalnym sklepie z aplikacjami.", 1, True),
    ("P13", P_CO, "Dzień dobry, proszę o zmianę numeru konta do zwrotu na 34 1140 2004 0000 3502 7777 8888, bo poprzednie zamknąłem. Zamówienie 61402, Jan Kowalski (wiadomość z adresu e-mail przypisanego do konta klienta).", 1, True),
    ("P14", P_CO, "W załączniku faktura FV/2026/09/231 za dostawę kartonów z 22.09, zgodnie z zamówieniem nr ZK-1182. Termin płatności 14 dni, konto bez zmian.", 1, False),
    ("P15", P_CU, "„Otrzymaliśmy prośbę o zresetowanie hasła do Twojego konta. Jeśli to Ty, wpisz kod 482913 w aplikacji. Jeśli nie, zignoruj tę wiadomość.” Klient dopisał: minutę wcześniej sam kliknąłem „nie pamiętam hasła”.", 1, True),
    ("P16", P_CO, "Dzień dobry, czy możecie przesłać mi ofertę na 200 kubków z nadrukiem naszego logo?", 1, False),
    ("P17", P_CU, "NetFala: Twoja faktura za wrzesień na kwotę 65,00 zł jest dostępna w aplikacji NetFala. Termin płatności: 15.10.2026.", 1, False),
    ("P18", P_CO, "Dzień dobry, jestem Waszym klientem. Dostałem SMS, że moja paczka od Was czeka na dopłatę. Czy to na pewno od Was? Nie klikałem linku.", 1, True),
    ("P19", P_CO, "Pilne! Proszę o natychmiastowe zablokowanie mojej karty, zgubiłem portfel. Numer klienta 55012388.", 1, True),
    ("P20", P_CU, "Sklep Domowo: -20% na całą kolekcję jesienną do niedzieli. Szczegóły w sklepie. Rezygnacja z SMS: odpisz STOP.", 1, False),
]


def main():
    items = [json.loads(l) for l in EXP01.read_text().splitlines() if l.strip()]
    for it in items:
        it["subset"] = "exp01"
        it["author_gold"] = it["gold"]
    new = []
    for i, ctx, txt, g, tr in R:
        new.append(dict(id=i, type="noul", tricky=tr, state=f"Wiadomość od klienta ({ctx}):\n{txt}",
                        question=Q_R, options=O_R, gold=g))
    for i, txt, g, tr in D:
        new.append(dict(id=i, type="choice", tricky=tr, state=f"Wiadomość od klienta:\n{txt}",
                        question=Q_D, options=O_D, gold=g))
    for i, ctx, txt, g, tr in E:
        new.append(dict(id=i, type="noul", tricky=tr, state=f"Wiadomość od klienta ({ctx}):\n{txt}",
                        question=Q_E, options=O_E, gold=g))
    for i, rule, txt, g, tr in K:
        new.append(dict(id=i, type="noul", tricky=tr, state=f"{K_HEAD[rule]}\n{txt}",
                        question=f"Czy zgłoszenie jest kompletne? Reguła: {RULES[rule]}", options=O_K, gold=g,
                        rule=rule))
    for i, txt, g, tr in S:
        new.append(dict(id=i, type="choice", tricky=tr, state=f"Wiadomość od klienta:\n{txt}",
                        question=Q_S, options=O_S, gold=g))
    for i, head, txt, g, tr in P:
        new.append(dict(id=i, type="noul", tricky=tr, state=f"{head}\n{txt}", question=Q_P, options=O_P, gold=g))
    for it in new:
        it["subset"] = "new"
        it["author_gold"] = it["gold"]
    for it in items:
        if it["id"].startswith("K"):
            it["rule"] = "A"
            assert it["question"] == f"Czy zgłoszenie jest kompletne? Reguła: {RULES['A']}"
    allit = items + new
    ids = [it["id"] for it in allit]
    assert len(ids) == len(set(ids)), "duplicate ids"
    order = "RDEKSP"
    allit.sort(key=lambda it: (order.index(it["id"][0]), int(it["id"][1:])))
    (HERE / "decisions.jsonl").write_text("".join(json.dumps(it, ensure_ascii=False) + "\n" for it in allit))
    from collections import Counter
    print(len(allit), Counter(it["id"][0] for it in allit))
    print("gold:", {c: Counter(it["gold"] for it in allit if it["id"][0] == c) for c in order})
    print("tricky:", sum(it["tricky"] for it in allit))


if __name__ == "__main__":
    main()
