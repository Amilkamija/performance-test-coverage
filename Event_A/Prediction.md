Event A prediction before execution 

Held-out project: HdrHistogram, selected from the original replication package and excluded from our four-project M2 sample (byte-buddy, fastjson, commons-bcel and SquidLib). 

Held-out dataset: We will use the HdrHistogram input data from the replication package frozen at PRE_EVENT_A (commit 3eaaedb). The dataset contains 780 Java methods, 12 JMH benchmarks and 570 JUnit tests. The exact original HdrHistogram source-code version could not be identified from the available metadata or data-collection scripts, so the frozen repository snapshot will identify our dataset. 

Reason for selection: HdrHistogram is a specialised Java performance-measurement library with different structural characteristics and functionality from our M2 projects. It was not included in our four-project bounded reproduction. 

Prediction: We predict that the original coverage and overlap analysis method will transfer to HdrHistogram and reproduce the supplied results without changing the original calculation rules. We expect the coverage percentages and overlap ratios to differ from our M2 projects due to differences in project structure and testing behaviour. 

Method: We will apply the same four Python analysis scripts and coverage/overlap measurement rules used during M2, without changing the calculations or retuning the method after viewing the results. 

What would challenge our M2 conclusion: Our conclusion would be challenged if the unchanged method failed to reproduce the supplied results, produced inconsistent coverage or overlap calculations, or required changes to the measurement rules. Different coverage percentages alone would not indicate failure, as different Java projects are expected to have different testing characteristics. 
