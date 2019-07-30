class OfflineTaskModel:
    def __init__(self, taskModel, func, request, uuid, extVal=None, taskType="0"):
        super().__init__()
        self.taskModel = taskModel
        self.taskType = taskType
        self.func = func
        self.request = request
        self.uuid = uuid
        self.extVal = extVal
        self.otherIndexName = None


class OnlineTaskModel:
    def __init__(self, indicators, fundCodes, startDate, endDate):
        self.indicators = indicators
        self.fundCodes = fundCodes
        self.startDate = startDate
        self.endDate = endDate
