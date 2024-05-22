from django.db.models import Q


class SpotHistoryDataHelper:
    def __init__(
        self, base_currency, foreign_currency, date_from, date_to, *args, **kwargs
    ):
        self.base_currency = base_currency
        self.foreign_currency = foreign_currency
        self.date_from = date_from
        self.date_to = date_to

    def serializer_spot_history_date(self):
        from time_series.models import SpotHistoryData
        from time_series.serializers import SpotHistoryDataSerializer

        spot_history_data = SpotHistoryData.objects.filter(
            Q(currency=self.base_currency) | Q(currency=self.foreign_currency),
            date__range=[self.date_from, self.date_to],
        ).order_by("-date")

        combined_data = self.combine_data(list(spot_history_data))
        rates = []
        for data in combined_data:
            rates.append({"date": data["date"], "rate": self.calculate_spot_rate(data)})
        return SpotHistoryDataSerializer(rates, many=True).data

    def combine_data(self, queryset):
        # Combine the data into one row based on date
        combined_data = []
        temp_data = {}
        for item in queryset:
            if item.date not in temp_data:
                # Initialize the data structure for this date
                temp_data[item.date] = {
                    "date": item.date,
                    "base_currency": None,
                    "base_rate": None,
                    "foreign_currency": None,
                    "foreign_rate": None,
                }

            # Assign base or foreign currency and rate
            if item.currency == self.base_currency:
                temp_data[item.date]["base_currency"] = item.currency
                temp_data[item.date]["base_rate"] = item.rate
            else:
                temp_data[item.date]["foreign_currency"] = item.currency
                temp_data[item.date]["foreign_rate"] = item.rate

            # Check if both base and foreign currency are filled for the date
            if (
                temp_data[item.date]["base_currency"]
                and temp_data[item.date]["foreign_currency"]
            ):
                combined_data.append(temp_data.pop(item.date))
        return combined_data

    def calculate_spot_rate(self, data):
        if self.base_currency == "USD":
            spot_rate = data["foreign_rate"]
        elif self.foreign_currency == "USD":
            spot_rate = 1 / data["base_rate"]
        else:
            spot_rate = data["foreign_rate"] / data["base_rate"]
        return spot_rate
