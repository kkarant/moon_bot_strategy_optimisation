from pydantic import BaseModel, Field, validator, root_validator


class EMA:
    typeFunc: str
    x: int
    y: int
    scale_x: str
    scale_y: str

    def __init__(self, typeFunc, x, y, scale_x, scale_y):
        self.typeFunc = typeFunc
        self.x = x  # first value in ema formula
        self.y = y  # second value in ema fromula
        self.scale_x = scale_x  # scale of x values s m h or " "
        self.scale_y = scale_y  # scale of start close values s m h " "

    @root_validator("typeFunc")
    def type_validator(self, tF):
        possible_tF = ["MIN", "MAX", "BTC", "MAvg"]
        if tF not in possible_tF:
            raise ValueError('typeFunc is wrong')
        return tF

    @root_validator("x", "y")
    def time_validator(self, x, y):
        if x <= 0 and y <= 0 or x <= y:
            raise ValueError('xy are wrong')
        return x, y

    @root_validator("scale_x", "scale_y")
    def scale_validator(self, sc_x, sc_y):
        # 1s...300s or 2m...90m or 1h...41h
        possible_scales = ["s", "m", "h", " "]
        if sc_x not in possible_scales and sc_y not in possible_scales:
            raise ValueError('scale is wrong')
        return sc_x, sc_y

    def EMA_real_range(self):
        match self.typeFunc:
            case "EMA":
                ...
            case "MIN":
                ...
            case "MAX":
                ...
            case "BTC":
                ...
            case "MAvg":
                ...
