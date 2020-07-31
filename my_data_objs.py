#
# Parameters for covid19 simulation
#
class sim_params:
    def __init__(self, label='NO LABEL', population=320e6, num_sim_days=150, frac_non_infectious=0, R0=2.3, 
            incubation_days=5, contagious_days=10, 
            initial_herd_immune_frac=0, initial_infected=35530, serious_illness_frac=.19,
            fatalities_of_infections=.01,
            clamp_down_new_cases=99999900999, clamp_down_R0=99):
      self.label = label
      self.population = population
      self.num_sim_days = num_sim_days
      self.frac_non_infectious = frac_non_infectious
      self.R0 = R0
      self.incubation_days = incubation_days
      self.contagious_days = contagious_days
      self.initial_herd_immune_frac = initial_herd_immune_frac
      self.initial_infected = initial_infected
      self.serious_illness_frac = serious_illness_frac
      self.fatalities_of_infections=fatalities_of_infections;
      self.clamp_down_new_cases = clamp_down_new_cases
      self.clamp_down_R0 = clamp_down_R0
      print 'Clamp down R0:',clamp_down_R0

class sim_results:
    def __init__(self, parms):
        self.parms = parms
        self.UNINFECTEDBYDAY = []    #current number uninfected
        self.CASESBYDAY = []         #current number infected not ended
        self.INFECTIOUSBYDAY = []    #current number infectious
        self.ENDEDBYDAY = []         #current number ended
        self.BYSTAGEDAY = []         #Number in each stage
        self.NEWINFSPERDAY = []      #New Infections per day
        self.FATALSPERDAY = []       #Fatalities per day
        self.ENDEDPERDAY = []        #Recovered per day
        self.MAX_SYMPTOMATIC = 0     #Maximum number symptomatic
        self.WORST_DAY = 0           #Day index of worst day
        self.MAX_INFECTED = 0        #Max number infected at once
        self.R0BYDAY = []            #R naught by day
        self.TOTAL_FATALITIES = 0    #Total fatalities
        self.TOTAL_INFECTED = 0      #Total infected
        self.INFECTED_AT_HERD_IMMUNITY = 0      #Total infected

