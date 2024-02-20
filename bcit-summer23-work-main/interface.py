
from revision.formula import Formula
from revision.operator import Operator
from revision.valuation import Valuation
from revision.belief_solver import evaluate_formula
from revision.utils import expand_belief
from revision import revision
from revision.revision import trust_revise_beliefs
from revision.revision import TrustThreshold
from revision.distance_finder import HammingDistanceFinder
from revision.distance_finder import WeightedHammingFinder
from revision.distance_finder import ParamDistanceFinder

from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
import logging

# The format of this file:
# - Classes that display GUI elements that can be added/removed
# - Functions that implement button/widget functionality
# - Layout of base GUI
# Functions share namespace with the GUI definitions, so direct references
# to GUi elements defined at the bottom of the file are common.

#logging.basicConfig(level=logging.DEBUG)

def main():

    # display state class

    class BeliefDisplay:

        belief_display_list = []
        belief_params = []

        def __init__(self, master, belief, mode="init"):

            if mode == "init" and BeliefDisplay.display_count() > 0:
                raise Exception("Attempting to create 2 init states")

            BeliefDisplay.belief_display_list.append(self)
            #logging.debug(f"New belief display w belief {belief.belief_state}")
            
            self.belief = belief
            self.master = master
            self.mode = mode
            s.configure('BeliefDisplay.TFrame', relief="sunken")
            self.widget = Frame(self.master, style='BeliefDisplay.TFrame')
            
            self.label = Label(self.widget)

            if self.mode == "init":
                self.xbutton = Button(self.widget, text="X",
                                      command=BeliefDisplay.delete_all_widgets,
                                      width=5)
                BeliefDisplay.belief_params = self.belief.belief_state[0].keys()
            else:
                self.xbutton = Button(self.widget, text="X",
                                      command=self.delete_widget, width=5)

            self.update_belief_display()                

            self.label.pack(padx=5, side="left")
            self.xbutton.pack(anchor="ne")
            self.widget.pack(ipadx=5, ipady=5, padx=5, pady=5, fill='x')

            BeliefDisplay.recalculate_master_height(self.master)

        # revision methods

        @classmethod
        def revise_all_states(cls):
            logging.debug(f"Agent states: {current_agents}")
            initial_belief = cls.belief_display_list[0].belief
            new_beliefs = [item.belief for item in cls.belief_display_list[1:]]
            if cls.belief_display_list[-1].mode == "out":
                cls.belief_display_list[-1].delete_widget()
                new_beliefs.pop()
            distance_finder_map = {
                "0": HammingDistanceFinder,
                "1": WeightedHammingFinder,
                "2": ParamDistanceFinder
            }
            new_distance = distance_finder_map[var_distfinder.get()]()
            new_thresholds = TrustThreshold(**threshold_values)
            final_belief = trust_revise_beliefs(initial_belief,
                                                current_weights,
                                                *new_beliefs,
                                                trusted_agents=current_agents,
                                                distance_finder=new_distance,
                                                trust_thresholds=new_thresholds)
            #logging.debug(f"Revision gui output: {final_belief}")
            BeliefDisplay(outputpack, final_belief, "out")
            AgentDisplay.update()

        # gui methods

        def update_belief_display(self):
            self.label["text"] = ""

            if self.mode == "init":
                self.label["text"] += "Initial state"
            elif self.mode == "obs":
                self.label["text"] += "Observation\t"
                self.label["text"] += f"Formula: {str(self.belief.formula)}"
            elif self.mode == "agent":
                self.label["text"] += f"Agent: {self.belief.agent}\t"
                self.label["text"] += f"Formula: {str(self.belief.formula)}"
            elif self.mode == "out":
                self.label["text"] += "Output"
            
            # if var_simpleview.get() == "1":

                # if not self.mode == "obs" or self.mode == "agent":
                #     self.label["text"] += "\n"
                #     simple_keys = dict()                    
                #     for valuation in self.belief.belief_state:
                #         for key in valuation:
                #             if key not in simple_keys:
                #                 simple_keys[key] = valuation[key]
                #             elif simple_keys[key] != valuation[key]:
                #                 simple_keys[key] = "Maybe"
                #     for key in simple_keys:
                #         self.label["text"] += f"{simple_keys[key]}\t"
                        
            if var_simpleview.get() == "1" and self.mode in "obsagent":
                pass
            else:
                self.label["text"] += "\n"
                for key in BeliefDisplay.belief_params:
                    self.label["text"] += f"{key}\t"
                for valuation in self.belief.belief_state:
                    self.label["text"] += "\n"
                    #for value in valuation.values():
                    for key in BeliefDisplay.belief_params:
                        self.label["text"] += f"{valuation[key]}\t"

        def delete_widget(self):
            BeliefDisplay.belief_display_list.remove(self)
            self.widget.destroy()
            BeliefDisplay.recalculate_master_height(self.master)
            if BeliefDisplay.display_count() == 0:
                var_agent_radio = "init"                
                rad_obs["state"] = "disabled"
                rad_agent["state"] = "disabled"
                ent_agent["state"] = "disabled"
                current_agents.clear()
                AgentDisplay.update()
                current_weights.clear()
                ParamDisplay.update()

        @classmethod
        def delete_all_widgets(cls):
            if messagebox.askyesno("Question", "Delete all current states?"):
                for item in cls.belief_display_list[:]:
                    item.delete_widget()

        @classmethod
        def recalculate_master_height(cls, master):
            master.update()
            req_height = 0
            for item in cls.belief_display_list:
                req_height += item.widget.winfo_reqheight() + 20 # padding extra
            master.config(height=req_height)

        @classmethod
        def update_all_displays(cls):
            for item in cls.belief_display_list:
                item.update_belief_display()
            cls.recalculate_master_height(outputpack)

        @classmethod
        def display_count(cls):
            return len(cls.belief_display_list)

        @classmethod
        def get_init_belief(cls):
            return cls.belief_display_list[0].belief.belief_state
        

    class AgentDisplay:

        def __init__(self, agent):
            self.agent = agent
            agentframe = Frame(trustgrid)
            Label(agentframe, text=f"Agent: {self.agent} Trust:").pack()
            self.trust = StringVar(value=current_agents[self.agent])
            self.trust_display = Label(agentframe)
            self.trust_display.pack()
            self.set_trust(self.trust.get())
            Scale(agentframe, orient="horizontal", from_=0, to=100,
                  variable=self.trust, command=self.set_trust).pack()
            for child in agentframe.winfo_children():
                child.pack_configure(side="left", padx=5, pady=5)
            agentframe.pack()

        def set_trust(self, value):
            self.trust_display["text"] = "%.0f" % float(value)
            current_agents[self.agent] = int(float(value))

        @classmethod
        def reset_trust(cls):
            for agent in current_agents:
                current_agents[agent] = 100
            cls.update()

        @classmethod
        def update(cls):
            for child in trustgrid.winfo_children():
                if not isinstance(child, Button):
                    child.destroy()
            for agent in current_agents:
                AgentDisplay(agent)

                
    class ParamDisplay:

        def __init__(self, param):
            self.param = param
            paramframe = Frame(paramweightgrid)
            Label(paramframe, text=f"Parameter {self.param} value:").pack()
            self.weight = StringVar(value=current_weights[self.param])
            self.spinbox = Spinbox(paramframe, from_=1.0, to=100.0,
                                   increment=1.0, textvariable=self.weight,
                                   command=self.set_weight)
            self.spinbox.state(["readonly"])
            self.spinbox.pack()
            for child in paramframe.winfo_children():
                child.pack_configure(side="left", padx=5, pady=5)
            paramframe.pack()

        def set_weight(self):
            current_weights[self.param] = int(float(self.weight.get()))

        @classmethod
        def update(cls):
            logging.debug(f"Updating to match params: {current_weights}")
            for child in paramweightgrid.winfo_children():
                child.destroy()
            for param in current_weights:
                ParamDisplay(param)
                

    # functions

    def choose_test_file():
        filename = filedialog.askopenfilename(initialdir=".")
        with open(filename, encoding="utf8") as openfile:

            init_state = openfile.readline().replace("\n", "")
            init_formulas = init_state.split("/")
            for formula_str in init_formulas:
                formula = Formula(formula_str)
                belief = evaluate_formula(formula)
                add_formula(belief, formula, None, "init")

            param_weights = openfile.readline().replace("\n", "")
            # deal with param weighs

            for line in openfile:
                line = line.replace("\n", "").split(":")
                agent, formula_str = line
                # if len(line) > 1:
                #     agent, formula = line
                # else:
                #     agent, formula = None, line[0]
                mode = "obs" if agent == "" else "agent"
                if agent == "":
                    agent = None
                formula = Formula(formula_str)
                belief = evaluate_formula(formula)
                add_formula(belief, formula, agent, mode)

        rad_obs["state"] = "normal"
        rad_agent["state"] = "normal"
        ent_agent["state"] = "normal"

    # formula, agents, and weights in use by interface
    current_formula = []
    current_agents = {}
    current_weights = {}

    # inc/dec and threshold values
    threshold_values = {
        "obs_decrease":revision.TRUST_OBS_DECREASE,
        "obs_increase":revision.TRUST_OBS_INCREASE,
        "decrease":revision.TRUST_DECREASE,
        "increase":revision.TRUST_INCREASE,
        "notrust_threshold":revision.NOTRUST_THRESHOLD,
        "diff_threshold":revision.DIFF_THRESHOLD,
    }
    
    # interface related functions
    
    def add_proposition(*args):
        proposition = new_prop.get()
        if proposition != "":
            current_formula.append(proposition)
            update_formula_display()
            ent_prop.delete(0, END)

    def add_operator(operator):
        current_formula.append(Operator(operator))
        update_formula_display()

    def update_formula_display():
        op_print_map = {Operator.AND: chr(8743),
                        Operator.OR: chr(8744),
                        Operator.IMPLY: chr(8594)}
        formula_copy = current_formula.copy()
        for index, item in enumerate(current_formula):
            if item in op_print_map:
                formula_copy[index] = op_print_map[item]
            elif isinstance(item, Operator):
                formula_copy[index] = item.value
        formula_str = " ".join(formula_copy)
        var_formula.set(formula_str)

    def formula_backspace():
        if len(current_formula) > 0:
            del current_formula[-1]
            update_formula_display()

    def add_formula_button():
        
        if current_formula == []:
            return None

        else:
            try:
                evaluate_formula(Formula(current_formula))
            except Exception as e:
                messagebox.showerror(message="Error creating formula")
                return None

        new_formula = Formula(current_formula)
        new_belief = evaluate_formula(new_formula)

        # check if parameters of new function match init state
        if BeliefDisplay.display_count() > 0:
            init_belief = BeliefDisplay.get_init_belief()
            for param in new_belief[0].keys():
                if param not in init_belief[0].keys():
                    messagebox.showwarning(message="New function parameters not in initial function")
                    return None
            new_belief = expand_belief(new_belief, init_belief)
        
        new_mode = var_agent_radio.get()
        new_agent = None if new_mode != "agent" else var_agent.get()
        if new_agent == "" and new_mode == "agent":
            new_agent = None
            new_mode = "obs"

        add_formula(new_belief, new_formula, new_agent, new_mode)
                
        BeliefDisplay.update_all_displays()
        current_formula.clear()
        update_formula_display()

        #enable radio buttons
        rad_obs["state"] = "normal"
        rad_agent["state"] = "normal"
        ent_agent["state"] = "normal"

    def add_formula(belief, formula, agent, mode):

        if agent is not None and agent != "" and agent not in current_agents.keys():
            current_agents.update({agent: 100})
            AgentDisplay.update()

        if BeliefDisplay.display_count() == 0:
            for param in formula.param_list:
                current_weights[param] = 1
            ParamDisplay.update()
        
        if mode == "init" and BeliefDisplay.display_count() > 0:
            init_belief = BeliefDisplay.get_init_belief()
            init_belief.extend(item for item in belief
                               if item not in init_belief)
            BeliefDisplay.update_all_displays()
        else:
            new_valuation = Valuation(belief, agent, formula)
            new_display = BeliefDisplay(outputpack, new_valuation, mode)

    # create a window to edit increase, decrease, and threshold values
    def window_threshold_values():
        win_threshold = Toplevel(window)
        win_threshold.title("Trust and threshold values")

        Label(win_threshold, text="Trust observation increase:").grid(row=0, column=0)
        var_obs_increase = StringVar(value=threshold_values["obs_increase"])
        Spinbox(win_threshold, from_=0.0, to=100.0, increment=0.1,
                textvariable=var_obs_increase).grid(row=0, column=1)
        Label(win_threshold,
              text="""Trust values for an agent which agrees with an observation
will be modified by this amount multiplicatively.
Default is a small increase.""").grid(row=1, column=0, columnspan=2)

        Label(win_threshold, text="Trust observation decrease:").grid(row=2, column=0)
        var_obs_decrease = StringVar(value=threshold_values["obs_decrease"])
        Spinbox(win_threshold, from_=0.0, to=100.0, increment=0.1,
                textvariable=var_obs_decrease).grid(row=2, column=1)
        Label(win_threshold,
              text="""Trust values for an agent which disagrees with an observation
will be modified by this amount multiplicatively.
Default is a large decrease.""").grid(row=3, column=0, columnspan=2)

        Label(win_threshold, text="Trust increase:").grid(row=4, column=0)
        var_increase = StringVar(value=threshold_values["increase"])
        Spinbox(win_threshold, from_=0.0, to=100.0, increment=0.1,
                textvariable=var_increase).grid(row=4, column=1)
        Label(win_threshold,
              text="""Trust values for an agent which agrees with a higher-trusted
agent will be modified by this amount multiplicatively.
Default is a very small increase.""").grid(row=5, column=0, columnspan=2)

        Label(win_threshold, text="Trust decrease:").grid(row=6, column=0)
        var_decrease = StringVar(value=threshold_values["decrease"])
        Spinbox(win_threshold, from_=0.0, to=100.0, increment=0.1,
                textvariable=var_decrease).grid(row=6, column=1)
        Label(win_threshold,
              text="""Trust values for an agent which disagrees with a higher-trusted
agent will be modified by this amount multiplicatively.
Default is a small decrease.""").grid(row=7, column=0, columnspan=2)        

        Label(win_threshold, text="No trust threshold:").grid(row=8, column=0)
        var_notrust = StringVar(value=threshold_values["notrust_threshold"])
        Spinbox(win_threshold, from_=0.0, to=100.0, increment=1,
                textvariable=var_notrust).grid(row=8, column=1)
        Label(win_threshold,
              text="""Agents who have less than this amount of trust will not be
included in the revision process.""").grid(row=9, column=0, columnspan=2)

        Label(win_threshold, text="Trust difference threshold:").grid(row=10, column=0)
        var_diff = StringVar(value=threshold_values["diff_threshold"])
        Spinbox(win_threshold, from_=0.0, to=100.0, increment=1,
                textvariable=var_diff).grid(row=10, column=1)
        Label(win_threshold,
              text="""If two agents disagree on information,
and the trust difference between them is
this amount or greater, the less trusted
agent will be ignored and its trust reduced.
If they agree, the less trusted agent's
trust will be increased.""").grid(row=11, column=0, columnspan=2)

        def apply_threshold_values():
            threshold_values["obs_increase"] = float(var_obs_increase.get())
            threshold_values["obs_decrease"] = float(var_obs_decrease.get())
            threshold_values["increase"] = float(var_increase.get())
            threshold_values["decrease"] = float(var_decrease.get())
            threshold_values["notrust_threshold"] = float(var_notrust.get())
            threshold_values["diff_threshold"] = float(var_diff.get())
            win_threshold.destroy()

        Button(win_threshold, text="Apply",
               command=apply_threshold_values).grid(row=12, column=0, columnspan=2)

        for child in win_threshold.winfo_children():
            child.grid_configure(padx=10, pady=10)

    # display

    window = Tk()
    s = Style()
    window.title("Revision interface")
    window.option_add("*tearOff", FALSE)

    # menu

    menubar = Menu(window)
    window["menu"] = menubar
    menu_file = Menu(menubar)
    menubar.add_cascade(menu=menu_file, label="File")
    menu_edit = Menu(menubar)
    menubar.add_cascade(menu=menu_edit, label="Edit")
    menu_view = Menu(menubar)
    menubar.add_cascade(menu=menu_view, label="View")

    menu_file.add_command(label="Load testcase from file...",
                          command=choose_test_file)
    var_distfinder = StringVar(value=0)
    menu_edit.add_radiobutton(label="Hamming Distance",
                              variable=var_distfinder, value=0)
    menu_edit.add_radiobutton(label="Weighted Hamming Distance",
                              variable=var_distfinder, value=1)
    #menu_edit.add_radiobutton(label="Parametrized Distance",
    #                          variable=var_distfinder, value=2)
    # implementation of parametrized distance identical to weighted hamming
    menu_edit.add_separator()
    menu_edit.add_command(label="Change trust and threshold values",
                          command=window_threshold_values)
    var_simpleview = StringVar(value=0)
    menu_view.add_checkbutton(label="Use simple view", variable=var_simpleview,
                              onvalue=1, offvalue=0,
                              command=BeliefDisplay.update_all_displays)

    # content
    
    content = Frame(window, padding="12 12 12 12")
    content.grid(sticky="nwes")
    content.rowconfigure(0, weight=1)
    content.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)

    # noteboox

    entrybook = Notebook(content)
    entrybook.grid(row=0, column=0)

    # formula entry window

    formulagrid = Frame(entrybook)
    entrybook.add(formulagrid, text=" Formula entry ")
    
    lbl_entry = Label(formulagrid, text="Enter formula:")
    lbl_entry.grid(row=0, column=0)

    var_formula = StringVar()
    lbl_formula = Label(formulagrid, textvariable=var_formula,
                        font="-weight bold")
    lbl_formula.grid(row=1, column=0)
    btn_back = Button(formulagrid, text="Backspace",
                      width=13, command=formula_backspace)
    btn_back.grid(row=1, column=0, sticky="ne")
    btn_enterf = Button(formulagrid, text="Add formula",
                        width=13, command=add_formula_button)
    btn_enterf.grid(row=1, column=0, sticky="se")
    formulagrid.rowconfigure(1, pad=25)

    propgrid = Frame(formulagrid)
    Label(propgrid, text="Proposition:").grid(row=0, column=0)
    new_prop = StringVar()
    ent_prop = Entry(propgrid, textvariable=new_prop)
    ent_prop.grid(row=0, column=1)
    Button(propgrid, text="Add", command=add_proposition).grid(row=0, column=2)
    propgrid.grid(row=2, column=0)
    for child in propgrid.winfo_children():
        child.grid_configure(padx=8, pady=8)

    operatorgrid = Frame(formulagrid)
    Button(operatorgrid, text="(",
           command=lambda: add_operator("(")).grid(row=0, column=0)
    Button(operatorgrid, text=")",
           command=lambda: add_operator(")")).grid(row=0, column=1)
    Button(operatorgrid, text="!",
           command=lambda: add_operator("!")).grid(row=0, column=2)
    Button(operatorgrid, text="\u2227",
           command=lambda: add_operator("^")).grid(row=0, column=3)
    Button(operatorgrid, text="\u2228",
           command=lambda: add_operator("v")).grid(row=0, column=4)
    Button(operatorgrid, text="\u2192",
           command=lambda: add_operator(">")).grid(row=0, column=5)
    Button(operatorgrid, text="=",
           command=lambda: add_operator("=")).grid(row=0, column=6)
    operatorgrid.grid(row=3, column=0)

    agentgrid = Frame(formulagrid)
    var_agent_radio = StringVar(value="init")
    Radiobutton(agentgrid, text="Initial state",
                variable=var_agent_radio, value="init").grid(row=0, column=0)
    rad_obs = Radiobutton(agentgrid, text="Observation", state="disabled",
                variable=var_agent_radio, value="obs")
    rad_obs.grid(row=0, column=1)
    rad_agent = Radiobutton(agentgrid, text="Agent:", state="disabled",
                variable=var_agent_radio, value="agent")
    rad_agent.grid(row=0, column=2)
    var_agent = StringVar()
    ent_agent = Entry(agentgrid, textvariable=var_agent, state="disabled")
    ent_agent.grid(row=0, column=3, padx=5)
    agentgrid.grid(row=4, column=0)

    for child in formulagrid.winfo_children():
        child.grid_configure(padx=5, pady=5)

    #formulagrid.columnconfigure(0, weight=1)

    # actor trust entry

    trustgrid = Frame(entrybook)
    entrybook.add(trustgrid, text=" Agent trust entry ")
    Button(trustgrid, text="Set all trust values to max",
           command=AgentDisplay.reset_trust).pack(padx=5, pady=5)

    # param weights entry

    paramweightgrid = Frame(entrybook)
    entrybook.add(paramweightgrid, text=" Parameter weight entry ")

    # calculate output button

    Button(content, text="Calculate output",
           command=BeliefDisplay.revise_all_states).grid(row=1, column=0)

    # output window

    outputcanvas = Canvas(content, width=400)
    outputcanvas.grid(row=0, column=1, sticky='nesw')
    
    scr_output = Scrollbar(content, orient="vertical", command=outputcanvas.yview)
    scr_output.grid(row=0, column=2, sticky="ns")

    # s.configure("out.TFrame", background="red")    
    outputpack = Frame(outputcanvas, width=400) # style="out.TFrame")
    outputpack.pack(fill=BOTH)
    outputpack.pack_propagate(False)

    # scrollable frame magic
    outputpack.bind(
        "<Configure>",
        lambda e: outputcanvas.configure(
            scrollregion=outputcanvas.bbox("all")
        )
    )
    outputcanvas.create_window((0, 0), window=outputpack, anchor="nw")
    outputcanvas.configure(yscrollcommand=scr_output.set)

    # content weights
    content.columnconfigure(0, weight=1)
    content.columnconfigure(1, weight=1, minsize=100)

    window.mainloop()

if __name__ == "__main__":
    main()
