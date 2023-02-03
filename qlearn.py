import random
import sys

DEFAULT_STATE = '       | ###  -| # #  +| # ####|       '


class Action:

    def __init__(self, name, dx, dy):
        self.name = name
        self.dx = dx
        self.dy = dy


ACTIONS = [
    Action('UP', 0, -1),
    Action('RIGHT', +1, 0),
    Action('DOWN', 0, +1),
    Action('LEFT', -1, 0)
]


class State:

    def __init__(self, env, x, y):
        self.env = env
        self.x = x
        self.y = y

    def clone(self):
        return State(self.env, self.x, self.y)

    def is_legal(self, action):
        cell = self.env.get(self.x + action.dx, self.y + action.dy)
        return cell is not None and cell in ' +-'

    def legal_actions(self, actions):
        legal = []
        for action in actions:
            if self.is_legal(action):
                legal.append(action)
        return legal

    def reward(self):
        cell = self.env.get(self.x, self.y)
        if cell is None:
            return None
        elif cell == '+':
            return +10
        elif cell == '-':
            return -10
        else:
            return 0

    def at_end(self):
        return self.reward() != 0

    def execute(self, action):
        self.x += action.dx
        self.y += action.dy
        return self

    def __str__(self):
        tmp = self.env.get(self.x, self.y)
        self.env.put(self.x, self.y, 'A')
        s = ' ' + ('-' * self.env.x_size) + '\n'
        for y in range(self.env.y_size):
            s += '|' + ''.join(self.env.row(y)) + '|\n'
        s += ' ' + ('-' * self.env.x_size)
        self.env.put(self.x, self.y, tmp)
        return s


class Env:

    def __init__(self, string):
        self.grid = [list(line) for line in string.split('|')]
        self.x_size = len(self.grid[0])
        self.y_size = len(self.grid)

    def get(self, x, y):
        if 0 <= x < self.x_size and 0 <= y < self.y_size:
            return self.grid[y][x]
        else:
            return None

    def put(self, x, y, val):
        if 0 <= x < self.x_size and 0 <= y < self.y_size:
            self.grid[y][x] = val

    def row(self, y):
        return self.grid[y]

    def random_state(self):
        x = random.randrange(0, self.x_size)
        y = random.randrange(0, self.y_size)
        while self.get(x, y) != ' ':
            x = random.randrange(0, self.x_size)
            y = random.randrange(0, self.y_size)
        return State(self, x, y)


class QTable:

    def __init__(self, environ, actions):
        # initialize q table
        # access element using this format: qtable[y][x][move]
        # UP = [y][x][0]   RIGHT = [y][x][1]   DOWN = [y][x][2]   LEFT = [y][x][3]
        self.environ = environ
        self.qtable = [[['----' for move in range(len(actions))] for x in range(environ.x_size)] for y in
                       range(environ.y_size)]

    def get_q(self, state, action):
        # return the value of the q table for the given state, action
        if action.name == 'UP':
            if self.qtable[state.y][state.x][0] == "----":
                return 0
            else:
                return self.qtable[state.y][state.x][0]
        if action.name == 'RIGHT':
            if self.qtable[state.y][state.x][1] == "----":
                return 0
            else:
                return self.qtable[state.y][state.x][1]
        if action.name == 'DOWN':
            if self.qtable[state.y][state.x][2] == "----":
                return 0
            else:
                return self.qtable[state.y][state.x][2]
        if action.name == 'LEFT':
            if self.qtable[state.y][state.x][3] == "----":
                return 0
            else:
                return self.qtable[state.y][state.x][3]

    def set_q(self, state, action, val):
        # set the value of the q table for the given state, action
        if action.name == 'UP':
            self.qtable[state.y][state.x][0] = val
        if action.name == 'RIGHT':
            self.qtable[state.y][state.x][1] = val
        if action.name == 'DOWN':
            self.qtable[state.y][state.x][2] = val
        if action.name == 'LEFT':
            self.qtable[state.y][state.x][3] = val

    def max_q(self, new_state):
        new_state_max_q = 0
        for action in ACTIONS:
            if new_state_max_q < self.get_q(new_state, action):
                new_state_max_q = self.get_q(new_state, action)
        return new_state_max_q

    def learn_episode(self, alpha, gamma):
        # generate a random state
        state = self.environ.random_state()
        print(state)
        while not state.at_end():
            # get random legal action and execute that action
            actions = state.legal_actions(ACTIONS)
            rand_action = actions[random.randint(0, (len(actions) - 1))]
            new_state = state.clone()
            new_state.execute(rand_action)
            # getting q for previous (state, action) pair
            previous_state_action_q = self.get_q(state, rand_action)
            # compute the reward of new state
            reward = new_state.reward()
            # determine max q for new state
            new_state_max_q = self.max_q(new_state)
            # update q table for previous (state, action)
            new_q = ((1 - alpha) * previous_state_action_q) + (alpha * (reward + (gamma * new_state_max_q)))
            self.set_q(state, rand_action, new_q)
            state = new_state  # set the current state to the new state for next iteration
            print(state)  # print out the new state

    def learn(self, episodes, alpha=.10, gamma=.90):
        # run <episodes> number of episodes for learning with the given alpha and gamma
        for episode in range(episodes):
            self.learn_episode(alpha, gamma)

    def __str__(self):
        # return a string for the qtable
        qtable_string = ''
        qtable_string += '\n\n' + 'UP'
        for x in range(5):
            qtable_string += '\n'
            for y in range(7):
                if type(self.qtable[x][y][0]) != str:
                    qtable_string += f'{self.qtable[x][y][0]:.2f}' + '\t'
                else:
                    qtable_string += self.qtable[x][y][0] + '\t'
        qtable_string += '\n\n' + 'RIGHT'
        for x in range(5):
            qtable_string += '\n'
            for y in range(7):
                if type(self.qtable[x][y][1]) != str:
                    qtable_string += f'{self.qtable[x][y][1]:.2f}' + '\t'
                else:
                    qtable_string += self.qtable[x][y][1] + '\t'
        qtable_string += '\n\n' + 'DOWN'
        for x in range(5):
            qtable_string += '\n'
            for y in range(7):
                if type(self.qtable[x][y][2]) != str:
                    qtable_string += f'{self.qtable[x][y][2]:.2f}' + '\t'
                else:
                    qtable_string += self.qtable[x][y][2] + '\t'
        qtable_string += '\n\n' + 'LEFT'
        for x in range(5):
            qtable_string += '\n'
            for y in range(7):
                if type(self.qtable[x][y][3]) != str:
                    qtable_string += f'{self.qtable[x][y][3]:.2f}' + '\t'
                else:
                    qtable_string += self.qtable[x][y][3] + '\t'
        return qtable_string
        # qtable_string += f'{self.qtable[4][0][0]:.2f}' + '\t'


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        env = Env(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_STATE)
        if cmd == 'learn':
            qt = QTable(env, ACTIONS)
            qt.learn(100)
            print(qt)
