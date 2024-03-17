# Market Simulator
This project is initiated, designed, and implemented by AZ (Arseniy Zvyagintsev).

## Motivation
This project aims to create a fictional world populated with consumers, producers, several markets, governments, and banks. Each agent makes many decisions each round of the simulation which creates space for testing various economic assumptions about consumers', producers', banks', and the government's behavior. I started this project hoping that it could improve the education in economics and merge STEM students with the economists. Indeed, the economists could use their intuition to come up with high-level strategies for the agents, whereas the STEM students could actually code this strategies and see the consequences of their choices in this interactive simulation. However, I saw that agents' strategies are too complex, and a human mind is not capable of hard-coding the optimal strategies for the agents. From there, I had a new idea: what if I hard-code the architecture of the simulation (set up the rules of the interactions between the agents), and then apply some machine learning algorithm that would find the optimal strategies for these agents? The hypothesis is that such an algorithm would converge to strategies that seem to be intuitive and make common sense, and the resulting simulated world would obey the laws of economics described in textbooks.

## Description
Let's analyze agents of the simulation one by one:

1) Goods \
Goods are something produced by Producers to increase income and purchased and consumed by Consumers to increase utility. The unique attributes of each good are the consumption and depreciation rates.
2) Consumers \
Consumers work for Producers in exchange for a salary. After that, they purchase goods on the Goods Market. Then they might seek a job on the Labor Market. Finally, they consume goods to increase their utility. The unique attributes of consumers are the utility function and skill.
3) Producers \
Producers produce Goods with the help of employed Consumers and sell them on the Goods Market to increase their profit. Then they revise their staff: fire and hire employees according to their strategy. Finally, they pay dividends to the company owners. The unique attributes of producers are the productivity function and the type of good produced.
4) Banks \
Banks take and give loans to consumers, producers, other banks, and the government.
5) Goods Market \
The Goods Market is the medium where transactions of Goods take place.
6) Labor Market \
The Labor Market is the medium where Producers meet Consumers to hire them.
7) Loans Market \
The Loans Market is the medium where agents seek for loans and banks accept them.
8) Government \
Government collects taxes (transactional, income, and corporate), buys public goods, and can increase or decrease the amount of money in the simulation
9) Census \
Census is the data center of the simulation: it stores references to other objects and all the relevant statistics over time.
10) Simulation \
Simulation is a class that correctly sets up the simulation, sequentially runs all the steps, and then correctly wraps it up.

Now let's have a look into the architecture of the simulation:

1) Agents.py stores all the relevant classes described above
2) AgentExamples.py is wrapper file that allows users to easily create specific entities of various classes
3) SimExamples.py is a wrapper file that stores in one place different pre-specified simulations
4) Visuals.py has class Visual that can easily graph all the important statistics
5) VisualExamples.py stores in one place different pre-specified visualizations
6) Multiple .csv files store the logs of the simulation in its different aspects
7) output.txt is a redundant text file that describes all the steps in the simulation. Used mainly for debugging purposes
8) Multiple .png files might be stored as visualizations of simulations

To run the simulation, launch SimExamples.py file. Then, to visualize it, launch VisualExamples.py file.

Each round of the simulation consists of ten phases: 
1) Reset day: technical phase to reset all the day-to-day variables 
2) Produce: producers produce goods and pay salaries to their employees (consumers) 
3) Trade goods: producers offer the goods on the goods market where consumers can buy private goods and the government can buy public goods 
4) Trade labor: producers fire employees and create new offers on the labor market, where consumers can accept the offers to get hired 
5) Trade stocks (not fully implemented): producers pay dividends to the their shareholders 
6) Pay & take loans: banks pay and collect periodic payments, all the agents create loans offers that the banks can accept 
7) Consume & depreciate: consumers consume the goods (both private and public), after that all the existing goods are depreciated 
8) Bankruptcy: producers and banks that have negative balance get kicked out of the simulation 
9) Reflect day: all the agents calculate relevant statistics. Goods, labor, and loans markets' statistics are shared publicly through the census_ object 
10) Logging: all the data of all the agents is stored in Pandas dataframes

## The Machine Learning in question
In the simulation, I have four type of agents that make decisions: consumers, producers, banks, and the government (to see what exact decisions they are making please refer to the CLASS_SPECIFICATION file). Note that they are trying to maximize different things! Consumers maximize their utility (that they achieved from private goods), producers and banks maximize their profit, and the government maximizes the total utility (both from private and public goods) of the population. Instead of having one learning algorithm, here we have four of them. The natural candidate for the algorithm is a neural network, where input would be the known parameters of the simulation when the agent makes the decision; output would be the decision made; and the loss function would be the (negated) discounted value the agent is trying to maximize (private utility, total utility, or profit). We can run the simulation, calculate the discounted values at each round, and then train the four NNs (idea is similar to batch stochastics gradient descent) simultaneously.

## Applications
Possible applications of the project:
1) Additional material for economic textbooks to illuminate economic concepts.
2) An interactive tool for classroom or online course use.
3) Hackathons focusing on implementing the best strategies, merging STEM and economics.
4) A sanity check tool for macroeconomic decisions.
5) Simulation of real-world scenarios to analyze past events.
6) Building the bridge between economics and reinforcement machine learning

## Project timeline
The start of the project - December 19th

### Milestone 1 -> Released December 27th
The simulation includes consumers, producers, the goods market, and the labor market. Consumers and producers follow built-in sub-optimal greedy strategies in choosing prices and salaries. The output is stored in three CSV tables, which summarize i) consumers, ii) producers, and iii) the goods market evolving over time. One application (the 'apples vs art' simulation) is attached and visualized.

### Milestone 2 -> Released January 21st
Strategies are improved. Goods functionality is extended to the point where all the "unusual" goods (like land, capital, or licenses) can be easily specified. Added additional statistics in the logging process and the labor market csv table. Created a user-friendly pipeline that allows users to set up simulations and visualizations. Five simulations and two visualizations are set up as important examples for potential users.

### Milestone 3 -> Released March 17th
Added government, banks, and the loans market. Refactored code, made it more modular and easier to follow. Came up with a rough design for the ML applications in the simulation

### Milestone 4 -> End of Spring Semester
Train the algorithm to come up with the optimal strategies for the agents of the simulation.
