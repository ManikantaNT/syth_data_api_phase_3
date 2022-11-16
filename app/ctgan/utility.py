import numpy as np
import pandas as pd




def get_discrete_cols(args, path):
    if args.discrete!= None:
        df= pd.read_csv(path)
        cate_feat = df.select_dtypes(include=[np.object])
        nominal_list = cate_feat.columns.tolist()
    return nominal_list