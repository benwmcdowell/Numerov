#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Numerov Schrodinger equation solver

Description: This script solves the 1 dimensional time-independant Schrodinger equation for any given potential. Its takes a potentiel as an entry and outputs the wanted energy level and
             a figure with the potentiel and the wave fonctions corresponding to the energy level that have been specicied.

Indications: The script ask for the number of energy levels that are desired and the potential. The potential must be centered at x=0 (the programm will itself translate the potential in y so
             that all the values are positive). Also if the potential behaves weirdly or the desired number of energy level is big, you may encounter some problem with the MeetingPoints function.
             Usually changing the x_V_min and x_V_max fixes the problem.

author: Félix Desrochers
email: felix.desrochers@polymtl.ca

MIT License

Copyright (c) 2017 Félix Desrochers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

###################
# Importing modules
###################

import numpy as np

#Imports the Fct_Numerov module which defines many functions that will be used in this script
import Fct_Numerov

#d is the tip-sample distance in nm
#V is the voltage bias in eV
#Vmin is the minimum potential of the substrate periodic potential in eV
#zm is the range of the potential set to a constant value near the sumple interface (nm)
def build_FER_potential_no_dielectric(n,zmin,w,Vg,V0,d,phi,V,zm):
    d*=1e-9 #convert nm to m
    zm*=1e-9 #convert nm to m
    zmin*=1e-9 #convert nm to m
    w*=1e-9 #convert nm to m
    Vg*=1.60218e-19 #eV to J
    V*=1.60218e-19 #eV to J
    V0*=1.60218e-19 #eV to J
    phi*=1.60218e-19 #eV to J
    e0=8.8541878128e-12 #F/m
    e=1.60217663e-19
    
    x=np.linspace(-zmin,d,n)
    field_pot=phi-V*(d-x)/d
    image_pot_sub=-e**2/4/x/e0/np.pi
    image_pot_tip=-e**2/4/abs(d-x)/e0/np.pi
    pot=field_pot+image_pot_sub+image_pot_tip
    pot=np.nan_to_num(pot)
    
    pot*=np.heaviside(x-zm,1)
    Vmin=image_pot_sub[np.argmin(abs(x-zm))]
    pot+=np.heaviside((x-zm)*-1,0)*(-V0-Vg)
    for i in range(len(x)):
        if pot[i]<(V0-Vg):
            max_index=i
            break
    
    pot*=np.heaviside(x,1)
    bulk_pot=-Vg*np.cos(2*np.pi*x/w)-V0
    pot[:np.argmin(abs(x))+1]+=bulk_pot[:np.argmin(abs(x))+1]
    
    for i in range(len(x)):
        if pot[i]<(-V0-Vg):
            pot[i]=(-V0-Vg)
    
    #convert x back to nm
    x*=1e9
    return x,pot

