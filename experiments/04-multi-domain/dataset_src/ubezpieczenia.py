# Domain: ubezpieczenia (insurance claims). Hand-written items, all names / numbers fictional.
ITEMS = [
    # ---------------- noul ----------------
    dict(id="INS01", type="noul", rule_based=True, tricky=True,
         state="Dziś jest czwartek, 2026-10-01.\n"
               "Zgłoszenie szkody do polisy POL-0000-123 (ubezpieczenie roweru od kradzieży).\n"
               "Ubezpieczony: Jan Testowy. Umowa zawarta w poniedziałek 2026-09-14.\n"
               "Opis: rower skradziony spod bloku przy ul. Przykładowej 1 w nocy z 27 na 28 września; "
               "kradzież nastąpiła 2026-09-28 około godz. 2:00, zgłoszona na policję tego samego dnia.",
         question="Czy szkoda jest objęta ochroną ubezpieczeniową? Reguła: obowiązuje karencja 14 dni. "
                  "Pierwszym dniem karencji jest dzień następujący po dniu zawarcia umowy. Zdarzenia, które "
                  "nastąpiły w okresie karencji, nie są objęte ochroną; ochrona obejmuje zdarzenia od pierwszego "
                  "dnia po zakończeniu karencji. Innych wyłączeń w tej sprawie nie ma.",
         options=["Tak, szkoda jest objęta ochroną", "Nie, zdarzenie nastąpiło w okresie karencji"], gold=1),
    dict(id="INS02", type="noul", rule_based=True, tricky=False,
         state="Szkoda z AC, polisa POL-0000-456, pojazd osobowy.\n"
               "Kierujący: Anna Przykładowa, prawo jazdy ważne. Notatka policji: badanie alkomatem 0,00 promila.\n"
               "Zdarzenie: otarcie zderzaka o słupek na parkingu podziemnym.\n"
               "Kosztorys likwidatora: 512,40 zł.",
         question="Czy ubezpieczyciel wypłaci odszkodowanie z AC? Reguła: polisa ma franszyzę integralną 500 zł, "
                  "czyli szkody o wartości nie wyższej niż 500 zł nie są wypłacane, a szkody o wartości wyższej niż "
                  "500 zł są wypłacane w pełnej wysokości; nie wypłaca się jednak odszkodowania, jeżeli kierujący był "
                  "nietrzeźwy lub nie miał uprawnień do kierowania pojazdem.",
         options=["Tak, odszkodowanie zostanie wypłacone", "Nie, odszkodowanie nie zostanie wypłacone"], gold=0),
    dict(id="INS03", type="noul", rule_based=True, tricky=True,
         state="Dziś jest piątek, 2026-10-09.\n"
               "Ubezpieczenie turystyczne TUR-0000-321, wariant: koszty leczenia (suma 50 000 zł) + dokupiony pakiet Sport.\n"
               "Ubezpieczony: Marek Fikcyjny. Wyjazd zagraniczny 2026-09-19 - 2026-10-02 (powrót w piątek 2026-10-02).\n"
               "Zdarzenie: uraz ucha podczas nurkowania na głębokość 25 m, wizyta w zagranicznej klinice, koszt 8 400 zł.\n"
               "Zgłoszenie szkody wpłynęło 2026-10-08 wraz z rachunkami.",
         question="Czy koszty leczenia zostaną pokryte z polisy? Reguła: (1) wyłączone są zdarzenia podczas sportów "
                  "wysokiego ryzyka (m.in. nurkowanie na głębokość większą niż 20 m, skoki spadochronowe), chyba że ubezpieczony "
                  "dokupił pakiet Sport; (2) szkodę trzeba zgłosić najpóźniej 7. dnia po powrocie, licząc od dnia "
                  "następującego po dniu powrotu; (3) koszty nie mogą przekroczyć sumy ubezpieczenia.",
         options=["Tak, koszty zostaną pokryte", "Nie, koszty nie zostaną pokryte"], gold=0),
    dict(id="INS04", type="noul", rule_based=True, tricky=False,
         state="Ubezpieczenie mieszkania POL-0000-789, rok polisowy: 2026-02-01 - 2027-01-31.\n"
               "Historia szkód w tym roku polisowym: 2026-03-10 stłuczenie szyby balkonowej, wypłacono 640 zł.\n"
               "Nowa szkoda: zalanie łazienki przez pękniętą spłuczkę w poniedziałek 2026-10-05, "
               "zgłoszona w środę 2026-10-07. Wstępna wycena klienta: 2 950 zł.",
         question="Czy szkodę można zlikwidować w trybie uproszczonym (bez oględzin), czyli czy spełnione są "
                  "łącznie wszystkie warunki: szacowana wartość szkody nie przekracza 3 000 zł, szkodę zgłoszono w "
                  "ciągu 3 dni od zdarzenia (liczonych od dnia następującego po zdarzeniu) i jest to pierwsza szkoda "
                  "z tej polisy w bieżącym roku polisowym?",
         options=["Tak, tryb uproszczony", "Nie, potrzebne oględziny"], gold=1),
    dict(id="INS05", type="noul", rule_based=False, tricky=True,
         state="Szanowni Państwo,\n"
               "bardzo dziękuję za sprawne przeprowadzenie likwidacji szkody SZK-0000-111 i miły kontakt z panią "
               "likwidator. Z decyzją o wypłacie 3 100 zł nie mogę się jednak zgodzić, bo naprawa w warsztacie "
               "kosztowała 5 800 zł (faktura w załączniku). Uprzejmie proszę o ponowne przeanalizowanie sprawy i "
               "dopłatę różnicy.\nZ wyrazami szacunku, Ewa Testowa",
         question="Czy klientka wnosi odwołanie od decyzji odszkodowawczej, czyli kwestionuje wysokość lub odmowę "
                  "wypłaty i prosi o ponowne rozpatrzenie sprawy?",
         options=["Tak, to odwołanie od decyzji", "Nie, to nie jest odwołanie"], gold=0),
    dict(id="INS06", type="noul", rule_based=True, tricky=False,
         state="Dziś jest środa, 2026-10-14.\n"
               "Polisa POL-0000-246 (ubezpieczenie roweru), zawarta 2026-09-20, suma ubezpieczenia 6 000 zł, "
               "bez zmian od zawarcia.\n"
               "Szkoda zgłoszona dziś: kradzież roweru z piwnicy, wartość 4 200 zł. Klient dołączył potwierdzenie "
               "zgłoszenia kradzieży na policji (nr RSD-0000-1). Klient nie miał wcześniej żadnych szkód.",
         question="Czy szkodę należy skierować do weryfikacji antyfraudowej? Reguła: kieruje się ją, jeżeli "
                  "występują co najmniej dwa z sygnałów: (a) szkodę zgłoszono w ciągu 30 dni od zawarcia umowy; "
                  "(b) sumę ubezpieczenia podwyższono w ciągu 60 dni przed zdarzeniem; (c) przy kradzieży brak "
                  "potwierdzenia zgłoszenia na policji; (d) więcej niż 2 szkody w ostatnich 12 miesiącach; "
                  "(e) wartość szkody przekracza 90% sumy ubezpieczenia.",
         options=["Tak, skierować do weryfikacji", "Nie, nie kierować do weryfikacji"], gold=1),
    dict(id="INS07", type="noul", rule_based=False, tricky=False,
         state="Wiadomość z formularza kontaktowego:\n"
               "Dzień dobry, tydzień temu zgłaszałem kradzież katalizatora z mojego auta, numer szkody "
               "SZK-0000-222. Od tamtej pory nikt się nie odezwał. Na jakim etapie jest sprawa i czy potrzebujecie "
               "ode mnie jeszcze jakichś dokumentów? Piotr Przykładowy",
         question="Czy wiadomość jest zgłoszeniem nowej szkody, czyli klient informuje o zdarzeniu, które nie "
                  "zostało jeszcze zgłoszone ubezpieczycielowi?",
         options=["Tak, to nowa szkoda", "Nie, to pytanie o szkodę już zgłoszoną"], gold=1),
    dict(id="INS08", type="noul", rule_based=False, tricky=False,
         state="Dzień dobry, sprzedaliśmy mieszkanie przy ul. Przykładowej 7 w Testowie, akt notarialny "
               "podpisany 2026-10-20. W związku z tym prosimy o wypowiedzenie polisy mieszkaniowej POL-0000-852 "
               "z końcem października i zwrot niewykorzystanej części składki na rachunek "
               "00 0000 0000 0000 0000 0000 0000. Anna i Tomasz Testowi",
         question="Czy klienci wypowiadają umowę ubezpieczenia, czyli żądają jej zakończenia?",
         options=["Tak, wypowiadają umowę", "Nie, nie wypowiadają umowy"], gold=0),
    # ---------------- choice ----------------
    dict(id="INS09", type="choice", rule_based=False, tricky=True,
         state="Zgłoszenie telefoniczne (notatka konsultanta):\n"
               "Klientka ma polisę mieszkaniową z rozszerzeniem OC w życiu prywatnym. Jej 10-letni syn grał w "
               "piłkę na osiedlowym boisku i wybił szybę w zaparkowanym samochodzie sąsiada. Sąsiad żąda "
               "pokrycia kosztu nowej szyby, 1 300 zł.",
         question="Do którego typu szkody należy to zgłoszenie?",
         options=["Komunikacyjna - szkoda z polisy OC lub AC pojazdu należącego do ubezpieczonego",
                  "Majątkowa - zniszczenie mienia ubezpieczonego w jego mieszkaniu lub domu",
                  "NNW - uszkodzenie ciała ubezpieczonego w nieszczęśliwym wypadku",
                  "OC w życiu prywatnym - szkoda wyrządzona osobie trzeciej przez ubezpieczonego lub jego domownika poza ruchem pojazdów",
                  "Turystyczna - zdarzenie w podróży zagranicznej (koszty leczenia, bagaż, opóźnienie lotu)"],
         keys=["komunikacyjna", "majatkowa", "nnw", "oc_prywatne", "turystyczna"], gold=3),
    dict(id="INS10", type="choice", rule_based=False, tricky=False,
         state="E-mail od klienta:\n"
               "Wróciłam wczoraj z urlopu za granicą. W trakcie pobytu z przechowalni bagażu w hotelu zginęła moja "
               "walizka z ubraniami i aparatem. Mam potwierdzenie z recepcji i zgłoszenie z miejscowej policji. "
               "Numer polisy wyjazdowej: TUR-0000-654. Alicja Fikcyjna",
         question="Do którego typu szkody należy to zgłoszenie?",
         options=["Komunikacyjna - szkoda z polisy OC lub AC pojazdu należącego do ubezpieczonego",
                  "Majątkowa - zniszczenie lub kradzież mienia w mieszkaniu lub domu wskazanym w polisie",
                  "NNW - uszkodzenie ciała ubezpieczonego w nieszczęśliwym wypadku",
                  "OC w życiu prywatnym - szkoda wyrządzona osobie trzeciej przez ubezpieczonego lub jego domownika poza ruchem pojazdów",
                  "Turystyczna - zdarzenie w podróży zagranicznej (koszty leczenia, bagaż, opóźnienie lotu)"],
         keys=["komunikacyjna", "majatkowa", "nnw", "oc_prywatne", "turystyczna"], gold=4),
    dict(id="INS11", type="choice", rule_based=False, tricky=False,
         state="Temat: SZK-0000-333 - dokumenty\n"
               "Dzień dobry, zgodnie z prośbą likwidatora przesyłam w załącznikach zdjęcia uszkodzonej bramy "
               "garażowej, fakturę za jej zakup oraz oświadczenie sprawcy. Proszę o potwierdzenie otrzymania. "
               "Karol Testowy",
         question="Jaki jest główny cel tej wiadomości?",
         options=["Zgłoszenie nowej szkody",
                  "Zapytanie o ofertę lub zakup nowego ubezpieczenia",
                  "Uzupełnienie dokumentów do szkody już prowadzonej",
                  "Skarga na obsługę lub pracownika ubezpieczyciela"],
         keys=["nowa_szkoda", "oferta", "uzupelnienie", "skarga"], gold=2),
    dict(id="INS12", type="choice", rule_based=False, tricky=False,
         state="Wiadomość na czacie, szkoda SZK-0000-444 (AC):\n"
               "Dzień dobry. Kasy do ręki nie chca, niech auto idzie do tego warsztatu z waszej listy przy "
               "ul. Przykładowej 3, a oni niech wom sami fakture wystawiom. Tak bydzie najprościej.",
         question="Jaki sposób rozliczenia szkody wybrał klient?",
         options=["Kosztorysowy - wypłata pieniędzy na konto klienta według wyceny, klient sam organizuje naprawę",
                  "Serwisowy - naprawa w warsztacie, który rozlicza się bezpośrednio z ubezpieczycielem na podstawie faktury",
                  "Klient nie wybrał jeszcze sposobu rozliczenia"],
         keys=["kosztorysowy", "serwisowy", "nie_wybral"], gold=1),
    dict(id="INS13", type="choice", rule_based=False, tricky=False,
         state="Zgłoszenie szkody majątkowej, polisa POL-0000-963:\n"
               "W nocy była burza, piorun uderzył w słup niedaleko domu. Rano okazało się, że nie działają "
               "telewizor, router i piec gazowy (elektronika sterownika). W domu nie było ognia, dym się nie "
               "pojawił, woda nigdzie nie wlała się do środka.",
         question="Jaka jest przyczyna szkody według opisu?",
         options=["Przepięcie - uszkodzenie urządzeń elektrycznych przez nagły wzrost napięcia, np. po wyładowaniu atmosferycznym",
                  "Pożar - ogień, który wydostał się poza palenisko",
                  "Zalanie - woda z instalacji wodno-kanalizacyjnej lub od sąsiada",
                  "Kradzież z włamaniem - zabór mienia po pokonaniu zabezpieczeń",
                  "Powódź - zalanie przez wezbrane wody lub wodę z opadów wlewającą się z zewnątrz"],
         keys=["przepiecie", "pozar", "zalanie", "kradziez", "powodz"], gold=0),
    # ---------------- score ----------------
    dict(id="INS14", type="score", rule_based=False, tricky=True,
         state="E-mail do biura obsługi:\n"
               "Dzień dobry, w zeszłym roku sąsiadowi doszczętnie spłonął garaż i od tamtej pory myślę o swoim "
               "domu. Chciałbym podwyższyć sumę ubezpieczenia domu z polisy POL-0000-159 i poznać nową składkę. "
               "U mnie wszystko w porządku, nic się nie stało. Jerzy Przykładowy",
         question="Jaka jest pilność obsługi tej sprawy? Poziomy: 1 = rutynowa (brak szkody do likwidacji: pytanie, "
                  "oferta, zmiana danych lub polisy); 2 = standardowa (szkoda już się zakończyła, nie może się "
                  "powiększać, nikt nie jest ranny); 3 = pilna (szkoda wciąż trwa lub może się powiększać, np. woda "
                  "nadal cieknie, mieszkanie otwarte po włamaniu, dach odkryty przed deszczem; nikt nie jest ranny); "
                  "4 = natychmiastowa (ktoś jest ranny lub chory i potrzebuje pomocy medycznej teraz, albo lokal "
                  "stał się niezdatny do zamieszkania).",
         options=["1 - rutynowa", "2 - standardowa", "3 - pilna", "4 - natychmiastowa"],
         keys=["rutynowa", "standardowa", "pilna", "natychmiastowa"], gold=0),
    dict(id="INS15", type="score", rule_based=False, tricky=False,
         state="Telefon na infolinię szkód, godz. 21:40:\n"
               "Klientka: pękł wężyk pod zlewem w kuchni, woda cały czas leci, zawór się nie domyka, podłoga już "
               "mokra i sąsiadka z dołu mówi, że ma plamę na suficie. Wszyscy domownicy zdrowi, czekam na "
               "hydraulika ze spółdzielni.",
         question="Jaka jest pilność obsługi tej sprawy? Poziomy: 1 = rutynowa (brak szkody do likwidacji: pytanie, "
                  "oferta, zmiana danych lub polisy); 2 = standardowa (szkoda już się zakończyła, nie może się "
                  "powiększać, nikt nie jest ranny); 3 = pilna (szkoda wciąż trwa lub może się powiększać, np. woda "
                  "nadal cieknie, mieszkanie otwarte po włamaniu, dach odkryty przed deszczem; nikt nie jest ranny); "
                  "4 = natychmiastowa (ktoś jest ranny lub chory i potrzebuje pomocy medycznej teraz, albo lokal "
                  "stał się niezdatny do zamieszkania).",
         options=["1 - rutynowa", "2 - standardowa", "3 - pilna", "4 - natychmiastowa"],
         keys=["rutynowa", "standardowa", "pilna", "natychmiastowa"], gold=2),
    dict(id="INS16", type="score", rule_based=False, tricky=False,
         state="Formularz zgłoszenia szkody AC:\n"
               "Tydzień temu ktoś porysował mi lewe drzwi auta na parkingu pod sklepem. Auto jeździ normalnie, "
               "mam zdjęcia rys. Proszę o wyznaczenie terminu oględzin. Tomasz Fikcyjny",
         question="Jaka jest pilność obsługi tej sprawy? Poziomy: 1 = rutynowa (brak szkody do likwidacji: pytanie, "
                  "oferta, zmiana danych lub polisy); 2 = standardowa (szkoda już się zakończyła, nie może się "
                  "powiększać, nikt nie jest ranny); 3 = pilna (szkoda wciąż trwa lub może się powiększać, np. woda "
                  "nadal cieknie, mieszkanie otwarte po włamaniu, dach odkryty przed deszczem; nikt nie jest ranny); "
                  "4 = natychmiastowa (ktoś jest ranny lub chory i potrzebuje pomocy medycznej teraz, albo lokal "
                  "stał się niezdatny do zamieszkania).",
         options=["1 - rutynowa", "2 - standardowa", "3 - pilna", "4 - natychmiastowa"],
         keys=["rutynowa", "standardowa", "pilna", "natychmiastowa"], gold=1),
    dict(id="INS17", type="score", rule_based=False, tricky=False,
         state="Wiadomość do centrum assistance, polisa TUR-0000-777:\n"
               "Hi, piszę z hotelu za granicą. Córka (7 lat) od wczoraj ma bardzo wysoką gorączkę i wymiotuje, "
               "leki z apteczki nie pomagają. Potrzebujemy lekarza albo informacji, do której placówki jechać. "
               "Please call back ASAP. Monika Testowa",
         question="Jaka jest pilność obsługi tej sprawy? Poziomy: 1 = rutynowa (brak szkody do likwidacji: pytanie, "
                  "oferta, zmiana danych lub polisy); 2 = standardowa (szkoda już się zakończyła, nie może się "
                  "powiększać, nikt nie jest ranny); 3 = pilna (szkoda wciąż trwa lub może się powiększać, np. woda "
                  "nadal cieknie, mieszkanie otwarte po włamaniu, dach odkryty przed deszczem; nikt nie jest ranny); "
                  "4 = natychmiastowa (ktoś jest ranny lub chory i potrzebuje pomocy medycznej teraz, albo lokal "
                  "stał się niezdatny do zamieszkania).",
         options=["1 - rutynowa", "2 - standardowa", "3 - pilna", "4 - natychmiastowa"],
         keys=["rutynowa", "standardowa", "pilna", "natychmiastowa"], gold=3),
]
