# Domain: uczelnia / administracja studencka (university administration). Hand-written items, fictional people.

_TYPE_Q = ("Jakiego rodzaju podanie złożył student? Rodzaje: urlop dziekański = przerwa w studiach z zachowaniem "
           "praw studenta; wznowienie studiów = powrót na studia osoby wcześniej skreślonej z listy studentów; "
           "zmiana promotora = zmiana opiekuna pracy dyplomowej; przeniesienie = przejście z innej uczelni lub "
           "innego kierunku na ten kierunek; warunkowy wpis = wpis na kolejny semestr mimo niezaliczonego przedmiotu.")
_TYPE_OPTS = ["Urlop dziekański", "Wznowienie studiów", "Zmiana promotora", "Przeniesienie", "Warunkowy wpis"]
_TYPE_KEYS = ["urlop_dziekanski", "wznowienie", "zmiana_promotora", "przeniesienie", "warunkowy_wpis"]

_URG_Q = ("Jaka jest pilność sprawy studenta? Poziomy liczone według najbliższego terminu podanego w sprawie, "
          "w dniach kalendarzowych od dziś: 1 = niska (sprawa bez żadnego terminu, pytanie informacyjne); "
          "2 = średnia (termin za więcej niż 7 dni); 3 = wysoka (termin za 2 do 7 dni); "
          "4 = krytyczna (termin mija dziś lub jutro).")
_URG_OPTS = ["1 - niska", "2 - średnia", "3 - wysoka", "4 - krytyczna"]
_URG_KEYS = ["u1_niska", "u2_srednia", "u3_wysoka", "u4_krytyczna"]

