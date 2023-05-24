import os.path
from tkinter import *
from agents import *
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def agent_label(agt):
    """creates a label based on direction"""
    dir = agt.direction
    lbl = 'v'
    if dir.direction == Direction.U:
        lbl = '^'
    elif dir.direction == Direction.L:
        lbl = '<'
    elif dir.direction == Direction.R:
        lbl = '>'

    return lbl

def is_agent_label(lbl):
    """determines if the label is one of the labels tht agents have: ^ v < or >"""
    return lbl == '^' or lbl == 'v' or lbl == '<' or lbl == '>'

class Gui(VacuumEnvironment):
    """This is a two-dimensional GUI environment. Each location may be
    dirty, clean or can have a wall. The user can change these at each step.
    """
    xi, yi = (0, 0)
    perceptible_distance = 1
    agentTypes = ['ReflexAgent', 'RuleAgent', "NoAgent"]

    def __init__(self, root, width=7, height=7):
        print("creating xv with width ={} and height={}".format( width, height))
        super().__init__(width, height)

        self.root = root
        self.create_frames(height)
        self.create_buttons(width)
        self.create_walls()
        self.agentType = self.agentTypes[0]
        self.secondAgentType = self.agentTypes[2]   # no second agent at start.

    def create_frames(self, h):
        """Adds frames to the GUI environment."""
        self.frames = []
        for _ in range(h):
            frame = Frame(self.root, bg='blue')
            frame.pack(side='bottom')
            self.frames.append(frame)

    def create_buttons(self, w):
        """Adds buttons to the respective frames in the GUI."""
        self.buttons = []
        for frame in self.frames:
            button_row = []
            for _ in range(w):
                button = Button(frame, bg='white', height=2, width=3, padx=2, pady=2)
                button.config(command=lambda btn=button: self.toggle_element(btn))
                button.pack(side='left')
                button_row.append(button)
            self.buttons.append(button_row)

    def create_walls(self):
        """Creates the outer boundary walls which do not move."""
        for row, button_row in enumerate(self.buttons):
            if row == 0 or row == len(self.buttons) - 1:
                for button in button_row:
                    button.config(bg='red', text='W', state='disabled', disabledforeground='black')
            else:
                button_row[0].config(bg='red',text='W', state='disabled', disabledforeground='black')
                button_row[len(button_row) - 1].config(bg='red', text='W', state='disabled', disabledforeground='black')

    def add_agent(self, agt, xyloc):
        """add an agent to the GUI"""
        self.add_thing(agt, xyloc)
        # Place the agent in the centre of the grid.
        lbl = agent_label(agt)
        self.buttons[xyloc[1]][xyloc[0]].config(bg='blue', text=lbl)

    def toggle_element(self, button):
        """toggle the element type on the GUI."""
        bgcolor = button['bg']
        txt = button['text']
        if is_agent_label(txt):
            if bgcolor == 'grey':
                button.config(bg='white')
            else:
                button.config(bg='grey')
        else:
            if bgcolor == 'red':
                button.config(bg='grey', text='D')
            elif bgcolor == 'grey':
                button.config(bg='white', text='')
            elif bgcolor == 'white':
                button.config(bg='red', text='W')

    def execute_action(self, agent, action):
        """Determines the action the agent performs."""
        xi, yi = (self.xi, self.yi)
        print("agent at location (", xi, yi, ") and action ", action)
        if action == 'Suck':
            dirt_list = self.list_things_at(agent.location, Dirt)
            if dirt_list:
                dirt = dirt_list[0]
                agent.performance += 100
                self.delete_thing(dirt)
                self.buttons[yi][xi].config(bg='white')

        else:
            agent.bump = False
            if action == 'TurnRight':
                agent.direction += Direction.R
                self.buttons[yi][xi].config(text=agent_label(agent))
            elif action == 'TurnLeft':
                agent.direction += Direction.L
                self.buttons[yi][xi].config(text=agent_label(agent))
            elif action == 'Forward':
                agent.bump = self.move_to(agent, agent.direction.move_forward(agent.location))
                if not agent.bump:
                    self.buttons[yi][xi].config(bg = 'white', text='')
                    xf, yf = agent.location
                    self.buttons[yf][xf].config(bg = 'blue', text=agent_label(agent))

        if action != 'NoOp':
            agent.performance -= 1

        performance_label.config(text=str(agent.performance))

    def read_env(self):
        """read_env: This sets proper wall or Dirt status based on bg color"""
        agt_loc = self.agents[0].location

        """Reads the current state of the GUI environment."""
        for j, btn_row in enumerate(self.buttons):
            for i, btn in enumerate(btn_row):
                if (j != 0 and j != len(self.buttons) - 1) and (i != 0 and i != len(btn_row) - 1):
                    if self.some_things_at((i, j)) and (i, j) != agt_loc:
                        for thing in self.list_things_at((i, j)):
                            if not isinstance(thing, Agent):
                                self.delete_thing(thing)
                    if btn['bg'] == 'grey': # adding dirt
                        self.add_thing(Dirt(), (i, j))
                    elif btn['bg'] == 'red': # adding wall
                        self.add_thing(Wall(), (i, j))

    def update_env(self):
        """Updates the GUI environment according to the current state."""
        self.read_env()
        agt = self.agents[0]
        previous_agent_location = agt.location
        self.xi, self.yi = previous_agent_location
        self.step()


    def toggle_agentType(self):
        """toggles the type of the agent. Choices are 'Reflex' and 'RuleBased'."""
        if env.agentType == env.agentTypes[0]:
            env.agentType = env.agentTypes[1]
        else:
            env.agentType = env.agentTypes[0]

        print(", new agentType = ", env.agentType)
        agentType_button.config(text=env.agentType)

        self.reset_env()

