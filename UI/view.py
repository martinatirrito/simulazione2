import flet as ft


class View(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        # page stuff
        self._page = page
        self._page.title = "Lab11-Simulazione esame"
        self._page.horizontal_alignment = 'CENTER'
        self._page.theme_mode = ft.ThemeMode.LIGHT
        # controller (it is not initialized. Must be initialized in the main, after the controller is created)
        self._controller = None
        # graphical elements
        self._title = None
        self.txt_name = None
        self.btn_hello = None
        self.txt_result = None
        self.txt_container = None

    def load_interface(self):
        # title
        self._title = ft.Text("TdP-Simulazione esame Chinook", color="blue", size=24)
        self._page.controls.append(self._title)


        self._ddGenre = ft.Dropdown(label="Genere")
        self._controller.fillDDGenre()
        self._ddAnno = ft.Dropdown(label="Anno")
        self._controller.fillDDYears()
        self._btnCreaGrafo = ft.ElevatedButton(text="Crea Grafo", on_click=self._controller.handleCreaGrafo)
        self._btnAnalizza = ft.ElevatedButton(text="Analizza", on_click=self._controller.handleAnalizza, disabled = True)
        self._txtSoglia = ft.TextField(label="Soglia S", width=150)
        self._txtK = ft.TextField(label="K", width=150)

        row1 = ft.Row([self._ddGenre, self._btnCreaGrafo, self._ddAnno, self._btnAnalizza,self._txtSoglia, self._txtK],
                      alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(row1)

        self._btnRicorsione = ft.ElevatedButton(text="Ricorsione", on_click=self._controller.handleRicorsione)

        row2 = ft.Row([self._btnRicorsione],
                      alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(row2)

        # List View where the reply is printed
        self.txt_result = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self._page.controls.append(self.txt_result)
        self._page.update()

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    def update_page(self):
        self._page.update()