AI RACER started as a simple 2D racing game built in the Pygame framework.
Reinforcment Learning via the PyTorch framework, was added to the game to allow a player to test, tune, train, and play with a Deep Q Learning Network.

![](gif/0_HowAisees.gif)The AI ​​perceives its environment using lines indicating the distance between its position and the edge of the road

![aaa](gif/1_rewards_if_Laps.gif) If the AI ​​is rewarded for each lap completed, it will try to cross the finish line in a loop, without going around...

![](gif/2_20Putting_rewards_gates.PNG)I set up “reward gates” to nudge the AI ​​to do the trick.

![](gif/3_Evolution.gif) Evolution after 800 + after 1000 tries

![](gif/4_Evolution_after__800_then_1000_tries.gif) Evolution after a night of training, we notice that she does not stop doing laps, but seeks to optimize her trajectories to go as quickly as possible.