"""Miscellaneous utilities needed for stats, filtering, IE computations, etc."""

def mol_from_json(filepath):
    """Builds Psi4 molecule from JSON schema at location `filepath`
    
    Parameters
    ----------
    filepath : str
        Absolute file path for JSON molschema to be imported.

    Returns
    -------
    psi4.core.Molecule
    """
    import copy
    import json
    import psi4

    schema = {}
    schema['schema_name'] = 'qc_schema'
    schema['schema_version'] = 1

    with open(filepath, 'r') as f:
        schema['molecule'] = copy.deepcopy(json.load(f))
        
    return psi4.core.Molecule.from_schema(schema)

def dashD_interaction(mol, func=None, dashlvl=None, dashparam=None):
    """Computes intermolecular dispersion interaction [Eh] from supramolecular
    treatment using empirical Grimme -D corrections from dimer and monomers.

    Parameters
    ----------
    mol : psi4.core.Molecule
        Dimer for which to compute dispersion interaction
    func : str
        DFT or other functional defining parameters for -D correction
    dashlvl : str
        String defining form of dispersion correction and damping function.
        Recognized corrections: ['d2', 'd3', 'd3m']
        Recognized damping functions: ['zero', 'bj']
    dashparam : dict of str: float64
        Dictionary defining custom parameters for functional `func` within DFTD3 
        for dashlevel `dashlvl`. Overwrites default DFTD3 parameters.

    Returns
    -------
    int_d3 : float64
        Supramolecular dispersion interaction energy [kcal/mol]
    """
    hartree2kcalmol = 627.5094737775374
    # Dimer -D
    dimer_d = mol.run_dftd3(func=func, dashlvl=dashlvl, dashparam=dashparam, dertype=0)

    # monoA -D
    monoA = mol.extract_subsets(1)
    A_d = monoA.run_dftd3(func=func, dashlvl=dashlvl, dashparam=dashparam, dertype=0)
    
    # monoB -D
    monoB = mol.extract_subsets(2)
    B_d = monoB.run_dftd3(func=func, dashlvl=dashlvl, dashparam=dashparam, dertype=0)
    
    int_d3 = dimer_d - A_d - B_d
    
    return int_d3 * hartree2kcalmol


def qfilter(df, filter_on=['SAPT0'], q=[0.05,0.995], keep_index=False, ret='filtered'):
    import pandas as pd
    import numpy as np

    def colfilter(col, q):
        lower = df[col].quantile(q[0])
        upper = df[col].quantile(q[1])
        mask = (df[col] < upper) & (df[col] > lower)
        return mask
        
    if filter_on == 'all':
        filter_on = df.columns
        
    filtered = df.copy()
    for col in filter_on:
        colmask = colfilter(col, q)
        if 'out' in ret:
            colmask = ~np.array(colmask)
        if keep_index:
            filtered[col] = df[col][colmask]
        else:
            filtered[col] = df[col][colmask].values
        
    return filtered

# Tests
if __name__ == '__main__':
    import psi4
    from math import isclose
    He2 = psi4.geometry("""0 1\n He 0 0 0\n --\n He 0 0 4""")
    ref = -8.89e-06
    Edisp_b3lyp_d3mbj = dashD_interaction(He2, 'b3lyp', 'd3mbj')
    Edisp_hf_d3zero = dashD_interaction(He2, 'hf', 'd3zero')

    assert isclose(Edisp_hf_d3zero, ref), f"Supramolecular dispersion interaction {Edisp_b3lyp_d3mbj} does not agree with reference {ref} to 5 digits."

