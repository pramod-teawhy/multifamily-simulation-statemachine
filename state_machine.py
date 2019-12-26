from transitions import Machine
from dateutil.relativedelta import relativedelta
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(message)s")
# Set transitions' log level to INFO; DEBUG messages will be omitted
logging.getLogger('transitions').setLevel(logging.INFO)
doLog = False

class UnitStateMachine(Machine):
    def __init__(self, state):
        
        states = ['occupied', 'renewed', 'notice_available', 'notice_leased', 'vacant_available_not_ready',
                  'vacant_available_ready', 'vacant_leased_ready', 'vacant_leased_not_ready']
        Machine.__init__(self, states=states, initial=state, auto_transitions=False)

        self.add_transition(trigger='renew', source='occupied', dest='renewed',
                            conditions='can_renew', after='occupied_to_renewed')

        self.add_transition(trigger='givenotice', source='occupied', dest='notice_available',
                            conditions='can_givenotice', after='occupied_to_notice_available')

        self.add_transition(trigger='notice_moveout', source='notice_available',
                            dest='vacant_available_not_ready', conditions='can_notice_moveout',
                            after='notice_available_to_vacant_available_not_ready')

        self.add_transition(trigger='makeready_VA', source='vacant_available_not_ready',
                            dest='vacant_available_ready', conditions='can_makeready_VA',
                            after='vacant_available_not_ready_to_ready')

        self.add_transition(trigger='movein', source='vacant_leased_ready',
                            dest='occupied', conditions='can_movein',
                            after='leased_ready_to_occupied')

        self.add_transition(trigger='renewal_lease_start', source='renewed',
                            dest='occupied', conditions='can_renewal_lease_start',
                            after='after_renewal_lease_start')

        self.add_transition(trigger='makeready_VL', source='vacant_leased_not_ready',
                            dest='vacant_leased_ready', conditions='can_makeready_VL',
                            after='vacant_leased_notready_to_ready')

        self.add_transition(trigger='lease_vacant_ready_unit', source='vacant_available_ready',
                            dest='vacant_leased_ready', conditions='can_lease_vacant_ready_unit',
                            after='after_lease_unit')

        self.add_transition(trigger='lease_vacant_not_ready_unit',
                            source='vacant_available_not_ready',
                            dest='vacant_leased_not_ready',
                            conditions='can_lease_vacant_not_ready_unit',
                            after='after_lease_unit')

        self.add_transition(trigger='lease_notice_unit',
                            source='notice_available',
                            dest='notice_leased',
                            conditions='can_lease_notice_unit',
                            after='after_lease_notice_unit')

        self.add_transition(trigger='vacate_notice_lease_unit',
                            source='notice_leased',
                            dest='vacant_leased_not_ready',
                            conditions='can_notice_lease_moveout',
                            after='notice_leased_to_vacant_leased_not_ready')
                    

