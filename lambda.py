import re

from aws_lambda_powertools import Logger
from domain.aws_actions.aws_actions import send_data_to_hive
from domain.utils.utils import convert_dict

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    dict_event = event['detail']
    to_remove = []
    for key in dict_event:
        if dict_event[key] is not None:
            dict_event[key] = re.sub(r'\s+', ' ', dict_event[key]).strip()
            dict_event[key] = re.sub(r'[^\w\s]+', '', dict_event[key])
        else:
            to_remove.append(key)
    for key in to_remove:
        dict_event.pop(key)
    return send_data_to_hive(convert_dict(dict_event))
