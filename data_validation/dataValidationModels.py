from datetime import datetime

from pydantic import BaseModel, Field, validator, root_validator
from decimal import Decimal


class KlineData(BaseModel):
    klinevalue: float = Field(..., gt=0)
    klinevaluetime: int

    # @root_validator
    # def ifNull(cls, values):
    #     price, time = values.get('klinevalue')
    #     if price < 0:
    #         raise ValueError('price is lower than zero')
    #     if time < 0:
    #         raise ValueError('time is wrong')
    #    return values

    # @root_validator
    # def timeIsRight(cls, values):
    #     buy, close = values.get('klinevaluetimebuy'), values.get('klinevaluetimeclose')
    #     if int(datetime.timestamp(buy) * 1000) > int(datetime.timestamp(close) * 1000):
    #         raise ValueError('buy is after close')
    #     if int(datetime.timestamp(buy) * 1000) < 2e10 or int(datetime.timestamp(close) * 1000) < 2e10:
    #         raise ValueError('dates are wrong')
    #     return values




