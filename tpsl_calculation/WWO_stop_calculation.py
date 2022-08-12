from itertools import groupby
from operator import itemgetter

from joblib.numpy_pickle_utils import xrange


def WWO_combinations_generator(Wlows, WOlows, priceActionData, openTimeDT,
                               TPtimeRanges, openPrice, lows, peaks, WpeaksValueIndex):
    WWO = Wlows + WOlows
    WWO.sort()
    WWO_string = []
    stopTime = []
    if WWO is not None:
        for el in WWO:
            if el in Wlows:
                WWO_string.append("W")
            elif el in WOlows:
                WWO_string.append("WO")  # list with positions of lows in trade in order (marked as W or WO)
    WWO_group = [list(g) for k, g in groupby(WWO_string)]  # group by same elements into lists in overall lows list
    if len(WWO_group) <= 2:  # if WWO_group matches the simple structure of calculation in match case
        stop, time = match_structure(WWO_group, Wlows, WOlows,
                                     priceActionData, openPrice, openTimeDT, WpeaksValueIndex)

        if stop != -1 and time != -1:
            stopTime.append([stop, time])

    elif len(WWO_group) > 2:
        # if WWO_group has more than 2 elements,  we should find all possible combinations of inner parts
        combinations_final_WWO = multiComb(WWO_group)  # function that generates variations
        for el in combinations_final_WWO:
            for ele in el:
                stop, time = match_structure(ele, Wlows, WOlows,
                                             priceActionData, openPrice, openTimeDT, WpeaksValueIndex)
                if stop != -1 and time != -1:
                    stopTime.append([stop, time])
    return stopTime


def match_structure(WWO_group, Wlows, WOlows, priceActionData, openPrice, openTimeDT, WpeaksValueIndex):
    stop = -1
    time = -1
    indexList = getStopIndex(WWO_group, Wlows, WOlows)
    valueTime = getStopValueTime(indexList, priceActionData, openPrice, openTimeDT)
    match WWO_group:
        case []:  # [1]
            return stop, time
        case [["W"]]:  # one W  [2]
            stop = valueTime[0][0][0] + 0.1 * valueTime[0][0][0]
            time = valueTime[0][0][1]
            return round(stop, 3), time

        case [["WO"]]:  # one WO  [3]
            stop = valueTime[0][0][0] - 0.2 * valueTime[0][0][0]
            time = valueTime[0][0][1]
            return round(stop, 3), time

        case [mW] if all(ele == "W" for ele in mW if len(mW) > 1):  # mult W  [4]
            stop, time = peakValueRatioMultW(valueTime[0], WpeaksValueIndex, indexList)
            stop = stop - 0.2 * stop
            return round(stop, 3), time

        case [mWO] if all(ele == "WO" for ele in mWO if len(mWO) > 1):  # mult WO  [5]
            stop, time = multiWOalgo(valueTime)
            return round(stop, 3), time

        case [["WO"], ["W"]]:  # one WO one W  [A]
            stop, time = WOthenWalgo(valueTime, priceActionData, indexList, openTimeDT)
            return round(stop, 3), time

        case [["WO"], mW] if all(ele == "W" for ele in mW if len(mW) > 1):  # one WO mult W [B]
            indexList = getStopIndex(mW, Wlows, WOlows)
            valueTime = getStopValueTime(indexList, priceActionData, openPrice, openTimeDT)
            stop, time = peakValueRatioMultW(valueTime[0], WpeaksValueIndex, indexList)

            valueTime = getStopValueTime(getStopIndex([["WO"]], Wlows, WOlows), priceActionData, openPrice, openTimeDT)
            valueTime = [valueTime[0], [[stop, time]]]
            indexList = getStopIndex([["WO"], mW], Wlows, WOlows)
            stop, time = WOthenWalgo(valueTime, priceActionData, indexList, openTimeDT)
            return round(stop, 3), time

        case [mWO, ["W"]] if all(ele == "WO" for ele in mWO if len(mWO) > 1):  # mult WO one W [C]
            stop, time = WOthenWalgo([[multiWOalgo([valueTime[0]])], valueTime[1]],
                                     priceActionData, indexList, openTimeDT)
            return round(stop, 3), time

        case [mWO, mW] if all(ele == "WO" for ele in mWO if len(mWO) > 1) and \
                          all(ele == "W" for ele in mW if len(mW) > 1) \
                          and len(mW) > 1 and len(mWO) > 1:  # mult WO mult W [D] 4 - C
            indexList = getStopIndex([mW], Wlows, WOlows)
            valueTime = getStopValueTime(indexList, priceActionData, openPrice, openTimeDT)
            stop, time = peakValueRatioMultW(valueTime[0], WpeaksValueIndex, indexList)
            valueTime = getStopValueTime(getStopIndex([mWO], Wlows, WOlows), priceActionData, openPrice, openTimeDT)
            indexList = getStopIndex([mWO, mW], Wlows, WOlows)
            stop, time = WOthenWalgo([multiWOalgo(valueTime), [stop, time]], priceActionData, indexList, openTimeDT)
            return round(stop, 3), time

        case [["W"], ["WO"]]:  # one W one WO  [E]
            stop, time = WthenWOalgo(valueTime, priceActionData, indexList, openTimeDT)
            return round(stop, 3), time

        case [["W"], mWO] if all(ele == "WO" for ele in mWO if len(mWO) > 1):  # one W mult WO [F]
            valueTime = [[valueTime[0][0]], [multiWOalgo([valueTime[1]])]]
            stop, time = WthenWOalgo(valueTime, priceActionData, indexList, openTimeDT)
            return round(stop, 3), time

        case [mW, ["WO"]] if all(ele == "W" for ele in mW if len(mW) > 1):  # mult W one WO [G]
            valueTime = [[peakValueRatioMultW(valueTime[0], WpeaksValueIndex, indexList)], valueTime[1]]
            stop, time = WthenWOalgo(valueTime, priceActionData, indexList, openTimeDT)
            return round(stop, 3), time

        case [mW, mWO] if all(ele == "W" for ele in mW if len(mW) > 1) and \
                          all(ele == "WO" for ele in mWO if len(mWO) > 1):  # mult W mult WO [H]
            valueTime = [[peakValueRatioMultW(valueTime[0], WpeaksValueIndex, indexList)],
                         [multiWOalgo([valueTime[1]])]]
            stop, time = WthenWOalgo(valueTime, priceActionData, indexList, openTimeDT)
            return round(stop, 3), time


