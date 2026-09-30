# Domain: moderacja e-commerce / marketplace (listing moderation, buyer protection). Hand-written, fictional.

_PROT_RULE = ("Reguła Ochrony Kupującego: spór jest objęty ochroną, gdy spełnione są łącznie warunki: (1) zakup "
              "opłacono przez system płatności platformy; (2) wartość zakupu nie przekracza 5 000,00 zł; (3) przyczyną "
              "sporu jest nieotrzymanie przedmiotu albo przedmiot istotnie niezgodny z opisem (zmiana zdania kupującego "
              "nie jest objęta ochroną); (4) spór zgłoszono w terminie: przy niezgodności z opisem najpóźniej 14. dnia "
              "od doręczenia przesyłki, przy nieotrzymaniu przedmiotu najpóźniej 30. dnia od daty zakupu; dni "
              "kalendarzowe liczy się od dnia następującego po doręczeniu lub zakupie.")

_RULE_Q = ("Który punkt regulaminu serwisu narusza ogłoszenie? Punkty: brak naruszenia = ogłoszenie zgodne "
           "z regulaminem; przedmiot zakazany = broń i amunicja, leki na receptę, narkotyki, materiały wybuchowe; "
           "dane kontaktowe = numer telefonu, e-mail, konto w komunikatorze lub numer konta w opisie, w dowolnym "
           "zapisie; fałszywy stan = stan \"nowy\" przy przedmiocie używanym; podróbka = przedmiot oferowany jako "
           "produkt marki, gdy sam opis wskazuje, że to replika lub kopia; przynęta cenowa = cena w ogłoszeniu "
           "niższa niż cena, za którą sprzedający faktycznie sprzedaje przedmiot z tytułu. Ogłoszenie narusza "
           "co najwyżej jeden punkt.")
_RULE_OPTS = ["Brak naruszenia", "Przedmiot zakazany", "Dane kontaktowe", "Fałszywy stan", "Podróbka",
              "Przynęta cenowa"]
_RULE_KEYS = ["brak_naruszenia", "przedmiot_zakazany", "dane_kontaktowe", "falszywy_stan", "podrobka",
              "przyneta_cenowa"]

_SEV_Q = ("Jaka jest waga naruszenia? Poziomy: 1 = niska (dane kontaktowe w opisie bez wezwania do płatności poza "
          "platformą, błędna kategoria); 2 = średnia (wprowadzenie w błąd co do stanu lub ceny, np. fałszywy stan "
          "\"nowy\", przynęta cenowa); 3 = wysoka (podróbka, naruszenie praw do marki); 4 = krytyczna (przedmiot "
          "zakazany albo wezwanie kupującego do zapłaty poza systemem płatności platformy). Jeśli pasuje kilka poziomów, "
          "wybierz najwyższy.")
_SEV_OPTS = ["1 - niska", "2 - średnia", "3 - wysoka", "4 - krytyczna"]
_SEV_KEYS = ["w1_niska", "w2_srednia", "w3_wysoka", "w4_krytyczna"]

