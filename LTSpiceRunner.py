from PyLTSpice import SimRunner, SpiceEditor, LTspice  
import ltspice
from pathlib import Path

def Run(nodeNames=['V(v_comp)','V(v_comp_sat)'],gainPGA=1):
    asc_path = Path(__file__).parent / "circuit.asc"

    runner = SimRunner(simulator=LTspice)
    editor = SpiceEditor(asc_path)

    r1=10000*(gainPGA-1)
    if r1<10: r1=10


    editor.set_component_value("R_PGA",str(int(r1)))

    raw_path, log_path = runner.run_now(editor)

    l = ltspice.Ltspice(raw_path)
    l.parse()

    waves = {"t": l.get_time()}
    for nodeName in nodeNames:
        try:
            waves[nodeName] = l.getData(nodeName)
        except:
            print(f"Nó {nodeName} não encontrado")

    return waves


'''from PyLTSpice import SimRunner, SpiceEditor, LTspice
import ltspice
from pathlib import Path

def Run(nodeNames=['V(v_comp)','V(v_comp_sat)']):
    asc_path = Path(__file__).parent / "circuit.asc"
    runner=SimRunner(simulator=LTspice)
    editor=SpiceEditor(asc_path)
    raw_path,log_path=runner.run_now(editor)
    l=ltspice.Ltspice(raw_path)
    l.parse()
    waves={}
    t=l.get_time()
    waves["t"]=t
    for nodeName in nodeNames:
        try:
            waves[nodeName]=l.getData(nodeName)
        except:
            print("Node",nodeName,"deu erro")
            
    return waves'''