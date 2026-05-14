"""
AGT Competition - Student Agent Template
========================================

Team Name: We_Run_Venezuela
Members:
  - Eden Topper 314055153
  - Daniel Engel 208322594
  - Yaniv Cheskis 327882742

Strategy Description:
The agent employs a dynamic "Opportunity Cost" strategy balanced with market inference.
It categorizes items into HIGH, MIXED, and LOW utility based on personal valuation percentiles.
The core logic relies on preserving budget for high-value future opportunities by calculating
a penalty (Opp Cost) derived from remaining market liquidity and the scarcity of high value items.
In the early/midgame, the agent uses 'Bid Shading' to maximize utility, while in the end game (last 7 rounds),
it shifts to an aggressive 'Surplus Liquidation' mode to ensure no capital is left unspent.

Key Features:
- Market Inference Engine: Deduces the distribution of items (High/Mixed/Low) based on 2nd price
  clearing results and inventory tracking (6-10-4 Rule).
- Dynamic Opponent Modeling: Tracks individual opponent budgets and identifies the 'Price Setter'
  (the 2nd richest rival) to calibrate bids just above the competitive threshold.
- Future Opportunity Cost: A mathematical penalty that adjusts bid aggression based on
  remaining rounds and total market cash (liquidity), preventing early budget exhaustion.
- End Game Safety Rails: Automatic aggressive bidding in final rounds and a hard ceiling (16.8)
  to protect against 'Winner's Curse' in high volatility scenarios.
"""

from typing import Dict, List


