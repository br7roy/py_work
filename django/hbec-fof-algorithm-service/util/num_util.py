from decimal import Decimal

from numpy import float64


def transformFloatIfAvaliable(arg):
    if type(arg) == float or type(arg) == int:
        return str(Decimal.from_float(arg).quantize(Decimal('0.000000')))
    else:
        return arg


def transformFloatIfAvaliable2(arg):
    if type(arg) == float or type(arg) == int:
        return str(Decimal.from_float(arg).quantize(Decimal('0.0')))
    else:
        return arg


def transformFloatIfAvaliable3(arg):
    if type(arg) == float:
        return str(Decimal.from_float(arg).quantize(Decimal('0.000000')))
    else:
        return arg

def transformFloatIfAvaliable4(arg):
    if type(arg) == float or type(arg) == float64:
        return str(Decimal.from_float(arg).quantize(Decimal('0.000000')))
    else:
        return arg

def transformString2Decimal(arg):
    return Decimal(arg) if type(arg) == str else None
