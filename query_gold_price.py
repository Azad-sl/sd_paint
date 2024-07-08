import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

# 黄金价格查询API的基础URL
GOLD_PRICE_API_URL = "https://api.pearktrue.cn/api/goldprice/"

@plugins.register(name="query_gold_price",
                  desc="查询黄金价格",
                  version="1.0",
                  author="azad",
                  desire_priority=100)
class query_gold_price(Plugin):

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = "发送【金价】获取最新的黄金价格以及详细信息"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.TEXT:
            return
        content = e_context["context"].content.strip()
        # 检查是否是金价查询的指令
        if content == "金价":
            logger.info(f"[{__class__.__name__}] 收到金价查询请求")
            reply = Reply()
            result = self.get_gold_price()
            if result:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取金价失败，请稍后再试。"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def get_gold_price(self):
        try:
            response = requests.get(url=GOLD_PRICE_API_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["code"] == 200:
                    formatted_output = f"最新黄金价格信息（更新时间：{data['time']}）：\n"
                    formatted_output += f"今日价格: {data['price']}\n"
                    # 添加各种黄金的详细信息
                    for item in data["data"]:
                        formatted_output += f"{item['title']} - 价格: {item['price']}, 涨跌幅: {item['changepercent']}, 最高价: {item['maxprice']}, 最低价: {item['minprice']}, 开盘价: {item['openingprice']}, 昨收价: {item['lastclosingprice']}\n"
                    return formatted_output.strip()
                else:
                    logger.error(f"API返回错误信息: {data['msg']}")
                    return None
            else:
                logger.error(f"接口返回值异常: 状态码 {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"接口异常：{e}")
            return None