#TODO: NEED TO FIX THE FUCKING RESET BUTTON
    def reset_env(self):
        """Resets the GUI environment to the initial clear state."""
        for j, btn_row in enumerate(self.buttons):
            for i, btn in enumerate(btn_row):
                if (j != 0 and j != len(self.buttons) - 1) and (i != 0 and i != len(btn_row) - 1):
                    if self.some_things_at((i, j)) :
                        for thing in self.list_things_at((i, j)):
                            if not isinstance(thing, Agent):
                                self.delete_thing(thing)
                    btn.config(bg='white', text='', state='normal')

        for agent in self.agents[:]:
            self.delete_thing(agent)

        theAgent = XYReflexAgent(program=XYReflexAgentProgram)
        print(env.agentType)
        if env.agentType == 'RuleAgent':
            theAgent = RuleBasedAgent(program=XYRuleBasedAgentProgram)

        # add an agent at location 2, 1.

        self.add_thing(theAgent, location=(2, 1))
        self.buttons[1][2].config(bg = 'blue', text=agent_label(theAgent))

    def second_agent(self):
        """Implement this: Click call back for second Agent. It rotates among possible options"""
        pass

#implement this. Rule is as follows: At each location, agent checks all the neighboring location: If a "Dirty"
# location found, agent goes to that location, otherwise follow similar rules as the XYReflexAgentProgram bellow.
def XYRuleBasedAgentProgram(percept):
    status, bump = percept
    # print("it is executing the rule based behaviour")

    if status == 'Dirty':
        return 'Suck'

    if bump == 'Bump':
        value = random.choice((1, 2))

    elif bump == 'Dirty':
        value = 3

    else:
        value = random.choice((1, 2, 3, 4))  # 1-right, 2-left, others-forward

    if value == 1:
        return 'TurnRight'
    elif value == 2:
        return 'TurnLeft'
    else:
        return 'Forward'


#Implement this: This will be similar to the ReflectAgent bellow.
class RuleBasedAgent(Agent):
    """Implement this: The modified SimpleRuleAgent for the GUI environment."""
    def __init__(self, program):
        super().__init__(program)
        self.location = (1, 2)
        self.direction = Direction("up")
        self.type = env.agentTypes[1]
    pass

def XYReflexAgentProgram(percept):
    """The modified SimpleReflexAgentProgram for the GUI environment."""
    status, bump = percept
    # print("it is executing the reflex based behaviour")
    if status == 'Dirty':
        return 'Suck'

    if bump == 'Bump':
        value = random.choice((1, 2))
    else:
        value = random.choice((1, 2, 3, 4))  # 1-right, 2-left, others-forward

    if value == 1:
        return 'TurnRight'
    elif value == 2:
        return 'TurnLeft'
    else:
        return 'Forward'

class XYReflexAgent(Agent):
    """The modified SimpleReflexAgent for the GUI environment."""
    def __init__(self, program):
        super().__init__(program)
        self.location = (1, 2)
        self.direction = Direction("up")
        self.type = env.agentTypes[0]


#
#
if __name__ == "__main__":
    win = Tk()
    win.title("Vacuum Robot Environment")
    win.geometry("800x800")
    win.resizable(True, True)
    frame = Frame(win, bg='black')
    frame.pack(side='bottom')
    wid = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    hig = int(sys.argv[2]) if len(sys.argv) > 1 else 7
    env = Gui(win, wid, hig)

    agt = XYReflexAgent(program=XYReflexAgentProgram)
    env.add_agent(agt, (2, 1))

    agentType_button = Button(frame, text=env.agentTypes[0], height=2, width=8, padx=2, pady=2)
    agentType_button.pack(side='left')
    secondAgent_button = Button(frame, text=env.agentTypes[2], height=2, width=8, padx=2, pady=2)
    secondAgent_button.pack(side='left')
    performance_label = Label(win, text='0', height=1, width = 3, padx=2, pady=2)
    performance_label.pack(side='top')
    reset_button = Button(frame, text='Reset', height=2, width=5, padx=2, pady=2)
    reset_button.pack(side='left')
    next_button = Button(frame, text='Next', height=2, width=5, padx=2, pady=2)
    next_button.pack(side='left')
    run_button = Button(frame, text='Run', height=2, width=5, padx=2, pady=2)
    run_button.pack(side='left')

    next_button.config(command=env.update_env)
    agentType_button.config(command=env.toggle_agentType)
    reset_button.config(command=env.reset_env)
    run_button.config(command=env.run)
    secondAgent_button.config(command=env.second_agent)


    win.mainloop()
