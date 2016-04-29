"""Construct a block section of Stages in a Spinnaker Pipeline."""
import json
import logging
from pprint import pformat

from ..utils import generate_encoded_user_data, get_subnets, get_template

LOG = logging.getLogger(__name__)


def construct_pipeline_block(env='',
                             generated=None,
                             previous_env=None,
                             region='us-east-1',
                             settings=None):
    """Create the Pipeline JSON from template.

    Args:
        env (str): Deploy environment name, e.g. dev, stage, prod.
        generated (gogoutils.Generator): Gogo Application name generator.
        previous_env (str): The previous deploy environment to use as
            Trigger.
        region (str): AWS Region to deploy to.
        settings (dict): Environment settings from configurations.

    Returns:
        dict: Pipeline JSON template rendered with configurations.
    """
    LOG.info('Create Pipeline for %s in %s.', env, region)

    if env.startswith('prod'):
        template_name = 'pipeline-templates/pipeline_{}.json'.format(env)
    else:
        template_name = 'pipeline-templates/pipeline_stages.json'

    LOG.debug('%s info:\n%s', env, pformat(settings))

    region_subnets = get_subnets(env=env, region=region)

    LOG.debug('Region and subnets in use:\n%s', region_subnets)

    user_data = generate_encoded_user_data(env=env,
                                           region=region,
                                           app_name=generated.app,
                                           group_name=generated.project),

    # Use different variable to keep template simple
    data = settings
    data['app'].update({
        'appname': generated.app,
        'environment': env,
        'regions': json.dumps(list(region_subnets.keys())),
        'region': region,
        'az_dict': json.dumps(region_subnets),
        'previous_env': previous_env,
        'encoded_user_data': user_data,
    })

    pipeline_json = get_template(template_file=template_name, data=data)
    return pipeline_json
