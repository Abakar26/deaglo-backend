class CoreAdapter:
    @staticmethod
    def strategy_simulation(user_id: str, result_id: str, data: dict) -> dict:
        return {
            "user_id": str(user_id),
            "result_id": str(result_id),
            "simulation_id": str(data["strategy_simulation_id"]),
            "type": "STRATEGY",
            "data": {
                "name": str(data["strategy_simulation_id"]),
                "notional": float(data["notional"]),
                "spread": 0.0,
                "is_base_sold": data["is_base_sold"],
                "base_currency": {
                    "symbol": data["base_currency"]["code"],
                    "name": data["base_currency"]["name"],
                },
                "foreign_currency": {
                    "symbol": data["foreign_currency"]["code"],
                    "name": data["foreign_currency"]["name"],
                },
                "simulation_environment": {
                    **data["simulation_environment"],
                    "start_date": str(data["start_date"]),
                    "end_date": str(data["end_date"]),
                    "initial_spot_rate": float(data["initial_spot_rate"]),
                    "initial_forward_rate": float(data["initial_forward_rate"]),
                },
                "strategies": list(
                    map(
                        lambda strategy: CoreAdapter.strategy(
                            strategy,
                            float(data["notional"]),
                            float(data["initial_spot_rate"]),
                            float(data["initial_forward_rate"]),
                            data["is_base_sold"],
                        ),
                        data["strategy_instance"],
                    )
                ),
            },
        }

    @staticmethod
    def strategy(
        data: dict,
        notional: float,
        spot_rate: float,
        fwd_rate: float,
        is_base_sold: bool,
    ) -> dict:
        is_composite = data["is_custom"] is False and len(data["legs"]) > 1
        return {
            "name": data["name"],
            "legs": list(
                map(
                    lambda leg: CoreAdapter.derivative(
                        leg, notional, spot_rate, fwd_rate, is_base_sold, is_composite
                    ),
                    data["legs"],
                )
            ),
        }

    @staticmethod
    def derivative(
        data: dict,
        notional: float,
        spot_rate: float,
        fwd_rate: float,
        is_base_sold: bool,
        is_composite: bool,
    ) -> dict:
        try:
            barrier_type = data["hidden_strategy_leg"]["barrier_type"]
            barrier_level = data["hidden_strategy_leg"]["barrier_level"]
        except KeyError:
            barrier_type = None
            barrier_level = None

        der_type = (
            "FORWARD"
            if data["hidden_strategy_leg"]["is_call"] is None
            else ("VANILLA" if barrier_type is None else "BARRIER")
        )

        is_call = (
            data["hidden_strategy_leg"]["is_call"]
            if data["hidden_strategy_leg"]["is_call"] is None or is_base_sold
            else (
                not data["hidden_strategy_leg"]["is_call"]
                if is_composite
                else data["hidden_strategy_leg"]["is_call"]
            )
        )

        # ITMS/OTMS% conversion to numeric
        strike = (
            1 - (float(data["strike_override"]) / 100)
            if is_call
            else 1 + (float(data["strike_override"]) / 100)
        ) * spot_rate
        barrier_level = (
            barrier_level
            if barrier_level is None
            else (
                1 - (float(barrier_level) / 100)
                if is_call
                else 1 + (float(barrier_level) / 100)
            )
        )

        is_bought = (
            (False if is_base_sold else True)
            if data["hidden_strategy_leg"]["is_call"] is None
            else data["hidden_strategy_leg"]["is_bought"]
        )

        return {
            "type": der_type,
            "data": {
                "name": str(data["strategy_leg_id"]),
                "is_bought": is_bought,
                "notional": notional,
                "is_call": is_call,
                "strike": strike,
                "premium": float(data["premium_override"]),
                "hedge_ratio": float(data["leverage_override"]),
                "barrier_type": barrier_type,
                "barrier_level": barrier_level,
                "fwd_rate": fwd_rate,
            },
        }

    @staticmethod
    def margin_simulation(user_id: str, result_id: str, data: dict) -> dict:
        return {
            "user_id": str(user_id),
            "result_id": str(result_id),
            "simulation_id": str(data["margin_simulation_id"]),
            "type": "MARGIN",
            "data": {
                "name": str(data["margin_simulation_id"]),
                "strategy_id": str(data["strategy_simulation_id"]),
                "strategy_result_id": str(data["strategy_result_id"]),
                "initial_margin": float(data["initial_margin_percentage"]),
                "variation_margin": float(data["variation_margin_percentage"]),
                "minimum_transfer_amount": float(data["minimum_transfer_amount"]),
            },
        }

    @staticmethod
    def hedge_simulation(user_id: str, result_id: str, data: dict) -> dict:
        return {
            "user_id": str(user_id),
            "result_id": str(result_id),
            "simulation_id": str(data["simulation_id"]),
            "type": "HEDGE",
            "data": {
                "skew": float(data["skew"]),
                "volatility": float(data["volatility"]),
                "spot_rate": float(data["spot_rate"]),
                "base_currency": {
                    "symbol": data["base_currency"]["symbol"],
                    "name": data["base_currency"]["name"],
                },
                "foreign_currency": {
                    "symbol": data["foreign_currency"]["symbol"],
                    "name": data["foreign_currency"]["name"],
                },
                "fwd_rates": data["fwd_rates"],
                "harvest": data["harvest"],
            },
        }