ITEMS = [
    dict(id="EDU01", type="noul", rule_based=True, tricky=False,
         state="Dziś jest piątek, 2026-10-16.\nDziekanat, wniosek złożony osobiście dziś przez: Jan Testowy, "
               "nr albumu 000000.\nPrzedmiot: urlop dziekański na semestr zimowy 2026/2027. Semestr zimowy rozpoczął "
               "się w czwartek, 2026-10-01.",
         question="Czy wniosek o urlop dziekański złożono w terminie? Reguła regulaminu: wniosek składa się nie później "
                  "niż 14 dni od rozpoczęcia semestru; termin liczy się od dnia następującego po dniu rozpoczęcia "
                  "semestru; jeżeli ostatni dzień terminu przypada w sobotę, niedzielę lub dzień ustawowo wolny od "
                  "pracy, termin upływa w najbliższy dzień roboczy.",
         options=["Tak, w terminie", "Nie, po terminie"], gold=1),
    dict(id="EDU02", type="noul", rule_based=True, tricky=True,
         state="Dziś jest poniedziałek, 2026-10-12.\nWniosek o stypendium rektora, Anna Przykładowa, 3. rok.\nŚrednia ocen z roku 2025/2026: 4,50. "
               "Punkty ECTS uzyskane w roku 2025/2026: 60. Wszystkie przedmioty zaliczone w pierwszym terminie, "
               "bez warunkowego wpisu.",
         question="Czy studentka spełnia warunki stypendium rektora? Reguła: stypendium przysługuje, gdy (1) średnia "
                  "ocen z poprzedniego roku akademickiego wynosi co najmniej 4,50, (2) student uzyskał w tym roku co "
                  "najmniej 60 ECTS i (3) nie miał w tym roku warunkowego wpisu.",
         options=["Tak, spełnia warunki", "Nie, nie spełnia warunków"], gold=0),
    dict(id="EDU03", type="noul", rule_based=True, tricky=False,
         state="Wniosek o stypendium socjalne, Marek Fikcyjny.\nGospodarstwo domowe: student, matka, ojciec, "
               "młodsza siostra (łącznie 4 osoby). Łączny miesięczny dochód netto rodziny wykazany we wniosku: "
               "6 150,00 zł.",
         question="Czy student spełnia kryterium dochodowe stypendium socjalnego? Reguła: miesięczny dochód netto na "
                  "osobę w rodzinie (łączny dochód podzielony przez liczbę członków rodziny wymienionych we wniosku) "
                  "nie może być wyższy niż 1 500,00 zł.",
         options=["Tak, spełnia kryterium", "Nie, nie spełnia kryterium"], gold=1),
    dict(id="EDU04", type="noul", rule_based=True, tricky=False,
         state="Wniosek o zmianę promotora, Katarzyna Testowa, 2. rok studiów magisterskich.\nZałączniki: "
               "uzasadnienie (1 strona), pisemna zgoda nowej promotorki dr Ewy Przykładowej, podpis studentki. "
               "Brak zgody dotychczasowego promotora. Stan pracy: napisane 2 z 4 rozdziałów, praca nie była "
               "przesyłana do systemu antyplagiatowego.",
         question="Czy wniosek jest kompletny? Reguła: wniosek o zmianę promotora jest kompletny, gdy zawiera "
                  "(1) uzasadnienie, (2) pisemną zgodę nowego promotora i (3) podpis studenta. Zgoda dotychczasowego "
                  "promotora nie jest wymagana, chyba że praca została już przesłana do systemu antyplagiatowego.",
         options=["Tak, wniosek jest kompletny", "Nie, wniosek jest niekompletny"], gold=0),
    dict(id="EDU05", type="noul", rule_based=True, tricky=False,
         state="Dziś jest poniedziałek, 2026-10-19.\nPodanie o wznowienie studiów, Piotr Przykładowy. Decyzja o "
               "skreśleniu z listy studentów: 2025-03-10. Powód skreślenia: rezygnacja w trakcie 1. semestru, przed "
               "sesją; student nie zaliczył żadnego semestru.",
         question="Czy wznowienie studiów jest możliwe? Reguła: wznowienie jest możliwe, gdy (1) od daty decyzji "
                  "o skreśleniu nie minęły więcej niż 2 lata i (2) student zaliczył przed skreśleniem co najmniej "
                  "pierwszy semestr studiów.",
         options=["Tak, wznowienie jest możliwe", "Nie, wznowienie nie jest możliwe"], gold=1),
    dict(id="EDU06", type="noul", rule_based=False, tricky=True,
         state="E-mail do prowadzącego:\nSzanowny Panie Doktorze, absolutnie nie proszę o żadne ulgi ani wyjątki. "
               "Chciałbym tylko zapytać, czy byłoby możliwe, żebym oddał projekt zaliczeniowy tydzień później niż "
               "wyznaczony termin, bo w tym tygodniu mam praktyki. Z wyrazami szacunku, Tomasz Testowy.",
         question="Czy student prosi o przedłużenie terminu, czyli o zgodę na oddanie pracy lub zaliczenie później "
                  "niż w wyznaczonym terminie?",
         options=["Tak, prosi o przedłużenie", "Nie, nie prosi o przedłużenie"], gold=0),
    dict(id="EDU07", type="noul", rule_based=False, tricky=False,
         state="Wiadomość do dziekanatu:\nDzień dobry, w systemie dziekanatowym mam wpisaną ocenę 3,0 z Analizy "
               "matematycznej, a prowadzący potwierdził mi mailem (w załączniku), że wystawił 4,0. Proszę o "
               "sprawdzenie. Julia Fikcyjna, nr albumu 000000.",
         question="Czy studentka zgłasza błąd wpisu w systemie, czyli ocena widoczna w systemie różni się od oceny "
                  "faktycznie wystawionej przez prowadzącego?",
         options=["Tak, zgłasza błąd wpisu", "Nie, nie zgłasza błędu wpisu"], gold=0),
    dict(id="EDU08", type="noul", rule_based=False, tricky=False,
         state="Wiadomość do prodziekana:\nDzień dobry, chciałam podziękować dr. Adamowi Przykładowemu za świetnie "
               "prowadzone zajęcia z Ekonometrii, wszystko było jasno wytłumaczone. Przy okazji pytanie: kiedy "
               "zostanie ogłoszony termin egzaminu poprawkowego? Pozdrawiam, Monika Testowa.",
         question="Czy wiadomość jest skargą na prowadzącego, czyli czy studentka zarzuca prowadzącemu naruszenie "
                  "zasad lub niewłaściwe zachowanie?",
         options=["Tak, to skarga", "Nie, to nie jest skarga"], gold=1),
    dict(id="EDU09", type="choice", rule_based=False, tricky=False,
         state="Podanie do dziekana:\nW lutym 2026 zostałem skreślony z listy studentów z powodu niezaliczenia "
               "semestru. Teraz sytuacja się ustabilizowała i chciałbym wrócić na studia od semestru letniego, na ten "
               "sam kierunek. Łukasz Fikcyjny.",
         question=_TYPE_Q, options=_TYPE_OPTS, keys=_TYPE_KEYS, gold=1),
    dict(id="EDU10", type="choice", rule_based=False, tricky=True,
         state="Podanie do dziekana:\nNie chodzi mi o urlop ani o przerwę, chcę normalnie studiować dalej. Proszę "
               "o zgodę na kontynuowanie nauki na 3. semestrze, mimo że nie zaliczyłam Statystyki z 2. semestru. "
               "Przedmiot powtórzę w tym roku. Natalia Przykładowa.",
         question=_TYPE_Q, options=_TYPE_OPTS, keys=_TYPE_KEYS, gold=4),
    dict(id="EDU11", type="choice", rule_based=False, tricky=False,
         state="Podanie do dziekana:\nMój promotor dr Jan Testowy wyjeżdża na roczny staż zagraniczny. Opiekę nad "
               "moją pracą magisterską zgodziła się przejąć dr Anna Fikcyjna. Proszę o zatwierdzenie tej zmiany. "
               "Karol Przykładowy.",
         question=_TYPE_Q, options=_TYPE_OPTS, keys=_TYPE_KEYS, gold=2),
    dict(id="EDU12", type="choice", rule_based=False, tricky=False,
         state="Podanie do dziekana:\nStudiuję obecnie informatykę na innej uczelni (Uczelnia Testowa w Testowie), "
               "mam zaliczone 2 semestry. Ze względu na przeprowadzkę chciałbym kontynuować studia na Państwa "
               "kierunku od 3. semestru. Oskar Fikcyjny.",
         question=_TYPE_Q, options=_TYPE_OPTS, keys=_TYPE_KEYS, gold=3),
    dict(id="EDU13", type="choice", rule_based=False, tricky=False,
         state="Podanie do dziekana:\nZe względu na konieczność opieki nad ciężko chorym ojcem proszę o przerwę "
               "w studiach na semestr zimowy 2026/2027, z zachowaniem praw studenta. Zuzanna Testowa.",
         question=_TYPE_Q, options=_TYPE_OPTS, keys=_TYPE_KEYS, gold=0),
    dict(id="EDU14", type="score", rule_based=False, tricky=False,
         state="Dziś jest poniedziałek, 2026-10-05.\nPytanie przez formularz: Dzień dobry, kiedy mniej więcej będą "
               "znane terminy sesji zimowej? Pytam z ciekawości, żeby coś zaplanować. Adam Fikcyjny.",
         question=_URG_Q, options=_URG_OPTS, keys=_URG_KEYS, gold=0),
    dict(id="EDU15", type="score", rule_based=False, tricky=False,
         state="Dziś jest poniedziałek, 2026-10-12.\nE-mail: Dzień dobry, składam wniosek o stypendium socjalne, "
               "termin mija w czwartek, 2026-10-15. Brakuje mi zaświadczenia z dziekanatu o statusie studenta, czy "
               "mogę je odebrać? Ewa Przykładowa.",
         question=_URG_Q, options=_URG_OPTS, keys=_URG_KEYS, gold=2),
    dict(id="EDU16", type="score", rule_based=False, tricky=True,
         state="Dziś jest poniedziałek, 2026-10-26.\nE-mail z tematem: PILNE!!! BARDZO PILNE!!!\nPotrzebuję "
               "zaświadczenia o studiowaniu w języku angielskim do wniosku o wizę, termin złożenia wniosku mam "
               "2026-11-20. Proszę o szybką odpowiedź!!! Michał Testowy.",
         question=_URG_Q, options=_URG_OPTS, keys=_URG_KEYS, gold=1),
    dict(id="EDU17", type="score", rule_based=False, tricky=True,
         state="Dziś jest czwartek, 2026-10-22.\nCzat z dziekanatem: hej, takie pytanko bez spiny, jutro mija "
               "ostatni dzień na wpłatę za powtarzanie przedmiotu, a nie widzę nigdzie numeru konta. Jak nie wpłacę, "
               "to podobno skreślenie. Da się podesłać? Kuba Fikcyjny.",
         question=_URG_Q, options=_URG_OPTS, keys=_URG_KEYS, gold=3),
]
