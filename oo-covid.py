import my_base_model as mod
import my_data_objs as data
import locale
locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
import numpy as np
import matplotlib.pyplot as plt
#
# This is a pretty simple epidemic simulator. Results are output to the command line, and graphed.
# A graph is generated for each situation (parameter set). It is currently set for two situations, but is easily upgraded.
#    if you want to add graphs, you need to know how pylot handles multiple graphs.
#
# To run this, modify the parameters (some passed to calculate when it is called - near the end of the source)
#
# For each step(day), it starts with the number of people in each stage of the simulation
# It then calculates the state for the next day, and advances to that state
#
# Stages are:
#   Susceptible (never infected, vaccinated, no natural immunity
#   Infected, not yet infectious [lasts multiple days]
#   Infected, infectious [lasts multiple days]
#   Ended - no longer infectious
#
# Basic parameters are either initiated directly in the calculate function, or passed, or declared up front
#   
# The epidemic specific parameters are:
#    R0 - the basic reproduction number - how many people are infected by an infectious person
#    L  - latency (incubation period) - days after infection before person is infectious
#    CT - contagious - days that a person is contagioous
#    SF - the fraction of infected who become seriously ill - requiring hospitalization
#

#  MAIN LINE OF PROGRAM
def main():
    print
    print
    print "----------- START ----------"
    POP=320e6
    #POP=7e6
    SIMDAYS=150 #Number of days
    fig = plt.figure(figsize=(9,9),facecolor='w')
    #parms = data.sim_params(label='US R0=2.5', population=POP, num_sim_days=SIMDAYS, frac_non_infectious=0., R0=2.50,
    #        incubation_days=5, contagious_days=5, initial_herd_immune_frac=0,
    #        initial_infected=5000, serious_illness_frac=.18, fatalities_of_infections=.01)
    parms = data.sim_params(label='AZ R0=2.25', population=7e6, num_sim_days=SIMDAYS, frac_non_infectious=0., R0=2.25,
            incubation_days=5, contagious_days=2, initial_herd_immune_frac=0,
            initial_infected=1e4, serious_illness_frac=.18)
    results = mod.calculate(parms)            #Do it for zero non-infectious (percentage)
    do_tots_subplot(fig, 221, results)
    do_deltas_subplot(fig, 223, results)

    #parms = data.sim_params(population=POP, num_sim_days=365, frac_non_infectious=0., R0=3.0,
    #        incubation_days=5, contagious_days=5, serious_frac=.18, initial_herd_immune_frac=0,
    #        initial_infected=1000, serious_illness_frac=.19,
    #        clamp_down_new_cases=10000, clamp_down_R0=0.75)
    parms = data.sim_params(label='AZ R0=2.25', population=7e6, num_sim_days=SIMDAYS, frac_non_infectious=0., R0=2.25,
            incubation_days=5, contagious_days=2, initial_herd_immune_frac=0,
            initial_infected=100, serious_illness_frac=.18)
    results = mod.calculate(parms)            #Do it for zero non-infectious (percentage)
    do_tots_subplot(fig, 222, results)
    do_deltas_subplot(fig, 224, results)
    #calculate(ND, .49, 1.1, 5, 10)          #Do it for non-zero non-infections (percentage)
    #do_tots_subplot(fig, 122, "R0 1.1", PLOTSCALE)
    plt.show()

#
# Plotting Section - import standard libraries

