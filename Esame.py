import random
import json
from typing import List, Optional

# Definizione delle carte
class Carta:
    def __init__(self, nome: str, tipo_carta: str, effetto: Optional[str] = None):
        self.nome = nome
        self.tipo_carta = tipo_carta
        self.effetto = effetto

    def __repr__(self):
        return self.nome

# Definizione dei ruoli
class Ruolo:
    def __init__(self, nome: str):
        self.nome = nome

    def __repr__(self):
        return self.nome

# Definizione delle armi
class Arma(Carta):
    def __init__(self, nome: str, distanza: int):
        super().__init__(nome, "Equipaggiabile")
        self.distanza = distanza

    def __repr__(self):
        return self.nome


filepath = "listaCarte (1).json"
with open(filepath, "r", encoding="utf-8") as file:
    data = json.load(file)

ruoli_data = data["ruoli"]
carattere_data = data["personaggi"]
armi_data = data["armi"]
carte_data = data["carte"]

# Creazione dei ruoli
ruoli = [Ruolo(nome) for nome in ruoli_data]

# Creazione le armi
armi = [Arma(arma["nome"], arma["distanza"]) for arma in armi_data]

# Creazione delle carte
carte = []
for carta_data in carte_data:
    tipo_carta = "Equipaggiabile" if carta_data.get("Equipaggiabile", False) else "Gioca e Scarta"
    carta = Carta(carta_data["nome"], tipo_carta, carta_data.get("descrizione"))
    if tipo_carta == "Gioca e Scarta":
        num_copie = len(carta_data.get("copie", []))
        if carta_data["nome"] == "BANG!":
            num_copie -= 1
        carte.extend([carta] * num_copie)

# Aggiunta le armi al mazzo
carte.extend(armi)

# Filtro BANG! e Mancato!
bang_conto = 0
mancato_conto = 0
filtered_carte = []
for carta in carte:
    if carta.nome == "BANG!":
        if bang_conto < 50:
            bang_conto += 1
            filtered_carte.append(carta)
    elif carta.nome == "Mancato!":
        if mancato_conto < 24:
            mancato_conto += 1
            filtered_carte.append(carta)
    else:
        filtered_carte.append(carta)
carte = filtered_carte

while len(carte) < 80:
    carte.append(random.choice(carte))

# Definizione il giocatore
class Giocatore:
    def __init__(self, nome: str, ruolo: str, salute: int, carattere: Optional[str] = None, abilita: Optional[str] = None):
        self.nome = nome
        self.ruolo = ruolo
        self.salute = salute
        self.salute_massima = salute
        self.mano = []
        self.equipaggiamento = [Arma("Colt 45", 1)]  # Ogni giocatore ha un'arma con distanza 1
        self.carattere = carattere
        self.abilita = abilita

    def __repr__(self):
        return f"{self.nome} {self.ruolo} - HP: {self.salute}/{self.salute_massima} - {self.carattere} - {self.equipaggiamento}"

    def vivo(self):
        return self.salute > 0

