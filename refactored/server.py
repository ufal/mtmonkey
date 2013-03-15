
def validate(task):
    schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "userId": {"type": "string", "required": False},
            "sourceLang": {"type": "string"},
            "targetLang": {"type": "string"},
            "text": {"type": "string"},
            "nBestSize": {"type": "integer", "required": False},
            "alignmentInfo": {"type": "string", "required": False},
            "docType": {"type": "string", "required": False},
            "profileType": {"type": "string", "required": False},
        },
    }
    validictory.validate(task, schema)
