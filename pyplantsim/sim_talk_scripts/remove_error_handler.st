//
// Removes the installed error handler in the model file under basis.ErrorHandler
// Returns, if the operation was succesful
-> boolean

// Check if the network exists
if not existsObject(".ErrorHandler")
    return false
end

if not .&ErrorHandler.deleteObject()
    return false
end

setErrorHandler(void)

return true