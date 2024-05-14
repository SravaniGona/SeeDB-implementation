import psycopg2
import pandas as pd
from scipy.stats import entropy
from collections import defaultdict
import math
import matplotlib.pyplot as plot

# Connect to database
connection = psycopg2.connect(database="census", user="postgres", password="grespost")
cursor = connection.cursor()

# Aggregate functions
f_list = ["count","sum", "min", "max", "avg"]

# Dimension attributes

a_list = ["workclass", "education", "occupation", "race", "sex", "relationship", "native_country", "salary_range"]

# Measure attributes
m_list = ["age", "fnlwgt", "education_num", "capital_gain", "capital_loss", "hours_per_week"]

# Categories of marital_status
married = ["Married-spouse-absent", "Married-AF-spouse", "Married-civ-spouse", "Separated"]
married_list_string = "('" + "','".join(married) + "')"
unmarried = ["Widowed", "Divorced", "Never-married"]
unmarried_list_string = "('" + "','".join(unmarried) + "')"

# Define hyper parameters
k = 5
partitions = 10
delta = 0.01

# Get total records count in db where dimension attributes are not null
query = "select count(*) from adults where " + " is not null and ".join(a_list) + " is not null"
cursor.execute(query)
records_count = cursor.fetchall()[0][0]

batch_size = math.ceil(records_count/partitions)

# List of all views
afm_combinations = []
for a in a_list:
    for f in f_list:
        for m in m_list:
            afm_combinations.append((a,f,m))

def createOptimizedQuery(a_list, f_list, m_list, offset, limit):
    a_list_str = ",".join(a_list)
    query = "select " + a_list_str
    for f in f_list:
        for m in m_list:
            query += ", " + f + "(" + m + ") as " + f + "_" + m 
    query += ", case when marital_status in " + married_list_string + " then 'Married' else 'Unmarried' end as maritalstatus from adults where "
    query += " is not null and ".join(a_list) + " is not null "
    query += "group by " + a_list_str + ", maritalstatus "
    query += "offset " + str(offset) + " limit " + str(limit)
    return query

def getFunctionValue(afm_result, result, a, a_value, f, m):
    if f != "avg":
        if f == "sum" or f == "count":
            return sum(afm_result)
        elif f == "max":
            return max(afm_result)
        else: # f == "min"
            return min(afm_result)
    # f == "avg"
    am_sum = sum(result[result[a] == a_value]["sum_"+m].tolist())
    am_count = sum(result[result[a] == a_value]["count_"+m].tolist())
    if am_count == 0:
        return 1e-10
    return am_sum/am_count

def getProbabilityDistribution(list):
    list_sum = sum(list)
    return [x/list_sum for x in list]

def getKLDivergence(result, married_result, unmarried_result, afm_combinations):
    kl_vals = defaultdict(list)
    for a,f,m in afm_combinations:
        attribute_values = result[a].unique()
        married_val_list, unmarried_val_list = [],[]
        for a_value in attribute_values:
            married_afm = married_result[married_result[a] == a_value][f+"_"+m].tolist()
            afm_value = 1e-10
            if len(married_afm) != 0:
                value = getFunctionValue(married_afm, married_result, a, a_value, f, m)
                if value != 0:
                    afm_value = value 
            married_val_list.append(afm_value)

            afm_value = 1e-10
            unmarried_afm = unmarried_result[unmarried_result[a] == a_value][f+"_"+m].tolist()
            if len(unmarried_afm) != 0:
                value = getFunctionValue(unmarried_afm, unmarried_result, a, a_value, f, m)
                if value != 0:
                    afm_value = value
            unmarried_val_list.append(afm_value)
            
        married_val_list = getProbabilityDistribution(married_val_list)
        unmarried_val_list = getProbabilityDistribution(unmarried_val_list)
        kl_utility_measure = entropy(married_val_list, unmarried_val_list)
        kl_vals[a,f,m] = kl_utility_measure
    return kl_vals

def getError(m, N, d):
    numerator = ((1-((m-1)/N))*(2*math.log(math.log(m)))) + (math.log(math.pi**2/(3*d)))
    denominator = 2*m
    return math.sqrt(numerator/denominator)

kl_values_list = defaultdict(list)
kl_intervals = defaultdict(dict)
for iteration in range(partitions):
    query = createOptimizedQuery(a_list, f_list, m_list, iteration * batch_size, batch_size)
    cursor.execute(query)
    head = [desc[0] for desc in cursor.description]
    result = pd.DataFrame(cursor.fetchall(), columns=head)
    married_result = result[result["maritalstatus"] == "Married"]
    unmarried_result = result[result["maritalstatus"] == "Unmarried"]
    batch_kl_values = getKLDivergence(result, married_result, unmarried_result, afm_combinations)
    
    lower_bounds = []
    for key, value in batch_kl_values.items():
        kl_values_list[key].append(value)
        if iteration > 0:
            mean = sum(kl_values_list[key])/len(kl_values_list[key])
            kl_intervals[key]['mean'] = mean
            error_margin = getError(len(kl_values_list[key]), partitions, delta)
            kl_intervals[key]['lower_bound'] = mean - error_margin
            kl_intervals[key]['upper_bound'] = mean + error_margin
            lower_bounds.append(mean - error_margin)
    
    if iteration > 0:
        top_k_lower_bound = sorted(lower_bounds, reverse=True)[k-1]
        for key in batch_kl_values.keys():
            if kl_intervals[key]['upper_bound'] < top_k_lower_bound:
                kl_intervals.pop(key)
                afm_combinations.remove(key)
    # print(len(afm_combinations))

kl_final_values = defaultdict(list)
for key, value in kl_intervals.items():
    kl_final_values[key] = value['mean']

top_k_kl_values = dict(sorted(kl_final_values.items(), key=lambda item: item[1], reverse=True)[:k])
print(top_k_kl_values)

for a,f,m in top_k_kl_values.keys():
    query = "select " + a + ", " + f + "(" + m + "), case when marital_status in " + married_list_string + " then 'Married' else 'Unmarried' end as maritalstatus from adults where " + a + " is not null group by " + a + ", maritalstatus"
    cursor.execute(query)
    head = [desc[0] for desc in cursor.description]
    result = pd.DataFrame(cursor.fetchall(), columns=head)
    pivot_table = result.pivot(index=a, columns='maritalstatus', values=f)
    pivot_table = pivot_table.apply(pd.to_numeric)
    pivot_table.plot(kind='bar', stacked=False)
    plot.ylabel(f + "(" + m + ")")
    plot.xlabel(a)
    plot.title("Plot showing " + f + "(" + m + ") by " + a + " and Marital Status")
    plot.tight_layout()
    plot.show()