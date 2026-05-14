My-AGT-Bidding-Agent: "We_Run_Venezuela"
An autonomous strategic bidding agent developed for the Algorithmic Game Theory (AGT) competition at The Hebrew University of Jerusalem. 
The agent is designed to compete in Second-Price (Vickrey) Auctions under strict budget constraints.

🧠 Strategy: Opportunity Cost & Market InferenceUnlike truthful bidders, this agent balances current utility against future opportunities by calculating a dynamic Opportunity Cost. It treats the auction as a long-term optimization problem rather than a series of isolated events.  

🛠 Key Technical FeaturesMarket Inference Engine: Deduces the actual distribution of items (High/Mixed/Low) based on clearing prices and statistical inventory tracking (the 6-10-4 Rule).  
Dynamic Opponent Modeling: Tracks individual opponent budgets in real-time to identify the "Price Setter" (the 2nd wealthiest rival) and calibrates bids just above the competitive threshold.  
Future Opportunity Cost: A mathematical penalty that adjusts bid aggression based on remaining market liquidity and the scarcity of high-value items, preventing early budget exhaustion. 

Asymmetric Bidding Logic:
Low Value: Bid truthfully to secure guaranteed utility.  
Mixed Value: Target efficient wins by outbidding the price setter.  
High Value: Bid with a controlled discount (shading) adjusted by opportunity cost.  
End-Game Surplus Liquidation: In the final 7 rounds, the agent shifts to an aggressive mode to ensure all remaining capital is converted into utility.  

🚀 Competitive AdvantagesBudget Awareness: Prevents "Winner's Curse" and early exhaustion through a hard bid ceiling (16.8) and liquidity analysis.  
Bullying Mechanism: When holding a significant budget lead, the agent strategically blocks competitors by bidding just above their maximum feasible range. 
Adaptive Behavior: Continuously adapts to market pressure and opponent behavior rather than following a static strategy.  

💻 Technical StackLanguage: Python
Concepts: Mechanism Design, Vickrey Auctions, Probabilistic Inventory Management, Finite State Adaptation.
