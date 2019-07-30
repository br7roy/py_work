# import simplejson
# from django.test import TestCase
# import random
# from TestModel.models import Article, Reporter
# # Create your tests here.
#
#
#
#
# def start():
#     print('conflict')
#     val = random.sample('zyxwvutsrqponmlkjihgfedcba', 5)
#     print(val)
#     var = ''
#     for l in val:
#         var += l
#
# def m2():
#
#     res = Reporter.objects.all()
#
#
#
#
#
#
#
#
#
# res = Reporter.objects.all()
# print(res)
#
# if __name__ == '__main__':
#     err = {
#         'error_code': 222,
#         'code': 22,
#         'message': 'haha',
#     }
#     res = simplejson.dumps(err)
#     print(res)
#     m2()
#

if __name__ == '__main__':
    import os
    zoneinfo_root = '/usr/share/zoneinfo'
    if (os.path.exists(zoneinfo_root) and not
    os.path.exists(os.path.join(zoneinfo_root, *(self.TIME_ZONE.split('/'))))):
        raise ValueError("Incorrect timezone setting: %s" % self.TIME_ZONE)