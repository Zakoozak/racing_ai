import pygame
import os
import math
import random
import numpy as np
import torch as torch
import torch.optim as optim
import pickle
import copy

from race.GameObject import ImageObject
from race import AiRadar
from race import DeepQNetwork

# The AIAgent initializes the Deep Q Learning Network (DQN) datastructure, and plays a critical role in the overall Reinforcement Learning
# algorithm. If it is initalized in a 'training' state, the agent will recieve input  from the player's environment (observe) via a radar 
# object and uses them as the nueral net's input data.  It then controls the player to take its action on the environment (keyboard outputs),
# calculates a reward based on each action taken and determines a "loss" between the actions taken and target actions that it approximates
# via a "Target" Q network. It then performs gradient descent to minimize this loss (backpropegation), thereby 'training' the DQN.
# The action, reward, and next_state data is saved to replay memory initialized by the agent.  This replay memory can then be sampled & is
# used for training.  If the agent is initalized in a 'non-training' mode, it will simply recieve the radar inputs and control the player's
# actions via an existing nueral net, without performing any training on the network.  The DQN network and replay memory state data
# is saved to file after each training episode in the dqn_model_data directory after each training episode.  Training ends when the
# network is trained sufficiently enough to allow the player to complete the levels configured lap count, as defined within
# that levels init_data.txt file. 
class AiAgent(ImageObject):
    
    def __init__(self, game, player_car, level, game_objects):
        self.game = game
        self.player_car = player_car
        self.level = level
        # Init AI's radar--provides collision detection input to Nueral Network 
        self.radar = AiRadar.AiRadar(player_car, level)
        # The NN inputs
        self.nn_inputs = []
        # Define file path to load/save the DQN and replay memory to
        self.dqn_file = "./race/dqn_model_data/dqn_policy.pt"
        self.data_path = "./race/dqn_model_data/"
        # Define action space - possible actions the agent can take to control the player (ie. different keypress combinations)
        #self.action_space = [[],["forward"], ["e_brake"], ["right"], ["left"], ["forward", "left"], ["forward", "right"], ["e_brake", "left"], ["e_brake", "right"]]
        self.action_space = [[],["forward"], ["forward", "left"], ["forward", "right"]]
        # Define all Deep Q-Learning Network (DQN) Hyper Parameters (tuning parameters for the nueral network):
        # --------------------------------------------------------------------------------------------------------------------------------------------
        self.action_size = len(self.action_space)   # Number of possible actions (network's output nodes)
        self.state_size = 6                         # Input dimension size !!Must match same number of radar beams plus the speed input!! (network's input nodes)
        self.fc1_dims = 16                          # Number of layer 1 fully-connected nodes
        self.fc2_dims = 16                          # Number of layer 2 fully-connected nodes
        self.replay_buffer_size = 50000             # Replay buffer max-size (N)
        self.batch_size = 40                        # Size of random sample from replay memory for back-prop
        self.min_replay_size = self.batch_size * 3  # Min replay buffer size before back-prop initiates for the first time--must be larger than batch size
        self.gamma = .98                            # The 'Discount Rate' parameter
        self.epsilon = 1                            # Initial explore constant (the % probability that the agent explores its environment in leui of exploiting it)
        self.epsilon_end = .02                      # Ending explore probability constant % 
        self.epsilon_decay_rate = .005              # Amount which epsilon decays after each learning iteration (decay's to epsilon end)
        self.learning_rate = .001                   # Learning rate constant α
        self.step_frequency = 1                     # Num of time steps between each state/action/reward iteration
        self.learning_frequency = 2                 # How many time steps between training the policy network & updating its weights (ie. the training step)
        self.target_net_update_freq = 1000          # Num of time steps between updating the target network's weights w/the policy network's weights
        self.episode_length = 120000                # Time (ms) before a training episode will automatically reset
        # ---------------------------------------------------------------------------------------------------------------------------------------------
        self.mem_index = 0
        self.time_step = 0
        self.score = 0
        self.episode_timer = 0
        
        # Load existing DQN policy network, if one exists
        if os.path.exists(self.dqn_file):
            self.load_model()
        # Otherwise init a new network
        else:
            # Init a new DQN policy model
            self.dqn_policy = DeepQNetwork.DeepQNetwork(self.learning_rate, self.state_size, self.fc1_dims, self.fc2_dims, self.action_size)
            self.dqn_policy.eval()
            # Save the new model to file
            self.save_model(self.dqn_policy)
        # Init a target DQN via a copy of policy the DQN
        self.dqn_target = copy.deepcopy(self.dqn_policy)

        # Init numpy array's used as replay memory buffer--will save previous states (inputs), actions, rewards, & next_state data 
        self.state_memory = np.zeros((self.replay_buffer_size, self.state_size), dtype=np.float32)
        self.action_memory = np.zeros((self.replay_buffer_size, 1), dtype=np.float32)
        self.reward_memory = np.zeros((self.replay_buffer_size, 1), dtype=np.float32)
        self.next_state_memory = np.zeros((self.replay_buffer_size, self.state_size), dtype=np.float32)
        self.done_memory = np.zeros((self.replay_buffer_size, 1), dtype=np.float32)
        # Load replay memory with previous episodes data, if it exists
        self.load_agent_state()
        
        # Whether the agent will be performing training or not (Backprop vs. feed-forward only)
        self.train = self.game.ai_train
        if self.train == False:
            self.epsilon = 0        # since no training, don't select actions randomly
        
    # 'update' controls the AI agent's overall operational sequence & 
    # timing of each function via its method calls & a time-step counter.
    # Depending on the selection made at the title screen, agent
    # will perform a feed-forward control only (should have a DQN that's 
    # already trained) OR feed-forward w/backprob to train the DQN.
    def update(self):
        # Feed forward only control sequence: (no training of network was selected at title screen) 
        if self.train == False:
            self.nn_inputs = self.radar.calc_radar_beams()              # Get the player car's current radar beam distance values
            self.nn_inputs.append(self.player_car.distance)             # Add the player car's current speed as the final parameter to the input list
            if self.time_step % self.step_frequency == 0:
                self.act()
            self.time_step += 1
            return
        
        # DQN control w/complete training sequence (back-propegation)
        if self.time_step % self.step_frequency == 0:
            self.mem_index += 1                                         # Increment replay memory index to store the step data
            self.mem_index = self.mem_index % self.replay_buffer_size   # Reset the memory index if it exceeds buffer size (begin to over-write)
            self.nn_inputs = self.radar.calc_radar_beams()              # Get the player car's current radar beam sensor distance values
            self.nn_inputs.append(self.player_car.distance)             # Add the player car's current speed as the last parameter to the input data list
            self.act()                                                  # Take an action--Feed forward to exploit or take randomized action to explore
            self.reward_calc()                                          # Calculate the reward
            self.save_to_replay()                                       # Save all current step data to replay memory (state, action, reward, next_state, terminal_state)
        if self.time_step % self.learning_frequency == 0:       
            self.learn()                                                # Perform a training step on the network (Backpropegate the policy DQN)
        if self.time_step % self.target_net_update_freq == 0:
            self.update_target_from_policy()                            # Update the target DQN weights with the policy DQN weights
         
        self.time_step += 1                                             # Increment the time step
        if self.time_step > self.replay_buffer_size:                    # Reset the timestep to zero to prevent it from getting too large
            self.tme_step = 0     
        
        self.episode_timer += self.game.clock.get_time()                # Increment the current episode's timer             
        #  Determine if this is the final iteration of the current episode i.e. the 'terminal state' (either time has exceeded or player has collided)
        if self.episode_timer > self.episode_length or self.player_car.collision_level == True: 
            self.done_memory[self.mem_index-1] = True                   # Save terminal state boolean to replay memory
            self.save_model(self.dqn_policy)                            # Save the current policy DQN to file
            self.save_agent_state()                                     # Save replay memory data to file
            self.write_episode_score()                                  # Write episode score to file
            self.restart_episode()                                      # Start a new training episode iteration
        
        # Training is done--the agent was able to successfully complete the level's lap count without a single player collision    
        if self.player_car.lap_count > self.level.laps:               
            self.save_model(self.dqn_policy)                            # Save the current policy DQN to file
            self.save_agent_state()                                     # Save replay memory data to file
            self.write_episode_score()                                  # Write episode score to file
            print("Training Completed, the model was saved.")
            self.game.running = False                                   # End training
            
    # Makes the player car act.  The action taken is determined either by a forward
    # pass of the policy DQN or is selected randomly, pending the value of epsilon.
    def act(self):
        if random.random() > self.epsilon:                                      # Randomly generates a num from 0 to 1 and compares w/epsilon
            state = torch.tensor(self.nn_inputs, dtype=torch.float32).unsqueeze(0).to(self.dqn_policy.device)  # Sends the input node values to the working device (GPU if avail)
            with torch.no_grad():                                               # Does not track gradients (because not currently training the network)
                actions = self.dqn_policy.forward(state)                        # Retreives the output node values by a forward pass of the policy DQN
            actions = actions.cpu().data.numpy()                                # Retrieves this output back from GPU to CPU and converts the tensor to numpy array
            self.action_choice = np.argmax(actions)                             # Selects the output node w/the  maximum value received from the forward pass as the decided action to take
        else:
            self.action_choice = random.choice(np.arange(self.action_size))     # Elect to take a random action instead (explore the environment)
        
        # Retreive the specific action (keypress combinations) from the pre-defined action-space list (keypress combinations)
        action = self.action_space[self.action_choice]
        # Now perform the action (send/switch the keypresses to actually send control signals to the player)
        for key, value in self.game.key_state.items():
            if key in action:
                self.game.key_state[key] = True
            else:
                self.game.key_state[key] = False
    
    # Calculates a 'reward' value for the action taken on the previous iteration.
    def reward_calc(self):
        beams = self.nn_inputs.copy()   # Copy input nodes to seperate the radar beam values from the speed value
        speed = beams.pop()
        # A custom-designed reward equation--dependant on the player's current speed & the radar beam sensor distances.
        self.reward = (speed * ((beams[0] - 500) + .25 * (beams[1] - 250) + .25 * (beams[2] - 250) + .125 * (beams[3] - 75) + .125 * (beams[4] - 75))) / 100
        self.score += self.reward       # Add the calculated reward to total score for the current episode
    
    # Saves each state, action, reward, and next state to replay memory
    def save_to_replay(self):
        self.state_memory[self.mem_index] = self.nn_inputs               # Save state (radar beam input)
        self.action_memory[self.mem_index] = self.action_choice          # Save action
        self.reward_memory[self.mem_index-1] = self.reward               # Save current reward to previous action taken
        self.next_state_memory[self.mem_index-1]  = self.nn_inputs       # Save next state to previous index
        self.done_memory[self.mem_index-1] = False                       # Episode is not in a terminal state
    
    # Samples a 'batch' of previously stored state data from replay memory to 'train' the network.
    def sample_replay(self):
        # Get the maximum memory index that data has been written to up to this point
        max_mem_index = min(self.mem_index, self.replay_buffer_size)
        
        # Retreive a random selection of replay memory indexes ranging from index 1 to max index
        mem_sample_indexes = np.random.choice(range(1,max_mem_index), self.batch_size, replace=False) 
        
        # Using the list of replay memory sample indexes, select the batch replay data from their memory buffers, convert to tensors, and make available to the processing device
        state_batch = torch.tensor(self.state_memory[mem_sample_indexes]).to(self.dqn_policy.device)
        reward_batch = torch.tensor(self.reward_memory[mem_sample_indexes]).to(self.dqn_policy.device)
        next_state_batch = torch.tensor(self.next_state_memory[mem_sample_indexes]).to(self.dqn_policy.device)
        action_batch = torch.tensor(self.action_memory[mem_sample_indexes], dtype=torch.int64).to(self.dqn_policy.device)
        done_batch = torch.tensor(self.done_memory[mem_sample_indexes]).to(self.dqn_policy.device)
        
        return state_batch, action_batch, reward_batch, next_state_batch, done_batch
    
    # Retreives a sample batch from replay memory, computes the loss eqation for the batch, then
    # performs backpropegation (gradient descent) on the policy network to minimize the loss,
    # ie. "trains the policy DQN" 
    def learn(self):
        # Do not begin learning until minimum replay memory size has been written to
        if self.mem_index < self.min_replay_size:
            return
        self.dqn_policy.train()                                              # Switch from eval to training mode for the DQN
        states, actions, rewards, next_states, dones = self.sample_replay()  # Sample replay memory and retreive the training batch       

        # Perform a forward pass of states and next_states through policy and target DQNs, respectively
        # Note: The .gather method uses actions as an index to parse max output(q-eval) values from the feed-forward output
        q_evaluated = self.dqn_policy.forward(states).gather(1, actions)    
        q_eval_next = self.dqn_target.forward(next_states).detach().max(1)[0].unsqueeze(1) # Take max of qπ(s',a')
        
        # Calculate Q targets based on the Bellman Equation:
        q_targets = rewards + self.gamma * q_eval_next * (1 - dones)

        # Send the actual (eval) and target data to the device to calculate the cost/loss between them
        loss = self.dqn_policy.loss(q_evaluated, q_targets).to(self.dqn_policy.device)
        # zero-out gradients for DQN's optimizer for the training
        self.dqn_policy.optimizer.zero_grad()                       
        # Perform the backprop/gradient descent to minimize the loss & step the optimizer
        loss.backward()                                       
        self.dqn_policy.optimizer.step()     
        # Learning is complete, switch policy DQN back to evaluate mode
        self.dqn_policy.eval()
        # Decrement epsilon by the defined decay rate value
        if self.epsilon > self.epsilon_end:
            self.epsilon -= self.epsilon_decay_rate
    
    # Updates the target dqn with the policy dqn's weights
    def update_target_from_policy(self):
        self.dqn_target.load_state_dict(self.dqn_policy.state_dict())
    
    # Start a new training episode by loading saved game state
    def restart_episode(self):
        print("TOTAL EPISODE SCORE: ", self.score)
        self.save_agent_state()
        self.game.load_game_state()
     
    # Saves the policy DQN to file 
    def save_model(self, model):
        torch.save(model.state_dict(), self.dqn_file)

    # Loads policy DQN from file    
    def load_model(self):
        self.dqn_policy = DeepQNetwork.DeepQNetwork(self.learning_rate, self.state_size, self.fc1_dims, self.fc2_dims, self.action_size)
        self.dqn_policy.load_state_dict(torch.load(self.dqn_file))
        self.dqn_policy.eval()
    
    # Save the agents variables and training state data (stored in replay memory) to file
    def save_agent_state(self):
        np.save(self.data_path+"states.npy", self.state_memory)
        np.save(self.data_path+"actions.npy", self.action_memory)
        np.save(self.data_path+"rewards.npy", self.reward_memory)
        np.save(self.data_path+"next_states.npy", self.next_state_memory)
        np.save(self.data_path+"dones.npy", self.done_memory)
        with open(self.data_path+"time_step_counter.pickle", 'wb') as f:
            pickle.dump(self.time_step, f)
        with open(self.data_path+"epsilon.pickle", 'wb') as f:
            pickle.dump(self.epsilon, f)         
    
    # Load agent state data
    def load_agent_state(self):
        # Ensure all files actually exist before loading
        files = ["states.npy", "actions.npy", "rewards.npy", "next_states.npy", "dones.npy", "time_step_counter.pickle", "epsilon.pickle"]
        for file in files:
            if not os.path.isfile(self.data_path + file):
                return
        self.state_memory = np.load(self.data_path+"states.npy")
        self.action_memory = np.load(self.data_path+"actions.npy")
        self.reward_memory = np.load(self.data_path+"rewards.npy")
        self.next_state_memory = np.load(self.data_path+"next_states.npy")
        self.done_memory = np.load(self.data_path+"dones.npy")
        with open(self.data_path+"time_step_counter.pickle", 'rb') as f:
            self.time_step = pickle.load(f)
        with open(self.data_path+"epsilon.pickle", 'rb') as f:
            self.epsilon = pickle.load(f)

    # Append each episode's score to file at end of each episode
    def write_episode_score(self):
        with open(self.data_path+"scores.txt", 'a+') as f:
            f.write("\nSCORE: " + str(int(self.score)))