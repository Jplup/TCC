from PyLTSpice import SimRunner, SpiceEditor, LTspice  # + LTspice simulator
import ltspice

def Run(nodeNames=['V(v_comp)','V(v_ref)']):
    asc_path=r"C:\Users\João Pedro\Desktop\Modulador\circuit.asc"
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
    return waves
