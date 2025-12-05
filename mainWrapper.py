import subprocess
import time

while True:
    print("\n==============================")
    print("Iniciando simulação...")
    print("==============================\n")

    # roda seu script
    p = subprocess.run(["python", "main.py"])

    # Se o script terminou sem erro, sair do loop
    if p.returncode == 0:
        print("Script terminou sem erro. Encerrando.")
        break
    
    # Se deu erro, reinicia
    print("O script falhou (returncode:", p.returncode, ")")
    print("Reiniciando em 3 segundos...\n")
    time.sleep(3)
