#!/usr/bin/env python
# coding: utf-8

# In[1]:


from __future__ import print_function
import pickle
from game import Board, Game
from mcts_pure import MCTSPlayer as MCTS_Pure
from mcts_alphaZero import MCTSPlayer
from policy_value_net_numpy import PolicyValueNetNumpy
#from policy_value_net_keras import PolicyValueNet as PolicyValueNetNumpy
from flask import Flask, request, send_from_directory
import os


# In[2]:


n = 5
width, height = 8, 8
model_file = 'best_policy_8_8_5.model'
policy_param = pickle.load(open(model_file, 'rb'), encoding='bytes')
best_policy = PolicyValueNetNumpy(width, height, policy_param)
mcts_player = MCTSPlayer(best_policy.policy_value_fn, c_puct=5, n_playout=400)


# In[3]:


boards = {}
agents = {}
app = Flask(__name__)
app._static_folder = 'D:/tf/AlphaZero_Gomoku/static'


# In[4]:


class Agent(object):
    def __init__(self):
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    def __str__(self):
        return "API {}".format(self.player)


# In[5]:


def check_and_create_board(uid):
    if uid not in boards:
        agent = Agent()
        board = Board(width=width, height=height, n_in_row=n)
        board.init_board(0)
        p1, p2 = board.players
        agent.set_player_ind(p1)
        mcts_player.set_player_ind(p2)
        boards[uid] = board
        agents[uid] = agent


# In[6]:


def board_state_to_array(board, agent):
    player1, player2 = agent, mcts_player
    arr = []
    for i in range(height - 1, -1, -1):
        row = []
        for j in range(width):
            loc = i * width + j
            p = board.states.get(loc, -1)
            row.append(p)
        arr.append(row)
    return arr


# In[7]:


@app.route('/play', methods=['GET', 'POST'])
def play():
    uid = request.args.get('uid')
    check_and_create_board(uid)
    board = boards[uid]
    agent = agents[uid]
    if request.method == 'GET':
        return { 'move': 0, 'board': board_state_to_array(board, agent) }
    if request.method == 'POST':
        x = request.args.get('x')
        y = request.args.get('y')
        human_location = [int(y), int(x)]
        human_move = board.location_to_move(human_location)
        board.do_move(human_move)
        end, winner = board.game_end()

        if not end:
            ai_move = mcts_player.get_action(board)
            board.do_move(ai_move)
            new_location = board.move_to_location(ai_move)
            end, winner = board.game_end()
            return {
                'move_x': int(new_location[1]),
                'move_y': int(new_location[0]),
                'board': board_state_to_array(board, agent),
                'end': end, 'winner': int(winner)
            }
        else:
            return {
                'move_x': -1,
                'move_y': -1,
                'board': board_state_to_array(board, agent),
                'end': end, 'winner': int(winner)
            }


# In[8]:

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

@app.route('/')
def index():
    return app.send_static_file('index.html')

#app.run(host='0.0.0.0', port=os.getenv('PORT', 8800))

