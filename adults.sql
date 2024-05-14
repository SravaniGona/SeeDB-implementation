create database census;

\c census;

create table adults(
    age integer NULL, 
    workclass varchar(50) NULL,
    fnlwgt integer NULL, 
    education varchar(50) NULL, 
    education_num integer NULL, 
    marital_status varchar(50) NULL, 
    occupation varchar(50) NULL, 
    relationship varchar(50) NULL, 
    race varchar(50) NULL, 
    sex varchar(50) NULL, 
    capital_gain integer NULL, 
    capital_loss integer NULL, 
    hours_per_week integer NULL, 
    native_country varchar(50) NULL, 
    salary_range varchar NULL
);

\copy adults from 'C:\Users\Sravani\Documents\Spring 2024\645 - Database Design and Implementation\Project\census+income\adult.data' with delimiter ',';
\copy adults from 'C:\Users\Sravani\Documents\Spring 2024\645 - Database Design and Implementation\Project\census+income\adult.test' with delimiter ',';

UPDATE adults 
SET 
    workclass = CASE WHEN TRIM(workclass) = '?' THEN NULL ELSE TRIM(workclass) END,
    education = CASE WHEN TRIM(education) = '?' THEN NULL ELSE TRIM(education) END,
    marital_status = CASE WHEN TRIM(marital_status) = '?' THEN NULL ELSE TRIM(marital_status) END,
    occupation = CASE WHEN TRIM(occupation) = '?' THEN NULL ELSE TRIM(occupation) END,
    relationship = CASE WHEN TRIM(relationship) = '?' THEN NULL ELSE TRIM(relationship) END,
    race = CASE WHEN TRIM(race) = '?' THEN NULL ELSE TRIM(race) END,
    sex = CASE WHEN TRIM(sex) = '?' THEN NULL ELSE TRIM(sex) END,
    native_country = CASE WHEN TRIM(native_country) = '?' THEN NULL ELSE TRIM(native_country) END,
    salary_range = CASE WHEN TRIM(salary_range) = '?' THEN NULL ELSE TRIM(salary_range) END;
