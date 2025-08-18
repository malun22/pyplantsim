//
// Installs an error handler in the given model network
// Returns, if the operation was succesful
param model_path:string -> boolean

// Check if the network exists
if not existsObject(model_path)
    return false
end
var model:object := str_to_obj(model_path)

// Check if there already is an error handler
if existsMethod(to_str(model, ".ErrorHandler"))
    return false
end

// Create the error handler
if not model.createAttr("ErrorHandler", "method")
    return false
end

// Set the code
model.&ErrorHandler.program := "param byref error: string,\
    method_path: string,\
    line_number: integer\
\
error := \"\"\
\
var errorPayload:json := { \"method_path\": method_path, \"line_number\": line_number }\
var message:json := { \"status\": \"error\", \"error\" : errorPayload }\
fireSimTalkMessage(message.asString())"

return true