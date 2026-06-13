param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Resolve-Path (Join-Path $ScriptDir "..")
$RunDate = Get-Date -Format "yyyy-MM-dd"
$RunTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$TestRoot = Join-Path $Root "_test-output\nvda-hybrid-test"
$Results = New-Object System.Collections.Generic.List[object]

function Add-Result {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Detail,
        [string]$Path = ""
    )

    $script:Results.Add([pscustomobject]@{
        name = $Name
        passed = $Passed
        detail = $Detail
        path = $Path
    }) | Out-Null
}

function Test-RequiredPath {
    param(
        [string]$Name,
        [string]$RelativePath,
        [string]$Kind = "Any"
    )

    $FullPath = Join-Path $Root $RelativePath
    $Exists = Test-Path -LiteralPath $FullPath

    if ($Exists -and $Kind -eq "File") {
        $Exists = (Get-Item -LiteralPath $FullPath).PSIsContainer -eq $false
    }

    if ($Exists -and $Kind -eq "Directory") {
        $Exists = (Get-Item -LiteralPath $FullPath).PSIsContainer -eq $true
    }

    Add-Result -Name $Name -Passed $Exists -Detail $RelativePath -Path $FullPath
}

function Test-FileContains {
    param(
        [string]$Name,
        [string]$RelativePath,
        [string[]]$Patterns
    )

    $FullPath = Join-Path $Root $RelativePath
    if (-not (Test-Path -LiteralPath $FullPath)) {
        Add-Result -Name $Name -Passed $false -Detail "Missing file: $RelativePath" -Path $FullPath
        return
    }

    $Content = Get-Content -LiteralPath $FullPath -Raw
    $Missing = @()
    foreach ($Pattern in $Patterns) {
        if ($Content -notmatch [regex]::Escape($Pattern)) {
            $Missing += $Pattern
        }
    }

    Add-Result `
        -Name $Name `
        -Passed ($Missing.Count -eq 0) `
        -Detail $(if ($Missing.Count -eq 0) { "Found required text" } else { "Missing: $($Missing -join ', ')" }) `
        -Path $FullPath
}

