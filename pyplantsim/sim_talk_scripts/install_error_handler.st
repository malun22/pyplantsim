//
// Installs an error handler in the model file under basis.ErrorHandler
// Returns, if the operation was succesful
-> boolean

var errorHandlerProgram:string := "param byref error: string,\
    method_path: string,\
    line_number: integer\
\
error := \"\"\
\
var errorPayload:json\
var message:json\
errorPayload[\"method_path\"] := method_path\
errorPayload[\"line_number\"] := line_number\
message[\"status\"] := \"error\"\
message[\"error\"] := errorPayload\
\
fireSimTalkMessage(message.asString())"

// Check if the network exists
if existsObject(".ErrorHandler")
	return .ErrorHandler.program = errorHandlerProgram
end

// Search for a method in the file
var folders:object[] := [basis]
var method:object
while folders.dim > 0
	var parent:object := folders.pop()

	for var i := 1 to parent.NumNodes
		var node:object := parent.node(i)

		if node.InternalClassType = "Method" and not node.encrypted
			method := node
			exitloop 2
		elseif node.InternalClassType = "Folder"
			folders.append(node)
		end
	next
end

if not isObject(method)
	return false
end

var errorHandler:object := method.duplicate(basis, "ErrorHandler")

// Set the code
errorHandler.program := errorHandlerProgram

setErrorHandler(errorHandler)

return true