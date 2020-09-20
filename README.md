# Daily COVID-19 Data by FIPS Code

## Summary
This tool will download and merge data from the following sources:
### New York Times COVID-19 Data
[README](https://github.com/nytimes/covid-19-data/blob/master/README.md)  
[Dataset URL](https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv) (21MB as of 2020-09-20, growing daily)
#### Important details about this file
* The earliest date we have numbers reported for is 2020-01-21.
* The "fips" field is coerced into string format (to preserve leading zeroes), and "date" is coerced into datetime format.
* Rows where "fips" is null are filtered out.
* Only cumulative case and death counts are provided in the file. We calculate daily cases and deaths for a given FIPS code by taking the difference between today's and the previous day's cumulative counts. For the first day reported for a given FIPS code, the daily counts are set to be equal to the cumulative counts.
* There are 83 FIPS codes representing 11,364 rows in this dataset that do not exist in the Census Population dataset. They collectively represent only 3 "states": Northern Mariana Islands, Puerto Rico, and Virgin Islands. We are moving forward with the assumption it is okay to drop these rows and consider them out of scope.
* Finally, we perform a validation to ensure that each combination of FIPS code + date is unique. Since this will ultimately be our lookup key, we need to ensure there is no ambiguity. An error will be thrown if this condition is not met.

### US Census Bureau Population Estimates by County (2019)
[README](https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2019/co-est2019-alldata.pdf)  
[Dataset URL](https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv) (~3.5MB)
#### Important details about this file
* This file is encoded as ISO-8859-1 and will throw errors if you try to decode it using the default UTF-8 encoding pandas uses.
* The fields SUMLEV, STATE, and COUNTY appear to be numeric and will be inferred as integers by pandas. However, the actual values contain leading zeroes which are important to their compatibility with other datasets. They are coerced into strings in order to preserve the leading zeroes.
* Rows where SUMLEV="040" are state-level populations, which are not relevant to our purposes. We keep only records where SUMLEV="050" (the county-level records).
* There are many extraneous fields in this dataset, so we keep only the relevant ones: STATE, COUNTY, STNAME, CTYNAME, POPESTIMATE2019.
* In order to join this dataset to the NYT dataset, we must create the proper FIPS code from it's components by concatenating STATE and COUNTY codes. This is where the leading zeroes become important.
* Finally, we perform a validation to ensure that FIPS code is unique in the resulting dataset. If this condition were not true, it could lead to unexpected results. If this requirement is not met, an error will be thrown, allowing for the opportunity to investigate.

### How to build the file

##### Optional: Create conda environment from the requirements.txt file  
`conda create --name covid --file requirements.txt`  
`conda activate covid`

##### Build the merged file
`python covid_data.py`  
It should take less than 10 seconds to download the source data and merge it.


### Output Dataset
File Name: `data/nyt_enriched.pkl`  
Fields:
* `fips: str`
* `date: datetime`
* `daily_cases: int`
* `cumulative_cases: int`
* `daily_deaths: int`
* `cumulative_deaths: int`
* `population: int`  

Note: to read this file, you will need to specify "bz2" compression, e.g.  
`df = pd.read_pickle("data/nyt_enriched.pkl", compression="bz2")`

fips + date act as a composite key on this dataset, and can be used to look up the COVID and population values.  

The output file that is generated should be somewhere in the range of 1MB-2MB.  
You can view the validations that were performed by viewing `test/validate_output_file.ipynb`

### Final Thoughts
##### Design Rationale
This project ultimately only consists of 3 functions, and they are sort of on the longer side. 
Yet, it is only setting out to do a very specific job. 
Perhaps if there were other jobs doing much of the same stuff, we could look to build something more generalizable. 
The benefit we get is that this should be very easy to trace through, and if there are any issues, we have some convenient ways of reading in each dataset individually and exploring it to aid in our investigation.

##### Things that would be cool to add
* More robust data validations. There is a newer library called [great expectations](https://greatexpectations.io/) that I've been interested in checking out for this purpose.
* More prebuilt calculations that would be useful to analytics, like cases per 100,000 people, 7-day rolling average of new cases, etc.
* Depending on anticipated use cases, maybe standing up an API on top of this data would be useful.
* Lookup functions that return plots that could be displayed in a notebook or flask app.
* If this were something that were going to stick around for a long time (I hope it isn't given the subject matter!), I might be inclined to store the results in a database table to make it more accessible.
