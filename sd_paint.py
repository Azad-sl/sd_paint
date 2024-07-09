import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

# 感谢pearAPI
ART_GENERATION_URL = "https://api.pearktrue.cn/api/stablediffusion/"

@plugins.register(name="sd_paint",
                  desc="stablediffusion生成图像",
                  version="1.0",
                  author="azad",
                  desire_priority=100)
class sd_paint(Plugin):

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = "发送【sd绘画 对应的绘画prompt】生成图像"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        content = e_context["context"].content.strip()

        # 检查是否是绘画生成的指令
        if content.startswith("sd绘画") and " " in content:
            prompt = content.split("sd绘画", 1)[1].strip()
            logger.info(f"[{__class__.__name__}] 收到绘画生成请求: {prompt}")
            reply = Reply()
            result = self.sd_paint(prompt)
            if result:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "生成图像失败，请稍后再试。"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def sd_paint(self, prompt, model="normal"):
        params = {
            "prompt": prompt,
            "model": model
        }
        try:
            response = requests.get(url=ART_GENERATION_URL, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    return f"SD绘画完成。生成图像链接: {data.get('imgurl')}"
                else:
                    logger.error(f"API返回错误信息: {data.get('msg')}")
                    return None
            else:
                logger.error(f"API返回状态码异常: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"API请求异常：{e}")
            return None
