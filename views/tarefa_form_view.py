from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from datetime import datetime
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import calendar


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
        data_layout = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)

        # Converter data corretamente
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
        salvar_btn = MDRaisedButton(
            text="Salvar",
            pos_hint={"center_x": 0.5}
        )
        salvar_btn.bind(on_release=self.salvar_tarefa)
        self.layout.add_widget(salvar_btn)

        # Botão voltar
        voltar_btn = MDRaisedButton(
            text="Voltar",
            pos_hint={"center_x": 0.5}
        )
        voltar_btn.bind(on_release=self.voltar)
        self.layout.add_widget(voltar_btn)

    # ====================== FUNÇÕES DE CRUD ======================

    def salvar_tarefa(self, instance):
        # Validação
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
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.fechar_dialog(dialog))]
        )
        dialog.open()

    def mostrar_erro(self, msg):
        dialog = MDDialog(
            title="Erro",
            text=msg,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def fechar_dialog(self, dialog):
        dialog.dismiss()
        self.manager.current = "main_view"

    def voltar(self, instance):
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