class BiddingAgent:
    """
       Your bidding agent for the AGT Auto-Bidding Competition.

       This template provides the required interface and helpful structure.
       Replace the TODO sections with your own strategy implementation.
       """

    def __init__(self, team_id: str, valuation_vector: Dict[str, float],
                 budget: float, auction_items_sequence: List[str]):
        """
        Initialize the bidding agent.

        Args:
            team_id: Unique identifier for the team
            valuation_vector: Dictionary mapping item_id to valuation
                             e.g., {"item_0": 15.3, "item_1": 8.2, ...}
            budget: Initial budget (typically 60)
            auction_items_sequence: List of item_ids that will be auctioned (15 items)
                                   Note: You know WHICH items but not the ORDER
        """
        self.team_id = team_id
        self.valuation_vector = valuation_vector
        self.budget = budget
        self.initial_budget = budget
        self.auction_items_sequence = auction_items_sequence
        self.utility = 0
        self.items_won = []

        # Students can add custom attributes here for their strategy
        # Examples:
        # self.beliefs = {}  # For Bayesian updates
        # self.opponent_models = {}
        # self.round_history = []
        # Counter for elapsed rounds to determine timing and urgency
        self.rounds_played = 0
        self.total_rounds = 15

        # --- Hard Inventory Management (6-10-4 Rule) ---
        # Global counter for remaining item types based on statistical expectations (6 High, 10 Mixed, 4 Low)
        self.remaining_inventory = {"HIGH": 6, "MIXED": 10, "LOW": 4}
        self.market_prices = []
        # Tracker for each opponent's remaining budget to identify market leaders
        self.opponent_budgets = {}

        # --- Private Valuation Percentiles (Prior Beliefs) ---
        # Sorts all 20 possible items to categorize them based on personal utility
        vals = sorted(valuation_vector.values(), reverse=True)
        # Dynamic thresholds to categorize items based on personal valuation percentiles
        self.high_threshold = vals[5]
        self.low_threshold = vals[15]

    def _update_available_budget(self, item_id: str, winning_team: str, price_paid: float):
        """
        Internal method to update budget after auction.
        DO NOT MODIFY - this is called automatically by the system.

        Args:
            item_id: ID of the auctioned item
            winning_team: ID of the winning team
            price_paid: Price paid by the winner (second-highest bid)
        """
        if winning_team == self.team_id:
            self.budget -= price_paid
            self.items_won.append(item_id)

    def update_after_each_round(self, item_id: str, winning_team: str, price_paid: float):
        """
        Called after each auction round with public information.
        Students can use this to update their beliefs, opponent models, etc.

        Args:
            item_id: ID of the item that was auctioned
            winning_team: ID of the team that won
            price_paid: Price paid (second-highest bid)

        Returns:
            True if update successful
        """
        # Update budget and utility (handled by system)
        self._update_available_budget(item_id, winning_team, price_paid)

        if winning_team == self.team_id:
            self.utility += (self.valuation_vector[item_id] - price_paid)

        # Students can add their own logic here
        # Examples:
        # - Update beliefs about opponent valuations
        # - Track bidding patterns
        # - Adjust strategy for future rounds
        my_val = self.valuation_vector.get(item_id, 0)

        # Dynamic Opponent Budget Tracking
        if winning_team and winning_team != self.team_id:
            if winning_team not in self.opponent_budgets:
                self.opponent_budgets[winning_team] = 60.0
            self.opponent_budgets[winning_team] -= price_paid

        # --- Market Inference Engine ---
        # Deduces actual item type by cross-referencing price paid and personal valuation
        if price_paid >= 8.0:
            if my_val > 10.0:
                actual_type = "HIGH"
            else:
                actual_type = "MIXED"

        elif price_paid <= 6.0:
            if my_val <= 10.0:
                actual_type = "LOW"
            else:
                actual_type = "MIXED"

        else:
            if my_val >= 10.0:
                actual_type = "HIGH"
            else:
                actual_type = "MIXED"
        # Inventory overflow logic: deduct from next logical category if the current one is empty
        if self.remaining_inventory[actual_type] > 0:
            self.remaining_inventory[actual_type] -= 1
        else:
            if actual_type == "LOW":
                if self.remaining_inventory["MIXED"] > 0:
                    self.remaining_inventory["MIXED"] -= 1
                else:
                    self.remaining_inventory["HIGH"] = max(0, self.remaining_inventory["HIGH"] - 1)

            elif actual_type == "HIGH":
                if self.remaining_inventory["MIXED"] > 0:
                    self.remaining_inventory["MIXED"] -= 1
                else:
                    self.remaining_inventory["LOW"] = max(0, self.remaining_inventory["LOW"] - 1)

            elif actual_type == "MIXED":
                if self.remaining_inventory["LOW"] > 0:
                    self.remaining_inventory["LOW"] -= 1
                else:
                    self.remaining_inventory["HIGH"] = max(0, self.remaining_inventory["HIGH"] - 1)

        self.market_prices.append(price_paid)
        self.rounds_played += 1
        return True

    def _get_market_metrics(self):
        """
        Calculates market pressure and 'Shadow Value' of money.
        Determines who sets the 2nd price (Price Setter).
        """
        if not self.opponent_budgets:
            return 60.0, 60.0, 240.0
        budgets = sorted(self.opponent_budgets.values(), reverse=True)
        richest = budgets[0]
        # The 2nd richest rival who likely dictates the clearing price in a second-price auction
        price_setter = budgets[1] if len(budgets) > 1 else richest
        total_market_cash = sum(budgets)
        return richest, price_setter, total_market_cash

    def bidding_function(self, item_id: str) -> float:
        """
        Decide how much to bid for the current item.
        This is the main method students need to implement.

        Args:
            item_id: ID of the current item being auctioned

        Returns:
            float: Your bid amount (must be 0 <= bid <= current_budget)

        Note:
            - You have 2 seconds to return a bid
            - Bids exceeding budget will be automatically capped
            - Invalid returns or timeouts result in a 0 bid
            - This is a second-price sealed-bid auction (Vickrey auction)
        """
        # STUDENTS: IMPLEMENT YOUR BIDDING STRATEGY HERE

        # Simple example strategy: bid your true valuation (truthful bidding)
        # This is optimal in standard second-price auctions without budget constraints
        val = self.valuation_vector.get(item_id, 0)
        rounds_left = max(1, self.total_rounds - self.rounds_played)

        if val <= 0 or self.budget <= 0:
            return 0.0

        richest, price_setter, market_cash = self._get_market_metrics()
        high_left = self.remaining_inventory["HIGH"]
        medium_left = self.remaining_inventory["MIXED"]

        # --- 1. Future Opportunity Cost Calculation ---
        # Measures how much we should save for future rounds.
        # Cost increases when HIGH items are scarce and rounds are few.
        # Average cash per remaining item to estimate overall market competition
        market_liquidity = market_cash / max(1, high_left + medium_left)
        # Future opportunity cost: penalty for spending now versus saving for upcoming high-value items
        # More HIGH items ahead -> agent is more conservative
        opp_cost = (high_left / rounds_left) * (market_liquidity / 15.0) * 4.2  # 4.2

        # --- 2. Item Categorization ---
        if val >= self.high_threshold:
            category = "HIGH"
        elif val <= self.low_threshold:
            category = "LOW"
        else:
            category = "MIXED"

        if val <= 10:
            bid = val
            return round(float(max(0.0, min(bid, self.budget - 0.01))), 2)

        # --- 3. Bidding Logic Layers ---

        # Layer A: Bullying Strategy
        # If we have a massive cash lead, we block others by bidding just above their capacity
        if self.budget > price_setter + 15 and val > 14:
            bid = price_setter + 0.42

        # Layer B: Category-Specific Strategies
        elif category == "HIGH":
            # Protective Bidding: Reduce bid by Opportunity Cost to avoid overpaying
            bid = val - opp_cost
            if val < 14.0:
                bid *= 0.8

        elif category == "MIXED":
            # Mixed Item Hunting: Target high utility by beating the 2nd richest rival
            bid = min(val * 0.90, price_setter + 1)
            bid = max(bid, val * 0.85)  # Safety floor to ensure victory on lucrative items

        else:  # LOW - only for safety , never reached
            bid = val

        # --- 4. End-Game & Surplus Liquidation ---
        if rounds_left <= 7:
            # Check if current budget exceeds total expected value of remaining items
            remaining_sequence = self.auction_items_sequence[self.rounds_played:]
            future_val = sum(self.valuation_vector.get(tid, 0) for tid in remaining_sequence)

            if self.budget >= future_val * 0.8:
                bid = max(bid, val * 0.96)  # Deploy capital to secure points

            if val > price_setter:
                bid = max(bid, richest + 0.05)  # Final round outbidding

        # --- 5. Safety Rails ---
        # Epsilon value for symmetry breaking to win ties against identical bids
        bid += 0.02

        # Guaranteed Utility Margin: Never bid exact value to ensure positive gain
        bid = min(bid, val - 0.02)

        # Absolute Budget Ceiling: Prevent illegal bids
        bid = min(bid, self.budget - 0.01)

        # Hard bid ceiling to prevent early budget exhaustion regardless of item valuation
        bid = min(bid, 16.8)

        return round(float(max(0.0, bid)), 2)
