from cohortextractor import (
    StudyDefinition,
    patients,
    filter_codes_by_category,
    combine_codelists,
)

from codelists import *

study = StudyDefinition(
    # Configure the expectations framework (optional)
    default_expectations={
        "date": {"earliest": "1970-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.2,
    },
    ## STUDY POPULATION (required)
    population=patients.satisfying(
        """
        (
          has_asthma OR
          (asthma_ever AND any_asthma_med)
        ) AND
        (age >=18 AND age <= 110) AND
        has_follow_up AND NOT
        copd AND NOT
        other_respiratory AND NOT
        nebules AND NOT
        (
          (lama_single OR laba_lama) AND NOT (
            high_dose_ics OR
            high_dose_ics_single_ing OR
            high_dose_ics_multiple_ingredient OR
            low_med_dose_ics_single_ingredient OR
            low_med_dose_ics_multiple_ingredient OR
            low_med_dose_ics OR
            ics_single OR
            laba_ics OR
            laba_lama_ics
          )
        )
        """,
        has_asthma=patients.with_these_clinical_events(
            asthma_codes, between=["2017-02-28", "2020-02-29"],
        ),
        has_follow_up=patients.registered_with_one_practice_between(
            "2019-02-28", "2020-02-29"
        ),
        nebules=patients.with_these_medications(
            nebulised_med_codes, between=["2019-02-28", "2020-02-29"],
        ),
        any_asthma_med=patients.satisfying(
            """
            ltra_single OR
            laba_lama_ics OR
            laba_lama OR
            laba_ics OR
            lama_single OR
            laba_single OR
            sama_single OR
            saba_single OR
            ics_single OR
            low_med_dose_ics OR
            low_med_dose_ics_multiple_ingredient OR
            low_med_dose_ics_single_ingredient OR
            high_dose_ics_multiple_ingredient OR
            high_dose_ics_single_ing OR
            high_dose_ics

            """
        ),
    ),
    ## OUTCOMES (at least one outcome or covariate is required)
    icu_date_admitted=patients.admitted_to_icu(
        on_or_after="2020-03-01",
        include_day=True,
        returning="date_admitted",
        return_expectations={"date": {"earliest": "2020-03-01"}},
    ),
    died_date_cpns=patients.with_death_recorded_in_cpns(
        on_or_after="2020-03-01",
        returning="date_of_death",
        include_month=True,
        include_day=True,
        return_expectations={"date": {"earliest": "2020-03-01"}},
    ),
    died_ons_covid_flag_any=patients.with_these_codes_on_death_certificate(
        covid_codelist,
        on_or_after="2020-03-01",
        match_only_underlying_cause=False,
        return_expectations={"date": {"earliest": "2020-03-01"}},
    ),
    died_ons_covid_flag_underlying=patients.with_these_codes_on_death_certificate(
        covid_codelist,
        on_or_after="2020-03-01",
        match_only_underlying_cause=True,
        return_expectations={"date": {"earliest": "2020-03-01"}},
    ),
    died_date_ons=patients.died_from_any_cause(
        on_or_after="2020-03-01",
        returning="date_of_death",
        include_month=True,
        include_day=True,
        return_expectations={"date": {"earliest": "2020-03-01"}},
    ),
    ## DEMOGRAPHIC INFORMATION
    age=patients.age_as_of(
        "2020-02-29",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),
    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.49, "F": 0.51}},
        }
    ),
    stp=patients.registered_practice_as_of(
        "2020-02-29",
        returning="stp_code",
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "STP1": 0.1,
                    "STP2": 0.1,
                    "STP3": 0.1,
                    "STP4": 0.1,
                    "STP5": 0.1,
                    "STP6": 0.1,
                    "STP7": 0.1,
                    "STP8": 0.1,
                    "STP9": 0.1,
                    "STP10": 0.1,
                }
            },
        },
    ),
    imd=patients.address_as_of(
        "2020-02-29",
        returning="index_of_multiple_deprivation",
        round_to_nearest=100,
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"100": 0.1, "200": 0.2, "300": 0.7}},
        },
    ),
    ethnicity=patients.with_these_clinical_events(
        ethnicity_codes,
        returning="category",
        find_last_match_in_period=True,
        include_date_of_match=True,
        return_expectations={
            "category": {"ratios": {"1": 0.8, "5": 0.1, "3": 0.1}},
            "incidence": 0.75,
        },
    ),
    ## COVARIATES
    bmi=patients.most_recent_bmi(
        between=["2010-02-28", "2020-02-29"],
        minimum_age_at_measurement=16,
        include_measurement_date=True,
        include_month=True,
        return_expectations={
            "date": {},
            "float": {"distribution": "normal", "mean": 35, "stddev": 10},
            "incidence": 0.95,
        },
    ),
    smoking_status=patients.categorised_as(
        {
            "S": "most_recent_smoking_code = 'S'",
            "E": """
                     most_recent_smoking_code = 'E' OR (    
                       most_recent_smoking_code = 'N' AND ever_smoked   
                     )  
                """,
            "N": "most_recent_smoking_code = 'N' AND NOT ever_smoked",
            "M": "DEFAULT",
        },
        return_expectations={
            "category": {"ratios": {"S": 0.6, "E": 0.1, "N": 0.2, "M": 0.1}}
        },
        most_recent_smoking_code=patients.with_these_clinical_events(
            clear_smoking_codes,
            find_last_match_in_period=True,
            on_or_before="2020-02-29",
            returning="category",
        ),
        ever_smoked=patients.with_these_clinical_events(
            filter_codes_by_category(clear_smoking_codes, include=["S", "E"]),
            on_or_before="2020-02-29",
        ),
    ),
    smoking_status_date=patients.with_these_clinical_events(
        clear_smoking_codes,
        on_or_before="2020-02-29",
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    #### HIGH DOSE ICS - all preparation
    high_dose_ics=patients.with_these_medications(
        high_dose_ics_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"}
        },
    ),
    #### HIGH DOSE ICS - single ingredient preparations
    high_dose_ics_single_ing=patients.with_these_medications(
        high_dose_ics_single_ingredient_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"}
        },
    ),
    #### HIGH DOSE ICS - multiple ingredient preparation
    high_dose_ics_multiple_ingredient=patients.with_these_medications(
        high_dose_ics_multiple_ingredient_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"}
        },
    ),
    ### LOW-MED DOSE ICS - single ingredient preparations
    low_med_dose_ics_single_ingredient=patients.with_these_medications(
        low_medium_ics_single_ingredient_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"},
        },
    ),
    ### LOW-MED DOSE ICS - multiple ingredient preparations
    low_med_dose_ics_multiple_ingredient=patients.with_these_medications(
        low_medium_ics_multiple_ingredient_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
    ),
    ### LOW-MED DOSE ICS - all preparation
    low_med_dose_ics=patients.with_these_medications(
        low_medium_ics_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"},
        },
    ),
    #### ICS SINGLE CONSTITUENT
    ics_single=patients.with_these_medications(
        ics_single_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"},
        },
    ),
    #### ORAL STEROIDS SINGLE CONSTITUENT
    oral_steroids=patients.with_these_medications(
        oral_steroid_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"},
        },
    ),
    #### SABA SINGLE CONSTITUENT
    saba_single=patients.with_these_medications(
        saba_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"},
        },
    ),
    #### SAMA SINGLE CONSTITUENT
    sama_single=patients.with_these_medications(
        sama_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"},
        },
    ),
    #### LABA SINGLE CONSTITUENT
    laba_single=patients.with_these_medications(
        single_laba_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"},
        },
    ),
    #### LAMA SINGLE CONSTITUENT
    lama_single=patients.with_these_medications(
        single_lama_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"},
        },
    ),
    #### LABA + ICS
    laba_ics=patients.with_these_medications(
        laba_ics_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"},
        },
    ),
    #### LABA + LAMA
    laba_lama=patients.with_these_medications(
        laba_lama_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"},
        },
    ),
    #### LABA + LAMA + ICS
    laba_lama_ics=patients.with_these_medications(
        laba_lama__ics_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"},
        },
    ),
    #### LTRA SINGLE CONSTITUENT
    ltra_single=patients.with_these_medications(
        leukotriene_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"},
        },
    ),
    ### OXYGEN THERAPY LEFT OUT AT PRESENT DUE TO POOR RECORDS
    ### COPD
    copd=patients.with_these_clinical_events(
        copd_codes,
        on_or_before="2020-02-29",
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    ### OTHER RESPIRATORY
    other_respiratory=patients.with_these_clinical_events(
        other_respiratory_codes,
        on_or_before="2020-02-29",
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    ### ASTHMA EVER
    asthma_ever=patients.with_these_clinical_events(
        asthma_ever_codes,
        on_or_before="2020-02-29",
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    ### OTHER HEART DISEASE
    other_heart_disease=patients.with_these_clinical_events(
        other_heart_disease_codes,
        on_or_before="2020-02-29",
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    ### ILI
    ili=patients.with_these_clinical_events(
        ili_codes,
        return_first_date_in_period=True,
        include_month=True,
        between=["2016-09-01", "2020-02-29"],
        return_expectations={
            "date": {"earliest": "2019-09-01", "latest": "2020-02-29"}
        },
    ),
    ### HYPERTENSION
    hypertension=patients.with_these_clinical_events(
        hypertension_codes,
        on_or_before="2020-02-29",
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    ### HEART FAILURE
    heart_failure=patients.with_these_clinical_events(
        heart_failure_codes,
        on_or_before="2020-02-29",
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    #### SYSTOLIC BLOOD PRESSURE
    bp_sys=patients.mean_recorded_value(
        systolic_blood_pressure_codes,
        on_most_recent_day_of_measurement=True,
        on_or_before="2020-02-29",
        include_measurement_date=True,
        include_month=True,
        return_expectations={
            "float": {"distribution": "normal", "mean": 80, "stddev": 10},
            "date": {"latest": "2020-02-29"},
            "incidence": 0.95,
        },
    ),
    ### DIASTOLIC BLOOD PRESSURE
    bp_dias=patients.mean_recorded_value(
        diastolic_blood_pressure_codes,
        on_most_recent_day_of_measurement=True,
        on_or_before="2020-02-29",
        include_measurement_date=True,
        include_month=True,
        return_expectations={
            "float": {"distribution": "normal", "mean": 120, "stddev": 10},
            "date": {"latest": "2020-02-29"},
            "incidence": 0.95,
        },
    ),
    ### DIABETES
    diabetes=patients.with_these_clinical_events(
        diabetes_codes,
        on_or_before="2020-02-29",
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    hba1c_mmol_per_mol=patients.with_these_clinical_events(
        hba1c_new_codes,
        find_last_match_in_period=True,
        on_or_before="2020-02-29",
        returning="numeric_value",
        include_date_of_match=True,
        include_month=True,
        return_expectations={
            "date": {"latest": "2020-02-29"},
            "float": {"distribution": "normal", "mean": 40.0, "stddev": 20},
            "incidence": 0.95,
        },
    ),
    hba1c_percentage=patients.with_these_clinical_events(
        hba1c_old_codes,
        find_last_match_in_period=True,
        on_or_before="2020-02-29",
        returning="numeric_value",
        include_date_of_match=True,
        include_month=True,
        return_expectations={
            "date": {"latest": "2020-02-29"},
            "float": {"distribution": "normal", "mean": 5, "stddev": 2},
            "incidence": 0.95,
        },
    ),
    ### CANCER - 3 TYPES
    lung_cancer=patients.with_these_clinical_events(
        lung_cancer_codes,
        on_or_before="2020-02-29",
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    haem_cancer=patients.with_these_clinical_events(
        haem_cancer_codes,
        on_or_before="2020-02-29",
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    other_cancer=patients.with_these_clinical_events(
        other_cancer_codes,
        on_or_before="2020-02-29",
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    # IMMUNOSUPPRESSION - 4 TYPES
    # https://github.com/ebmdatalab/tpp-sql-notebook/issues/36
    aplastic_anaemia=patients.with_these_clinical_events(
        aplastic_codes,
        on_or_before="2020-02-29",
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    hiv=patients.with_these_clinical_events(
        hiv_codes,
        on_or_before="2020-02-29",
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    permanent_immunodeficiency=patients.with_these_clinical_events(
        permanent_immune_codes,
        on_or_before="2020-02-29",
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    temporary_immunodeficiency=patients.with_these_clinical_events(
        temp_immune_codes,
        between=["2019-03-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-03-01", "latest": "2020-02-29"}
        },
    ),
    ### CHRONIC KIDNEY DISEASE
    creatinine=patients.with_these_clinical_events(
        creatinine_codes,
        find_last_match_in_period=True,
        between=["2019-02-28", "2020-02-29"],
        returning="numeric_value",
        include_date_of_match=True,
        include_month=True,
        return_expectations={
            "float": {"distribution": "normal", "mean": 60.0, "stddev": 15},
            "date": {"earliest": "2019-02-28", "latest": "2020-02-29"},
            "incidence": 0.95,
        },
    ),
    #### end stage renal disease codes incl. dialysis / transplant
    esrf=patients.with_these_clinical_events(
        ckd_codes,
        on_or_before="2020-02-29",
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={"date": {"latest": "2020-02-29"}},
    ),
    ### VACCINATION HISTORY
    flu_vaccine_tpp_table=patients.with_tpp_vaccination_record(
        target_disease_matches="INFLUENZA",
        between=["2019-09-01", "2020-02-29"],  # current flu season
        find_first_match_in_period=True,
        returning="date",
        return_expectations={
            "date": {"earliest": "2019-09-01", "latest": "2020-02-29"}
        },
    ),
    flu_vaccine_med=patients.with_these_medications(
        flu_med_codes,
        between=["2019-09-01", "2020-02-29"],  # current flu season
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-09-01", "latest": "2020-02-29"}
        },
    ),
    flu_vaccine_clinical=patients.with_these_clinical_events(
        flu_clinical_given_codes,
        ignore_days_where_these_codes_occur=flu_clinical_not_given_codes,
        between=["2019-09-01", "2020-02-29"],  # current flu season
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-09-01", "latest": "2020-02-29"}
        },
    ),
    flu_vaccine=patients.satisfying(
        """
        flu_vaccine_tpp_table OR
        flu_vaccine_med OR
        flu_vaccine_clinical
        """,
    ),
    # PNEUMOCOCCAL VACCINE
    pneumococcal_vaccine_tpp_table=patients.with_tpp_vaccination_record(
        target_disease_matches="PNEUMOCOCCAL",
        between=["2015-03-01", "2020-02-29"],
        find_first_match_in_period=True,
        returning="date",
        return_expectations={
            "date": {"earliest": "2015-03-01", "latest": "2020-02-29"}
        },
    ),
    pneumococcal_vaccine_med=patients.with_these_medications(
        pneumococcal_med_codes,
        between=["2015-03-01", "2020-02-29"],  # past five years
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2015-03-01", "latest": "2020-02-29"}
        },
    ),
    pneumococcal_vaccine_clinical=patients.with_these_clinical_events(
        pneumococcal_clinical_given_codes,
        ignore_days_where_these_codes_occur=pneumococcal_clinical_not_given_codes,
        between=["2015-03-01", "2020-02-29"],  # past five years
        return_first_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2015-03-01", "latest": "2020-02-29"}
        },
    ),
    pneumococcal_vaccine=patients.satisfying(
        """
        pneumococcal_vaccine_tpp_table OR
        pneumococcal_vaccine_med OR
        pneumococcal_vaccine_clinical
        """,
    ),
    ### EXACERBATION
    # count
    exacerbation_count=patients.with_these_medications(
        oral_steroid_med_codes,
        between=["2019-03-01", "2020-02-29"],
        ignore_days_where_these_clinical_codes_occur=combine_codelists(
            sle_codes,
            interstital_lung_codes,
            ra_codes,
            ms_codes,
            temporal_arteritis_codes,
        ),
        returning="number_of_episodes",
        episode_defined_as="series of events each <= 14 days apart",
        return_expectations={
            "int": {"distribution": "normal", "mean": 2, "stddev": 1},
            "incidence": 0.2,
        },
    ),
    # # binary flag
    exacerbations=patients.satisfying(
        """
        exacerbation_count > 0
        """,
    ),
    ### INSULIN USE
    insulin=patients.with_these_medications(
        insulin_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"}
        },
    ),
    ### STATIN USE
    statin=patients.with_these_medications(
        statin_med_codes,
        between=["2019-11-01", "2020-02-29"],
        return_last_date_in_period=True,
        include_month=True,
        return_expectations={
            "date": {"earliest": "2019-11-01", "latest": "2020-02-29"}
        },
    ),
    ### GP CONSULTATION RATE
    gp_consult_count=patients.with_gp_consultations(
        between=["2019-03-01", "2020-02-29"],
        returning="number_of_matches_in_period",
        return_expectations={
            "int": {"distribution": "normal", "mean": 4, "stddev": 2},
            "date": {"earliest": "2019-03-01", "latest": "2020-02-29"},
            "incidence": 0.7,
        },
    ),
    has_consultation_history=patients.with_complete_gp_consultation_history_between(
        "2019-03-01", "2020-02-29", return_expectations={"incidence": 0.9},
    ),
)
