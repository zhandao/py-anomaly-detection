from copy import deepcopy

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

from pandas.api.types import is_numeric_dtype


def numerical_check(df):
    ''' function to check if the dataframe are fully numerical

    :param df:
    :return:
    '''

    # check if it is a pandas framework or series
    integrity_check(df)

    # count how many pandas
    num_vars = df.select_dtypes(include=[np.number])
    l_num_vars = num_vars.shape[1]

    if l_num_vars == df.shape[1]:
        return True
    else:
        return False


def integrity_check(df):
    ''' check if the input data is compliant with the model requirement

    :param df:
    :return:
    '''
    if isinstance(df, pd.DataFrame):
        return True
    elif isinstance(df, pd.Series):
        raise TypeError("Pyador does not support single column data." \
                        " Try simple statistical outlier detection instead")
    else:
        raise TypeError("Pyador only supports pandas dataframe")


def missing_check(df, imputation="zero", verbose=True):
    '''check the missing percentage. Impute the missing values if necessary
    Note: for numerical variables and categorical variables we should handle
    differently

    :param df:
    :param imputation: "zero" or "mean"
    :return:
    '''
    n_df = df.shape[0]
    cols = df.columns.tolist()
    if verbose:
        print("\nMissing value check and imputation starts...")

    for col in cols:
        missing = n_df - np.count_nonzero(df[col].isnull().values)
        mis_perc = 100 - float(missing) / n_df * 100

        if mis_perc > 0:
            if verbose:
                print("    {col} missing percentage is {miss}%" \
                      .format(col=col, miss=mis_perc))
            # impute categorical var by NaN
            if not is_numeric_dtype(df[col]):
                df[col].fillna('NaN', inplace=True)
                continue
            # impute num variables
            if imputation == "mean":
                df[col].fillna(df[col].mean, inplace=True)
            else:
                df[col].fillna(int(0), inplace=True)
    return df


def cat_to_num(df, verbose=True):
    '''convert categorical variables into numerical format

    :param df:
    :return:
    '''
    cat_vars = df.select_dtypes(exclude=[np.number]).columns
    le_dict = {}
    if verbose:
        print("\nAutomatic variable type conversion starts...")
    for cat_var in cat_vars:

        # append num_ to variable name
        num_name = "num_" + cat_var

        if verbose:
            print("    Convert {cat_var}  to numerical as {num_name}" \
                  .format(cat_var=cat_var, num_name=num_name))

        le = LabelEncoder()

        # build encoder and save in the dictionary
        tran_np = le.fit_transform(df[cat_var])
        le_copy = deepcopy(le)
        le_dict[num_name] = le_copy

        tran_df = pd.DataFrame(tran_np, columns=[num_name])
        # print("{col} is converted to {num_name}".
        #       format(col=cat_var, num_name=num_name))
        # print (le.classes_)
        df = pd.concat([df, tran_df], axis=1)

    # extract numerical variables into a new df
    num_df = df.select_dtypes(include=[np.number])
    num_vars = num_df.columns.tolist()

    return {"df": df,
            "num_df": num_df,
            "num_vars": num_vars,
            "le_dict": le_dict}
