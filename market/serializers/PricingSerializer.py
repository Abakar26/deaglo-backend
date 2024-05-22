from datetime import datetime

from rest_framework import serializers


class SpotRateRequestSerializer(serializers.Serializer):
    base_currency = serializers.CharField(min_length=3, max_length=3)
    foreign_currency = serializers.CharField(min_length=3, max_length=3)
    is_base_sold = serializers.BooleanField()
    start_date = serializers.DateTimeField(required=False)


class SpotRateResponseSerializer(serializers.Serializer):
    base_currency = serializers.CharField()
    foreign_currency = serializers.CharField()
    spot_rate = serializers.FloatField()
    timestamp = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data", {})
        data["base_currency"] = data.get("Currency")
        data["foreign_currency"] = data.get("CtrCcy")
        data["spot_rate"] = data.get("Spot")
        super().__init__(*args, **kwargs)

    def get_timestamp(self, obj):
        hor_date = self.initial_data.get("HorDate", "")
        if hor_date:
            parsed_date = datetime.strptime(hor_date, "%H:%M %a %d %b %y")
            return parsed_date.isoformat() + "Z"
        return None


class ForwardRateRequestSerializer(serializers.Serializer):
    base_currency = serializers.CharField(min_length=3, max_length=3)
    foreign_currency = serializers.CharField(min_length=3, max_length=3)
    is_base_sold = serializers.BooleanField()
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField()
    spot_override = serializers.FloatField(required=False)


class ForwardRateResponseSerializer(serializers.Serializer):
    base_currency = serializers.CharField()
    foreign_currency = serializers.CharField()
    spot_rate = serializers.FloatField()
    forward_rate = serializers.FloatField()
    expiry = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data", {})
        data["base_currency"] = data.get("Currency")
        data["foreign_currency"] = data.get("CtrCcy")
        data["spot_rate"] = data.get("Spot")
        data["forward_rate"] = data.get("Forward")
        super().__init__(*args, **kwargs)

    def get_expiry(self, obj):
        ex_time = self.initial_data.get("ExTime", "")
        ex_date = self.initial_data.get("ExDate", "")
        if ex_time and ex_date:
            expiry_datetime = datetime.strptime(
                f"{ex_time} {ex_date}", "%H:%M %Z %d %b %y"
            )
            return {
                "date": expiry_datetime.isoformat() + "Z",
                "days": int(self.initial_data.get("ExDays").replace(",", "")),
            }
        return None

    def get_timestamp(self, obj):
        hor_date = self.initial_data.get("HorDate", "")
        if hor_date:
            parsed_date = datetime.strptime(hor_date, "%H:%M %a %d %b %y")
            return parsed_date.isoformat() + "Z"
        return None


class OptionPriceRequestSerializer(serializers.Serializer):
    base_currency = serializers.CharField(min_length=3, max_length=3)
    foreign_currency = serializers.CharField(min_length=3, max_length=3)
    is_base_sold = serializers.BooleanField()
    is_bought = serializers.BooleanField()
    is_call = serializers.BooleanField()
    option_style = serializers.ChoiceField(
        default="european", choices=["european", "american"], required=False
    )
    notional = serializers.FloatField()
    strike = serializers.FloatField()
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField()
    barrier_type = serializers.ChoiceField(
        choices=["up-in", "up-out", "down-in", "down-out"], required=False
    )
    barrier_level = serializers.FloatField(required=False)
    spot_override = serializers.FloatField(required=False)
    forward_override = serializers.FloatField(required=False)


