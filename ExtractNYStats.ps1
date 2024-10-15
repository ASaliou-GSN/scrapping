$eventCode = 'm2023'
$newYorkStatsFileName = "NewYorkStats-$eventCode.csv"
$newYorkStatsSplitTimesFileName = "NewYorkStatsSplitTimes-$eventCode.csv"
$eventRunnerUri = 'https://rmsprodapi.nyrr.org/api/v2/runners/eventRunner'
$resultDetailsUri = 'https://rmsprodapi.nyrr.org/api/v2/runners/resultDetails'

$finishers = $finishersDetails = @()
$maxRunners = 300
$firstBibNumber = 1
$lastBibNumber = $firstBibNumber + $maxRunners
$bibNumbers = $firstBibNumber..$lastBibNumber

$headers = @{'Content-Type' = 'application/json;charset=utf-8' }
$eventRunnerBody = @{
    'eventCode' = $eventCode
    'bib'       = ''
}
$eventRunnerParameters = @{
    Method  = 'Post'
    Uri     = $eventRunnerUri
    Body    = $null
    Headers = $headers
}

$resultDetailsBody = @{
    'runnerId' = ''
}
$resultDetailsParameters = @{
    Method  = 'Post'
    Uri     = $resultDetailsUri
    Body    = $null
    Headers = $headers
}

Write-Host -ForegroundColor Green ('{0} - START OF EXTRACTION FROM BIB {1} TO BIB {2}' -f (Get-Date -Format 'HH:mm:ss'), $firstBibNumber, $lastBibNumber)

foreach ($bib in $bibNumbers) {
    if ($bib % 200 -eq 1) {
        Write-Host -ForegroundColor Green ('{0} - Bib number {1}..' -f (Get-Date -Format 'HH:mm:ss'), $bib)
        $finishers | Export-Csv -Path $newYorkStatsFileName -Append -Encoding UTF8 -Delimiter ';' -NoTypeInformation
        $finishersDetails | Export-Csv -Path $newYorkStatsSplitTimesFileName -Append -Encoding UTF8 -Delimiter ';' -NoTypeInformation
        $finishers = $finishersDetails = @()
    }
    $eventRunnerBody.bib = $bib
    $eventRunnerParameters.Body = $eventRunnerBody | ConvertTo-Json
    try {
        $finisher = (Invoke-RestMethod @eventRunnerParameters).finisher
        if ($finisher) {
            $finishers += $finisher
            $resultDetailsBody.runnerId = $finisher.runnerId
            $resultDetailsParameters.Body = $resultDetailsBody | ConvertTo-Json
            $finisherDetails = (Invoke-RestMethod @resultDetailsParameters).details.splitResults
            if ($finisherDetails) {
                $finisherDetails | Add-Member -Type NoteProperty -Name 'runnerId' -Value $finisher.runnerId
                $finishersDetails += $finisherDetails
            }
            else {
                Write-Host -ForegroundColor Yellow "No split times for bib $bib"
            }
        }
        else {
            Write-Host -ForegroundColor Yellow "No stats for bib $bib"
        }
        Start-Sleep -Milliseconds 100
    }
    catch {
        if ($_ -like '*Just a moment..*') {
            Write-Host -ForegroundColor Yellow "Just a moment to retrieve bib $bib.."
            Start-Sleep -Milliseconds 500
            # To avoid bib duplicates in cas of retry
            if ($finisher.bib -ne $bib) {
                $finisher = (Invoke-RestMethod @eventRunnerParameters).finisher
            }
            if ($finisher) {
                $finishers += $finisher
                $resultDetailsBody.runnerId = $finisher.runnerId
                $resultDetailsParameters.Body = $resultDetailsBody | ConvertTo-Json
                $finisherDetails = (Invoke-RestMethod @resultDetailsParameters).details.splitResults
                if ($finisherDetails) {
                    $finisherDetails | ForEach-Object {
                        $finishersDetails += $_ | Add-Member -Type NoteProperty -Name 'runnerId' -Value $finisher.runnerId
                    }
                }
                else {
                    Write-Host -ForegroundColor Red "No split times for bib $bib"
                }
            }
        }
        else {
            Write-Host -ForegroundColor Red "An error occurred when retrieving bib '$bib' => $_"
        }
    }
}

$finishers | Export-Csv -Path $newYorkStatsFileName -Append -Encoding UTF8 -Delimiter ';' -NoTypeInformation
$finishersDetails | Export-Csv -Path $newYorkStatsSplitTimesFileName -Append -Encoding UTF8 -Delimiter ';' -NoTypeInformation

Write-Host -ForegroundColor Green ('{0} - THE END!' -f (Get-Date -Format 'HH:mm:ss'))