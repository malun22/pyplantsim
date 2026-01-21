//
// Returns a json with the collected call cycles
param maxNumCycles:integer := -1 -> string

if maxNumCycles = -1
    return to_str(getProfileCallCycles())
end

return to_str(getProfileCallCycles(maxNumCycles))