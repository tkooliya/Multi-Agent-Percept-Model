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


    # need to have this shit run until its not dirty anymore
    def runAgent(self, steps=1000):
        """Run the Environment for given number of time steps."""
        self.update_env()
        for step in range(steps):
            if not any(isinstance(x ,Dirt) for x in self.things):
                print("It takes", step, "steps to clean all dirt. This was done under a ", env.agentType, "agent." )
                return
            self.update_env()
            if self.is_done():
                print("The dirt was not completely cleanable.")
                return


    #need to make a helper function to determine if agent is in region
    def is_agent_in_region(self, agent):
        lim = len(self.agents)
        agentOK = [0, 0]
        if(self.agents[0]):
            #Agent 1 bounds
            x1, y1 = self.agents[0].location
            if(1 < x1 <= wid - 1) and (1 < x1 < int(hig/2)):
                agentOK[0] = 1
            else:
                agentOK[0] = 0
        if(lim == 2):
            if(self.agents[1]):
                #Agent 2 bounds
                x2, y2 = self.agents[1].location
                if(1 < x2 <= wid - 1) and (int(hig/2) < x2 < hig - 1):
                    agentOK[1] = 1
                else:
                    agentOK[1] = 0
        return agentOK



    def execute_action(self, agent, action):
        """Determines the action the agent performs."""
        xi, yi = agent.location
        print("agent at location (", xi, yi, ") and action ", action)

        array = self.is_agent_in_region(agent)

        if action == 'Suck':
            dirt_list = self.list_things_at(agent.location, Dirt)
            if dirt_list:
                dirt = dirt_list[0]

                #performance standard will be 1000~!
                agent.performance += 1000
                self.delete_thing(dirt)
                self.buttons[yi][xi].config(bg='white')

                if(agent == self.agents[0]):
                    self.buttons[yi][xi].config(bg='white', text='')
                    xf, yf = agent.location
                    self.buttons[yf][xf].config(bg='blue', text=agent_label(agent))
                elif(agent == self.agents[1]):
                    self.buttons[yi][xi].config(bg='white', text='')
                    xf, yf = agent.location
                    self.buttons[yf][xf].config(bg='Green', text=agent_label(agent))

        else:
            agent.bump = False
            restrict_location = agent.direction.move_forward(agent.location)

            if action == 'TurnRight':
                agent.direction += Direction.R
                self.buttons[yi][xi].config(text=agent_label(agent))
            elif action == 'TurnLeft':
                agent.direction += Direction.L
                self.buttons[yi][xi].config(text=agent_label(agent))
            elif action == 'Forward':
                if(len(self.agents) > 1):

                    if(self.agents.index(agent) == 1):
                        agent2 = 0
                    else:
                        agent2 = 1

                    # issue a bump to agent if it reaches proximity boundary
                    if (self.agents.index(agent) == 0 and restrict_location[1] >= (int(hig/2) + 1)):
                        agent.bump = True
                    elif (self.agents.index(agent) == 1 and restrict_location[1] < (int(hig/2))):
                        agent.bump = True
                    elif (restrict_location == self.agents[agent2].location):
                        agent.bump = True

                    # If agents come into contact
                    else:
                        agent.bump = self.move_to(agent, restrict_location)
                else:
                    agent.bump = self.move_to(agent, agent.direction.move_forward(agent.location))
                    self.buttons[yi][xi].config(bg='white', text='')
                    xf, yf = agent.location
                    self.buttons[yf][xf].config(bg='blue', text=agent_label(agent))

                if not agent.bump:
                    if(self.agents.index(agent) == 0):
                        if(len(self.agents) == 1) or self.agents[0] == agent:
                            self.buttons[yi][xi].config(bg = 'white', text='')
                            xf, yf = agent.location
                            self.buttons[yf][xf].config(bg = 'blue', text=agent_label(agent))
                    elif(self.agents.index(agent) == 1):
                        self.buttons[yi][xi].config(bg = 'white', text='')
                        xf, yf = agent.location
                        self.buttons[yf][xf].config(bg = 'Green', text=agent_label(agent))

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
        for i, agt in enumerate(self.agents):
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
        secondAgent_button.config(text=env.agentTypes[2])

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

        Xstart_agent1 = random.choice(range(1, wid - 1))
        Ystart_agent1 = random.choice(range(1, int(hig/2)))

        self.add_thing(theAgent, location=(Xstart_agent1, Ystart_agent1))
        self.buttons[Ystart_agent1][Xstart_agent1].config(bg = 'blue', text=agent_label(theAgent))

    def second_agent(self):
        """Implement this: Click call back for second Agent. It rotates among possible options"""
        if(len(self.agents) == 1):
            self.reset_env()
            Xstart_agent2 = random.choice(range(1, wid - 1))
            Ystart_agent2 = random.choice(range(int(hig / 2), hig - 1))
            x2, y2 = self.agents[0].location

            while (x2 == Xstart_agent2 and y2 == Ystart_agent2):
                Xstart_agent2 = random.choice(range(1, wid - 1))
                Ystart_agent2 = random.choice(range(int(hig / 2), hig - 1))

            xyloc = Xstart_agent2, Ystart_agent2

            if env.agentType == 'RuleAgent':
                agt2 = XYReflexAgent(program=XYRuleBasedAgentProgram)
                print("agent 2 is rule based")
                secondAgent_button.config(text=("2 agents - " + env.agentTypes[1]))
            elif env.agentType == 'ReflexAgent':
                agt2 = XYReflexAgent(program=XYReflexAgentProgram)
                print("agent 2 is reflex based")
                secondAgent_button.config(text=("2 agents - " + env.agentTypes[0]))
            else:
                agt2 = XYReflexAgent(program=XYReflexAgentProgram)
                secondAgent_button.config(text=("2 agents - " + env.agentTypes[0]))

            env.add_agent(agt2, xyloc)
            # Place the agent in the centre of the grid.
            lbl = agent_label(agt)
            self.buttons[xyloc[1]][xyloc[0]].config(bg='Green', text=lbl)
            agentType_button.config(text=env.agentType)

        else:
            self.delete_thing(self.agents[1])
            self.reset_env()
            secondAgent_button.config(text=env.agentTypes[2])


