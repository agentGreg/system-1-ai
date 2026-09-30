# Format example only (not part of the dataset).
ITEMS = [
    dict(id="XX01", type="noul", rule_based=True, tricky=False,
         state="Dziś jest wtorek, 2026-10-06.\nWniosek z ePUAP od: Jan Testowy\n...",
         question="Czy odwołanie zostało wniesione w terminie? Reguła: ...",
         options=["Tak, w terminie", "Nie, po terminie"], gold=0),
    dict(id="XX02", type="choice", rule_based=False, tricky=True,
         state="...", question="Do której kategorii należy zgłoszenie?",
         options=["Opis A", "Opis B", "Opis C"], keys=["a", "b", "c"], gold=2),
    dict(id="XX03", type="score", rule_based=False, tricky=False,
         state="...", question="Jaki priorytet ma to zgłoszenie? Poziomy: 1 = ..., 2 = ..., 3 = ..., 4 = ...",
         options=["1 - niski (...)", "2 - ...", "3 - ...", "4 - krytyczny (...)"],
         keys=["p1_niski", "p2", "p3", "p4_krytyczny"], gold=1),
]
