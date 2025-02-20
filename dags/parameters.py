# Validation functions
validation_functions = {
    "notEmpty" : lambda x: isinstance(x, str) and bool(x.strip()),
    "notNull"  : lambda x: x is not None,
    "isInteger": lambda x: isinstance(x, int),
    "positive" : lambda x: isinstance(x, int) and x > 0
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

# Metadata JSON
metadata = {
    "dataflows": [
        {
            "name": "prueba-acceso",
            "sources": [
                {
                    "name": "person_inputs",
                    "path": "/data/input/events/person/",
                    "format": "JSON"
                }
            ],
            "transformations": [
                {
                    "name": "validation",
                    "type": "validate_fields",
                    "params": {
                        "input": "person_inputs",
                        "validations": [
                            {
                                "field": "office",
                                "validations": ["notEmpty"]
                            },
                            {
                                "field": "age",
                                "validations": ["notNull"]
                            }
                        ]
                    }
                },
                {
                    "name": "ok_with_date",
                    "type": "add_fields",
                    "params": {
                        "input": "validation_ok",
                        "addFields": [
                            {
                                "name": "dt",
                                "function": "current_timestamp"
                            }
                        ]
                    }
                }
            ],
            "sinks": [
                {
                    "input": "ok_with_date",
                    "name": "raw-ok",
                    "paths": [
                        "/data/output/events/person"
                    ],
                    "format": "JSON",
                    "saveMode": "OVERWRITE"
                },
                {
                    "input": "validation_ko",
                    "name": "raw-ko",
                    "paths": [
                        "/data/output/discards/person"
                    ],
                    "format": "JSON",
                    "saveMode": "APPEND"
                }
            ]
        }
    ]
}

input = {"source": [
  {"name": "Xabier", "age": 39, "office": ""},
  {"name": "Miguel", "office": "RIO"},
  {"name": "Fran", "age": 31, "office": "RIO"}
]}