ITEMS = [
    dict(id="ECM01", type="noul", rule_based=True, tricky=True,
         state="Zgłoszenie sporu nr SPR-0000-101, złożone w piątek, 2026-10-16.\nKupujący: Jan Testowy. Przedmiot: "
               "rower elektryczny, wartość zakupu 5 000,00 zł, zapłacono przez system płatności platformy. Przesyłkę "
               "doręczono w piątek, 2026-10-02. Opis: \"bateria 500 Wh, zasięg 80 km\"; kupujący przesłał zdjęcie "
               "tabliczki baterii 250 Wh.",
         question="Czy spór jest objęty Ochroną Kupującego? " + _PROT_RULE,
         options=["Tak, objęty ochroną", "Nie, nieobjęty ochroną"], gold=0),
    dict(id="ECM02", type="noul", rule_based=True, tricky=False,
         state="Zgłoszenie sporu nr SPR-0000-102, złożone w środę, 2026-10-14.\nKupująca: Anna Przykładowa. "
               "Przedmiot: kurtka, 320 zł, zapłacono przez platformę, doręczona 2026-10-12. Uzasadnienie: \"Kurtka "
               "jest dokładnie taka jak w opisie i na zdjęciach, ale na żywo kolor mi się nie podoba, chcę oddać.\"",
         question="Czy spór jest objęty Ochroną Kupującego? " + _PROT_RULE,
         options=["Tak, objęty ochroną", "Nie, nieobjęty ochroną"], gold=1),
    dict(id="ECM03", type="noul", rule_based=True, tricky=False,
         state="Zgłoszenie sporu nr SPR-0000-103, złożone w poniedziałek, 2026-10-19.\nKupujący: Marek Fikcyjny. "
               "Przedmiot: konsola do gier, 1 400 zł, zakup 2026-10-05. Sprzedający poprosił w wiadomości o przelew "
               "bezpośrednio na swoje konto bankowe i kupujący tak zapłacił. Przesyłka do dziś nie dotarła, sprzedający "
               "nie odpisuje.",
         question="Czy spór jest objęty Ochroną Kupującego? " + _PROT_RULE,
         options=["Tak, objęty ochroną", "Nie, nieobjęty ochroną"], gold=1),
    dict(id="ECM04", type="noul", rule_based=True, tricky=False,
         state="Zgłoszenie sporu nr SPR-0000-104, złożone w czwartek, 2026-10-29.\nKupująca: Ewa Testowa. "
               "Przedmiot: ekspres do kawy, 890 zł, zapłacono przez platformę w poniedziałek, 2026-09-28. Przesyłka "
               "nie dotarła, status śledzenia nie zmienia się od 2026-09-30.",
         question="Czy spór jest objęty Ochroną Kupującego? " + _PROT_RULE,
         options=["Tak, objęty ochroną", "Nie, nieobjęty ochroną"], gold=1),
    dict(id="ECM05", type="noul", rule_based=True, tricky=False,
         state="Zgłoszenie sporu nr SPR-0000-105, złożone w poniedziałek, 2026-10-26.\nKupujący: Tomasz Przykładowy. "
               "Przedmiot: laptop, 1 250 zł, zapłacono przez platformę, doręczony w poniedziałek, 2026-10-19. Opis "
               "ogłoszenia: \"w pełni sprawny\". Kupujący: laptop nie włącza się, nagranie z próby uruchomienia "
               "w załączniku.",
         question="Czy spór jest objęty Ochroną Kupującego? " + _PROT_RULE,
         options=["Tak, objęty ochroną", "Nie, nieobjęty ochroną"], gold=0),
    dict(id="ECM06", type="noul", rule_based=False, tricky=True,
         state="Ogłoszenie: Rower szosowy, rama aluminiowa 56 cm, stan: używany.\nOpis: Rower po jednym sezonie, "
               "regularnie serwisowany. Numer seryjny ramy 0000-1234-5678 (widoczny na zdjęciu nr 4) do sprawdzenia "
               "w bazie rowerów kradzionych. Kontakt tylko przez czat serwisu.",
         question="Czy ogłoszenie zawiera dane kontaktowe sprzedającego, czyli numer telefonu, adres e-mail, nazwę "
                  "konta w komunikatorze lub numer konta bankowego, w dowolnym zapisie?",
         options=["Tak, zawiera dane kontaktowe", "Nie, nie zawiera danych kontaktowych"], gold=1),
    dict(id="ECM07", type="noul", rule_based=False, tricky=False,
         state="Ogłoszenie: Pamiątka po dziadku - amunicja 9 mm, 50 szt.\nOpis: Znalazłem przy porządkowaniu "
               "strychu, oryginalne pudełko, stan kolekcjonerski. Tylko odbiór osobisty w Testowie, cena 150 zł.",
         question="Czy ogłoszenie dotyczy przedmiotu zakazanego, czyli broni, amunicji, leków na receptę, narkotyków "
                  "lub materiałów wybuchowych?",
         options=["Tak, przedmiot zakazany", "Nie, przedmiot dozwolony"], gold=0),
    dict(id="ECM08", type="noul", rule_based=False, tricky=True,
         state="Ogłoszenie: Opony zimowe 205/55 R16, komplet 4 szt. - 150 zł\nOpis: Bieżnik 7 mm, bez napraw. "
               "Cena 150 zł dotyczy 1 sztuki, za komplet 600 zł. Nie sprzedaję pojedynczo, tylko cały komplet.",
         question="Czy ogłoszenie stosuje przynętę cenową, czyli cena podana w ogłoszeniu jest niższa niż cena, za "
                  "którą sprzedający faktycznie sprzedaje przedmiot opisany w tytule?",
         options=["Tak, przynęta cenowa", "Nie, cena jest rzetelna"], gold=0),
    dict(id="ECM09", type="choice", rule_based=False, tricky=False,
         state="Ogłoszenie: Rower miejski damski, stan: używany, 450 zł.\nOpis: Sprawny, nowe opony, koszyk gratis. "
               "Szybciej się dogadamy telefonicznie: pięć-zero-zero, zero-zero-zero, zero-zero-zero.",
         question=_RULE_Q, options=_RULE_OPTS, keys=_RULE_KEYS, gold=2),
    dict(id="ECM10", type="choice", rule_based=False, tricky=False,
         state="Ogłoszenie: Buty do biegania rozmiar 42, stan: nowy, 180 zł.\nOpis: Założone tylko dwa razy na "
               "krótkie wybieganie, prawie bez śladów użycia, bez pudełka.",
         question=_RULE_Q, options=_RULE_OPTS, keys=_RULE_KEYS, gold=3),
    dict(id="ECM11", type="choice", rule_based=False, tricky=True,
         state="Ogłoszenie: Laptop 15\" - 300 zł!!! okazja\nStan: uszkodzony. Opis: Nie włącza się, uszkodzona płyta "
               "główna, sprzedaję na części. Matryca i klawiatura sprawne. Zdjęcia własne, płatność przez serwis, "
               "wysyłka lub odbiór.",
         question=_RULE_Q, options=_RULE_OPTS, keys=_RULE_KEYS, gold=0),
    dict(id="ECM12", type="choice", rule_based=False, tricky=False,
         state="Ogłoszenie: Telewizor 55\" 4K - 1 zł\nOpis: Stan bardzo dobry, pilot w zestawie. Cena 1 zł tylko po "
               "to, żeby ogłoszenie było wyżej w wynikach, prawdziwa cena 2 400 zł, bez negocjacji.",
         question=_RULE_Q, options=_RULE_OPTS, keys=_RULE_KEYS, gold=5),
    dict(id="ECM13", type="choice", rule_based=False, tricky=False,
         state="Ogłoszenie: Antybiotyk - zostało pół opakowania, 30 zł\nOpis: Kupiony w aptece na receptę, termin "
               "ważności do 2027 r., szkoda wyrzucić. Wysyłka listem.",
         question=_RULE_Q, options=_RULE_OPTS, keys=_RULE_KEYS, gold=1),
    dict(id="ECM14", type="choice", rule_based=False, tricky=False,
         state="Ogłoszenie: Zegarek Chronaux Marinier - 390 zł, stan: nowy\nOpis: Jakość 1:1 z oryginałem, nie do "
               "odróżnienia, logo i grawer jak w oryginale marki Chronaux. Nowy, nieużywany, w pudełku.",
         question=_RULE_Q, options=_RULE_OPTS, keys=_RULE_KEYS, gold=4),
    dict(id="ECM15", type="score", rule_based=False, tricky=True,
         state="Ogłoszenie: Kurtka zimowa męska L, stan: używany, 220 zł.\nOpis: Bardzo ciepła, noszona jeden sezon. "
               "Żeby nie płacić prowizji serwisowi, uprzejmie proszę o przelew bezpośrednio na moje konto "
               "00 0000 0000 0000 0000 0000 0000, wtedy odejmę 20 zł. Dziękuję i pozdrawiam serdecznie!",
         question=_SEV_Q, options=_SEV_OPTS, keys=_SEV_KEYS, gold=3),
    dict(id="ECM16", type="score", rule_based=False, tricky=False,
         state="Ogłoszenie: Fotelik rowerowy dla dziecka, stan: nowy, 150 zł.\nOpis: Używany przez jeden sezon, "
               "drobne otarcia na pasach. Płatność przez serwis.",
         question=_SEV_Q, options=_SEV_OPTS, keys=_SEV_KEYS, gold=1),
    dict(id="ECM17", type="score", rule_based=False, tricky=False,
         state="Ogłoszenie: Stolik kawowy drewniany, stan: używany, 90 zł.\nOpis: Odbiór osobisty w Testowie, "
               "w sprawie terminu odbioru proszę dzwonić: 000-000-000. Płatność przy odbiorze przez aplikację serwisu.",
         question=_SEV_Q, options=_SEV_OPTS, keys=_SEV_KEYS, gold=0),
]
