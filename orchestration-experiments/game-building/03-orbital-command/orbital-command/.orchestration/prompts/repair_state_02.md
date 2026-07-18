Repair the supplied `src/state.js` and return the complete replacement JavaScript only.
Browser failure: initial `state.crew` values do not sum to
`data.world.crew_total`. Preserve the public namespace fix and all original state and
persistence requirements.

Create numeric assignments for exactly engineering, science, and operations. Distribute
the total deterministically: engineering gets floor(total/3), science gets
floor(total/3), and operations gets the remainder, so the sum is always exact. Validation
must require those three finite nonnegative integers and their exact total. No Markdown.
