import logging
from app.placemats.data.ncbi_client import *
from collections import defaultdict
logger = logging.getLogger(__name__)

def radial_tree_for_clinical_trials(nctid_to_title, nctid_to_status, nctid_to_conditions, nctid_to_phase, nctid_to_sponsor, nctid_to_enrollment, nctid_to_start, nctid_to_end, term):

    clinical_trial_tree = []

    axis_depth2 = []
    for condition, id_list in nctid_to_conditions.items():
        study_phase_dict = defaultdict(set)
        for each_id in id_list:
            study_phase = nctid_to_phase[each_id]
            if not study_phase:
                study_phase = 'Unknown'
            study_phase_dict[study_phase].add(each_id)

        axis_depth3 = []
        for each_phase, ids_in_each_phase in study_phase_dict.items():
            study_status_dict = defaultdict(set)
            for each_id in ids_in_each_phase:
                study_status = nctid_to_status[each_id]
                if not study_status:
                    study_status = 'Unknown'
                study_status_dict[study_status].add(each_id)

            axis_depth4 = []
            for study_status, ids_in_each_status in study_status_dict.items():
                axis_depth5 = []
                for each_id in ids_in_each_status:
                    study_title = nctid_to_title[each_id]
                    study_sponsor = ', '.join(nctid_to_sponsor[each_id])
                    onclick_information = {'start date': nctid_to_start[each_id].isoformat() if nctid_to_start[each_id] else '',
                                           'end date': nctid_to_end[each_id].isoformat() if nctid_to_end[each_id] else '',
                                           'enrollment': nctid_to_enrollment[each_id] if nctid_to_enrollment[each_id] else ''}
                    axis_depth5.append({'info': onclick_information, 'name': study_title, 'hover': study_sponsor})
                axis_depth4.append({'name': study_status, 'children': axis_depth5[:50]})
            axis_depth3.append({'name': each_phase, 'children': axis_depth4})
        axis_depth2.append({'name': condition, 'children': axis_depth3})
    clinical_trial_tree.append({'name': term, 'children': axis_depth2})
    return clinical_trial_tree