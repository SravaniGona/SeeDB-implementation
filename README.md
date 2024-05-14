This project focuses on reproducing partial results from the research paper [SeeDB: efficient data-driven visualization recommendations to support visual analytics](https://dl.acm.org/doi/10.14778/2831360.2831371). In this paper the authors propose a SeeDB, a visualization recommendation engine to facilitate fast visual analysis. 
They proposed Sharing-based Optimizations to intelligently merge and batch queries, reducing the number of queries issued to the database and, in turn, minimizing the number of scans of the underlying data and Pruning-Based Optimizations to quickly identify high-utility visualizations we adopt a deviation based metric for visualization utility, while indicating how we may be able to generalize it to other factors influencing utility. We implemented the algorithm based on these Optimizations to find top-5 aggregate views on the [Census dataset](https://archive.ics.uci.edu/dataset/20/census+income).

The files 'adult.data' and 'adult.test' represent the training and testing instances of the Census dataset. 

Run the file 'adult.sql' to import and preprocess the data.

Run the file 'visualizations.py' to generate top-k interesting visualizations on this data.

Note: Refer to the [Project report](https://github.com/SravaniGona/SeeDB-implementation/blob/main/645%20Project%20Report.pdf) for more details about this project.
