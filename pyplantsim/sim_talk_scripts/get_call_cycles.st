//
// Returns a json with the collected call cycles
param maxNumCycles:integer := -1 -> json

if maxNumCycles = -1
    return getProfileCallCycles()
end

return getProfileCallCycles(maxNumCycles)