clinical_trial_context = """Pandas DataFrame name is 'clinical_trials_df' :
Useful for answering questions related to clinical trials
The column headings and its description are given
-nctId: The unique identifier for each clinical trial registered on ClinicalTrials.gov.
-organization:  The name of the organization conducting the clinical trial.
-organizationType:  The type of organization, such as 'OTHER', 'INDUSTRY', 'NIH', 'OTHER_GOV', 'INDIV', 'FED', 'NETWORK', 'UNKNOWN'.
-briefTitle:  A short title for the clinical trial, intended for easy reference.
-officialTitle:  The full official title of the clinical trial.
-statusVerifiedDate:  The date when the status of the clinical trial was last verified.
-overallStatus:  The current overall status of the clinical trial like 'COMPLETED', 'UNKNOWN', 'ACTIVE_NOT_RECRUITING', 'RECRUITING', 'WITHDRAWN', 'TERMINATED', 'ENROLLING_BY_INVITATION', 'NOT_YET_RECRUITING', 'APPROVED_FOR_MARKETING', 'SUSPENDED','AVAILABLE'.
-hasExpandedAccess:  It has boolean values and it indicates whether the clinical trial includes expanded access to the investigational drug or device outside of the clinical trial.
-startDate:  The date when the clinical trial began.
-completionDate:  The date when the clinical trial was completed.
-completionDateType:  The type of completion date, specifying whether it refers to the ACTUAL or ESTIMATED.
-studyFirstSubmitDate:  The date when the clinical trial information was first submitted to ClinicalTrials.gov.
-studyFirstPostDate:  The date when the clinical trial information was first posted on ClinicalTrials.gov.
-lastUpdatePostDate:  The date when the clinical trial information was last updated on ClinicalTrials.gov.
-lastUpdatePostDateType:  The type of last update post date, specifying whether it refers to the actual or anticipated date.
-HasResults:  It contains boolean values and indicates whether the results of the clinical trial have been posted on ClinicalTrials.gov.
-responsibleParty:  The individual or organization responsible for the overall conduct of the clinical trial.
-leadSponsor:  The primary sponsor responsible for the initiation, management, and financing of the clinical trial.
-leadSponsorType:  The type of the lead sponsor, such as academic, industry, or government.
-collaborators:  Other organizations or individuals collaborating on the clinical trial.
-collaboratorsType:  The types of collaborators involved in the clinical trial.
-briefSummary:  A brief summary of the clinical trial, providing an overview of the study's purpose and key details.
-detailedDescription:  A detailed description of the clinical trial, including comprehensive information about the study design, methodology, and objectives.
-conditions:  The medical conditions or diseases being studied in the clinical trial.
-studyType:  The type of study (e.g., 'INTERVENTIONAL', 'OBSERVATIONAL', 'EXPANDED_ACCESS').
-phases:  The phase of the clinical trial (e.g., 'NA', 'PHASE2', 'PHASE2, PHASE3', 'PHASE3', 'PHASE1', 'PHASE4','PHASE1, PHASE2', 'EARLY_PHASE1').
-allocation:  The method of assigning participants to different arms of the clinical trial (e.g., 'RANDOMIZED','NON_RANDOMIZED').
-interventionModel:  The model of intervention used in the clinical trial (e.g., 'SINGLE_GROUP', 'PARALLEL', 'CROSSOVER', 'SEQUENTIAL', 'FACTORIAL').
-primaryPurpose:  The primary purpose of the clinical trial like 'PREVENTION', 'TREATMENT', 'SUPPORTIVE_CARE','BASIC_SCIENCE', 'DIAGNOSTIC', 'OTHER', 'ECT', 'SCREENING','HEALTH_SERVICES_RESEARCH', 'DEVICE_FEASIBILITY').
-masking:  The method used to prevent bias by concealing the allocation of participants (e.g., 'QUADRUPLE', 'NONE', 'DOUBLE', 'TRIPLE', 'SINGLE').
-whoMasked:  Specifies who is masked in the clinical trial etc. PARTICIPANT, INVESTIGATOR etc).
-enrollmentCount:  The number of participants enrolled in the clinical trial.
-enrollmentType:  The type of enrollment, specifying whether the number is ACTUAL or ESTIMATED.
-arms:  The number of rms or groups in the clinical trial.
-interventionDrug:  The drugs or medications being tested or used as interventions in the clinical trial.
-interventionDescription:  Descriptions of the interventions used in the clinical trial.
-interventionOthers:  Other types of interventions used in the clinical trial (e.g., devices, procedures).
-primaryOutcomes:  The primary outcome measures being assessed in the clinical trial.
-secondaryOutcomes:  The secondary outcome measures being assessed in the clinical trial.
-eligibilityCriteria:  The criteria that determine whether individuals can participate in the clinical trial.
-healthyVolunteers:  Indicates whether healthy volunteers are accepted in the clinical trial.
-eligibilityGender:  The gender eligibility criteria for participants in the clinical trial.
-eligibilityMinimumAge:  The minimum age of participants eligible for the clinical trial.
-eligibilityMaximumAge:  The maximum age of participants eligible for the clinical trial.
-eligibilityStandardAges:  Standard age groups eligible for the clinical trial.
-LocationName:  The names of the locations where the clinical trial is being conducted.
-city:  The city where the clinical trial locations are situated.
-state:  The state where the clinical trial locations are situated.
-country:  The country where the clinical trial locations are situated.
-interventionBiological:  Biological interventions (e.g., vaccines, blood products) used in the clinical trial.
"""

fda_context = """Pandas DataFrame name is 'FDA_drugs_df' :
All the drugs present in the data are approved no need to filter for approved drugs
Useful for answering questions about the drug or disease from FDA database
Its columns are {FDA_drugs_df.columns}is more about use, contraindications, labels and other infomrations.
Table 'fda_drug_database': Table containing information related to FDA drug database.
Some column details are:
-brand_name:  The brand name of the drug
-generic_name: The generic name of the drug
-manufacturer_name: The name of company or institution which manufactures that drug
-application_number: If it stars with NDA its new drug application otherwise its a reference product
-indications_and_usage: Indications and recommended usage of the drug.
-description: This column contains description only about of the drug physical properties, chemical name and other properties of drug.
-clinical_pharmacology: Information about the clinical pharmacology of the drug.
-contraindications: Conditions under which the drug should not be used.
-information_for_patients: Guidance and information for patients using the drug.
-drug_interactions: Interactions with other drugs.
-adverse_reactions: Possible adverse reactions to the drug.
-dosage_and_administration: Recommended dosage and administration instructions for the drug.
-how_supplied: Information on how the drug is supplied.
-pharm_class_moa: Pharmacological class and mechanism of action of the drug.
-unii: Unique Ingredient Identifier for the drug.
-mechanism_of_action: Detailed mechanism of action of the drug.
-pharmacokinetics: Information on the drug's pharmacokinetics.
-warnings_and_cautions: Important warnings and cautions associated with the drug.
-pharmacodynamics: Effects of the drug on the body's physiological systems.
-precautions: What pre-caution should be taken while using the drug.
-clinical_studies: This is long text field that includs details of any clinical studies conducted on the drug including its NCTIDs that might led to its approval.
-is_original_packager: Indication if the drug is from the original packager.
-upc: Universal Product Code for the drug.
-pharm_class_cs: Chemical structure-based pharmacological class of the drug.
"""
