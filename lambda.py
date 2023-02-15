import re

from aws_lambda_powertools import Logger
from domain.aws_actions.aws_actions import send_data_to_hive
from domain.utils.utils import convert_dict

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    dict_event = event['detail']
    dict_event['name'] = re.sub(r'\s+', ' ', dict_event['name']).strip()
    return send_data_to_hive(convert_dict(dict_event))