def Numerov(n,x,potential,quiet=True,rescale=True):
    ############################
    # 1) Initializing parameters
    ############################
    
    #Indication :Theses parameters determine the precision of the calculations and can be adjust as wanted
    
    #Setting the range from wich we will evaluate the potential and the number of division we will use to discretise the potential
    #x_V_min = -13
    #x_V_max = 13
    x_V_min=np.min(x)
    x_V_max=np.max(x)
    #nbr_division_V = 800000
    nbr_division_V=len(x)
    
    #Setting the number of division from the initial point in the classical forbidden zone x_0 to the ending point x_max
    nbr_division = 5000
    
    #Setting the initial augmentation after the point where the wave function will be set to zero
    Initial_augmentation = 0.00001
    
    #Setting the tolerance for the wave fonction at the ending point (x_max) to accept the energy level as the wnated energy level
    Tolerance = 0.00000001
    
    
    ###########################################################################
    # 2) Entering the parameters concerning the energy levels and the potential
    ###########################################################################
    
    # i) Energy levels
    #E_level = int(input('Which first energy levels do you want (enter an integer) : '))
    E_level=n
    E_lvl = list(range(0,E_level))
    
    # ii) Potential
    #potential=input('Potential (as a fonction of x): ')
    
    #Verify if the potential expression is correct (Syntax, bounadries value and "global concavity")
    #Changes the expression to be sure it matches python mathematical syntax
    #potential = Fct_Numerov.ModifyPotential(potential)

    #Verify if the potential expression has any syntax error
    #potential = Fct_Numerov.VerifySyntaxPotential(potential)

    #Verify if the potential seems to respect the boundaries conditions
    #potential = Fct_Numerov.VerifyLimitsPotential(potential)

    #Convert the potential into a numpy array (see the settings for this potential array in the "Initializing parameters section")
    #EvaluatePotential = np.vectorize(Fct_Numerov.EvaluateOnePotential)
    DivisionPotential = (x_V_max - x_V_min) / nbr_division_V
    PositionPotential = x
    #converts nm input to bohr radii
    if rescale:
        PositionPotential*=18.8973
    potential-=np.min(potential)
    #converts joule potential to hartree
    if rescale:
        potential*=2.294e17
    PotentialArray = potential

    #Translate the potential
    #PositionPotential,PotentialArray = Fct_Numerov.TranslationPotential(PositionPotential, PotentialArray)

    #Recenters this new potential array for more accuracy
    #PotentialArray,PositionPotential = Fct_Numerov.RecenterPotential(PotentialArray,PositionPotential)

    #Defines the initial Energy guess that will be used to verify the concavity
    #First_E_guess = Fct_Numerov.GetFirstEnergyGuess(PotentialArray)

    #Verify the concavity of the potential
    #concavity,First_E_guess = Fct_Numerov.VerifyConcavity(PotentialArray, First_E_guess)

    #If it is correct exit the loop
    #if concavity == 'positive':
    #    i = 0
    #Else ask for a new one or take this one anyway
    #elif concavity == 'negative':
    #    potential2 = input('The concavity of the potential isn\'t correct enter a new one (or "O" to overule): ')
    #    if potential2 == 'O':
    #        i = 0
    #    else :
    #        potential = potential2
    First_E_guess=(np.max(potential)-np.min(potential))/2
    
    ###################################6
    # 3) Numerov algorithm
    ###################################
    
    #Initializing paramaters for the while loop
    EnergyLevelFound = {} #Defines energy levels that avec been found. Has the structure {0:E0, 1:E1, 2:E2, ...}
    WaveFunctionFound = {} #Defines the wave functions that have been found. Has the structure {0:WaveFunction0, 1:WaveFunction1, ...}
    E_guess_try = {} #Defines the lowest and higest energy levels that have been used so far for each number of nodes. Has the structure {NbrNodes1:[Energy guessed min, Energy guessed max], ...}
    iteration = 1 #Defines the number of iterations
    E_found = list() #A list of the energy levels that have been found (ex: [0,2,3] if the energy levels 0,2 and 3 have been found)
    # Note: All the wave function are a list of tuple and have the following structure: [(x0, \psi(x0), (x1, \psi(x1)), ...]
    
    #Continue while we don't have the n first energy level
    while not E_found == list(range(E_level)):
    
        #########################################################
        # i) Initial Energy guess
    
        E_guess = Fct_Numerov.E_Guess(EnergyLevelFound,E_guess_try,iteration, First_E_guess)
        if not quiet:
            print('E_guess: ', E_guess)
    
        ##########################################################
        # ii) Setting the initial and final points (where \psi=0)
    
        #Gets the meeting points with the energy and the potential
        MeetingPoints,end_program,E_guess = Fct_Numerov.MeetingPointsPotential(E_guess, PotentialArray, PositionPotential, E_guess_try)
    
        if end_program:
            break
    
        #Sets the minimum and maximum value for the position where the wave function equals zero
        Position_min,Position_max = Fct_Numerov.DetermineMinAndMax(MeetingPoints)
    
        ###############################################################
        # iii) Calculate the wave fonction for the guessed energy value
    
        WaveFunction = Fct_Numerov.WaveFunctionNumerov(potential, E_guess, nbr_division, Initial_augmentation, Position_min, Position_max, PositionPotential)
    
        ###############################################################################
        # iv) Determine the number of nodes in the wave fonction and set the tolerance
    
        NumberOfNodes,PositionNodes,x_max = Fct_Numerov.NumberNodes(WaveFunction)
        if not quiet:
            print('NumberOfNodes:', NumberOfNodes)
    
        ####################################################################################
        # v) See if the wave fonction for this energy respects the restriction (if yes save)
    
        VerificationTolerance = Fct_Numerov.VerifyTolerance(WaveFunction,Tolerance,E_guess,E_guess_try,NumberOfNodes)
    
        if VerificationTolerance == 'yes':
            print('Energy level found')
            NumberOfNodesCorrected = Fct_Numerov.CorrectNodeNumber(NumberOfNodes,PositionNodes,x_max,E_guess,E_guess_try)
            EnergyLevelFound.update({NumberOfNodesCorrected:E_guess})
            WaveFunctionFound.update({NumberOfNodesCorrected:WaveFunction})
    
        ######################################################################################
        # vi) Saves Energy guess and the corresponding number of nodes (no matter if it fails)
    
        E_guess_try = Fct_Numerov.SaveEnergy(NumberOfNodes, E_guess, E_guess_try)
        if not quiet:
            print('E_guess_try: ',E_guess_try)
    
        #Increments the iteration
        if not quiet:
            print('iterations:',iteration,'\n')
        iteration += 1
    
        ###################################################################################
        # vii) Updates the Energy levels found list to verify if the condition is respected
        E_found = list()
        for i in EnergyLevelFound.keys():
            E_found.append(i)
        E_found.sort()
        if not quiet:
            print('Energy level found',EnergyLevelFound)
    
    
    ######################################
    # 4) Output (energy levels and figure)
    ######################################
    
    #rescale energy values from hartree to eV
    for i in EnergyLevelFound.keys():
        EnergyLevelFound[i]*=27.2114
        
    #converts bohr radii to nm
    PositionPotential/=18.8973
    for i in WaveFunctionFound.keys():
        tempvar=np.array(WaveFunctionFound[i])
        tempvar[:,0]/=18.8973
        WaveFunctionFound[i]=tuple(tempvar)
        
    #converts potential from hartree to eV
    potential*=27.2114
    PotentialArray*=27.2114
        
    # i) Energy levels
    Fct_Numerov.OuputEnergy(EnergyLevelFound)
    
    # ii) Figure
    #Get all the information about what to draw
    y_max,min_x,max_x,WavPlot,WavLines,EnergyLines = Fct_Numerov.DefineWhatToPlot(WaveFunctionFound,EnergyLevelFound)
    
    #Draw all the wave functions
    Fct_Numerov.DrawWaveFunction(y_max, min_x, max_x, WavPlot, WavLines, EnergyLines, PositionPotential, PotentialArray)
    
    return PositionPotential, PotentialArray, WavPlot, EnergyLevelFound