from elasticsearch import Elasticsearch, helpers


class Esetl:
    es = Elasticsearch(hosts="http://probd03:9200/", http_auth=('abc', 'dataanalysis'))

    def update_customer(self, start=0, rows=1000):
        global stime, etime
        results = self.get_customer(start, rows)
        actions = []
        for result in results:
            id = str(result['_id'])
            # print("id is {}".format(id))
            # logger.debug('id is {} '.format(id))
            # tm = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                stime = result['_source']['stime']
                etime = int(stime) + 1
            except:
                stime = 0
                etime = 0

            try:
                mac = result['_source']['mac']
            except:
                mac = ''

            src = result['_source']

            action = {
                '_index': 'mactrace202005',
                '_type': 'title',
                '_id': result['_id'],
                '_source': {
                    'mac': str(src['mac'] if 'mac' in src.keys() else ''),
                    'other': str(src['other'] if 'other' in src.keys() else ''),
                    'source': str(src['source'] if 'source' in src.keys() else ''),
                    'servicecode': str(src['servicecode'] if 'servicecode' in src.keys() else ''),
                    'stime': str(stime),
                    'etime': str(etime),
                }
            }
            actions.append(action)
        if len(actions) > 0:
            success, msg = helpers.bulk(self.es, actions)
            return success, msg
        else:
            return "OK", "这一页没啥数据可更新"

    def get_customer(self, start=0, rows=1000):
        body = {
            "query": {
                "match_all": {}
            },
            "from": start * rows,
            "size": rows
        }
        results = self.es.search(index='mactrace202005_new', body=body)
        return results['hits']['hits']

    def get_count(self):
        body = {
            "query": {
                "match_all": {}
            }
        }
        result = self.es.count(index='mactrace202005_new', body=body)
        return result['count']


if __name__ == '__main__':
    etl = Esetl()
    # res = etl.get_customer(0, 100)
    # print(res)
    # # h=res['hits']['hits']
    # # print(h)
    cnt = etl.get_count()
    print(cnt)
    res = etl.update_customer(0, cnt)
