# Define the path to the log file
$logPath = "C:\Users\Temidayo\Desktop\Test_Question\Script\log.txt"

# Check if the file exists
if (Test-Path $logPath) {
    # Try to delete the file
    try {
        Remove-Item -Path $logPath -Force
        Write-Output "The file $logPath has been successfully deleted."
    }
    catch {
        Write-Error "An error occurred while trying to delete the file: $_"
    }
}
else {
    Write-Output "The file $logPath does not exist."
}