def multiWOalgo(valueTime):
    lowestStop = max(valueTime[0], key=lambda x: x[0])
    stop = lowestStop[0] - 0.2 * lowestStop[0]
    time = lowestStop[1]
    return stop, time


def WthenWOalgo(valueTime, priceActionData, indexList, openTimeDT):
    WvalueTime = valueTime[0][0]
    WOvalueTime = valueTime[1][0]
    stop = -1
    time = -1
    if WvalueTime[0] > WOvalueTime[0]:
        stop = (WvalueTime[0] + WOvalueTime[0]) / 2
        stopAbs = (float(priceActionData[indexList[0][0]][0]) + float(priceActionData[indexList[1][0]][0])) / 2
        closestVal = min(priceActionData, key=lambda x: abs(float(x[0]) - stopAbs))
        indexClosest = priceActionData.index(closestVal)
        time = (priceActionData[indexClosest][1] - openTimeDT).total_seconds()
    elif WvalueTime[0] < WOvalueTime[0]:
        stop = WvalueTime[0] + 0.1 * WvalueTime[0]
        time = WvalueTime[1]
    return stop, time


def WOthenWalgo(valueTime, priceActionData, indexList, openTimeDT):
    if len(valueTime[0]) == 1 and len(valueTime[1]) == 1:
        valueTime = [valueTime[0][0], valueTime[1][0]]
    stop = -1
    if valueTime[0][0] < valueTime[1][0]:
        stop = (valueTime[0][0] + valueTime[1][0]) / 2
        stopAbs = (float(priceActionData[indexList[0][0]][0]) + float(priceActionData[indexList[1][0]][0])) / 2
        closestVal = min(priceActionData, key=lambda x: abs(float(x[0]) - stopAbs))
        indexClosest = priceActionData.index(closestVal)
        time = (priceActionData[indexClosest][1] - openTimeDT).total_seconds()
    elif valueTime[0][0] >= valueTime[1][0]:
        stop = valueTime[1][0] + 0.1 * valueTime[1][0]
        time = valueTime[1][1]
    return stop, time


def getStopIndex(WWO_group, Wlows, WOlows):
    stopIndex = []
    Windex = 0
    WOindex = 0
    for el in WWO_group:
        stopIndexLocal = []
        for ele in el:
            if ele == "W":
                stopIndexLocal.append(Wlows[Windex])
                Windex += 1
            elif ele == "WO":
                stopIndexLocal.append(WOlows[WOindex])
                WOindex += 1
        stopIndex.append(stopIndexLocal)
    return stopIndex


def getStopValueTime(stopIndex, priceActionData, openPrice, openTimeDT):
    valueTimeList = []
    for el in stopIndex:
        valueTimeListLocal = []
        for ele in el:
            value = round(((float(priceActionData[ele][0]) - float(openPrice)) / float(openPrice) * 100), 3)
            time = (priceActionData[ele][1] - openTimeDT).total_seconds()
            valueTimeListLocal.append([value, time])
        valueTimeList.append(valueTimeListLocal)
    return valueTimeList


def peakValueRatioMultW(valueTime, WpeaksValueIndex, indexList):
    ratioList = []
    i = 0
    for el in valueTime:
        stopVal = el[0]
        peakVal = WpeaksValueIndex[indexList[0][i]]
        i = i + 1
        peakStopRatio = round(peakVal / -stopVal, 3)
        ratioList.append(peakStopRatio)
    maxIndex = ratioList.index(max(ratioList))
    stop = valueTime[maxIndex][0]
    time = valueTime[maxIndex][1]
    return stop, time


def multiComb(WWO_group):
    result = [WWO_group[i:j] for i in xrange(len(WWO_group)) for j in xrange(i + 1, len(WWO_group) + 1)]
    # all possible groups of elements in sequence of more than two lists, elements in groups should be neighbours, and
    # in sum must be the same as given WWO_group
    WWO_slices = [el for el in result if 0 < len(el) <= 2]
    # cut off variations which are empty or bigger than two (can't be put into match case )
    combinations_long_WWO = []
    for el in WWO_slices:
        for ele in WWO_slices:
            if ele != el:
                if el + ele == WWO_group:
                    combinations_long_WWO.append([el, ele])

    combinations_final_WWO = sort_and_deduplicate(combinations_long_WWO)  # remuve duplicate variations
    return combinations_final_WWO


def uniq(lst):
    last = object()
    for item in lst:
        if item == last:
            continue
        yield item
        last = item


def sort_and_deduplicate(l):
    return list(uniq(l))
