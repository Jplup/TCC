from PyLTSpice import SimRunner, SpiceEditor, LTspice  # + LTspice simulator
import ltspice
import matplotlib.pyplot as plt
import os

# Caminhos
asc_path = r"C:\Users\João Pedro\Desktop\Modulador\circuit.asc"
# você pode informar o simulador fazendo algo como `simulator=LTspice` no SimRunner

# Cria o runner — não use `exe_path`, use `simulator=LTspice`
runner = SimRunner(output_folder="./saida", simulator=LTspice)

# Cria editor para o circuito
editor = SpiceEditor(asc_path)

# (Opcional) Alterações no circuito antes da simulação:
# editor.set_component_value('R1', '10k')

# Executa simulação
raw_path, log_path = runner.run_now(editor)
print("Executado. RAW:", raw_path, "LOG:", log_path)

# Lê o resultado usando a lib ltspice que você já utiliza
l = ltspice.Ltspice(raw_path)
l.parse()

t = l.get_time()
vout = l.getData('V(v_comp)')

# Plota
plt.plot(t, vout)
plt.xlabel("Tempo (s)")
plt.ylabel("V(v_comp)")
plt.grid(True)
plt.show()
