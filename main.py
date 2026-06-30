import os
import sys
import webview
from controller.controller import ControladorAgenda

class Logger:
    def __init__(self, status_log):
        self.status_log = status_log
        self.caminho = 'logs.txt'

    def escrever(self, texto: str):
        if self.status_log:
            with open(self.caminho, 'a', encoding='UTF-8') as arquivo:
                arquivo.writelines(texto + '\n')

def obter_caminho_html():
    if hasattr(sys, '_MEIPASS'):
        pasta_base = sys._MEIPASS
    else:
        pasta_base = os.path.dirname(os.path.abspath(__file__))
        
    caminho_index = os.path.join(pasta_base, "view", "index.html")
    
    if not os.path.exists(caminho_index):
        print(f"Erro: index.html não encontrado em {caminho_index}")
        sys.exit(1)
    return caminho_index

def iniciar_app(status_log=False):
    logger = Logger(status_log=status_log)
    controlador = ControladorAgenda(logger)
    caminho_html = obter_caminho_html()

    webview.create_window(
        title="clique.agenda",
        url=caminho_html,
        js_api=controlador,
        width=1024,
        height=720,
        min_size=(800, 600)
    )
    webview.start()

def criar_executavel():
    os.system('pyinstaller --onefile --windowed --clean --add-data "view;view" --name="clique.agenda" main.py')

def mostrar_menu():
    print("Escolha uma opção:")
    print("(1) Criar executavel")
    print("(2) Abrir app")
    comando = input(">:").strip()
    
    if comando == "1":
        criar_executavel()
    else:
        iniciar_app(status_log=True)

if __name__ == "__main__":
    e_executavel = getattr(sys, "frozen", False)

    if e_executavel:
        iniciar_app()
    else:
        mostrar_menu()