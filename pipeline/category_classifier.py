def classify(title):

    t = title.lower()

    if "result" in t:
        return "RESULT"
    if "exam" in t:
        return "EXAM"
    if "admission" in t:
        return "ADMISSION"

    return "GENERAL"
#@roshhellwett makaut tele bot