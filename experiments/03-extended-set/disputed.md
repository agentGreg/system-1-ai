# Disputed items (experiment 03)

Items where the author label and the two LLM annotators do not all agree. They are kept out of the headline numbers (the clean set) and wait for human adjudication by Greg. No author label was changed.

2 items. Annotators: Claude Opus 5.5, GPT-6.1 Sol (reasoning on, blind to the author label and to each other).

Adjudication: fill in the `Decision` line of each item (A/B/... or `drop` if genuinely ambiguous).


## K39 (kompletnosc)

```
Zgłoszenie do helpdesku IT:
Program pocztowy od dziś od 9:00 nie wysyła maili, komunikat: „Błąd 0x800CCC0F: połączenie z serwerem zostało przerwane”.
```

**Question:** Czy zgłoszenie jest kompletne? Reguła: zgłoszenie awarii jest kompletne, jeśli zawiera (1) nazwę systemu lub aplikacji, (2) opis problemu, (3) informację, od kiedy problem występuje, oraz (4) treść komunikatu błędu albo zrzut ekranu, ale tylko wtedy, gdy pojawił się komunikat błędu.

**Options:** A. Tak, zgłoszenie jest kompletne; B. Nie, zgłoszeniu czegoś brakuje

- **Author:** A (Tak, zgłoszenie jest kompletne)
- **Claude Opus 5.5:** B (Nie, zgłoszeniu czegoś brakuje). Zgłoszenie podaje opis problemu, czas wystąpienia (od dziś od 9:00) i treść komunikatu błędu, ale „program pocztowy” to ogólne określenie, a nie nazwa konkretnej aplikacji.
- **GPT-6.1 Sol:** B (Nie, zgłoszeniu czegoś brakuje). Brakuje nazwy systemu lub aplikacji — określenie „program pocztowy” nie jest nazwą.
- **Decision:** _pending_


## S14 (irytacja)

```
Wiadomość od klienta:
Czekam na odpowiedź od tygodnia. Czy ktoś w ogóle czyta te maile?
```

**Question:** Jak bardzo zirytowany jest klient, który napisał tę wiadomość?

**Options:** A. Spokojny (brak irytacji); B. Lekko zirytowany; C. Bardzo zirytowany

- **Author:** B (Lekko zirytowany)
- **Claude Opus 5.5:** B (Lekko zirytowany). Klient wyraźnie okazuje frustrację tygodniowym oczekiwaniem i retorycznym pytaniem, ale nie używa gróźb, obelg, wykrzykników ani wielkich liter.
- **GPT-6.1 Sol:** C (Bardzo zirytowany). Klient wyraża silną frustrację tygodniowym oczekiwaniem i podważa, czy ktokolwiek czyta jego maile.
- **Decision:** _pending_

