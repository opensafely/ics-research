/*==============================================================================
DO FILE NAME:			07_models_interact_copd
PROJECT:				ICS in COVID-19 
DATE: 					18th of May 2020  
AUTHOR:					A Schultze
VERSION: 				Stata 16.1 						
DESCRIPTION OF FILE:	program 07, evaluate age interaction 
DATASETS USED:			data in memory ($tempdir/analysis_dataset_STSET_outcome)

DATASETS CREATED: 		none
OTHER OUTPUT: 			logfiles, printed to folder analysis/$logdir
						table3, printed to analysis/$outdir
							
==============================================================================*/

* Open a log file

cap log close
log using $logdir\07_an_models_interact_copd, replace t

* Open Stata dataset
use $tempdir\analysis_dataset_STSET_$outcome, clear

/* Age Interaction============================================================*/ 

/* The smallest age group in COPD is much smaller than for asthma (35-40). 
   To be able to fit a meaningful model, combining this with the category above, 
   to create a category 35 - 50 */ 
/* So few deaths occuring below 50 years this cannot be used as a category, 
   so updating to 35-60 */ 
   
recode agegroup(1 = 2)
recode agegroup(2 = 3)
tab agegroup, nolabel 

label define agegroup2 	3 "35-<60" ///
						4 "60-<70" ///
						5 "70-<80" ///
						6 "80+"
						
label values agegroup agegroup2
tab agegroup 

/* Check Counts */ 

bysort agegroup: tab exposure $outcome, row

/* Univariable model */ 

stcox i.exposure i.agegroup
estimates store A

stcox i.exposure##i.agegroup
estimates store B
estimates save ./$tempdir/univar_int, replace 

lrtest A B
local univar_p = round(r(p),0.001)

/* Multivariable models */ 

* Age and Gender 

stcox i.exposure i.agegroup i.male
estimates store A

stcox i.exposure##i.agegroup i.male
estimates store B
estimates save ./$tempdir/multivar1_int, replace 

lrtest A B
local multivar1_p = round(r(p),0.001)

* Age, Gender and Comorbidities 
stcox i.exposure i.agegroup i.male $varlist, strata(stp)					
										
estimates store A

stcox i.exposure##i.agegroup i.male $varlist, strata(stp)			
estimates store B
estimates save ./$tempdir/multivar2_int, replace 

lrtest A B
local multivar2_p = round(r(p),0.001)

/* Print interaction table====================================================*/ 
cap file close tablecontent
file open tablecontent using ./$outdir/table3.txt, write text replace

* Column headings 
file write tablecontent ("Table 3: Current ICS use and $tableoutcome, Age Interaction - $population Population") _n
file write tablecontent _tab _tab _tab _tab ("Univariable") _tab _tab _tab ("Age/Sex Adjusted") _tab _tab _tab  ///
						("Age/Sex and Comorbidity Adjusted") _tab _tab _tab _n
file write tablecontent _tab ("Events") _tab ("Person-weeks") _tab ("Rate per 1,000") _tab ///
						("HR") _tab ("95% CI") _tab ("p (interaction)") _tab ("HR") _tab ///
						("95% CI") _tab ("p (interaction)") _tab ("HR") _tab ("95% CI") _tab ("p (interaction)") _tab _n	
* Overall p-values 
file write tablecontent ("Agegroup") _tab _tab _tab _tab _tab _tab ("`univar_p'") ///
						_tab _tab _tab ("`multivar1_p'") /// 
						_tab _tab _tab ("`multivar2_p'") _n

						
* Generic program to print model for a level of another variable 
cap prog drop printinteraction
prog define printinteraction 
syntax, variable(varname) min(real) max(real) 

	forvalues varlevel = `min'/`max'{ 

		* Row headings 
		file write tablecontent ("`varlevel'") _n 	

		local lab0: label exposure 0
		local lab1: label exposure 1
		 
		/* Counts */
					
		* First row, exposure = 0 (reference)
		
		file write tablecontent ("`lab0'") _tab

			count if exposure == 0 & $outcome == 1 & `variable' == `varlevel' 
			local event = r(N)
			bysort exposure `variable': egen total_follow_up = total(_t)
			summarize total_follow_up if exposure == 0 & `variable' == `varlevel'
			local person_week = r(mean)/7
			local rate = 1000*(`event'/`person_week')
			
		file write tablecontent (`event') _tab %10.0f (`person_week') _tab %3.2f (`rate') _tab
        file write tablecontent ("1.00 (ref)") _tab _tab _tab ("1.00 (ref)") _tab _tab _tab ("1.00 (ref)") _n
			
		* Second row, exposure = 1 (comparator)

		file write tablecontent ("`lab1'") _tab  

			count if exposure == 1 & $outcome == 1 & `variable' == `varlevel'
			local event = r(N)
			summarize total_follow_up if exposure == 1 & `variable' == `varlevel'
			local person_week = r(mean)/7
			local rate = 1000*(`event'/`person_week')
			file write tablecontent (`event') _tab %10.0f (`person_week') _tab %3.2f (`rate') _tab


		* Print models 
		estimates use ./$tempdir/univar_int 
		qui lincom 1.exposure + 1.exposure#`varlevel'.`variable', eform
		file write tablecontent %4.2f (r(estimate)) _tab %4.2f (r(lb)) (" - ") %4.2f (r(ub)) _tab _tab

		estimates use ./$tempdir/multivar1_int
		qui lincom 1.exposure + 1.exposure#`varlevel'.`variable', eform
		file write tablecontent %4.2f (r(estimate)) _tab %4.2f (r(lb)) (" - ") %4.2f (r(ub)) _tab _tab

		estimates use ./$tempdir/multivar2_int
		qui lincom 1.exposure + 1.exposure#`varlevel'.`variable', eform
		file write tablecontent %4.2f (r(estimate)) _tab %4.2f (r(lb)) (" - ") %4.2f (r(ub)) _tab _n 
		
		*drop macro, so this can be redefined
		drop total_follow_up
	
	} 
		
end

printinteraction, variable(agegroup) min(3) max(6) 

file write tablecontent _n
file close tablecontent

* Close log file 
log close
