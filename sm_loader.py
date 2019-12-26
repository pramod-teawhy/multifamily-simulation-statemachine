from datetime import datetime
from dateutil.relativedelta import relativedelta
from state_machine import UnitStateMachine


class StateMachineLoader(UnitStateMachine):
    OccupancyStatus_State_Mapping = {
        "OC": "occupied",
        "NA": "notice_available",
        "NL": "notice_leased",
        "VL": "vacant_leased_ready",
    }

    def __init__(self, config, simulation_params):
        self.params = {**config, **simulation_params}
        self.params['SimulationStartDate'] = self.params['ReportDate']
        self._update_dates()
        self._update_days()
        self._map_OccupancyStatus_State()
       
        UnitStateMachine.__init__(self, self.state)

    def _map_OccupancyStatus_State(self):
        OccupancyStatus = self.params['OccupancyStatus']
        if OccupancyStatus in self.OccupancyStatus_State_Mapping.keys():
            self.state = self.OccupancyStatus_State_Mapping[OccupancyStatus]
        else:
            if OccupancyStatus == "VA":
                if self.params['MakeReadyDateFutureLease'] is None:
                    self.state = "vacant_available_not_ready"
                    self.params['_VacantNotReadyStartDate'] = self.params['ReportDate']
                else:
                    self.state = "vacant_available_ready"
            elif OccupancyStatus == "VL":
                if self.params['MakeReadyDateFutureLease'] is None:
                    self.state = "vacant_leased_not_ready"
                    self.params['_VacantNotReadyStartDate'] = self.params['ReportDate']
                else:
                    self.state = "vacant_leased_ready"
            else:
                raise ValueError(f"Unhandeled OccupancyStatus = {OccupancyStatus}")

    def _update_dates(self):
        for key, val in self.params.items():
            if 'Date' in key:
                self.params[key] = self._load_date(val)

    def _update_days(self):
        labels = ['AverageNoticeLeadDays', 'MakeReadyDays', 'ApplicationToMoveInLeadDays']
        for label in labels:
            self.params[label] = relativedelta(days=self.params[label])

    @staticmethod
    def _load_date(date_string):
        try:
            return datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S GMT')
        except Exception as e:
            return date_string
