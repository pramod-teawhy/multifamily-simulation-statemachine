from random import choices
from mesa import Agent
from sm_loader import StateMachineLoader
import logging

class UnitAgent(Agent):
    def __init__(self, unique_id, model, config, simulation_params):
        super().__init__(unique_id, model)
        self.sm = StateMachineLoader(config, simulation_params)

    def step(self):
        self.sm.params['SimulationDate'] = self.model.SimulationDate
        self.sm.params['AvailableLeasePerWeek'] = self.model.AvailableLeasePerWeek
        self.sm.params['_willRenew'] = choices(population=[True, False],
                                               weights=[self.sm.params['RenewalProbability'],
                                                        1-self.sm.params['RenewalProbability']])[0]

        for trigger in self.sm.get_triggers(self.sm.state):
            try:
                #logging.info(f"Date: {self.model.SimulationDate} ** Agent:{self.unique_id} Unit: {self.sm.params['UnitNumber']} taking a step, Current State: {self.sm.state}, trigger: {trigger}")
                if eval('self.sm.{}()'.format(trigger)):
                    continue
            except:
                #print('Illegal Transition')
                continue

        self.model.AvailableLeasePerWeek = self.sm.params['AvailableLeasePerWeek']
        return
