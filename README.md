# Market Simulator
This project is initiated, designed, and implemented by AZ (Arseniy Zvyagintsev).

## Motivation
This project aims to create a fictional world populated with consumers, producers, markets, governments, banks, and so on, that would simulate real-world economic scenarios in order to improve education in economics. I believe that for STEM-inclined people, such an approach to studying economics would be more effective compared to a classical textbook/lecture-based approach.

## Description
Let's analyze parts of the simulation one by one:

1) Goods \
Goods are something produced by Producers to increase income and purchased and consumed by Consumers to increase utility. The unique attributes of each good are the consumption rate and depreciation rate.
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

### Milestone 2 -> ETA - January 10th
Real estate and stock exchange markets are added to the simulation. Complex market statistics (such as total surplus or elasticity) are added to the output. Consumers' and producers' strategies are improved and diversified (so different agents might follow different strategies). Multiple applications are attached and visualized.

### Milestone 3 -> End of winter break
International trade is added (for now, within one currency). The pipeline of applications and visualizations is added.

### Milestone 4 (complete Microeconomics 101) -> Ever
The simulation gets a government (no central bank for now), government expenditure, taxes, externalities, and goods with the risk of market failure. The government has a sub-optimal strategy to prevent market failures and account for externalities.

### Milestone 5 (Presentation)
Show the product, get feedback.
