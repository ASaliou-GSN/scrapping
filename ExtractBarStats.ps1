$eventId = '65edc070-2890-4c11-895c-ed17ac1f1b8c' # 2024
$statsFileName = "BarcelonaStats-2024.csv"
$statsSplitTimesFileName = "BarcelonaStatsSplitTimes-2024.csv"
$eventRunnerUri = "https://sportmaniacs.com/races/rankings/$eventId"

Write-Host -ForegroundColor Green ('{0} - START OF EXTRACTION' -f (Get-Date -Format 'HH:mm:ss'))

$rankings = (Invoke-RestMethod -Method Get -Uri $eventRunnerUri).data.Rankings | Select-Object -Property * -ExcludeProperty *image, *photos, *videos, *diploma, pos_*
$finishers = $finishersDetails = @()
Write-Host -ForegroundColor Green ('{0} - Found {1} finishers' -f (Get-Date -Format 'HH:mm:ss'), $rankings.Count)
foreach ($finisher in $rankings) {
    if ($finisher.pos % 1000 -eq 1) {
        Write-Host -ForegroundColor Green ('{0} - Finisher pos {1}..' -f (Get-Date -Format 'HH:mm:ss'), $finisher.pos)
        $finishers | Export-Csv -Path $statsFileName -Append -Encoding UTF8 -Delimiter ';' -NoTypeInformation
        $finishersDetails | Export-Csv -Path $statsSplitTimesFileName -Append -Encoding UTF8 -Delimiter ';' -NoTypeInformation
        $finishers = $finishersDetails = @()
    }
    $finishers += $finisher | Select-Object -Property * -ExcludeProperty points
    $finishersDetails += $finisher.points
}

$finishers | Export-Csv -Path $statsFileName -Append -Encoding UTF8 -Delimiter ';' -NoTypeInformation
$finishersDetails | Export-Csv -Path $statsSplitTimesFileName -Append -Encoding UTF8 -Delimiter ';' -NoTypeInformation

Write-Host -ForegroundColor Green ('{0} - THE END!' -f (Get-Date -Format 'HH:mm:ss'))