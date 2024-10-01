import pandas as pd
import json
import numpy as np

def persona(p):
    st = '<div class=\"persona\">'
    st += "<p class=\"persona-name\">"+p["Name"]+"</p>"
    st += " ".join(["<p class=\"persona-prop\">"+_k+": "+_v+"</p>" for _k,_v in p.items() if _k != "Name"])
    st+= "</div>"
    return st

def table(_json):
    st = '<div class=\"target-prediction\">'
    _df = pd.json_normalize(_json)
    st += _df.to_html(index=False)
    st += "</div>"
    return st    

# def target(df):
#     st = '<div class=\"target-prediction\">'
#     st += df.to_html(index=False)
#     st += "</div>"
#     return st


# def func_0(v1, v2):
#     return round(float(v1)*float(v2), 2)

# def lime_explanation(explainer_result, output_description):
#     st ='<a href=\"'+explainer_result["plot_png"]+'\" target=\"_blank\"><img src=\"'+explainer_result["plot_png"]+'\"style=\" width:80%; \"></a>'
#     st +='<p><strong>Explanation Description:</strong> <br>'+output_description+'</p>'
#     return st

# def discern_explanation(instance, explainer_result, output_description):

#     cf = pd.json_normalize(json.loads(explainer_result["explanation"]))
#     meta_data = '{\"target_names\":[\"loan_status\"],\"target_values\":[\"Rejected\",\"Accepted\"],\"features\":[{\"id\":\"loan_amnt\",\"min\":1000,\"max\":40000},{\"id\":\"total_pymnt\",\"min\":41.62,\"max\":44881.66051},{\"id\":\"total_rec_int\",\"min\":0,\"max\":7036.9},{\"id\":\"term\",\"values\":[\"36 months\",\"60 months\"]},{\"id\":\"int_rate\",\"min\":5.31,\"max\":30.79},{\"id\":\"installment\",\"min\":32.47,\"max\":1474.75},{\"id\":\"home_ownership\",\"values\":[\"Rent\",\"Own\",\"Mortgage\"]},{\"id\":\"annual_inc\",\"min\":3600,\"max\":700000},{\"id\":\"verification_status\",\"values\":[\"Source Verified\",\"Not Verified\",\"Verified\"]},{\"id\":\"loan_status\",\"values\":[\"Rejected\",\"Accepted\"]},{\"id\":\"purpose\",\"values\":[\"major purchase\",\"other\",\"home improvement\",\"debt consolidation\",\"house\",\"credit card\",\"car\",\"medical\",\"vacation\",\"small business\",\"moving\"]}]}'
#     meta_data = json.loads(meta_data)
#     cf_np = cf.to_numpy().reshape((len(meta_data["features"])-1, 2)).transpose()
#     cf_df = pd.DataFrame(cf_np, columns=[f["id"] for f in meta_data["features"] if f["id"] not in meta_data["target_names"]])
#     features = meta_data["features"]
#     for item in [f for f in features if "values" in f and f["id"] not in meta_data["target_names"]]:
#         l1 = np.linspace(0.0, 1.0, num=len(item["values"]))
#         cf_df[item["id"]] = cf_df[item["id"]].map(dict(zip([round(f,2) for f in l1], item["values"])))
#     for item in [f for f in features if "max" in f and f["id"] not in meta_data["target_names"]]:
#         cf_df[item["id"]] = cf_df[item["id"]].apply(lambda r: func_0(r, item["max"]))
#     cf_df.insert(0, "", ["Original", "Counterfactual"])
#     st = '<div class=\"target-prediction\">'
#     st += cf_df.to_html(index=False)
#     st += "</div>"
#     st +='<p><strong>Explanation Description:</strong> <br>'+output_description+'</p>'
#     return st
