from datetime import datetime

from pydantic import BaseModel, Field, validator, root_validator
from decimal import Decimal


class KlineData(BaseModel):
    klinevaluehigh: float = Field(..., gt=0)
    klinevaluelow: float = Field(..., gt=0)
    klinevaluetimebuy: datetime
    klinevaluetimeclose: datetime

    @root_validator
    def ifNull(cls, values):
        high, low = values.get('klinevaluehigh'), values.get('klinevaluelow')
        if high < 0:
            raise ValueError('high is lower than zero')
        if low < 0:
            raise ValueError('low is lower than zero')
        return values

    @root_validator
    def timeIsRight(cls, values):
        buy, close = values.get('klinevaluetimebuy'), values.get('klinevaluetimeclose')
        if int(datetime.timestamp(buy) * 1000) > int(datetime.timestamp(close) * 1000):
            raise ValueError('buy is after close')
        if int(datetime.timestamp(buy) * 1000) < 2e10 or int(datetime.timestamp(close) * 1000) < 2e10:
            raise ValueError('dates are wrong')
        return values




