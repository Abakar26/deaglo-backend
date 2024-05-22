def get_custom_strategy_from_response(response):
    custom_strategies = []
    for object in response:
        if object["is_custom"]:
            custom_strategies.append(object)
    return custom_strategies


def get_default_strategy_from_response(response):
    default_strategies = []
    for object in response:
        if not object["is_custom"]:
            default_strategies.append(object)
    return default_strategies
