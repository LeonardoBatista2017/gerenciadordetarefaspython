from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from controllers.tarefa_controller import TarefaController
from views.tarefaform import MainView, TarefaFormView   # agora vem tudo do mesmo arquivo

class GerenciadorTarefasApp(MDApp):
    def build(self):
        self.controller = TarefaController()
        self.sm = ScreenManager()

        # adiciona as telas
        self.main_view = MainView(controller=self.controller, name="main_view")
        self.form_view = TarefaFormView(controller=self.controller, name="form_view")

        self.sm.add_widget(self.main_view)
        self.sm.add_widget(self.form_view)

        return self.sm

if __name__ == "__main__":
    GerenciadorTarefasApp().run()
