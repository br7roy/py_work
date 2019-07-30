from django.test import TestCase
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from hbase import Hbase
from thrift import Thrift
from hbase.ttypes import ColumnDescriptor, Mutation, BatchMutation, TRegionInfo
from hbase.ttypes import IOError, AlreadyExists


# Create your tests here.

def start():
    """
    建立连接
    """
    tIp = '10.0.30.160'
    tPort = 9090
    transport = TSocket.TSocket(tIp, tPort)

    transport = TTransport.TBufferedTransport(transport)

    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    client = Hbase.Client(protocol)

    transport.open()

    '''
    建表
    '''
    # cf1 = ColumnDescriptor(name='cf2:'.encode(), maxVersions=10)
    # cf2 = ColumnDescriptor(name='cf1:'.encode(), maxVersions=10)
    # client.createTable('fth_py_thrift_03'.encode(), [cf1,cf2])

    '''插入数据'''
    socket = TSocket.TSocket(tIp, tPort)
    # socket.setTimeout(5000)

    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    client = Hbase.Client(protocol)
    transport.open()

    mutation1 = [Mutation(column="cf1:name".encode(), value="tom".encode())]
    client.mutateRow('fth_py_thrift_03'.encode(), "row1".encode(), mutation1, None)

    mutation2 = [Mutation(column="cf1:age".encode(), value="10".encode())]
    client.mutateRow('fth_py_thrift_03'.encode(), "row1".encode(), mutation2, None)

    mutation1 = [Mutation(column="cf1:name".encode(), value="jerry".encode())]
    client.mutateRow("fth_py_thrift_03".encode(), "row2".encode(), mutation1, None)

    mutation2 = [Mutation(column="cf1:age".encode(), value="10".encode())]
    client.mutateRow('fth_py_thrift_03'.encode(), "row2".encode(), mutation2, None)

    mutation3 = [Mutation(column="cf2:city".encode(), value="shanghai".encode())]
    client.mutateRow('fth_py_thrift_03'.encode(), "row2".encode(), mutation3, None)

    # socket.close()

    '''
    查询
    '''
    res1 = client.getRow("fth_py_thrift_03".encode(), "row1".encode(), None)

    for r in res1:
        print('the rowname is ', r.row)
    print('the column family is ', res1[0].columns['cf1'].value)
    print('all below this line is qualifier========')
    for i in range(len(res1)):
        '''
        解决“tuple parameter unpacking is not supported in python3”
        '''
        print(dict(map(lambda k_v: (k_v[0], k_v[1].value), res1[i].columns.items())))

    '''
    scan查询
    '''
    scanId = client.scannerOpen('fth_py_thrift_03'.encode(), "".encode(), ["cf1".encode()], None)
    print('scanId:%s' % scanId)
    res2 = client.scannerGetList(scanId, 10)
    print('scanRes:%s' % res2)

    '''删除'''

    client.deleteAllRow("fth_py_thrift_03".encode(), "row1".encode(), None)

    '''
    关闭连接
    '''
    client.scannerClose(scanId)
    socket.close()


if __name__ == '__main__':
    start()
