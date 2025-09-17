from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from datetime import datetime
import calendar
from kivy.uix.button import Button

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton, MDIconButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog


class MainView(MDScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.page = 1
        self.items_per_page = 5
        self.lista_tarefas = []

        # Layout principal
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=20)
        self.add_widget(self.layout)

        # Logo
        self.logo = Image(source="assets/logo-luft.png", size_hint=(None, None), size=(150, 150))
        logo_box = BoxLayout(size_hint_y=None, height=160, padding=(0,10))
        logo_box.add_widget(self.logo)
        self.layout.add_widget(logo_box)

        # Título
        self.title_label = MDLabel(text="Gerenciador de Tarefas", halign="center", font_style="H4", size_hint_y=None, height=50)
        self.layout.add_widget(self.title_label)

        # Botões principais
        self.buttons_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.cadastrar_btn = MDRaisedButton(text="Cadastrar Tarefa", size_hint=(None,None), size=(200,40))
        self.cadastrar_btn.bind(on_release=self.abrir_cadastro)
        self.atualizar_btn = MDRaisedButton(text="Atualizar Lista", size_hint=(None,None), size=(200,40))
        self.atualizar_btn.bind(on_release=lambda x: self.atualizar_lista())
        self.buttons_box.add_widget(self.cadastrar_btn)
        self.buttons_box.add_widget(self.atualizar_btn)
        self.layout.add_widget(self.buttons_box)

        # Campo de busca
        self.search_field = MDTextField(hint_text="Buscar tarefa...", size_hint_y=None, height=50, mode="rectangle")
        self.search_field.bind(text=lambda inst, val: self.atualizar_lista())
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

    # ================== FUNÇÕES ==================
    def reset_buttons_state(self):
        for btn in [self.cadastrar_btn, self.atualizar_btn, self.prev_btn, self.next_btn]:
            btn.state = "normal"
            btn.elevation = 6

    def abrir_cadastro(self, instance):
        self.manager.current = "form_view"
        form_screen = self.manager.get_screen("form_view")
        form_screen.tarefa = None
        form_screen.titulo_input.text = ""
        form_screen.assunto_input.text = ""
        form_screen.data_input.text = ""
        form_screen.status_spinner.text = "Baixo"

    def on_pre_enter(self):
        self.reset_buttons_state()

    def atualizar_lista(self):
        self.list_layout.clear_widgets()
        tarefas = self.controller.listar_tarefas()  # Função do controller
        termo = self.search_field.text.strip().lower()
        if termo:
            tarefas = [t for t in tarefas if termo in t["titulo"].lower() or termo in t["assunto"].lower()]
        self.lista_tarefas = tarefas

        # Paginação
        total_pages = (len(tarefas) + self.items_per_page - 1) // self.items_per_page or 1
        if self.page > total_pages:
            self.page = total_pages
        start = (self.page - 1) * self.items_per_page
        end = start + self.items_per_page

        # Cabeçalho
        header = BoxLayout(size_hint_y=None, height=40, padding=(5,0))
        header.add_widget(MDLabel(text="[b]Título[/b]", halign="left", markup=True))
        header.add_widget(MDLabel(text="[b]Status[/b]", halign="center", markup=True))
        header.add_widget(MDLabel(text="[b]Ações[/b]", halign="center", markup=True))
        self.list_layout.add_widget(header)

        for tarefa in tarefas[start:end]:
            row = BoxLayout(size_hint_y=None, height=40)
            row.add_widget(MDLabel(text=tarefa["titulo"], halign="left"))
            row.add_widget(MDLabel(text=tarefa["status"], halign="center"))

            # Botões de ação
            view_btn = MDIconButton(icon="eye", theme_text_color="Custom", text_color=(0,0,1,1))
            view_btn.bind(on_release=lambda x, t=tarefa: self.visualizar_tarefa(t))
            row.add_widget(view_btn)

            edit_btn = MDIconButton(icon="pencil", theme_text_color="Custom", text_color=(0,1,0,1))
            edit_btn.bind(on_release=lambda x, t=tarefa: self.editar_tarefa(t))
            row.add_widget(edit_btn)

            del_btn = MDIconButton(icon="trash-can", theme_text_color="Custom", text_color=(1,0,0,1))
            del_btn.bind(on_release=lambda x, t=tarefa: self.confirmar_delete(t))
            row.add_widget(del_btn)

            self.list_layout.add_widget(row)

        # Atualiza estado dos botões de navegação
        self.prev_btn.disabled = self.page == 1
        self.next_btn.disabled = end >= len(self.lista_tarefas)

    def anterior_pagina(self, instance):
        if self.page > 1:
            self.page -= 1
            self.atualizar_lista()

    def proxima_pagina(self, instance):
        if self.page * self.items_per_page < len(self.lista_tarefas):
            self.page += 1
            self.atualizar_lista()

    # Funções de visualizar, editar e deletar
    def visualizar_tarefa(self, tarefa):
        detalhes = f"Título: {tarefa['titulo']}\nAssunto: {tarefa['assunto']}\nStatus: {tarefa['status']}"
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

    def editar_tarefa(self, tarefa):
        self.manager.current = "form_view"
        form_screen = self.manager.get_screen("form_view")
        form_screen.tarefa = tarefa
        form_screen.titulo_input.text = tarefa.get("titulo", "")
        form_screen.assunto_input.text = tarefa.get("assunto", "")

        # ✅ Correção aqui — garantir que data seja string no formato DD/MM/AAAA
        data_val = tarefa.get("data", "")
        if isinstance(data_val, datetime):
            form_screen.data_input.text = data_val.strftime("%d/%m/%Y")
        else:
            form_screen.data_input.text = str(data_val) if data_val else ""

        form_screen.status_spinner.text = tarefa.get("status", "Baixo")

    def confirmar_delete(self, tarefa):
        dialog = MDDialog(
            title="Confirmar Exclusão",
            text=f"Deseja realmente excluir a tarefa '{tarefa['titulo']}'?",
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="Excluir",
                    on_release=lambda x: self.deletar_tarefa(dialog, tarefa)
                )
            ]
        )
        dialog.open()

    def deletar_tarefa(self, dialog, tarefa):
        dialog.dismiss()
        self.controller.deletar_tarefa(tarefa["id"])
        self.atualizar_lista()

