# AI Racer
An Artificially Intelligent agent that can drive on user-drawn racetracks using NEAT (Neuroevolution of Augmenting Topologies)

Play at: <Used to be a link but currently switching to another hosting platform since Heroku is no longer free, my apologies>

https://user-images.githubusercontent.com/46911428/191157826-d043cd5a-db29-4eec-a1ea-7f4c9e39f8c5.mp4


https://user-images.githubusercontent.com/46911428/191150451-e51e94e5-11f0-4e55-9616-a59644ed9eb9.mp4

## Training
The agent was trained in a python pygame environment, then, once trained, ported over to Javascript using p5.js to render on a webpage using Flask.
### Network Inputs
The agent's observations included:
 - The distance straight to a road
 - The distance left to a road
 - The distance right to a road
 - The distance diagonally left to a road
 - The distance diagonally right to a road

![image alt >](https://user-images.githubusercontent.com/46911428/191151872-84b86dbf-fc5d-44b4-9047-b59343554ee4.png)

### NEAT (Neuroevolution of Augmenting Topologies)
NEAT is a NeuroEvolution algorithm, an algorithm that simulates genetic evolution for Reinforcement Learning (RL). For this AI Racer, 100 candidate neural networks are generated. Each candidate, while similar, has various mutations and differences in genotype that can cause it to perform better or worse than its peers. After all candidates are evaluated on some race track, the highest-performing cars reproduce to mix their genes, creating a new and improved generation of candidates. This process repeats until convergence or the AIs exceed some standard of performance (i.e. completing the race in under 30 seconds).

The AI winner currently driving generated this neural network:

![image](https://user-images.githubusercontent.com/46911428/191159129-e69389fa-40c0-4172-afa1-979c8e0f4361.png)

Where the items at the top represent the inputs, and "right_arr," "left_arr," and "up_arr" represent Turn Right, Turn Left, and Accelerate, respectively. 51 and 52 are two hidden nodes adding extra complexity.
