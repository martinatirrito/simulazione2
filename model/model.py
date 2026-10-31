import copy

import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph = nx.DiGraph()
        self._idMapA = {}

    def buildGraph(self, genere, anno, soglia):
        self._graph.clear()
        self._idMapA.clear()

        nodi = DAO.getAllNodes(genere, anno, soglia)
        for a in nodi:
            self._idMapA[a.AlbumId] = a
        self._graph.add_nodes_from(nodi)

        archi = DAO.getAllEdges(self._idMapA, genere, anno, soglia)
        for a in archi:
            self._graph.add_edge(a.a1, a.a2, weight = a.peso)

    def getGraphDetails(self):
        return len(self._graph.nodes), len(self._graph.edges)

    def getComponentiConnesse(self):
        if len(self._graph.nodes) == 0:
            return 0, [], [], []

        components = list(nx.weakly_connected_components(self._graph))
        num_components = len(components)
        return num_components

    def bilancio5(self):
        # deve per ogni nodo associare la somma dei pesi uscenti meno la somma dei pesi entranti
        listNodesPesata = []
        for n in self._graph.nodes:
            score = 0
            for a in self._graph.out_edges(n, data=True):  # arco uscente  #data = true : dammi gli attributi
                score += a[2]["weight"]  # il peso perchè è una tupla
            for a in self._graph.in_edges(n, data=True):  # entranti
                score -= a[2]["weight"]
            listNodesPesata.append((n, score))

        listNodesPesata.sort(key=lambda x: (-x[1], x[0].Title) )

        return listNodesPesata[0:5]

    def getAllGenre(self):
        return DAO.getAllGenre()

    def getAllYears(self):
        return DAO.getAllYears()


    """scegli esattamente K album, ognuno in una componente debolmente connessa diversa, che massimizzano 
        la somma dei valori. Se K supera il numero di componenti, stampa un errore. 
        Stampa gli album in ordine alfabetico con il loro valore, poi il totale.
        C’è un nodo di partenza scelto dall’utente? Se no, parti da [] e set().
        Il grafo è orientato? Se sì, usa weakly_connected_components.
        Cosa devo sommare? Quel campo va nella riga dello score
        """

    # PUNTO 2 - K album in componenti debolmente connesse diverse, somma dei valori massima
    # (ricerca esaustiva di SOTTOINSIEMI con backtracking, "schema a indice")
    #
    # getSelezione(K):
    #   1) Prima della ricorsione calcolo UNA volta la componente di ogni nodo:
    #      self._comp = {nodo: indice componente}. Uso weakly_connected_components
    #      perché il grafo è orientato (le componenti ignorano il verso degli archi).
    #      Va calcolato qui e non nell'__init__: lì il grafo è ancora vuoto, e così
    #      viene ricalcolato ogni volta che ricreo il grafo.
    #   2) Candidati = tutti i nodi, messi in una lista FISSA (serve un ordine per l'indice).
    #   3) Azzero la soluzione migliore (_bestScore = -1) e parto da una soluzione
    #      vuota: non c'è un nodo di partenza scelto dall'utente.
    #
    # _ricorsioneSel(parziale, compUsate, i, K):
    #   - parziale = album scelti finora, compUsate = componenti già occupate.
    #   - CASO TERMINALE: quando ho esattamente K album calcolo la somma dei valori;
    #     se è migliore della migliore salvo una COPIA (parziale cambia con append/pop),
    #     poi return, perché non ha senso aggiungerne altri.
    #   - ESPANSIONE: provo solo i candidati dall'indice i in poi. Scelto il candidato j,
    #     la chiamata successiva parte da j+1. Così ogni insieme viene generato UNA sola
    #     volta: {A,B} e {B,A} sono lo stesso insieme e l'ordine non conta.
    #   - VINCOLO: scarto un candidato se la sua componente è già in compUsate
    #     (al massimo un album per componente).
    #   - BACKTRACKING: dopo la chiamata annullo la scelta su ENTRAMBE le strutture
    #     (pop su parziale e remove su compUsate) e provo il candidato successivo.
    #
    # Complessità esponenziale (tutti i sottoinsiemi di K elementi), ma il vincolo
    # sulle componenti scarta molti rami.

    def getSelezione(self, K):  # <-- CAMBIATO: niente source
        # 1) per ogni nodo, l'indice della sua componente
        self._comp = {}
        for i, cc in enumerate(nx.weakly_connected_components(self._graph)):  # <-- CAMBIATO: weakly (DiGraph)
            for n in cc:
                self._comp[n] = i

        self._candidati = list(self._graph.nodes)  # <-- CAMBIATO: tutti i nodi
        self._bestSol = []
        self._bestScore = -1
        self._ricorsioneSel([], set(), 0, K)  # <-- CAMBIATO: parto vuota
        return self._bestSol, self._bestScore

    def _ricorsioneSel(self, parziale, compUsate, i, K):
        if len(parziale) == K:
            score = sum(n.valore for n in parziale)  # <-- CAMBIATO: il tuo campo
            if score > self._bestScore:
                self._bestScore = score
                self._bestSol = copy.deepcopy(parziale)
            return

        for j in range(i, len(self._candidati)):
            c = self._candidati[j]
            if self._comp[c] in compUsate:
                continue
            parziale.append(c)
            compUsate.add(self._comp[c])
            self._ricorsioneSel(parziale, compUsate, j + 1, K)
            parziale.pop()
            compUsate.remove(self._comp[c])