# ---------- FORMULÁRIO ----------
class TarefaFormView(MDScreen):
    def __init__(self, controller, tarefa=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.tarefa = tarefa

        # Layout com scroll
        scroll = ScrollView()
        self.layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20,
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter("height"))
        scroll.add_widget(self.layout)
        self.add_widget(scroll)

        # Campo título
        self.titulo_input = MDTextField(
            hint_text="Título",
            text=tarefa.get("titulo", "") if tarefa else ""
        )
        self.layout.add_widget(self.titulo_input)

        # Campo assunto
        self.assunto_input = MDTextField(
            hint_text="Assunto",
            text=tarefa.get("assunto", "") if tarefa else ""
        )
        self.layout.add_widget(self.assunto_input)

        # Campo data com botão para abrir calendário
        data_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)

        if tarefa and "data" in tarefa:
            data_val = tarefa["data"]
            if isinstance(data_val, datetime):
                data_text = data_val.strftime("%d/%m/%Y")
            else:
                data_text = str(data_val)
        else:
            data_text = datetime.now().strftime("%d/%m/%Y")

        self.data_input = MDTextField(
            hint_text="Data (DD/MM/AAAA)",
            text=data_text,
            readonly=True
        )

        data_btn = MDRaisedButton(text="📅", size_hint_x=None, width=50)
        data_btn.bind(on_release=self.abrir_calendario)

        data_layout.add_widget(self.data_input)
        data_layout.add_widget(data_btn)
        self.layout.add_widget(data_layout)

        # Campo status com Spinner
        status_inicial = tarefa.get("status", "Baixo") if tarefa else "Baixo"
        self.status_spinner = Spinner(
            text=status_inicial,
            values=["Baixo", "Médio", "Alto"],
            size_hint=(1, None),
            height=48
        )
        self.layout.add_widget(self.status_spinner)

        # Botão salvar
        self.salvar_btn = MDRaisedButton(text="Salvar", pos_hint={"center_x": 0.5})
        self.salvar_btn.bind(on_release=self.salvar_tarefa)
        self.layout.add_widget(self.salvar_btn)

        # Botão voltar
        self.voltar_btn = MDRaisedButton(text="Voltar", pos_hint={"center_x": 0.5})
        self.voltar_btn.bind(on_release=self.voltar)
        self.layout.add_widget(self.voltar_btn)

    # ====================== FUNÇÕES DE CRUD ======================
    def salvar_tarefa(self, instance):
        if not self.titulo_input.text.strip():
            self.mostrar_erro("O título não pode estar vazio.")
            return
        if not self.assunto_input.text.strip():
            self.mostrar_erro("O assunto não pode estar vazio.")
            return
        if self.status_spinner.text not in ["Baixo", "Médio", "Alto"]:
            self.mostrar_erro("Selecione um status válido.")
            return

        tarefa = {
            "id": self.tarefa["id"] if self.tarefa else None,
            "titulo": self.titulo_input.text.strip(),
            "assunto": self.assunto_input.text.strip(),
            "data": self.data_input.text.strip(),
            "status": self.status_spinner.text,
        }

        self.controller.salvar_tarefa(tarefa)

        dialog = MDDialog(
            title="Sucesso",
            text="Tarefa cadastrada/atualizada com sucesso!",
            buttons=[MDRectangleFlatButton(text="OK", on_release=lambda x: self.fechar_dialog(dialog))]
        )
        dialog.open()

    def mostrar_erro(self, msg):
        dialog = MDDialog(
            title="Erro",
            text=msg,
            buttons=[MDRectangleFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def fechar_dialog(self, dialog):
        dialog.dismiss()
        self.manager.current = "main_view"

    # ====================== VOLTAR ======================
    def voltar(self, instance):
        # Resetar botões para evitar ripple/sombra
        for btn in [self.salvar_btn, self.voltar_btn]:
            btn.state = "normal"
            btn.elevation = 6
        self.manager.current = "main_view"

    # ====================== CALENDÁRIO ======================
    def abrir_calendario(self, instance):
        self.mes_atual, self.ano_atual = datetime.now().month, datetime.now().year
        try:
            dia, mes_campo, ano_campo = map(int, self.data_input.text.split("/"))
            self.mes_atual = mes_campo
            self.ano_atual = ano_campo
        except:
            pass

        self.popup = Popup(title="Selecione a data", size_hint=(0.9, 0.9))
        self.atualizar_calendario()
        self.popup.open()

    def atualizar_calendario(self):
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Cabeçalho
        header = BoxLayout(size_hint_y=None, height=40, spacing=10)
        prev_btn = Button(text="<", size_hint_x=None, width=40)
        next_btn = Button(text=">", size_hint_x=None, width=40)
        month_label = Label(text=f"{calendar.month_name[self.mes_atual]} {self.ano_atual}")
        header.add_widget(prev_btn)
        header.add_widget(month_label)
        header.add_widget(next_btn)
        main_layout.add_widget(header)

        # Dias da semana
        week_layout = GridLayout(cols=7, size_hint_y=None, height=30, spacing=5)
        for day in ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]:
            lbl = Label(text=day, halign="center")
            lbl.bind(size=lbl.setter("text_size"))
            week_layout.add_widget(lbl)
        main_layout.add_widget(week_layout)

        # Dias do mês
        cal_layout = GridLayout(cols=7, spacing=5, size_hint_y=None)
        _, num_dias = calendar.monthrange(self.ano_atual, self.mes_atual)
        first_weekday = calendar.monthrange(self.ano_atual, self.mes_atual)[0]

        for _ in range((first_weekday + 6) % 7):
            cal_layout.add_widget(Label(text=""))

        for d in range(1, num_dias + 1):
            btn = Button(text=str(d), size_hint_y=None, height=40)
            btn.bind(on_release=lambda inst, dia=d: self.selecionar_data_popup(dia))
            cal_layout.add_widget(btn)

        linhas = ((num_dias + (first_weekday + 6) % 7 - 1) // 7) + 1
        cal_layout.height = linhas * 45
        main_layout.add_widget(cal_layout)

        prev_btn.bind(on_release=lambda x: self.navegar_mes(-1))
        next_btn.bind(on_release=lambda x: self.navegar_mes(1))

        self.popup.content = main_layout

    def navegar_mes(self, delta):
        self.mes_atual += delta
        if self.mes_atual < 1:
            self.mes_atual = 12
            self.ano_atual -= 1
        elif self.mes_atual > 12:
            self.mes_atual = 1
            self.ano_atual += 1
        self.atualizar_calendario()

    def selecionar_data_popup(self, dia):
        self.data_input.text = f"{dia:02d}/{self.mes_atual:02d}/{self.ano_atual}"
        self.popup.dismiss()
