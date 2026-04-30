New-Item -ItemType Directory -Force -Path .manuals | Out-Null

$body = @{
  utilName = ''
  requestPage = 1
  startDate = $null
  endDate = $null
  pageMin = $null
  pageMax = $null
  totalPage = $null
  periodRange = 'day'
  pagePerCount = 100
  manual = $null
} | ConvertTo-Json

$list = Invoke-RestMethod `
  -Uri https://api.visitkorea.or.kr/use/useUtilExercises.do `
  -Method Post `
  -ContentType 'application/json;charset=UTF-8' `
  -Body $body

$list | ConvertTo-Json -Depth 5 | Set-Content -Path .manuals\useUtilExercises.json -Encoding UTF8

foreach ($item in $list) {
  if ($item.manual) {
    $fileName = ('{0:00}_{1}' -f [int]$item.exercisesNum, ($item.manual.Split('/')[-1]))
    $url = 'https://api.visitkorea.or.kr' + $item.manual
    Invoke-WebRequest -Uri $url -OutFile (Join-Path .manuals $fileName) -UseBasicParsing
  }
}

Get-ChildItem .manuals | Select-Object Name, Length
