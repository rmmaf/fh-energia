$csvFolderPath = "./data/estabelecimentos" # Replace with your folder path containing CSV files
$outputFile = "./data/estabelecimentos.csv" # Replace with your output file path

# Get all CSV files in the folder
$csvFiles = Get-ChildItem -Path $csvFolderPath -Filter *.csv

# Initialize an empty array to hold the content of all CSV files
$csvContent = @()

# Loop through each CSV file
foreach ($csvFile in $csvFiles) {
    # Get the content of the CSV file and add it to the array
    $csvContent += Get-Content $csvFile.FullName
}

# Write the content of the array to the output file
$csvContent | Set-Content -Path $outputFile