### Conditions ################

    def can_notice_lease_moveout(self):
        return all([
            self.params['RenewalStatus'] == "NTV",
            self.params['SimulationDate'] == self.params['NoticeForDateCurrentLease'],
            self.params['UnitStatus'] == "Normal",
            self.params['LeaseStartDateFutureLease'] is not None,
            self.params['LeaseTypeFutureLease'] == "New Lease"
        ])

    def can_lease_notice_unit(self):
         return all([
            self.params['AvailableLeasePerWeek'] > 0,
            self.params['OccupancyStatus'] == "NA",
            self.params['UnitStatus'] == "Normal",
            self.params['SimulationDate'] <= (
                self.params['NoticeForDateCurrentLease'] + 10)
        ])

    def can_lease_vacant_not_ready_unit(self):
        return all([
            self.params['AvailableLeasePerWeek'] > 0,
            self.params['OccupancyStatus'] == "VA",
            self.params['UnitStatus'] == "Normal",
            self.params['MakeReadyDateFutureLease'] is None
        ])

    def can_lease_vacant_ready_unit(self):
        return all([
            self.params['AvailableLeasePerWeek'] > 0,
            self.params['OccupancyStatus'] == "VA",
            self.params['UnitStatus'] == "Normal",
            self.params['MakeReadyDateFutureLease'] is not None
        ])

    def can_renewal_lease_start(self):
         return all([
            self.params['RenewalStatus'] == "Renewed",
            self.params['OccupancyStatus'] == "OC",
            self.params['SimulationDate'] == self.params['LeaseStartDateFurureLease'],
            self.params['UnitStatus'] == "Normal"
        ])

    def can_makeready_VL(self):
        if doLog:
            logging.info(f"*****Can VL Unit be made ready***** = {self.params['UnitNumber']}")
            logging.info(f"UnitStatus = {self.params['UnitStatus']}")
            logging.info(f"OccupancyStatus = {self.params['OccupancyStatus']}")
            logging.info(f"SimulationDate = {self.params['SimulationDate']}")
            logging.info(f"_VacantNotReadyStartDate = {self.params['_VacantNotReadyStartDate']}")
            logging.info(f"MadeReadyDate = {self.params['_VacantNotReadyStartDate'] + self.params['MakeReadyDays']}")
        return all([
            self.params['OccupancyStatus'] == "VL",
            self.params['UnitStatus'] == "Normal",
            self.params['MakeReadyDateFutureLease'] is None
        ])

    def can_movein(self):
        if doLog:
            logging.info(f"*****Can MoveIn***** = {self.params['UnitNumber']}")
            logging.info(f"OccupancyStatus = {self.params['OccupancyStatus']}")
            logging.info(f"SimulationDate = {self.params['SimulationDate']}")
            logging.info(f"LeaseStartDateFutureLease = {self.params['LeaseStartDateFutureLease']}")
        return all([
            self.params['OccupancyStatus'] == 'VL',
            self.params['MakeReadyDateFutureLease'] is not None,
             self.params['SimulationDate'] == self.params['LeaseStartDateFutureLease']
        ])

    def can_renew(self):
        return all([
            self.params['_willRenew'],
            self.params['RenewalStatus'] == "Undecided",
            self.params['SimulationDate'] == (
                self.params['LeaseEndDateCurrentLease'] - self.params['AverageNoticeLeadDays']),
            self.params['UnitStatus'] == "Normal"
        ])

    def can_givenotice(self):
        return all([
            not self.params['_willRenew'],
            self.params['RenewalStatus'] == "Undecided",
            self.params['SimulationDate'] == (
                self.params['LeaseEndDateCurrentLease'] - self.params['AverageNoticeLeadDays']),
            self.params['UnitStatus'] == "Normal"
        ])

    def can_notice_moveout(self):
        return all([
            self.params['RenewalStatus'] == "NTV",
            self.params['SimulationDate'] == self.params['NoticeForDateCurrentLease'],
            self.params['UnitStatus'] == "Normal"
        ])

    def can_makeready_VA(self):
        if doLog:
            logging.info(f"*****Can VA Unit be made ready***** = {self.params['UnitNumber']}")
            logging.info(f"UnitStatus = {self.params['UnitStatus']}")
            logging.info(f"OccupancyStatus = {self.params['OccupancyStatus']}")
            logging.info(f"SimulationDate = {self.params['SimulationDate']}")
            logging.info(f"_VacantNotReadyStartDate = {self.params['_VacantNotReadyStartDate']}")
            logging.info(f"MadeReadyDate = {self.params['_VacantNotReadyStartDate'] + self.params['MakeReadyDays']}")
        return all([
            self.params['OccupancyStatus'] == "VA",
            self.params['UnitStatus'] == "Normal",
            self.params['SimulationDate'] == (
                self.params['_VacantNotReadyStartDate'] + self.params['MakeReadyDays'])
       ])


