/*==============================================================================
DO FILE NAME:			01_cr_create_asthma_population
PROJECT:				ICS in COVID-19 
DATE: 					14th of May 2020 
AUTHOR:					A Wong, A Schultze, C Rentsch
						adapted from K Baskharan, E Williamson 	
VERSION: 				Stata 16.1
DESCRIPTION OF FILE:	program 01, COPD population for ICS project  
						check inclusion/exclusion citeria
						drop patients if not relevant 
DEPENDENCIES: 
DATASETS USED:			data in memory (from analysis/input_asthma.csv)

DATASETS CREATED: 		analysis_dataset.dta
						lives in folder analysis/$tempdir 
OTHER OUTPUT: 			logfiles, printed to folder analysis/$logdir
							
==============================================================================*/

* Open a log file

cap log close
log using $logdir\01_cr_create_asthma_population, replace t

/* APPLY INCLUSION/EXCLUIONS==================================================*/ 

noi di "DROP MISSING GENDER:"
drop if inlist(sex,"I", "U")

noi di "DROP AGE <18:"
drop if age < 18 

noi di "DROP AGE >110:"
drop if age > 110 & age != .

noi di "DROP AGE MISSING:"
drop if age == . 

noi di "DROP IMD MISSING"
drop if imd == .u

noi di "DROP IF DEAD BEFORE INDEX"
drop if stime_$outcome  <= date("$indexdate", "DMY")

/* CHECK INCLUSION AND EXCLUSION CRITERIA=====================================*/ 

* DATA STRUCTURE: Confirm one row per patient 
duplicates tag patient_id, generate(dup_check)
assert dup_check == 0 
drop dup_check

* INCLUSION 1: Asthma in 3 years before 1 March 2020 
datacheck asthma_ever == 1, nol

* Check time from index to asthma, if asthma 
* + 15 because dates are imputed for covariates 
gen asthma_time = ((enter_date - asthma_ever_date) + 15)/365.25
datacheck asthma_time > 3, nol
drop asthma_time

* INCLUSION 2: >=18 and <=110 at 1 March 2020 
assert age < .
assert age >= 18 
assert age <= 110
 
* INCLUSION 3: M or F gender at 1 March 2020 
assert inlist(sex, "M", "F")

* EXCLUSION 1: 12 months or baseline time 
* [CANNOT BE QUANTIFIED AS VARIABLE NOT EXPORTED]

* EXCLUSION 2: No diagnosis of conflicting respiratory conditions 
datacheck other_respiratory == 0, nol
datacheck copd == 0, nol

* EXCLUSION 4: Nebulising treament 
* [NEBULES CANNOT BE QUANTIFIED AS VARIABLE NOT EXPORTED] 

* EXCLUDE 5:  MISSING IMD
assert inlist(imd, 1, 2, 3, 4, 5)

* EXCLUDE 6: NO LAMA (COPD treatment), unless LAMA and ICS 
gen lama_check = 1 if (lama_single == 1 | laba_lama ==1) & ///
                       ics_single != 1 & ///
					   laba_ics != 1 & ///
					   laba_lama_ics != 1 
					   
datacheck lama_check >=., nol
drop lama_check

* Close log file 
log close					   
