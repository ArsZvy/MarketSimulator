# Market Simulator
This project is initiated, designed, and implemented by AZ (Arseniy Zvyagintsev).

## Motivation
This project aims to create a fictional world populated with consumers, producers, markets, governments, banks, and so on, that would simulate real-world economic scenarios in order 1) to improve education and 2) test game theory applications in economics. I believe that for STEM-inclined / game theory students, such an approach to studying economics would be more effective compared to a classical textbook/lecture-based approach.

## Description
Let's analyze agents of the simulation one by one:

1) Goods \
Goods are something produced by Producers to increase income and purchased and consumed by Consumers to increase utility. The unique attributes of each good are the consumption and depreciation rates.
2) Consumers \
Consumers work for Producers in exchange for a salary. After that, they purchase goods on the Goods Market. Then they might seek a job on the Labor Market. Finally, they consume goods to increase their utility. The unique attributes of consumers are the utility function and skill.
3) Producers \
Producers produce Goods with the help of employed Consumers and sell them on the Goods Market to increase their profit. Then they revise their staff: fire and hire employees according to their strategy. Finally, they pay dividends to the company owners. The unique attributes of producers are the productivity function and the type of good produced.
4) Goods Market \
The Goods Market is the medium where transactions of Goods take place.
5) Labor Market \
The Labor Market is the medium where Producers meet Consumers to hire them.
6) Census \
Census is the data center of the simulation: it stores references to other objects and all the relevant statistics over time.
7) Simulation \
Simulation is a class that correctly sets up the simulation, sequentially runs all the steps, and then correctly wraps it up.

Now let's have a look into the architecture of the simulation:

1) Agents.py stores all the relevant classes described above
2) AgentExamples.py is wrapper file that allows users to easily create specific entities of various classes
3) SimExamples.py is a wrapper file that stores in one place different pre-specified simulations
4) Visuals.py has class Visual that can easily graph all the important statistics
5) VisualExamples.py stores in one place different pre-specified visualizations
6) consumers.csv, producers.csv, goods_market.csv, and labor_market.csv store the logs of the simulation in its different aspects
7) output.txt is a redundant text file that describes all the steps in the simulation. Used mainly for debugging purposes
8) Multiple .png files might be stored as visualizations of simulations

To run the simulation, launch SimExamples.py file. Then, to visualize it, launch VisualExamples.py file

## Applications
Possible applications of the project:
1) Additional material for economic textbooks to illuminate economic concepts.
2) An interactive tool for classroom or online course use.
3) Hackathons focusing on implementing the best strategies, merging STEM and economics.
4) A sanity check tool for macroeconomic decisions.
5) Simulation of real-world scenarios to analyze past events.

## Project timeline
The start of the project - December 19th

### Milestone 1 -> Released December 27th
The simulation includes consumers, producers, the goods market, and the labor market. Consumers and producers follow built-in sub-optimal greedy strategies in choosing prices and salaries. The output is stored in three CSV tables, which summarize i) consumers, ii) producers, and iii) the goods market evolving over time. One application (the 'apples vs art' simulation) is attached and visualized.

### Milestone 2 -> Released January 21st
Strategies are improved. Goods functionality is extended to the point where all the "unusual" goods (like land, capital, or licenses) can be easily specified. Added additional statistics in the logging process and the labor market csv table. Created a user-friendly pipeline that allows users to set up simulations and visualizations. Five simulations and two visualizations are set up as important examples for potential users.

### Milestone 3 -> ETA - End of Spring semester
Agents' strategies are diversified and fine-tuned (under Prof Neugeboren guidance, hopefully, as a part of HCRP program). The code is refactored to be completely reliable, easy-to-follow and easy-to-modify. International trade is added (for now, within one currency)

### Milestone 4 (complete Microeconomics 101) -> Ever
The simulation gets a government (no central bank for now), government expenditure, taxes, externalities, and goods with the risk of market failure. The government has a sub-optimal strategy to prevent market failures and account for externalities.

### Milestone 5 (Presentation)
Show the product, get feedback.