class Gioco:
    def __init__(self, giocatori: List[str]):
        self.giocatori = self.assegna_ruoli(giocatori)
        self.mazzo = carte.copy()
        self.pila_scartata = []
        self.turn_index = 0
        self.classifica = {giocatore.nome: {"sbleuri": 500, "partite_giocate": 0} for giocatore in self.giocatori}
        self.pesca_carte_iniziali()

    def assegna_ruoli(self, giocatore_nomi: List[str]) -> List[Giocatore]:
        num_giocatori = len(giocatore_nomi)
        ruoli = self.determina_ruoli(num_giocatori)
        caratteri = self.assegna_caratteri(num_giocatori)
        random.shuffle(ruoli)
        giocatori = [Giocatore(nome, ruolo, carattere[1], carattere[0], carattere[2]) for nome, ruolo, carattere in zip(giocatore_nomi, ruoli, caratteri)]
        random.shuffle(giocatori)
        return giocatori

    def determina_ruoli(self, num_giocatori: int) -> List[str]:
        ruoli = ["Sceriffo", "Rinnegato"]
        if num_giocatori >= 4:
            ruoli += ["Fuorilegge"] * 2
        if num_giocatori >= 5:
            ruoli.append("Vice")
        if num_giocatori >= 6:
            ruoli.append("Fuorilegge")
        if num_giocatori >= 7:
            ruoli.append("Vice")
        return ruoli

    def assegna_caratteri(self, num_giocatori: int) -> List[tuple]:
        caratteri = [
            ("Bart Cassidy", 4, "Ogni volta che perde un PF, pesca una carta"),
            ("El Gringo", 3, "Ogni volta che perde un PF, pesca una carta a caso dalla mano di chi lo ha colpito"),
            ("Jourdonnais", 4, "E' come se avesse sempre in gioco un Barile"),
            ("Paul Regret", 3, "E' come se avesse sempre in gioco un Mustung"),
            ("Rose Doolan", 4, "E' come se avesse in gioco un Mirino"),
            ("Sid Ketchum", 4, "Può scartare 2 carte per recuperare 1 PF"),
            ("Suzy LaFayette", 4, "Non appena rimane senza carte in mano, pesca una carta")
        ]
        random.shuffle(caratteri)
        return caratteri[:num_giocatori]

    def pesca_carte_iniziali(self):
        for giocatore in self.giocatori:
            self.draw_carte(giocatore, giocatore.salute)

    def draw_carte(self, giocatore: Giocatore, num_carte: int):
        for _ in range(num_carte):
            if not self.mazzo:
                self.mazzo = self.pila_scartata
                random.shuffle(self.mazzo)
                self.pila_scartata = []
            giocatore.mano.append(self.mazzo.pop(0))

    def gioca_carta(self, giocatore: Giocatore, carta: Carta, target: Optional[Giocatore] = None):
        pass

    def calcolo_distanza(self, giocatore1: Giocatore, giocatore2: Giocatore) -> int:
        idx1 = self.giocatori.index(giocatore1)
        idx2 = self.giocatori.index(giocatore2)
        return min(abs(idx1 - idx2), len(self.giocatori) - abs(idx1 - idx2))

    def prossimo_turno(self):
        if len(self.giocatori) == 0:
            return
        giocatore_corrente = self.giocatori[self.turn_index]
        if not giocatore_corrente.vivo():
            self.elimina_giocatore(giocatore_corrente)
        self.turn_index = (self.turn_index + 1) % len(self.giocatori)
        self.verifica_vincitore()

    def elimina_giocatore(self, giocatore: Giocatore):
        print(f"{giocatore.nome} è stato eliminato! Era un {giocatore.ruolo}.")
        self.giocatori.remove(giocatore)
        self.pila_scartata.extend(giocatore.mano)
        self.pila_scartata.extend(giocatore.equipaggiamento)
        giocatore.mano.clear()
        giocatore.equipaggiamento.clear()

    def verifica_vincitore(self):
        sceriffo_vivo = any(g.ruolo == "Sceriffo" and g.vivo() for g in self.giocatori)
        rinnegato_vivo = any(g.ruolo == "Rinnegato" and g.vivo() for g in self.giocatori)
        fuorilegge_vivi = any(g.ruolo == "Fuorilegge" and g.vivo() for g in self.giocatori)

        if not sceriffo_vivo:
            if rinnegato_vivo and not fuorilegge_vivi:
                print("Il Rinnegato vince!")
            else:
                print("I Fuorilegge vincono!")
            self.termina_partita()
        elif not fuorilegge_vivi and not rinnegato_vivo:
            print("Lo Sceriffo e i suoi Vice vincono!")
            self.termina_partita()

    def termina_partita(self):
        print("La partita è terminata.")
        for giocatore in self.giocatori:
            print(f"{giocatore.nome} ({giocatore.ruolo}) - HP: {giocatore.salute}/{giocatore.salute_massima}")

    def interazione_utente(self, giocatore: Giocatore):
        print(f"\nTurno di {giocatore.nome}.")
        print("Le tue carte:")
        for carta in giocatore.mano:
            print(carta)
        print("Il tuo equipaggiamento:")
        for arma in giocatore.equipaggiamento:
            print(arma)
        print(f"La tua vita: {giocatore.salute}/{giocatore.salute_massima}")
        print("Distanza dagli altri giocatori:")
        for altro_giocatore in self.giocatori:
            if altro_giocatore != giocatore:
                distanza = self.calcolo_distanza(giocatore, altro_giocatore)
                print(f"{altro_giocatore.nome}: {distanza}")
        while True:
            target_nome = input("Inserisci il nome del giocatore da attaccare: ")
            target = next((g for g in self.giocatori if g.nome == target_nome), None)
            if target:
                distanza = self.calcolo_distanza(giocatore, target)
                arma_disponibile = None
                for arma in giocatore.equipaggiamento:
                    if isinstance(arma, Arma) and distanza <= arma.distanza:
                        arma_disponibile = arma
                        break

                if arma_disponibile:
                    self.attacca_giocatore(giocatore, target, arma_disponibile)
                    break
                else:
                    print("Non hai un'arma per attaccare questo giocatore a questa distanza.")
            else:
                print("Giocatore non trovato.")

    def attacca_giocatore(self, attaccante: Giocatore, difensore: Giocatore, arma: Arma):
        print(f"{attaccante.nome} attacca {difensore.nome} con {arma.nome}!")
        if any(isinstance(carta, Carta) and carta.nome == "Mancato!" for carta in difensore.equipaggiamento):
            print(f"{difensore.nome} ha la carta Mancato! e non perde punti vita!")
        else:
            difensore.salute -= 1
            if difensore.salute <= 0:
                self.elimina_giocatore(difensore)

#informazioni sui giocatori
def chiedi_info_giocatori() -> List[str]:
    num_giocatori = int(input("Inserisci il numero di giocatori (da 4 a 7): "))
    if num_giocatori < 4 or num_giocatori > 7:
        print("Il numero di giocatori deve essere compreso tra 4 e 7.")
        return chiedi_info_giocatori()
    giocatori = []
    for i in range(num_giocatori):
        nome_giocatore = input(f"Inserisci il nome del giocatore {i+1}: ")
        giocatori.append(nome_giocatore)
    return giocatori

# Dati dei giocatori
giocatore_nomi = chiedi_info_giocatori()

# visualizzazione delle informazioni iniziali
gioco = Gioco(giocatore_nomi)

# Esecuzione del gioco 
while True:
    if len(gioco.giocatori) == 0:
        break
    gioco.prossimo_turno()
    if len(gioco.giocatori) == 0:
        break
    gioco.interazione_utente(gioco.giocatori[gioco.turn_index])