#### Effects ################
    def _common_lease(self):
        self.params['RenewalStatus'] = "Undecided"
        self.params['OccupancyStatus'] = "OC"
        self.params['MakeReadyDateFutureLease'] = None

        self.params['LeaseStartDateCurrentLease'] = self.params['LeaseStartDateFutureLease']
        self.params['LeaseEndDateCurrentLease'] = self.params['LeaseEndDateFutureLease']
        self.params['LeaseRentCurrentLease'] = self.params['LeaseRentFutureLease']
        self.params['NoticeOnDateCurrentLease'] = None
        self.params['NoticeForDateCurrentLease'] = None
        self.params['MTMFeesCurrentLease'] = None
        self.params['LengthOfStay'] = 0

        self.params['LeaseStartDateFutureLease'] = None
        self.params['LeaseEndDateFutureLease'] = None
        self.params['LeaseTypeFutureLease'] = None
        self.params['LeaseRentFutureLease'] = None

    def after_renewal_lease_start(self):
        if doLog:
            logging.info(f"*****Unit Renewal Lease Started***** = {self.params['UnitNumber']}")
            logging.info(f"RenewalStatus = {self.params['RenewalStatus']}")
            logging.info(f"OccupancyStatus = {self.params['OccupancyStatus']}")
            logging.info(f"SimulationDate = {self.params['SimulationDate']}")
            logging.info(f"UnitStatus = {self.params['UnitStatus']}")

        self.params['LeaseTypeCurrentLease'] = "Renewal"
        self._common_lease()

    def leased_ready_to_occupied(self):
        if doLog:
            logging.info(f"*****Unit Moved In***** = {self.params['UnitNumber']}")
            logging.info(f"OccupancyStatus = {self.params['OccupancyStatus']}")
            logging.info(f"MakeReadyDateFutureLease = {self.params['MakeReadyDateFutureLease']}")

        self.params['LeaseTypeCurrentLease'] = "New Lease"
        self._common_lease()

    def occupied_to_renewed(self):
        if doLog:
            logging.info(f"*****Unit Renewed***** = {self.params['UnitNumber']}")
            logging.info(f"_willRenew = {self.params['_willRenew']}")
            logging.info(f"RenewalStatus = {self.params['RenewalStatus']}")
            logging.info(f"SimulationDate = {self.params['SimulationDate']}")
            logging.info(f"LeaseEndDateCurrentLease = {self.params['LeaseEndDateCurrentLease']}")
            logging.info(f"UnitStatus = {self.params['UnitStatus']}")

        self.params['RenewalStatus'] = "Renewed"
        self.params['LeaseStartDateFutureLease'] = (
            self.params['LeaseEndDateCurrentLease'] + relativedelta(days=1))
        self.params['LeaseEndDateFutureLease'] = (
            self.params['LeaseStartDateFutureLease'] + relativedelta(months=12))
        self.params['LeaseTypeFutureLease'] = "Renewal"
        self.params['LeaseRentFutureLease'] = (
            min(self.params['LeaseRentCurrentLease'] * 1.05,
                self.params['TotalMarketRent'] *
                (1 + (self.params['SimulationDate'] - self.params['SimulationStartDate']).days * 0.03 / 365))
            )

    def occupied_to_notice_available(self):
        if doLog:
            logging.info(f"*****Unit Gave Notice***** = {self.params['UnitNumber']}")
            logging.info(f"_willRenew = {self.params['_willRenew']}")
            logging.info(f"RenewalStatus = {self.params['RenewalStatus']}")
            logging.info(f"SimulationDate = {self.params['SimulationDate']}")
            logging.info(f"LeaseEndDateCurrentLease = {self.params['LeaseEndDateCurrentLease']}")
            logging.info(f"UnitStatus = {self.params['UnitStatus']}")

        self.params['RenewalStatus'] = "NTV"
        self.params['OccupancyStatus'] = "NA"
        self.params['NoticeOnDateCurrentLease'] = self.params['SimulationDate']
        self.params['NoticeForDateCurrentLease'] = self.params['LeaseEndDateCurrentLease']

        self.params['LeaseStartDateFutureLease'] = None
        self.params['LeaseEndDateFutureLease'] = None
        self.params['LeaseTypeFutureLease'] = None

    def notice_available_to_vacant_available_not_ready(self):
        if doLog:
            logging.info(f"*****Notice Unit Moved Out***** = {self.params['UnitNumber']}")
            logging.info(f"RenewalStatus = {self.params['RenewalStatus']}")
            logging.info(f"SimulationDate = {self.params['SimulationDate']}")
            logging.info(f"NoticeForDateCurrentLease = {self.params['NoticeForDateCurrentLease']}")
            logging.info(f"UnitStatus = {self.params['UnitStatus']}")


        self.params['_VacantNotReadyStartDate'] = self.params['SimulationDate']
        self.params['RenewalStatus'] = None
        self.params['OccupancyStatus'] = "VA"
        self.params['MakeReadyDateFutureLease'] = None

        self.params['LeaseStartDateCurrentLease'] = None
        self.params['LeaseEndtDateCurrentLease'] = None
        self.params['LeaseRentCurrentLease'] = None
        self.params['LeaseTermCurrentLease'] = None
        self.params['LeaseTypeCurrentLease'] = None
        self.params['LeaseTermCurrentLease'] = None
        self.params['NoticeOnDateCurrentLease'] = None
        self.params['NoticeForDateCurrentLease'] = None
        self.params['MTMFeesCurrentLease'] = None
        self.params['LengthOfStay'] = None

    def notice_leased_to_vacant_leased_not_ready(self):
        if doLog:
            logging.info(f"*****Notice Unit Moved Out***** = {self.params['UnitNumber']}")
            logging.info(f"RenewalStatus = {self.params['RenewalStatus']}")
            logging.info(f"SimulationDate = {self.params['SimulationDate']}")
            logging.info(f"NoticeForDateCurrentLease = {self.params['NoticeForDateCurrentLease']}")
            logging.info(f"UnitStatus = {self.params['UnitStatus']}")


        self.params['_VacantNotReadyStartDate'] = self.params['SimulationDate']
        self.params['RenewalStatus'] = None
        self.params['OccupancyStatus'] = "VL"
        self.params['MakeReadyDateFutureLease'] = None

        self.params['LeaseStartDateCurrentLease'] = None
        self.params['LeaseEndtDateCurrentLease'] = None
        self.params['LeaseRentCurrentLease'] = None
        self.params['LeaseTermCurrentLease'] = None
        self.params['LeaseTypeCurrentLease'] = None
        self.params['LeaseTermCurrentLease'] = None
        self.params['NoticeOnDateCurrentLease'] = None
        self.params['NoticeForDateCurrentLease'] = None
        self.params['MTMFeesCurrentLease'] = None
        self.params['LengthOfStay'] = None

    def vacant_available_not_ready_to_ready(self):
        if doLog:
            logging.info(f"*****VA Unit Made Ready***** = {self.params['UnitNumber']}")
            logging.info(f"OccupancyStatus = {self.params['OccupancyStatus']}")
            logging.info(f"SimulationDate = {self.params['SimulationDate']}")
            logging.info(f"_VacantNotReadyStartDate = {self.params['_VacantNotReadyStartDate']}")
            logging.info(f"MakeReadyDays = {self.params['MakeReadyDays']}")
            logging.info(f"UnitStatus = {self.params['UnitStatus']}")

        self.params['RenewalStatus'] = None
        self.params['OccupancyStatus'] = "VA"
        self.params['MakeReadyDateFutureLease'] = self.params['SimulationDate']

    def vacant_leased_notready_to_ready(self):
        #if doLog:
        logging.info(f"*****VL Unit Made Ready***** = {self.params['UnitNumber']}")
        logging.info(f"OccupancyStatus = {self.params['OccupancyStatus']}")
        logging.info(f"UnitStatus = {self.params['UnitStatus']}")
        logging.info(f"MakeReadyDateFutureLease = {self.params['MakeReadyDateFutureLease']}")
        logging.info(f"SimulationDate = {self.params['SimulationDate']}")

        self.params['MakeReadyDateFutureLease'] = self.params['SimulationDate']

    def after_lease_notice_unit(self):
        if doLog:
            logging.info(f"*****Leased Notice***** = {self.params['UnitNumber']}")
            logging.info(f"AvailableLeasePerWeek = {self.params['AvailableLeasePerWeek']}")
            logging.info(f"OccupancyStatus = {self.params['OccupancyStatus']}")
            logging.info(f"UnitStatus = {self.params['UnitStatus']}")

        self.params['OccupancyStatus'] = "NL"
        self._common_after_lease()

    def after_lease_unit(self):
        logging.info(f"*****Leased Vacant Unit - check make ready date ***** = {self.params['UnitNumber']}")
        logging.info(f"AvailableLeasePerWeek = {self.params['AvailableLeasePerWeek']}")
        logging.info(f"MakeReadyDateFutureLease = {self.params['MakeReadyDateFutureLease']}")

        self.params['OccupancyStatus'] = "VL"
        self._common_after_lease()

    def _common_after_lease(self):
        self.params['AvailableLeasePerWeek'] -= 1
        self.params['RenewalStatus'] = None

        self.params['LeaseStartDateFutureLease'] = (
            self.params['SimulationDate'] + self.params['ApplicationToMoveInLeadDays'])

        self.params['LeaseEndDateFutureLease'] = (
            self.params['LeaseStartDateFutureLease'] + relativedelta(months=12))
        self.params['LeaseTypeFutureLease'] = "New Lease"
        self.params['LeaseRentFutureLease'] = (
            min(self.params['LeaseRentCurrentLease'] * 1.05,
                self.params['TotalMarketRent'] *
                (1 +
                    (self.params['SimulationDate'] - self.params['SimulationStartDate']).days
                    * self.params['MarketRentGrowth'] / 365.0))
            )
