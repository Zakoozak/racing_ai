AI RACER started as a simple 2D racing game built in the Pygame framework.
Reinforcment Learning via the PyTorch framework, was added to the game to allow a player to test, tune, train, and play with a Deep Q Learning Network.
The goal here is to show the ia, and thee racing game.


global system :
AI rewarded if it does a lap  
Resets if it goes off road.  
  
The AI ​​perceives its environment using lines indicating the distance between its position and the edge of the road  
![](gif/0_HowAIsees.gif) 

If the AI ​​is rewarded for each lap completed, it will try to cross the finish line in a loop, without going around...  
![](gif/1_rewards_if_Laps.gif) 

I set up “reward gates” to nudge the AI ​​to do the trick.  
![](gif/2_Putting_rewards_gates.png)

Evolution after few tries   
![](gif/3_Evolution.gif)

Evolution after 800 + after 1000 tries  
![a](gif/4_Evolution_after__800_then_1000_tries.gif) 

Evolution after a night of training, we notice that she does not stop doing laps, but seeks to optimize her trajectories to go as quickly as possible.  
![](gif/5_after_one_night_of_training.gif) 


