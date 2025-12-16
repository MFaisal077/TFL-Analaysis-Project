import pandas as pd
from csv_trimming import CSVTrimmer

# Load your csv
csv = pd.read_csv(r"data_raw\2012.csv")
# Instantiate the trimmer
trimmer = CSVTrimmer()
# And trim it
trimmed_csv = trimmer.trim(csv)
trimmed_csv=trimmed_csv.dropna()
# That's it!

print(trimmed_csv)