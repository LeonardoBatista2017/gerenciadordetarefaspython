from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image


class MainView(MDScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.page = 1
        self.items_per_page = 5

        # Layout principal
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=20)
        self.add_widget(self.layout)

        # Logo
        self.logo = Image(
            source="assets/logo-luft.png",
            size_hint=(None, None),
            size=(150, 150),
            allow_stretch=True
        )
        logo_box = BoxLayout(size_hint_y=None, height=160, padding=(0, 10))
        logo_box.add_widget(self.logo)
        self.layout.add_widget(logo_box)

        # Título
        self.title_label = MDLabel(
            text="Gerenciador de Tarefas",
            halign="center",
            font_style="H4",
            size_hint_y=None,
            height=50
        )
        self.layout.add_widget(self.title_label)

        # Botões principais
        buttons_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        cadastrar_btn = MDRaisedButton(
            text="Cadastrar Tarefa",
            pos_hint={"center_x": 0.5},
            size_hint=(None, None),
            size=(200, 40)
        )
        cadastrar_btn.bind(on_release=self.abrir_cadastro)

        atualizar_btn = MDRaisedButton(
            text="Atualizar Lista",
            pos_hint={"center_x": 0.5},
            size_hint=(None, None),
            size=(200, 40)
        )
        atualizar_btn.bind(on_release=lambda x: self.atualizar_lista())

        buttons_box.add_widget(cadastrar_btn)
        buttons_box.add_widget(atualizar_btn)
        self.layout.add_widget(buttons_box)

        # Campo de busca
        self.search_field = MDTextField(
            hint_text="Buscar tarefa...",
            size_hint_y=None,
            height=50,
            mode="rectangle"
        )
        self.search_field.bind(text=lambda instance, value: self.atualizar_lista())
        self.layout.add_widget(self.search_field)

        # Área de listagem
        self.scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        self.layout.add_widget(self.scroll)

        # Paginação
        nav_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.prev_btn = MDRaisedButton(text="Anterior")
        self.prev_btn.bind(on_release=self.anterior_pagina)
        self.next_btn = MDRaisedButton(text="Próximo")
        self.next_btn.bind(on_release=self.proxima_pagina)
        nav_layout.add_widget(self.prev_btn)
        nav_layout.add_widget(self.next_btn)
        self.layout.add_widget(nav_layout)

        # Atualiza lista inicial
        self.atualizar_lista()

    # Abrir formulário para cadastro
    def abrir_cadastro(self, instance):
        self.manager.current = "form_view"
        form_screen = self.manager.get_screen("form_view")
        form_screen.tarefa = None
        # Resetar campos do formulário
        form_screen.titulo_input.text = ""
        form_screen.assunto_input.text = ""
        form_screen.data_input.text = ""
        form_screen.status_spinner.text = "Baixo"

    # Atualiza a listagem de tarefas
       # Atualiza a listagem de tarefas
    def atualizar_lista(self):
        self.list_layout.clear_widgets()
        tarefas = self.controller.listar_tarefas()

        # Filtragem pelo campo de busca
        termo_busca = self.search_field.text.strip().lower()
        if termo_busca:
            tarefas = [
                t for t in tarefas
                if termo_busca in t["titulo"].lower() or termo_busca in t["assunto"].lower()
            ]

        # Paginação
        total_pages = (len(tarefas) + self.items_per_page - 1) // self.items_per_page or 1
        if self.page > total_pages:
            self.page = total_pages

        start = (self.page - 1) * self.items_per_page
        end = start + self.items_per_page

        # === Cabeçalho da tabela ===
        header = BoxLayout(size_hint_y=None, height=40, padding=(5, 0))
        header.add_widget(MDLabel(text="[b]Título[/b]", halign="left", markup=True))
        header.add_widget(MDLabel(text="[b]Status[/b]", halign="center", markup=True))
        header.add_widget(MDLabel(text="[b]Ações[/b]", halign="center", markup=True))
        self.list_layout.add_widget(header)

        for tarefa in tarefas[start:end]:
            box = BoxLayout(size_hint_y=None, height=40)
            box.add_widget(MDLabel(text=tarefa["titulo"], halign="left"))
            box.add_widget(MDLabel(text=tarefa["status"], halign="center"))

            # Botão Visualizar
            view_btn = MDIconButton(
                icon="eye",
                theme_text_color="Custom",
                text_color=(0, 0, 1, 1),  # Azul
                icon_size="24sp"
            )
            view_btn.bind(on_release=lambda x, t=tarefa: self.visualizar_tarefa(t))
            box.add_widget(view_btn)

            # Botão Editar
            edit_btn = MDIconButton(
                icon="pencil",
                theme_text_color="Custom",
                text_color=(0, 1, 0, 1),  # Verde
                icon_size="24sp"
            )
            edit_btn.bind(on_release=lambda x, t=tarefa: self.editar_tarefa(t))
            box.add_widget(edit_btn)

            # Botão Deletar
            del_btn = MDIconButton(
                icon="trash-can",
                theme_text_color="Custom",
                text_color=(1, 0, 0, 1),  # Vermelho
                icon_size="24sp"
            )
            del_btn.bind(on_release=lambda x, t=tarefa: self.confirmar_delete(t))
            box.add_widget(del_btn)

            self.list_layout.add_widget(box)

    # Visualizar tarefa
    def visualizar_tarefa(self, tarefa):
        detalhes = (
            f"[b]Título:[/b] {tarefa['titulo']}\n"
            f"[b]Assunto:[/b] {tarefa['assunto']}\n"
            f"[b]Data:[/b] {tarefa['data']}\n"
            f"[b]Status:[/b] {tarefa['status']}"
        )

        dialog = MDDialog(
            title="Detalhes da Tarefa",
            text=detalhes,
            buttons=[
                MDFlatButton(
                    text="Fechar",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    # Paginação próxima
    def proxima_pagina(self, instance):
        tarefas = self.controller.listar_tarefas()
        termo_busca = self.search_field.text.strip().lower()
        if termo_busca:
            tarefas = [t for t in tarefas if termo_busca in t["titulo"].lower() or termo_busca in t["assunto"].lower()]

        total_pages = (len(tarefas) + self.items_per_page - 1) // self.items_per_page
        if self.page < total_pages:
            self.page += 1
            self.atualizar_lista()

    # Paginação anterior
    def anterior_pagina(self, instance):
        if self.page > 1:
            self.page -= 1
            self.atualizar_lista()

    # Editar tarefa
    def editar_tarefa(self, tarefa):
        self.manager.current = "form_view"
        form_screen = self.manager.get_screen("form_view")
        form_screen.tarefa = tarefa

        form_screen.titulo_input.text = str(tarefa.get("titulo", ""))
        form_screen.assunto_input.text = str(tarefa.get("assunto", ""))
        data_val = tarefa.get("data")
        if hasattr(data_val, "strftime"):
            form_screen.data_input.text = data_val.strftime("%Y-%m-%d")
        else:
            form_screen.data_input.text = str(data_val or "")
        form_screen.status_spinner.text = str(tarefa.get("status", "Baixo"))

    # Confirmação antes de deletar
    def confirmar_delete(self, tarefa):
        dialog = MDDialog(
            title="Confirmar Exclusão",
            text=f"Deseja realmente excluir a tarefa '{tarefa['titulo']}'?",
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="Excluir", on_release=lambda x: self.deletar_tarefa(dialog, tarefa))
            ]
        )
        dialog.open()

    # Deletar tarefa
    def deletar_tarefa(self, dialog, tarefa):
        dialog.dismiss()
        self.controller.deletar_tarefa(tarefa["id"])
        self.atualizar_lista()
