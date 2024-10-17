import asyncio
import websockets
import json
import time
import requests

# 配置信息
start_time = 0  # 替换为你的开始时间戳
user_id = 0  # 替换为你的用户 ID
classid = 0
time = 1000 #替换为你想刷的时间
cookie = ""








headers = {
    "Origin": "https://www.yuketang.cn",
    "Cookie": cookie
    }

# WebSocket 连接函数
async def connect_to_ws(uri,headers):
    try:
        websocket = await websockets.connect(uri,extra_headers=headers)
        print(f"Connected to {uri}")
        print(await websocket.recv())
        return websocket
    except Exception as e:
        print(f"Error connecting to {uri}: {e}")
        return None

#get_cardsID函数
async def get_cardsID(headers):
    uri="https://www.yuketang.cn/v2/api/web/logs/learn/"+str(classid)+"?actype=-1&page=0&offset=20&sort=-1"
    response = requests.get(uri,headers=headers)
    json = response.json()
    json = json["data"]["activities"]
    cardsID=[]
    for i in json:
        if i["type"]==2:
            try: cardsID.append(i["courseware_id"])
            except: print("error")
    print(cardsID)
    return cardsID#返回cardsID列表
    

# 发送和接收消息的函数
async def send_and_receive_message(websocket, message):
    if websocket is not None:
        try:
            # 发送消息
            await websocket.send(message)  # 发送消息
            print(f"Sent: {message}")

            # 接收服务器的响应
            response = await websocket.recv()  # 接收消息
            print(f"Received: {response}")

        except websockets.ConnectionClosedError as e:
            print(f"Connection closed with error: {e}")
        except Exception as e:
            print(f"Error during message handling: {e}")
    else:
        print("WebSocket is not connected.")
    

#获取深度
async def get_depth(cardID):
    uri="https://www.yuketang.cn/v2/api/web/cards/view_depth?classroom_id="+str(classid)+"&cards_id="+str(cardID)
    response = requests.get(uri,headers=headers)
    depth = int(response.json()["data"]["depth"])
    return depth

#构造消息
async def build_message(cardID,start_time,user_id,depth):
    data = {
        "op": "view_record",
        "cardsID": cardID,
        "start_time": start_time,
        "data": [time]*depth,
        "user_id": user_id,
        "platform": "web",
        "type": "cache"
    }

    data1 = {
    "op": "view_record",
    "type": "page",
    "auto_page": True,
    "cardsID": cardID,
    "start_time": start_time,
    "user_id": user_id,
    "errmsg": "正确",
    "errno": 0,
    "ret": {
        "total": 89,
        "right": 0,
        "total_score": 0,
        "rank": None,
        "answered_count": 0,
        "score": 0,
        "done": False,
        "duration": 7145899979,
        "pages": [65, 66],
        "total_problem": 0
    }
    }


    # 将字典转为 JSON 字符串
    message = json.dumps(data)
    print(message)
    return message

# 主函数
async def main():
    id_list=await get_cardsID(headers)
    for cardID in id_list:
        uri = "wss://www.yuketang.cn/ws/"  # 替换为你的 WebSocket 服务器地址
        websocket = await connect_to_ws(uri,headers)  # 建立连接
        depth=await get_depth(cardID)
        message = await build_message(cardID,start_time,user_id,depth)
        #for i in range(depth):
        await send_and_receive_message(websocket, message)
        websocket.close()
        

    

# 运行事件循环
if __name__ == "__main__":
    asyncio.run(main())



