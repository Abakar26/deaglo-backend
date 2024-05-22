import os
from datetime import datetime
from typing import Literal, Optional

import requests
import xmltodict
from django.template import loader
import xml.etree.ElementTree as ET


class FenicsApiClient:
    """A client for interacting with the FENICS API."""

    def __init__(self, username=None, password=None, api_url=None):
        self.username = username or os.getenv("FENICS_USERNAME")
        self.password = password or os.getenv("FENICS_PASSWORD")
        self.api_url = api_url or os.getenv("FENICS_PRICING_API_URL")

    def _send_request(self, xml_payload: str) -> dict:
        """Sends the request to Fenics Pricing API"""
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        minified_payload = self._minify_xml(xml_payload)

        response = requests.post(
            self.api_url, data="xml=" + minified_payload, headers=headers
        )

        if response.status_code == 200:
            response_dict = xmltodict.parse(response.text)["gfi_message"]["body"]
            if "data" not in response_dict:
                return {"errors": response_dict["response"]["option"]}
            else:
                return self._transform_response(response_dict["data"])
        else:
            response.raise_for_status()

    def _transform_response(self, input_dict: dict) -> dict:
        """Strips away unnecessary data from response"""
        # Extract the nested node
        node = input_dict.get("node", {})

        # Initialize the new dictionary
        new_dict = {}

        # Loop through each field in the node and add it to the new dictionary
        for field in node.get("field", []):
            field_name = field.get("@name")
            field_value = field.get("@value")
            new_dict[field_name] = field_value

        return new_dict

    def _create_xml_payload(self, template_path: str, data: dict) -> str:
        """Populates Django template with data dictionary values"""
        django_template = loader.get_template(template_path)
        return django_template.render(data)

    def _parse_and_format_date(self, value: datetime | str) -> str:
        """Validate and format date fields."""
        if isinstance(value, datetime):
            return value.strftime("%d %b %y")
        try:
            datetime.strptime(value, "%d %b %y")
            return value
        except ValueError:
            raise ValueError(f"Invalid date format: {value}")

    def _minify_xml(self, xml_string: str) -> str:
        # Parse the XML
        root = ET.fromstring(xml_string)

        # Remove whitespace and newlines
        for element in root.iter():
            if element.text is not None:
                element.text = element.text.strip()
            if element.tail is not None:
                element.tail = element.tail.strip()

        # Serialize the XML back to a string
        return ET.tostring(root, encoding="unicode", method="xml")

    def vanilla_pricing_query(
        self,
        foreign_currency: str,
        base_currency: str = "USD",
        notional: Optional[float | int] = None,
        spot_override: Optional[float | int] = None,
        strike: Optional[float | int] = None,
        is_call: bool = True,
        start_date: Optional[datetime | str] = datetime.utcnow(),
        end_date: Optional[datetime | str] = None,
        transaction_id: str = "1234567890",
        option_style: str = "European",
        hedge_ratio: float | int = 1.0,
        is_base_sold: Optional[bool] = False,
        is_bought: Optional[bool] = False,
    ):
        """Requests vanilla option pricing data"""
        option_type = "call" if is_call else "put"
        data = {
            "transactionId": transaction_id,
            "timestamp": datetime.utcnow(),
            "horDate": self._parse_and_format_date(start_date)
            if start_date is not None
            else None,
            "exDate": self._parse_and_format_date(end_date)
            if end_date is not None
            else None,
            "strike": strike,
            "ctrCcy": base_currency if is_base_sold else foreign_currency,
            "currency": foreign_currency if is_base_sold else base_currency,
            "strategy": option_type,
            "username": self.username,
            "password": self.password,
            "amount": notional,
            "pctHedge": hedge_ratio,
            "spot": spot_override,
            "class": option_style.capitalize(),
            "direction": "buy" if is_bought else "sell",
        }
        data = {k: v for k, v in data.items() if v is not None}
        xml_payload = self._create_xml_payload("fenics/option_pricing.xml", data)
        return self._send_request(xml_payload)

    def _map_barrier_type(self, barrier_type, option_type):
        if barrier_type == "up-in":
            return "Knockin" if option_type == "put" else "Reverse Knockin"
        elif barrier_type == "up-out":
            return "Knockout" if option_type == "put" else "Reverse Knockout"
        elif barrier_type == "down-in":
            return "Reverse Knockin" if option_type == "put" else "Knockin"
        elif barrier_type == "down-out":
            return "Reverse Knockout" if option_type == "put" else "Knockout"
        else:
            raise ValueError(f"Unsupported barrier type: {barrier_type}")

    def barrier_pricing_query(
        self,
        end_date: datetime | str,
        foreign_currency: str,
        barrier_type: Literal["up-in", "up-out", "down-in", "down-out"],
        barrier_level: float | int,
        base_currency: str = "usd",
        is_call: bool = True,
        strike: Optional[float | int] = None,
        start_date: Optional[datetime | str] = None,
        notional: Optional[float | int] = None,
        spot_override: Optional[float | int] = None,
        forward_override: Optional[float | int] = None,
        option_style: str = "European",  # TODO: use when adding american options to API
        low_barrier: Optional[float | int] = None,
        high_barrier: Optional[float | int] = None,
        maturity: Optional[str] = None,
        transaction_id: str = "1234567890",
        hedge_ratio: float | int = 1.0,
        is_base_sold: Optional[bool] = False,
        is_bought: Optional[bool] = False,
    ):
        """Requests barrier option pricing data"""
        if barrier_type in [
            "Knockin",
            "Reverse Knockin",
            "Knockout",
            "Reverse Knockout",
        ]:
            # Only consider barrier level
            if barrier_level is None:
                raise ValueError(
                    "Trigger is required for Knockin/Reverse Knockout options."
                )
        elif barrier_type in ["Double Knockin", "Double Knockout"]:
            # Consider low barrier and high barrier values
            if low_barrier is None or high_barrier is None:
                raise ValueError(
                    "Both LoTrigger and HiTrigger are required for Double Knockin/Double Knockout options."
                )

        option_type = "call" if is_call else "put"
        data = {
            "transactionId": transaction_id,
            "horDate": start_date,
            "exDate": end_date,
            "timestamp": datetime.utcnow(),
            "username": self.username,
            "password": self.password,
            "ctrCcy": base_currency if is_base_sold else foreign_currency,
            "currency": foreign_currency if is_base_sold else base_currency,
            "class": self._map_barrier_type(barrier_type, option_type),
            # "class": _class,
            "strategy": option_type,
            "maturity": maturity,
            "strike": strike,
            "trigger": barrier_level,
            "loTrigger": low_barrier,
            "hiTrigger": high_barrier,
            "amount": notional,
            "pctHedge": hedge_ratio,
            "spot": spot_override,
            "forward": forward_override,
            "direction": "buy" if is_bought else "sell",
        }
        data = {k: v for k, v in data.items() if v is not None}
        xml_payload = self._create_xml_payload(
            "fenics/barrier_option_pricing.xml", data
        )
        return self._send_request(xml_payload)
