import logging
from app.placemats.data.ncbi_client import *

logger = logging.getLogger(__name__)


def radial_tree_for_clinical_trials(nctid_to_title, nctid_to_status, nctid_to_conditions, term):

    clinical_trial_tree = []
    axis_depth2 = []
    for condition, id_list in nctid_to_conditions.items():
        axis_depth3 = []
        for each_id in id_list:
            study_title = ''.join(nctid_to_title[each_id])
            study_status = ''.join(nctid_to_status[each_id])
            axis_depth3.append({'name': study_title, 'info': study_status})
        axis_depth2.append({'name': condition, 'children': axis_depth3})
    clinical_trial_tree.append({'name': term, 'children': axis_depth2})

    return clinical_trial_tree