import requests
class RequestsHandle():
    def visit(self,method,url,params=None, data=None, json=None,headers=None,**kwargs):
        res=requests.request(method,url, params=params, data=data, json=json,headers=headers, **kwargs)
        try:
            return res.json()
        except ValueError:
            print("响应数据不是json格式!")


if __name__=="__main__":
        res = RequestsHandle().visit("post",
                                 "http://120.78.128.25:8766/futureloan/member/recharge",
                                 json={"member_id": "909086","amount": "100"},
                                 headers={"X-Lemonban-Media-Type":"lemonban.v2","Authorization":"Bearer eyJhbGciOiJIUzUxMiJ9.eyJtZW1iZXJfaWQiOjkwOTA4NiwiZXhwIjoxNTgwMzY5NjkyfQ.AJeKECpWAo77aQ0-oLNFWTmojKYGtys7yYx3JCsGKSs_G9SOg2Z9bhs2EU8AvzYdiNo_mzKGT1URnezRDjF38g"})
        print(res)
        # print(res["data"]["token_info"]["token"])