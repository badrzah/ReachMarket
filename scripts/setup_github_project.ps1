# ReachGTM — create the Projects v2 board UNDER yousef4git and link it to the repo.
#
# WHO RUNS THIS: Yousef (the repo owner). A collaborator cannot create a project
# under a personal account, which is why this must be run by yousef4git.
#
# PREREQS (one time):
#   1. Install GitHub CLI:  winget install --id GitHub.cli   (or https://cli.github.com)
#   2. Log in AS YOURSELF with the project scope:
#        gh auth login --hostname github.com --git-protocol https --web --scopes "repo,project,read:org"
#      (Authorize the one-time code in the browser.)
#   3. Run this script:  pwsh ./scripts/setup_github_project.ps1
#
# WHAT IT DOES: creates (or reuses) the "ReachGTM Roadmap" board under yousef4git,
# links it to the repo's Projects tab, and adds every open issue. It does NOT create
# issues/labels/milestones — those already exist on the repo.

$ErrorActionPreference = 'Continue'
$repo  = 'yousef4git/ReachGTM'
$owner = 'yousef4git'
$title = 'ReachGTM Roadmap'

# --- sanity: correct account? ---
$me = (gh api user --jq '.login' 2>$null)
if ($LASTEXITCODE -ne 0) { Write-Error "Not logged in. Run: gh auth login ... --scopes 'repo,project,read:org'"; exit 1 }
if ($me -ne $owner) { Write-Warning "You are logged in as '$me', not '$owner'. The board will be created under '$owner' and that requires you to BE $owner." }

# --- create or reuse the project ---
$projNum = gh project list --owner $owner --format json --jq ".projects[] | select(.title==`"$title`") | .number" 2>$null | Select-Object -First 1
if ($projNum) {
  Write-Host "Reusing existing project #$projNum"
} else {
  $proj = gh project create --owner $owner --title $title --format json | ConvertFrom-Json
  if ($LASTEXITCODE -ne 0) { Write-Error "Failed to create project (do you have 'project' scope and own '$owner'?)"; exit 1 }
  $projNum = $proj.number
  Write-Host "Created project #$projNum -> $($proj.url)"
}

# --- link it to the repo's Projects tab ---
gh project link $projNum --owner $owner --repo $repo 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "Linked project #$projNum to $repo" } else { Write-Host "(link skipped or already linked)" }

# --- add every open issue ---
$urls = gh issue list --repo $repo --state open --limit 200 --json url --jq '.[].url'
Write-Host ("Adding {0} open issues..." -f $urls.Count)
$ok = 0; $fail = 0
foreach ($u in $urls) {
  if (-not $u) { continue }
  gh project item-add $projNum --owner $owner --url $u 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { $ok++ } else { $fail++ }
}
Write-Host "Done. Added $ok issue(s), $fail failed. Board: https://github.com/users/$owner/projects/$projNum"
Write-Host "Tip: in the board UI, group by 'Milestone' to see Week 1/2/3 + Backlog as columns."