function New-TextFile {
    param(
        [string]$Path,
        [string]$Content
    )

    $Parent = Split-Path -Parent $Path
    New-Item -ItemType Directory -Force -Path $Parent | Out-Null
    Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

if ($Clean -and (Test-Path -LiteralPath $TestRoot)) {
    Remove-Item -LiteralPath $TestRoot -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $TestRoot | Out-Null

$RawCategories = @(
    "articles",
    "pdfs",
    "images",
    "audio",
    "video",
    "documents",
    "datasets",
    "github",
    "trading",
    "jobs",
    "research",
    "meetings",
    "ideas"
)

$ParaDirs = @(
    "05-knowledge\projects",
    "05-knowledge\areas",
    "05-knowledge\resources",
    "05-knowledge\archives"
)

$Skills = @(
    "auto-research",
    "braindump",
    "comprehensive-analysis",
    "create-user-story",
    "daily-brief",
    "export-open-issues",
    "generate-prd",
    "generate-release-notes",
    "knowledge-consolidation",
    "meeting-transcript",
    "onboarding",
    "publish-to-confluence",
    "scout",
    "team-brief",
    "update-cog",
    "update-knowledge-base",
    "url-dump",
    "weekly-checkin"
)

$HybridCommands = @(
    "raw-capture",
    "para-classify",
    "schema-compile",
    "raw-inbox-review"
)

Write-Host "Hybrid COG test run: $RunTime"
Write-Host "Root: $Root"
Write-Host "Financial fixture: NVDA"
Write-Host ""

Test-RequiredPath -Name "README exists" -RelativePath "README.md" -Kind "File"
Test-RequiredPath -Name "Hybrid guide exists" -RelativePath "docs\HYBRID-SECOND-BRAIN.md" -Kind "File"
Test-RequiredPath -Name "Raw README exists" -RelativePath "raw\README.md" -Kind "File"
Test-RequiredPath -Name "PARA guide exists" -RelativePath "05-knowledge\PARA.md" -Kind "File"
Test-RequiredPath -Name "Schema README exists" -RelativePath "05-knowledge\schema\README.md" -Kind "File"
Test-RequiredPath -Name "Schema relationships file exists" -RelativePath "05-knowledge\schema\relationships.md" -Kind "File"

foreach ($Category in $RawCategories) {
    Test-RequiredPath -Name "Raw category: $Category" -RelativePath "raw\$Category" -Kind "Directory"
}

foreach ($Dir in $ParaDirs) {
    Test-RequiredPath -Name "PARA directory: $Dir" -RelativePath $Dir -Kind "Directory"
}

Test-RequiredPath -Name "Schema concepts directory" -RelativePath "05-knowledge\schema\concepts" -Kind "Directory"
Test-RequiredPath -Name "Schema logs directory" -RelativePath "05-knowledge\schema\logs" -Kind "Directory"

foreach ($Skill in $Skills) {
    $SkillPath = ".claude\skills\$Skill\SKILL.md"
    Test-RequiredPath -Name "Skill file exists: $Skill" -RelativePath $SkillPath -Kind "File"
    Test-FileContains -Name "Skill has name marker: $Skill" -RelativePath $SkillPath -Patterns @("name: $Skill")
}

foreach ($Command in $HybridCommands) {
    $CommandPath = ".claude\commands\$Command.md"
    Test-RequiredPath -Name "Hybrid command exists: /$Command" -RelativePath $CommandPath -Kind "File"
    Test-FileContains -Name "Hybrid command documents trigger: /$Command" -RelativePath $CommandPath -Patterns @("/$Command")
}

Test-FileContains -Name "README is customized for Perry" -RelativePath "README.md" -Patterns @("Perry's Hybrid COG Second Brain")
Test-FileContains -Name "README documents NVDA workflow" -RelativePath "README.md" -Patterns @("Analyze NVDA", "Financial-Market Workflow")
Test-FileContains -Name "README documents raw-first rule" -RelativePath "README.md" -Patterns @("Raw first", "raw_sources")
Test-FileContains -Name "Hybrid guide documents schema compilation" -RelativePath "docs\HYBRID-SECOND-BRAIN.md" -Patterns @("Schema Compilation", "05-knowledge/schema")
Test-FileContains -Name "URL dump skill enforces raw capture" -RelativePath ".claude\skills\url-dump\SKILL.md" -Patterns @("Raw Capture First", "raw/articles")
Test-FileContains -Name "Auto research skill enforces raw sources" -RelativePath ".claude\skills\auto-research\SKILL.md" -Patterns @("Raw-First Research Rule", "raw_sources")
Test-FileContains -Name "Knowledge consolidation reads raw metadata" -RelativePath ".claude\skills\knowledge-consolidation\SKILL.md" -Patterns @("raw/**/metadata.md", "PARA")
Test-FileContains -Name "Generate PRD requires raw sources" -RelativePath ".claude\skills\generate-prd\SKILL.md" -Patterns @("Raw-First Requirement", "raw_sources")

$FixtureRawDir = Join-Path $TestRoot "raw\research\$RunDate-nvda-test"
$FixtureProcessedDir = Join-Path $TestRoot "05-knowledge\resources"
$FixtureSchemaDir = Join-Path $TestRoot "05-knowledge\schema"
$FixtureRawMetadata = Join-Path $FixtureRawDir "metadata.md"
$FixtureAnalysis = Join-Path $FixtureProcessedDir "nvda-market-analysis-test.md"
$FixtureRelationships = Join-Path $FixtureSchemaDir "relationships.md"
$FixtureConcept = Join-Path $FixtureSchemaDir "concepts\NVDA.md"

New-TextFile -Path $FixtureRawMetadata -Content @"
---
type: raw-source
category: research
captured: $RunTime
source_url: https://example.com/nvda-test-source
source_title: NVDA Test Source
source_author: Test Fixture
source_date: $RunDate
status: captured
processed_to:
  - 05-knowledge/resources/nvda-market-analysis-test.md
tags: [nvda, semiconductors, ai-infrastructure]
---

# Raw Capture: NVDA Test Source

## Why Saved

Test fixture for Perry's Hybrid COG Second Brain financial-market workflow.
"@

New-TextFile -Path $FixtureAnalysis -Content @"
---
type: market-analysis
symbol: NVDA
created: $RunTime
para:
  type: resource
  name: market-analysis
raw_sources:
  - raw/research/$RunDate-nvda-test/metadata.md
tags: [nvda, semiconductors, ai-infrastructure]
---

# NVDA Market Analysis Test

## Thesis

NVDA is used as the financial-market test fixture for raw capture, processed analysis, PARA classification, and schema compilation.

## Evidence

- Raw source metadata exists.
- Processed analysis links back to raw source metadata.
- Schema concepts and relationships can reference NVDA.

## Risks

This is a deterministic workflow test. It does not fetch live prices and is not investment advice.

## Invalidation

The test fails if raw metadata, processed note links, PARA metadata, or schema references are missing.
"@

New-TextFile -Path $FixtureRelationships -Content @"
# Relationships

- [[NVDA]] -- part_of --> [[AI Infrastructure]]
- [[NVDA]] -- related_to --> [[GPU Supply Chain]]
- [[Options Flow]] -- related_to --> [[NVDA]]
"@

New-TextFile -Path $FixtureConcept -Content @"
# Concept: NVDA

## Type

Company / market symbol

## Related

- [[AI Infrastructure]]
- [[GPU Supply Chain]]
- [[Options Flow]]
"@

Test-RequiredPath -Name "NVDA fixture raw metadata created" -RelativePath "_test-output\nvda-hybrid-test\raw\research\$RunDate-nvda-test\metadata.md" -Kind "File"
Test-RequiredPath -Name "NVDA fixture processed note created" -RelativePath "_test-output\nvda-hybrid-test\05-knowledge\resources\nvda-market-analysis-test.md" -Kind "File"
Test-RequiredPath -Name "NVDA fixture schema relationship created" -RelativePath "_test-output\nvda-hybrid-test\05-knowledge\schema\relationships.md" -Kind "File"
Test-RequiredPath -Name "NVDA fixture concept created" -RelativePath "_test-output\nvda-hybrid-test\05-knowledge\schema\concepts\NVDA.md" -Kind "File"

$RawText = Get-Content -LiteralPath $FixtureRawMetadata -Raw
$AnalysisText = Get-Content -LiteralPath $FixtureAnalysis -Raw
$RelationshipText = Get-Content -LiteralPath $FixtureRelationships -Raw

Add-Result -Name "NVDA raw metadata status captured" -Passed ($RawText -match "status:\s*captured") -Detail "metadata.md has captured status" -Path $FixtureRawMetadata
Add-Result -Name "NVDA raw metadata links processed output" -Passed ($RawText -match "processed_to:" -and $RawText -match "nvda-market-analysis-test.md") -Detail "metadata.md links to processed note" -Path $FixtureRawMetadata
Add-Result -Name "NVDA processed note has raw_sources" -Passed ($AnalysisText -match "raw_sources:" -and $AnalysisText -match "raw/research/$RunDate-nvda-test/metadata.md") -Detail "processed note links raw source" -Path $FixtureAnalysis
Add-Result -Name "NVDA processed note has PARA metadata" -Passed ($AnalysisText -match "para:" -and $AnalysisText -match "type:\s*resource") -Detail "processed note classified as resource" -Path $FixtureAnalysis
Add-Result -Name "NVDA schema relationships include market concepts" -Passed ($RelationshipText -match "\[\[NVDA\]\]" -and $RelationshipText -match "\[\[Options Flow\]\]") -Detail "relationships include NVDA and Options Flow" -Path $FixtureRelationships

$PassedCount = ($Results | Where-Object { $_.passed }).Count
$FailedCount = ($Results | Where-Object { -not $_.passed }).Count
$TotalCount = $Results.Count

$JsonPath = Join-Path $TestRoot "results.json"
$MarkdownPath = Join-Path $TestRoot "results.md"

$Summary = [pscustomobject]@{
    run_time = $RunTime
    root = $Root.Path
    fixture = "NVDA"
    total = $TotalCount
    passed = $PassedCount
    failed = $FailedCount
    results = $Results
}

$Summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $JsonPath -Encoding UTF8

$MarkdownLines = New-Object System.Collections.Generic.List[string]
$MarkdownLines.Add("# Hybrid COG Test Results") | Out-Null
$MarkdownLines.Add("") | Out-Null
$MarkdownLines.Add("- Run time: $RunTime") | Out-Null
$MarkdownLines.Add("- Fixture: NVDA") | Out-Null
$MarkdownLines.Add("- Total: $TotalCount") | Out-Null
$MarkdownLines.Add("- Passed: $PassedCount") | Out-Null
$MarkdownLines.Add("- Failed: $FailedCount") | Out-Null
$MarkdownLines.Add("") | Out-Null
$MarkdownLines.Add("| Result | Test | Detail |") | Out-Null
$MarkdownLines.Add("|---|---|---|") | Out-Null
foreach ($Result in $Results) {
    $Status = if ($Result.passed) { "PASS" } else { "FAIL" }
    $Detail = ($Result.detail -replace "\|", "/")
    $MarkdownLines.Add("| $Status | $($Result.name) | $Detail |") | Out-Null
}
$MarkdownLines | Set-Content -LiteralPath $MarkdownPath -Encoding UTF8

Write-Host "Results"
Write-Host "-------"
foreach ($Result in $Results) {
    $Status = if ($Result.passed) { "PASS" } else { "FAIL" }
    Write-Host ("[{0}] {1} - {2}" -f $Status, $Result.name, $Result.detail)
}

Write-Host ""
Write-Host "Summary"
Write-Host "-------"
Write-Host "Total:  $TotalCount"
Write-Host "Passed: $PassedCount"
Write-Host "Failed: $FailedCount"
Write-Host "JSON:   $JsonPath"
Write-Host "MD:     $MarkdownPath"

if ($FailedCount -gt 0) {
    exit 1
}

exit 0