# Function to create one subplot of totals - called with:
# fig - the figure to plot inside of
# subplotIII - the subplot location information
def do_tots_subplot(fig, subplotIII, results):
    parms = results.parms
    scale = 1e9
    svals = [ 1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9 ]
    sstrs = [ '10', '100', '1,000', '10,000', '100,000', '1,000,000', '10,000,000', '100,000,000', '1,000,000,000' ]
    for foo in range (0, 9):
        scale = svals[foo]
        scale_str = sstrs[foo]
        if scale > results.MAX_INFECTED/150:
            print results.MAX_INFECTED,'scale:',scale
            break
    # Plot the data on three separate curves for S(t), I(t) and R(t)
    # A grid of time points (in days) - first scale the arrays
    UNINF = [ x/scale for x in results.UNINFECTEDBYDAY ]
    INF = [ x/scale for x in results.CASESBYDAY ]
    ENDED = [ x/scale for x in results.ENDEDBYDAY ]
    INFECTIOUS = [ x/scale for x in results.INFECTIOUSBYDAY ]

    t = np.linspace(0, parms.num_sim_days, parms.num_sim_days)
    ax = fig.add_subplot(subplotIII, axis_bgcolor='#dddddd', axisbelow=True)
    #ax.plot(t, UNINF, 'b', alpha=0.5, lw=2, label='Susceptible')
    ax.plot(t, UNINF, 'y', alpha=0.5, lw=2, label='Susceptible')
    ax.plot(t, INF, 'r', alpha=0.5, lw=2, label='Infected')
    ax.plot(t, INFECTIOUS, 'b', alpha=0.5, lw=2, label='Infectious')
    ax.plot(t, ENDED, 'g', alpha=0.5, lw=2, label='Post-Infection')
    ax.set_xlabel(parms.label + ' - Days')
    ax.set_ylabel('Cases in %s\'s'%scale_str)
    ax.set_ylim(0,100)
    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)
    ax.grid(b=True, which='major', c='w', lw=2, ls='-')
    legend = ax.legend()
    legend.get_frame().set_alpha(0.5)
    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)
    # place a text box in upper left in axes coords
    # ...these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    MSYMPf = locale.format("%d", results.MAX_SYMPTOMATIC, grouping=True)
    MSERf = locale.format("%d", results.MAX_SYMPTOMATIC*parms.serious_illness_frac, grouping=True)
    MSFATf = locale.format("%d", results.TOTAL_FATALITIES, grouping=True)
    label = ' WORST DAY %d\r\nInfectious:%s\nSeriously Ill:%s\nTotal Fatalities:%s\n%% after herd immunity %.1f'%(
        results.WORST_DAY, MSYMPf, MSERf, MSFATf,
        100.*(results.TOTAL_INFECTED - results.INFECTED_AT_HERD_IMMUNITY)/results.TOTAL_INFECTED)
    ax.text(0.05, 0.7, label, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=props)
    print 'Total infections:%d  Total at herd immunity:%d  %% after herd immunity:%.1f'%(results.TOTAL_INFECTED,results.INFECTED_AT_HERD_IMMUNITY, 100.*(results.TOTAL_INFECTED - results.INFECTED_AT_HERD_IMMUNITY)/results.TOTAL_INFECTED)


# Function to create one subplot of deltas - called with:
# fig - the figure to plot inside of
# subplotIII - the subplot location information
def do_deltas_subplot(fig, subplotIII, results):
    parms = results.parms
    scale = 1e9
    svals = [ 1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9 ]
    sstrs = [ '10', '100', '1,000', '10,000', '100,000', '1,000,000', '10,000,000', '100,000,000', '1,000,000,000' ]
    _max = 0
    for day in range(0, parms.num_sim_days):
        if results.NEWINFSPERDAY[day] > _max:
            _max = results.NEWINFSPERDAY[day]
        if results.FATALSPERDAY[day] > _max:
            _max = results.FATALSPERDAY[day] 
        if results.ENDEDPERDAY[day] > _max:
            _max = results.ENDEDPERDAY[day] 
    for foo in range (0, 9):
        scale = svals[foo]
        scale_str = sstrs[foo]
        if scale > _max/500:
            print '_max:',_max,'scale:',scale
            break
    # Plot the data on three separate curves for S(t), I(t) and R(t)
    # A grid of time points (in days) - first scale the arrays
    NEWINFSPERDAY = [ x/scale for x in results.NEWINFSPERDAY ]
    FATALSPERDAY = [ x/scale for x in results.FATALSPERDAY ]
    ENDEDPERDAY = [ x/scale for x in results.ENDEDPERDAY ]

    t = np.linspace(0, parms.num_sim_days, parms.num_sim_days)
    ax = fig.add_subplot(subplotIII, axis_bgcolor='#dddddd', axisbelow=True)
    #ax.plot(t, UNINF, 'b', alpha=0.5, lw=2, label='Susceptible')
    ax.plot(t, NEWINFSPERDAY, 'y', alpha=0.5, lw=2, label='New Infs')
    ax.plot(t, FATALSPERDAY, 'r', alpha=0.5, lw=2, label='New Deaths')
    ax.plot(t, ENDEDPERDAY, 'g', alpha=0.5, lw=2, label='New Ended')
    ax.set_xlabel(parms.label + ' - Days')
    ax.set_ylabel('Cases in %s\'s'%scale_str)
    ax.set_ylim(0,100)
    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)
    ax.grid(b=True, which='major', c='w', lw=2, ls='-')
    legend = ax.legend()
    legend.get_frame().set_alpha(0.5)
    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)

if __name__ == "__main__":
    main()
#  MAIN LINE OF PROGRAM
#===jrmND=150 #Number of days
#===jrmPLOTSCALE=1e6
#===jrmfig = plt.figure(facecolor='w')
#===jrmcalculate(ND, 0, 2.3, 5, 10, 0)            #Do it for zero non-infectious (percentage)
#===jrmdo_tots_subplot(fig, 121, "R0 2.3", PLOTSCALE)
#===jrmcalculate(ND, 0, 2.3, 5, 10, .1)            #Do it for zero non-infectious (percentage)
#===jrmdo_tots_subplot(fig, 122, "R0 2.3 Im:.1", PLOTSCALE)
#===jrm#calculate(ND, .49, 1.1, 5, 10)          #Do it for non-zero non-infections (percentage)
#===jrm#do_tots_subplot(fig, 122, "R0 1.1", PLOTSCALE)
#===jrm
#===jrmplt.show()
