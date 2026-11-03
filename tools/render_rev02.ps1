param([string]$InputPattern='manuscript/REV02/*.docx',[string]$OutputRoot='build/REV02/render',[switch]$RefreshFields)
$ErrorActionPreference='Stop'
$taskRoot=(Get-Location).Path
$renderRoot=[IO.Path]::GetFullPath((Join-Path $taskRoot $OutputRoot))
New-Item -ItemType Directory -Force -Path $renderRoot | Out-Null
$word=New-Object -ComObject Word.Application
$word.Visible=$false
$word.DisplayAlerts=0
try {
  foreach($item in (Get-ChildItem -Path $InputPattern -File)) {
    $pdfPath=Join-Path $renderRoot ($item.BaseName+'.pdf')
    $document=$null
    try {
      $document=$word.Documents.Open($item.FullName,$false,(-not $RefreshFields),$false)
      if($RefreshFields) {
        if(-not $item.FullName.StartsWith((Join-Path $taskRoot 'manuscript\REV02'),[StringComparison]::OrdinalIgnoreCase)){throw 'Field update is restricted to REV02.'}
        $document.Fields.Update() | Out-Null
        $document.Repaginate()
        $document.Save()
      }
      $document.ExportAsFixedFormat($pdfPath,17)
      Write-Output ($item.BaseName+' '+$document.ComputeStatistics(2))
    } finally {
      if($null -ne $document){$document.Close(0);[Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)|Out-Null}
    }
  }
} finally {$word.Quit();[Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)|Out-Null}
