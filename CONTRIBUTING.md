## Process of working
1. Create an issue, following the rules from the "issues" section below
2. Assign the issue to a team member and milestone (week number)
3. Create a branch for that issue off of develop, following the rules from the "Branching" section below
4. Work on that branch for the specific issue created from
5. When the issue is finished, merge back into "develop"
6. Tell us you're done so we can merge "develop" into our own feature branches so we have the most up to date version
7. Repeat for next feature/issue

## Issues
- Name them however, just make sure they make sense based on what they are covering
- Each issue should cover a certain feature (Server, Landing Page, Products Page...)
- Tasks within issues are sections of a feature (Files created, pages created, server routes added...)
- Each issue should be added to the relevant Milestone for the week
- Make sure to move the issue along the relevant Board so it is obvious how far along development each feature is

## Branching
- Branch off of "develop" for each issue
- Branch should have a name relevant to the issue it relates to
- Merge back into "develop" when an issue is completed
- All testing to be done in "develop"
- Only branch back into "master" when all testing on current "develop" branch has been completed, or at the end of a  week (monday)
- DO NOT DELETE SOURCE BRANCHES - done by default, watch walkthrough from 16/03/21 for clarity on meaning

## Using atom's git integration
- To switch to a branch:
  - Must be done in Git Bash
  - Commands:
    - git fetch - fetches all new branches
    - git checkout BRANCH-NAME - switches to the branch with the name "BRANCH-NAME"
  - Atom should automatically switch to the specified branch
- Commiting changes:
  - Click the "git" button in the bottom left while in correct branch
  - Either click "Stage All", or only stage specific changes by right clicking each change and hit "stage"
  - Add a relevant commit message
  - Click "Commit"
  - Right click on the "Push" button, and click "Pull"
  - Then push by clicking "Push"

## When people will most likely be working on the project
- Josh:
  - Tuesday (During project hours)
  - Thursday (Afternoons)
  - Friday (During project hours)
- Tino:
  - Monday (Project hours)
  - Tuesday (Project hours)
  - Friday (Project hours)
- Mohammad:
  - Monday (Project hours)
  - Tuesday (Project hours)
  - Thursday (Mornings)
  - Friday (Project hours)
- Mazin:
  - Monday (Project hours)
  - Tuesday (Project hours)
  - Wednesday (Afternoon)
  - Sunday (Mornings)
