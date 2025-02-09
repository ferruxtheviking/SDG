# Validation functions
validation_functions = {
    "notEmpty": lambda x: isinstance(x, str) and bool(x.strip()),
    "notNull": lambda x: x is not None,
    "isInteger": lambda x: isinstance(x, int),
    "positive": lambda x: isinstance(x, int) and x > 0
}

# Output formats
formats = {
    'JSON': '.json',
    'TXT' : '.txt',
}

# Save Mode
savemode = {
    'OVERWRITE': 'w',
    'APPEND'   : 'a',
}
