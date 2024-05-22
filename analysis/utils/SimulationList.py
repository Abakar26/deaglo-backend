from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from hedge_simulation.models import HedgeSimulation
from margin_simulation.models import MarginSimulation
from strategy_simulation.models import StrategySimulation
from rest_framework.exceptions import NotFound


def process_parameter(parameter):
    result = []
    if isinstance(parameter, str):
        result = parameter.split(",")
    return result


class CustomPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 100


class SimulationListHelper:
    @staticmethod
    def toggle_simulation(simulation_type, simulation_id):
        match simulation_type:
            case "STRATEGY":
                simulation = StrategySimulation.objects.get(pk=simulation_id)
            case "MARGIN":
                simulation = MarginSimulation.objects.get(pk=simulation_id)
            case "HEDGE":
                simulation = HedgeSimulation.objects.get(pk=simulation_id)
            case _:
                raise NotFound("Simulation not found")
        simulation.pin = not simulation.pin
        simulation.save(new_result=False)

    @staticmethod
    def to_representation(
        instance,
        request,
        simulation_order=None,
        simulation_type=None,
        simulation_status=None,
    ):
        combined_results = []
        pagination = CustomPagination()
        simulation_instances = []
        if (
            "Strategy Simulation" in process_parameter(simulation_type)
            or simulation_type is None
        ):
            simulation_instances.extend(
                StrategySimulation.objects.filter(
                    analysis_id=instance.analysis_id,
                    is_deleted=False,
                ).order_by(simulation_order)
                if simulation_order
                else StrategySimulation.objects.filter(analysis_id=instance.analysis_id)
            )

        if (
            "Margin Simulation" in process_parameter(simulation_type)
            or simulation_type is None
        ):
            simulation_instances.extend(
                MarginSimulation.objects.filter(
                    analysis_id=instance.analysis_id,
                    is_deleted=False,
                ).order_by(simulation_order)
                if simulation_order
                else MarginSimulation.objects.filter(analysis_id=instance.analysis_id)
            )

        if "Hedge IRR" in process_parameter(simulation_type) or simulation_type is None:
            simulation_instances.extend(
                HedgeSimulation.objects.filter(
                    analysis_id=instance.analysis_id,
                    is_deleted=False,
                ).order_by(simulation_order)
                if simulation_order
                else HedgeSimulation.objects.filter(analysis_id=instance.analysis_id)
            )

        if simulation_status:
            simulation_instances = [
                simulation
                for simulation in simulation_instances
                if getattr(
                    simulation,
                    (
                        "status"
                        if isinstance(simulation, HedgeSimulation)
                        else "type_status"
                    ),
                ).name
                in process_parameter(simulation_status)
            ]

        if simulation_order:
            reverse = simulation_order.lower() == "name"
            simulation_instances.sort(
                key=lambda x: (
                    getattr(x, simulation_order).lower()
                    if reverse
                    else getattr(x, simulation_order)
                ),
                reverse=not reverse,
            )

        if simulation_instances:
            paginated_instances = pagination.paginate_queryset(
                simulation_instances, request
            )

            for simulation in paginated_instances:
                combined_results.append(
                    {
                        "id": str(simulation.pk),
                        "type": simulation.type,
                        "date_updated": simulation.date_updated,
                        "name": simulation.name,
                        "simulation_status": simulation.simulation_status,
                        "pin": simulation.pin,
                        "result_id": simulation.result_id,
                    }
                )

            combined_results.sort(key=lambda x: (x["pin"]), reverse=True)

        return (
            pagination.get_paginated_response(combined_results[:3])
            if combined_results
            else Response([])
        )
