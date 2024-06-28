import numpy as np
import random
import torch as torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F

# Inits a Pytorch DeepQNetwork model w/ 2 fully-connected hidden layers (ie. a "deep" nn)--called by AiAgent Class
class DeepQNetwork(nn.Module):
    def __init__(self, learning_rate, input_dims, fc1_dims, fc2_dims, num_actions):
        super(DeepQNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.num_actions = num_actions
        
        self.fc1 = nn.Linear(self.input_dims, self.fc1_dims)  # input layer: (input, output)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)    # hidden layer1
        self.fc3 = nn.Linear(self.fc2_dims, self.num_actions) # hidden layer2
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)    # Init optimizer for training of network
        self.loss = nn.MSELoss() # Use Mean Square Error equation for loss
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu') # Define the device--use GPU, if available
        self.to(self.device) # Sends itself to the device for processing

    # forward method overides parent class' (Module) forward method
    def forward(self, state):
        x = F.relu(self.fc1(state))         # Passes input into first layer, activate output with relu function
        x = F.relu(self.fc2(x))             # Pass layer 1 output into layer 2, activate output with relu function
        actions = self.fc3(x)               # Pass layer 2 output into layer 3, returns final output (actions)
        return actions                      # Returns output node values (determines best "action" to take)
