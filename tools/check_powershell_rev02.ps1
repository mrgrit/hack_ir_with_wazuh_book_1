# Parse only. Never invoke any manuscript input.
$taskRows=Get-Content examples/rev02/input-index.json -Raw | ConvertFrom-Json
$taskErrors=@()
$taskChecked=@()
foreach($row in $taskRows) {
    if($row.where -notlike '*PowerShell*'){continue}
    $parseTokens=$null
    $parseErrors=$null
    [System.Management.Automation.Language.Parser]::ParseInput($row.text,[ref]$parseTokens,[ref]$parseErrors) | Out-Null
    $taskChecked+= $row.id
    foreach($item in $parseErrors){$taskErrors+=@{id=$row.id;message=$item.Message}}
}
$report=@{checked=$taskChecked.Count;ids=@($taskChecked);errors=@($taskErrors);scope='PowerShell parse only; no commands executed'}
$report | ConvertTo-Json -Depth 8 | Set-Content editorial/REV02/powershell-syntax.json -Encoding utf8
Write-Output ('PowerShell: '+$taskChecked.Count+' checked; '+$taskErrors.Count+' errors')
if($taskErrors.Count){throw 'PowerShell syntax errors found'}
