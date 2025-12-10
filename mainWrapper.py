import subprocess
import time
from LTSpiceCleaner import Clean

Clean()

script="mainOnlyTIA.py"

while True:
    print("\n==============================")
    print("Iniciando simulação...")
    print("==============================\n")

    # roda seu script
    p = subprocess.run(["python", script])

    # Se o script terminou sem erro, sair do loop
    if p.returncode == 0:
        print("Script terminou sem erro. Encerrando.")
        break
    
    # Se deu erro, reinicia
    print("O script falhou (returncode:", p.returncode, ")")

    Clean()
    print("Removeu as coisas")
    print("Reiniciando em 3 segundos...\n")
    time.sleep(3)
