x = {
    "S2B_MSIL2A_20240820T100559_N0511_R022_T34VDH_20240820T130319.SAFE": {
        "title": "S2B_MSIL2A_20240820T100559_N0511_R022_T34VDH_20240820T130319.SAFE",
        "cloud": 1.04,
        "date": "20240820",
        "tile": "T34VDH",
    }
}

print(x)

for y in x.values():
    print(y["tile"])
    # print(value)
