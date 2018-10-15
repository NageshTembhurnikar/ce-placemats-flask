import logging
from app.placemats.data.ncbi_client import *

logger = logging.getLogger(__name__)

def radial_tree_for_clinical_trials(nctid_to_title, nctid_to_status, nctid_to_conditions, nctid_to_locations, term):

    clinical_trial_tree = []
    axis_depth2 = []
    for condition, id_list in nctid_to_conditions.items():
        axis_depth3 = []
        for each_id in id_list:
            study_title = ''.join(nctid_to_title[each_id])
            if nctid_to_status[each_id][0] is not None:
                study_status = ''.join(nctid_to_status[each_id])
                study_title = study_title+': '+study_status.upper()
            locations_list = nctid_to_locations[each_id]
            axis_depth4 = []
            for site_loc in locations_list:
                if site_loc:
                    axis_depth4.append({'name': site_loc})
            if axis_depth4:
                axis_depth3.append({'name': study_title, 'children': axis_depth4[:10]})
            else:
                axis_depth3.append({'name': study_title})
        axis_depth2.append({'name': condition, 'children': axis_depth3})
    clinical_trial_tree.append({'name': term, 'children': axis_depth2})

    return clinical_trial_tree