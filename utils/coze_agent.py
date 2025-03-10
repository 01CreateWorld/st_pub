import os
import time

from cozepy import COZE_CN_BASE_URL
from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType  # noqa

coze_api_token = "pat_3xeECicYAnAijwCVUaeMuZEvN4WLimnAfrmu9HApdw5amSPRsu142pqi49RLUVZV" # os.getenv("COZE_API_TOKEN")
coze_api_base = os.getenv("COZE_API_BASE") or COZE_CN_BASE_URL

coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

bot_id = os.getenv("COZE_BOT_ID") or "7471918474705747977"
user_id = "macbook"

def ask_coze(message_question: str) -> tuple[str, list]:
    
    chat = coze.chat.create(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[
            # Message.build_user_question_text("Who are you?"),
            # Message.build_assistant_answer("I am Bot by Coze."),
            Message.build_user_question_text(message_question),
        ],
    )

    start = int(time.time())
    timeout = 600
    while chat.status == ChatStatus.IN_PROGRESS:
        if int(time.time()) - start > timeout:
            # too long, cancel chat
            coze.chat.cancel(conversation_id=chat.conversation_id, chat_id=chat.id)
            break

        time.sleep(1)
        # Fetch the latest data through the retrieve interface
        chat = coze.chat.retrieve(conversation_id=chat.conversation_id, chat_id=chat.id)

    messages = coze.chat.messages.list(conversation_id=chat.conversation_id, chat_id=chat.id)

    message_answer = ""
    message_follow_up = []

    for message in messages:
        if message.type == "answer":
            message_answer = message.content
        elif message.type == "follow_up":
            message_follow_up.append(message.content)

    #print(message_answer)
    #print(message_follow_up)

    return message_answer, message_follow_up


#ret_answer, ret_follow_up = ask_coze("煎牛排推荐用什么锅具？")

#print(ret_answer)
#print(ret_follow_up)