#implement this. Rule is as follows: At each location, agent checks all the neighboring location: If a "Dirty"
# location found, agent goes to that location, otherwise follow similar rules as the XYReflexAgentProgram bellow.
def XYRuleBasedAgentProgram(percept):
    status, bump, dirty, directionFace = percept
    # print("it is executing the rule based behaviour")
    print(directionFace)

    if status == 'Dirty':
        return 'Suck'

    if bump == 'Bump':
        value = random.choice((1, 2))


    if directionFace == 'up':
        print("UPPPIES")
        if dirty[0] == 1:
            return 'Forward'
        elif dirty[1] == 1:
            return 'TurnLeft'
        elif dirty[2] == 1:
            return 'TurnRight'
        elif dirty[3] == 1:
            return 'TurnRight' # Costs 2 rotations to pickup dirt spot behind so doesn't matter which direction
        else:
            value = random.choice((1, 2, 3, 4))  # 1-right, 2-left, others-forward
            if value == 1:
                return 'TurnRight'
            elif value == 2:
                return 'TurnLeft'
            else:
                return 'Forward'

    elif directionFace == 'left':
        print("LEFTIES")

        if dirty[1] == 1:
            return 'Forward'
        elif dirty[3] == 1:
            return 'TurnLeft'
        elif dirty[0] == 1:
            return 'TurnRight'
        elif dirty[2] == 1:
            return 'TurnRight' # Costs 2 rotations to pickup dirt spot behind
        else:
            value = random.choice((1, 2, 3, 4))  # 1-right, 2-left, others-forward
            if value == 1:
                return 'TurnRight'
            elif value == 2:
                return 'TurnLeft'
            else:
                return 'Forward'

    elif directionFace == 'right':
        print("RIGHTIES")

        if dirty[2] == 1:
            return 'Forward'
        elif dirty[0] == 1:
            return 'TurnLeft'
        elif dirty[3] == 1:
            return 'TurnRight'
        elif dirty[1] == 1:
            return 'TurnRight' # Costs 2 rotations to pickup dirt spot behind
        else:
            value = random.choice((1, 2, 3, 4))  # 1-right, 2-left, others-forward
            if value == 1:
                return 'TurnRight'
            elif value == 2:
                return 'TurnLeft'
            else:
                return 'Forward'

    elif directionFace == 'down':
        print("UPPPIES")

        if dirty[3] == 1:
            return 'Forward'
        elif dirty[2] == 1:
            return 'TurnLeft'
        elif dirty[1] == 1:
            return 'TurnRight'
        elif dirty[0] == 1:
            return 'TurnRight' # Costs 2 rotations to pickup dirt spot behind

        else:
            value = random.choice((1, 2, 3, 4))  # 1-right, 2-left, others-forward
            if value == 1:
                return 'TurnRight'
            elif value == 2:
                return 'TurnLeft'
            else:
                return 'Forward'

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
    status, bump, dirt, direction = percept
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

    Xstart_agent1 = random.choice(range(1, wid - 1))
    Ystart_agent1 = random.choice(range(1, int(hig/2)))
    Xstart_agent2 = Xstart_agent1
    Ystart_agent2 = Ystart_agent1

    # Avoids generating the same coordinates to spawn agent 2
    print(str(Xstart_agent1) + " " + str(Ystart_agent1))
    while Xstart_agent2 == Xstart_agent1 and Ystart_agent2 == Ystart_agent1:
        Xstart_agent2 = random.choice(range(1, wid - 1))
        Ystart_agent2 = random.choice(range(int(hig/2), hig - 1))
    print(str(Xstart_agent2) + " " + str(Ystart_agent2))

    env.add_agent(agt, (Xstart_agent1, Ystart_agent1))

    xyloc = Xstart_agent2, Ystart_agent2

    agentType_button = Button(frame, text=env.agentTypes[0], height=2, width=8, padx=2, pady=2)
    agentType_button.pack(side='left')
    secondAgent_button = Button(frame, text=env.agentTypes[2], height=2, width=16, padx=2, pady=2)
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
    run_button.config(command=env.runAgent)
    secondAgent_button.config(command=env.second_agent)


    win.mainloop()
