/*==============================================================================
DO FILE NAME:			gr_e-value_plot
PROJECT:				ICS in COVID-19 
DATE: 					18th of May 2020  
AUTHOR:					Jeremy Brown, adapted by Anna Schultze
VERSION: 				Stata 16.1									
DESCRIPTION OF FILE:	read in saved datasets 
						generate e-value plots 
DATASETS USED:			dta saved as 'temp' in each tempdata directory created
DATASETS CREATED: 		none
OTHER OUTPUT: 			logfiles, printed to folder analysis/$logdir
						forest plot, printed to analysis/$outdir
							
==============================================================================*/

cap log close
log using $logdir\gr_e-value_plot, replace t

****************************
/* Input effect estimates */
****************************
clear
use copd_tempdata/temp_copd.dta

* COPD
glob hr_copd = estimate
glob lci_copd = min95
glob uci_copd = max95

clear 
use asthma_tempdata/temp_asthma.dta

* Asthma low-dose ICS
glob hr_asthma_ld = estimate
glob lci_asthma_ld = min95
glob uci_asthma_ld = max95

* Asthma high-dose ICS
glob hr_asthma_hd = estimate
glob lci_asthma_hd = min95
glob uci_asthma_hd = max95

**************************
/* Create e-value plots */
**************************

* COPD 
evalue hr $hr_copd, lcl($lci_copd) ucl($uci_copd) true(1.0) figure(scheme("s1color") aspect(1.01) ytitle(,size(small) margin(medium)) xtitle(,size(small) margin(medium)))
* addplot: 
graph save "$outdir/evalue_COPD.gph", replace
graph export "$outdir/evalue_COPD.svg", replace 

* Ashtma low-dose ICS
evalue hr $hr_asthma_ld, lcl($lci_asthma_ld) ucl($uci_asthma_ld) true(1.0) figure(scheme("s1color") aspect(1.01) ytitle(,size(small) margin(medium)) xtitle(,size(small) margin(medium))) 
graph save "$outdir/evalue_Asthma_LD.gph", replace
graph export "$outdir/evalue_Asthma_LD.svg", replace 

* Asthma high-dose ICS
evalue hr $hr_asthma_hd, lcl($lci_asthma_hd) ucl($uci_asthma_hd) true(1.0) figure(scheme("s1color") aspect(1.01) ytitle(,size(small) margin(medium)) xtitle(,size(small) margin(medium)))
graph save "$outdir/evalue_Asthma_HD.gph", replace 
graph export "$outdir/evalue_Asthma_HD.svg", replace 
*close log
log close 


