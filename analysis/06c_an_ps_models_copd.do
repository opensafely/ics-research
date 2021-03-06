/*==============================================================================
DO FILE NAME:			06b_an_ps_models_copd
PROJECT:				ICS in COVID-19 
DATE: 					11th August 2020 
AUTHOR:					A Schultze 
VERSION: 				Stata 16.1									
DESCRIPTION OF FILE:	adapted program 06
DATASETS USED:			weighted stset data (ATT weights)
						($tempdir/analysis_dataset_STSET_IPW_$outcome)

DATASETS CREATED: 		none
OTHER OUTPUT: 			logfiles, printed to folder analysis/$logdir
						table2-ps, printed to analysis/$outdir
							
==============================================================================*/

* Open a log file

cap log close
log using $logdir\06c_an_ps_models_copd, replace t

* Open Stata dataset
use $tempdir\analysis_dataset_STSET_IPWATT_$outcome, clear

/* Sense check outcomes=======================================================*/ 

tab exposure $outcome, missing row

/* Main Model=================================================================*/

*Post to a stata dataset for appending with other results later
capture postfile temp str30 outcome str30 population str30 level str30 title estimate min95 max95 using "$tempdir/temp_copd_att.dta",replace

/* Univariable model */ 

stcox i.exposure, vce(robust)
estimates save ./$tempdir/univar, replace 

/* Print table================================================================*/ 
*  Print the results for the main model 

cap file close tablecontent
file open tablecontent using ./$outdir/table2att.txt, write text replace

* Column headings 
file write tablecontent ("Table 2 - PS: Association between current ICS use and $tableoutcome - $population Population ATT weights") _n
file write tablecontent _tab ("HR") _tab ("95% CI") _n				

* Row headings 
local lab0: label exposure 0
local lab1: label exposure 1
	
	file write tablecontent ("`lab0'") _tab
	file write tablecontent ("1.00 (ref)") _tab _n
	file write tablecontent ("`lab1'") _tab  

/* Main Model */ 
estimates use ./$tempdir/univar 
lincom 1.exposure, eform
file write tablecontent %4.2f (r(estimate)) _tab %4.2f (r(lb)) (" - ") %4.2f (r(ub)) _tab 
post temp ("$tableoutcome") ("$population") ("PS - IPW") ("`lab1'") (round(r(estimate)),0.01) (round(r(lb)),0.01) (round(r(ub)),0.01)           

file write tablecontent _n
file close tablecontent
postclose temp  

* At editorial request, need to add number of people in each category for forest plots 

capture postfile temp str20 exp1 using "$tempdir/temp2.dta", replace

count if exposure == 1 & $outcome == 1
local event = r(N)
count if exposure == 1 
local denom = r(N)

gen exp1string = string(`event', "%6.0f") + "/" + string(`denom', "%6.0f") 

post temp (exp1string) 
post temp ("")
post temp ("")

postclose temp

capture postfile temp str20 exp0 using "$tempdir/temp3.dta", replace

count if exposure == 0 & $outcome == 1
local event = r(N)
count if exposure == 0 
local denom = r(N)

gen exp0string = string(`event', "%6.0f") + "/" + string(`denom', "%6.0f")

post temp (exp0string) 
post temp ("")
post temp ("")

postclose temp

use $tempdir/temp_copd.dta, clear
gen ID = _n 
save $tempdir/temp_copd.dta, replace

use $tempdir/temp2.dta, clear
gen ID = _n
save $tempdir/temp2.dta, replace

use $tempdir/temp3.dta, clear
gen ID = _n
save $tempdir/temp3.dta, replace

use $tempdir/temp_copd.dta, clear

merge 1:1 ID using $tempdir/temp2 
drop _merge
merge 1:1 ID using $tempdir/temp3
drop _merge 
drop ID
 
save $tempdir/temp_copd.dta, replace

* Close log file 
log close
