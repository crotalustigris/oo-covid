# # This is the SEIR compartmented model simulator module # # To run this, modify the parameters (some passed to calculate when it is called - near the end of the source) # # For each step(day), it starts with the number of people in each stage of the simulation # It then calculates the state for the next day, and advances to that state # # Stages are: #   Susceptible (never infected, vaccinated, no natural immunity #   Infected, not yet infectious [lasts multiple days] #   Infected, infectious [lasts multiple days] #   Ended - no longer infectious
#
# Basic parameters are either initiated directly in the calculate function, or passed, or declared up front
#   
# The epidemic specific parameters are:
#    R0 - the basic reproduction number - how many people are infected by an infectious person
#    L  - latency (incubation period) - days after infection before person is infectious
#    CT - contagious - days that a person is contagioous
#    SF - the fraction of infected who become seriously ill - requiring hospitalization
#
# For a given step

import my_data_objs


# simdays - number of days to simulate
# fraction_non_infections - those infected and immune but never infectious
# R0 - basic reproduction number. On any generation, new infections = R0*susceptible_population
def calculate(parms):
    print
    print '  ======================================================== '
    results = my_data_objs.sim_results(parms)
    I0 = parms.initial_infected #Initial number infected
    results.MAX_INFECTED = I0
    R0 = parms.R0               #Reproduction number - #infected by each case that become infectious
    INC = parms.incubation_days #Mean Latency (time from infection until spreader0 in days
    CT = parms.contagious_days  #days contagious
    SF = parms.serious_illness_frac  #SF = serious illness fraction
    doubleBase = I0
    doubleDay = 0
    #Counters
    INF, E = 0, 0     #I = Infectious, E = Ended - not infectious or susceptible
    UNINF = parms.population*(1-parms.initial_herd_immune_frac)     #UNINF - Uninfected
    print "UNINF", UNINF
    CUMINF = I0              #CUMINF - cumulate number infected
    results.MAX_SYMPTOMATIC = I0            #MAXSYMP - max number of days symptomatic
    # Counts by day of infection - for staging  (INC latency days, then CT contagious days)
    #   (not the same as counts by simulation day)
    initperday = I0/(INC+CT)
    #print 'initperday:%d I0:%d INC+CT:%d'%(initperday, I0, INC+CT)
    for i in range(0, INC + CT):
        results.BYSTAGEDAY.append(initperday)
        INF = INF + initperday
    print 'Incubation:%d Contagious:%d Initial Inf:%d of %-10d'%(INC, CT, I0, parms.population)
    print 'results.BYSTAGEDAY:',results.BYSTAGEDAY

    #Calculate - one day at a time, over full days range
    R0prev = R0 #===jrm
    for d in range(0, parms.num_sim_days):
        # Reduce R0 based on how many are still available to infect
        results.R0BYDAY.append(R0)
        R0adj = R0 * UNINF/parms.population
        R0NSadj = R0adj * parms.frac_non_infectious
        if R0 <> R0prev: #===jrm
            print 'R0: %.2f <<=== %.2f'%(R0prev, R0)
            R0prev = R0

        #Print a debugging line
        Dstr = '%3d:'%d       
        for i in range(0, INC):
            Dstr = '%s %8.1f'%(Dstr, results.BYSTAGEDAY[i])
        Dstr = Dstr+' | '
        for i in range(INC, INC+CT):
            Dstr = '%s %8.1f'%(Dstr, results.BYSTAGEDAY[i])
        #print '%s CUMIN:%.1f R0:%.2f R0adj:%.2f'%(Dstr, CUMINF, R0, R0adj) 

        NEW = list(results.BYSTAGEDAY)        #Create a staging list from the current

        # Calculate number of new infections, and number currently infectious
        if R0adj <= 1.0 and results.INFECTED_AT_HERD_IMMUNITY == 0:
            results.INFECTED_AT_HERD_IMMUNITY = results.TOTAL_INFECTED
        newInf, newNS, infectious = 0, 0, 0
        for i in range(INC, INC+CT):    #Make new infections
            newInf = newInf + results.BYSTAGEDAY[i]*R0adj/CT
            newNS = newNS + results.BYSTAGEDAY[i]*R0NSadj/CT
            infectious = infectious + results.BYSTAGEDAY[i]
        # Update master counters 
        ending = results.BYSTAGEDAY[INC+CT-1]
        newFatals = newInf*parms.fatalities_of_infections
        results.TOTAL_FATALITIES = results.TOTAL_FATALITIES + newFatals
        #print 'newInf:%12d newFatals:%12.0f totFat:%12.0f'%(newInf, newFatals, results.TOTAL_FATALITIES)
        UNINF = UNINF - newInf - newNS              # Subtract new infections from uninfected 
        INF = INF + newInf - ending         # Calc num infectious by adding new, subtracting ended
        E = E + ending + newNS              # Calc number ended (no longer infectious)
        results.NEWINFSPERDAY.append(newInf)
        results.TOTAL_INFECTED = results.TOTAL_INFECTED + newInf
        results.FATALSPERDAY.append(newFatals)
        results.ENDEDPERDAY.append(ending)
        if results.MAX_SYMPTOMATIC < infectious:            #Max symptomatic (same as infectious)
            results.MAX_SYMPTOMATIC = infectious
            results.WORST_DAY = d + 1
        CUMINF = CUMINF + newInf            # Update cumulative infected count
        #print 'Day:%4d cumulative:%6d  infected:%6d'%(d, CUMINF, INF)
        #print '%4d: newInf:%7d newNS:%7d Uninf:%12d'%(d, newInf, newNS, UNINF)

        # Now update the new staging list by
        #  using new infection rate for day 0, and shifting other days forward in list
        NEW[0] = newInf
        for i in range(0, INC+CT):
            if i > 0:
                NEW[i] = results.BYSTAGEDAY[i-1]
        #if d%7 == 0 and d > 0:
        #    print 'end of wk:%3d cases/1000:%12d'%(d/7+1, CASESBYDAY[d-1])
        if INF > results.MAX_INFECTED:
            results.MAX_INFECTED = INF
        #print '%4d  R0adj:%.2f'%(d, R0adj)
        if newInf >= parms.clamp_down_new_cases:
            R0 = parms.clamp_down_R0
            print 'Clamping down'
        if INF >= 2*doubleBase:
            #print '%4d DOUBLING was %10d is %10d days:%3d max_inf:%10d R0:%4.2f'%(d,doubleBase, INF, d - doubleDay, results.MAX_INFECTED, R0)
            doubleBase = INF
            doubleDay = d

        results.BYSTAGEDAY = NEW

        #Update the by-day lists - for plotting
        results.CASESBYDAY.append(INF)
        #print 'day:%3d newInf:%d newNS:%d ending:%d infectious:%12d'%(d, newInf, newNS, ending, INF)
        results.UNINFECTEDBYDAY.append(UNINF)
        results.ENDEDBYDAY.append(E)
        results.INFECTIOUSBYDAY.append(infectious)
        #print 'INF=%10d TOT=%10d'%(INF, CUMINF)

    return results
