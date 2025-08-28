//
// Checks if the path exists in the model
param path:string -> boolean

if existsObject(path)
	return true
end

if existsMethod(path)
	return true
end

if executeSilent(to_str("->boolean; ", path, "; return true"))
	return true
end

return false