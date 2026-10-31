import traceback

import flet as ft
import networkx as nx


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    def fillDDGenre(self):
        generi = self._model.getAllGenre()
        for g in generi:
            self._view._ddGenre.options.append(ft.dropdown.Option(g))
        self._view.update_page()

    def fillDDYears(self):
        anni = self._model.getAllYears()
        for a in anni:
            self._view._ddAnno.options.append(ft.dropdown.Option(a))
        self._view.update_page()

    def fillDDArtist(self):
        artisti = self._model.getAllArtist()
        for a in artisti:
            self._view._ddArtist.options.append(ft.dropdown.Option(key=str(a.ArtistId), text=a.Name))
        self._view.update_page()

    def handleCreaGrafo(self, e):
        genere = self._view._ddGenre.value
        anno = self._view._ddAnno.value

        if genere is None or anno is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text(f'Errore, inserire genere e anno', color="red"))
            self._view._page.update()
            return

        try:
            soglia = int(self._view._txtSoglia.value)
        except (ValueError, TypeError):
            self._view.create_alert("La soglia deve essere un intero.")
            return

        if soglia < 1:
            self._view.create_alert("La soglia deve essere almeno 1.")
            return

        try:
            self._model.buildGraph(genere, anno, soglia)
            self._view._btnAnalizza.disabled = False
            self._view.txt_result.controls.clear()
            Nnodi, Narchi = self._model.getGraphDetails()
            self._view.txt_result.controls.append(
                ft.Text("Grafo correttamente creato.")
            )
            self._view.txt_result.controls.append(
                ft.Text(f"Numero di nodi: {Nnodi}")
            )
            self._view.txt_result.controls.append(
                ft.Text(f"Numero di archi: {Narchi}")
            )
            numComp = self._model.getComponentiConnesse()
            self._view.txt_result.controls.append(
                ft.Text(f"Numero componenti debolmente connesse: {numComp}")
            )

            self._view._page.update()

        except Exception as ex:
            traceback.print_exc()
            self._view.create_alert(f"Errore nella creazione del grafo: {ex}")
            # self._view.txt_result.controls.append(ft.Text(f"Errore nella creazione del grafo: {ex}")) se non ho il metodo nella view
            # self._view._page.update()

    def handleAnalizza(self,e):
        self._view.txt_result.controls.clear()

        nNodi, nArchi = self._model.getGraphDetails()
        if nNodi == 0:
            self._view.create_alert("Creare prima il grafo.")
            return

        try:
            lista = self._model.bilancio5()
            self._view.txt_result.controls.append(ft.Text("Il bilancio di ogni album è:"))
            for titolo, bilancio in lista:
                self._view.txt_result.controls.append(ft.Text(f'{titolo} -- bilancio {bilancio}'))
            self._view.update_page()

        except Exception as ex:
            traceback.print_exc()
            self._view.create_alert(f"Errore nella stampa delle info: {ex}")


# Handler "Trova Cammino": controlla che sia stato scelto un artista,
# converte la key del dropdown (id stringa) nell'oggetto nodo con idMap[int(...)]
# e chiama il model. Stampa il cammino NELL'ORDINE DI PERCORRENZA (non ordinato,
# perché è una sequenza) con il peso di ogni arco, per verificare che non scenda mai.

    # Handler "Ricorsione": controlla nell'ordine che
    #   1) il grafo sia stato creato,
    #   2) K sia un intero positivo (int() dentro try/except perché il TextField dà una stringa),
    #   3) K non superi il numero di componenti debolmente connesse, altrimenti
    #      sarebbe impossibile scegliere K album in componenti tutte diverse.
    # Poi chiama il model e stampa gli album in ordine ALFABETICO di titolo
    # (la soluzione è un insieme, l'ordine non conta, quindi lo decido io),
    # ognuno con il suo valore, e infine il valore totale.

    def handleRicorsione(self, e):
        self._view.txt_result.controls.clear()

        # 1. grafo creato?
        if self._model._graph.number_of_nodes() == 0:
            self._view.create_alert("Creare prima il grafo.")
            return

        # 2. K intero positivo?
        try:
            K = int(self._view._txtK.value)
        except (ValueError, TypeError):
            self._view.create_alert("K deve essere un intero.")
            return
        if K <= 0:
            self._view.create_alert("K deve essere positivo.")
            return

        # 3. K non può superare il numero di componenti
        nComp = nx.number_weakly_connected_components(self._model._graph)
        if K > nComp:
            self._view.create_alert(f"K deve essere al massimo {nComp} (numero di componenti).")
            return

        # 4. ricorsione e stampa in ordine alfabetico
        sol, score = self._model.getSelezione(K)
        for a in sorted(sol, key=lambda x: x.Title):
            self._view.txt_result.controls.append(ft.Text(f"{a.Title} -- valore {a.valore}"))
        self._view.txt_result.controls.append(ft.Text(f"Valore totale: {score}"))
        self._view.update_page()