class OptionPriceResponseSerializer(serializers.Serializer):
    base_currency = serializers.CharField()
    foreign_currency = serializers.CharField()
    is_call = serializers.BooleanField()
    strike = serializers.FloatField()
    expiry = serializers.SerializerMethodField()
    premium = serializers.SerializerMethodField()
    spot_rate = serializers.FloatField()
    forward_rate = serializers.FloatField()
    timestamp = serializers.SerializerMethodField()
    greeks = serializers.SerializerMethodField(required=False)

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data", {})
        data["base_currency"] = data.get("Currency")
        data["foreign_currency"] = data.get("CtrCcy")
        data["strike"] = data.get("Strike")
        data["spot_rate"] = data.get("Spot")
        data["forward_rate"] = data.get("Forward")
        option_type = data.get("Strategy", "").lower()
        data["is_call"] = None if option_type == "" else option_type == "call"
        super().__init__(*args, **kwargs)

    def get_expiry(self, obj):
        ex_time = self.initial_data.get("ExTime", "")
        ex_date = self.initial_data.get("ExDate", "")
        if ex_time and ex_date:
            expiry_datetime = datetime.strptime(
                f"{ex_time} {ex_date}", "%H:%M %Z %d %b %y"
            )
            return {
                "date": expiry_datetime.isoformat() + "Z",
                "days": int(self.initial_data.get("ExDays").replace(",", "")),
            }
        return None

    def get_premium(self, obj):
        prem_date = self.initial_data.get("PremDate", "")
        premium_timestamp = None
        if prem_date:
            premium_timestamp = (
                datetime.strptime(prem_date, "%a %d %b %y").isoformat() + "Z"
            )
        return {
            "type": self.initial_data.get("PremType", "").lower(),
            "percentage": self.initial_data.get("PctPrice"),
            "amount": self.initial_data.get("Premium"),
            "currency": self.initial_data.get("PremCcy"),
            "counter_amount": self.initial_data.get("CtrPrem"),
            "counter_currency": self.initial_data.get("CtrCcy"),
            "timestamp": premium_timestamp,
        }

    def get_timestamp(self, obj):
        hor_date = self.initial_data.get("HorDate", "")
        if hor_date:
            parsed_date = datetime.strptime(hor_date, "%H:%M %a %d %b %y")
            return parsed_date.isoformat() + "Z"
        return None

    def get_greeks(self, obj) -> dict:
        return {
            "delta": {
                "value": self.initial_data.get("Delta"),
                "percentage": self.initial_data.get("PctDelta"),  # respect to spot
                "volatility_adjusted_value": self.initial_data.get(
                    "VolAdjDelta"
                ),  # respect to fwd
                "volatility_adjusted_percentage": self.initial_data.get(
                    "PctVolAdjDelta"
                ),
                "amount": self.initial_data.get("DeltaAmt"),
                "counter_amount": self.initial_data.get("CtrDeltaAmt"),
                "counter_percentage_amount": self.initial_data.get("CtrPctDeltaAmt"),
            },
            "gamma": {
                "value": self.initial_data.get("Gamma"),
                "amount": self.initial_data.get("GammaAmt"),
            },
            "vega": {
                "value": self.initial_data.get("PctVega"),
                "amount": self.initial_data.get("CtrVegaAmt"),
                "counter_value": self.initial_data.get("Vega"),
                "counter_amount": self.initial_data.get("CtrPctVegaAmt"),
            },
            "d_vega_d_vol": {
                "value": self.initial_data.get("Dvegadvol"),
                "amount": self.initial_data.get("DvegadvolAmt"),
                "percentage": self.initial_data.get("PctDvegadvol"),
                "percentage_amount": self.initial_data.get("PctDvegadvolAmt"),
            },
            "phi": {
                "percentage": self.initial_data.get("PctPhi"),
                "value": self.initial_data.get("Phi"),
            },
            "theta": {
                "percentage": self.initial_data.get("PctDecay"),
                "value": self.initial_data.get("Decay"),
            },
            "rho": {
                "value": self.initial_data.get("Rho"),
                "percentage": self.initial_data.get("PctRho"),
            },
            "vanna": {
                "value": self.initial_data.get("Vanna"),
                "amount": self.initial_data.get("VannaAmount"),
            },
        }
