"""Check the notebook's analysis functions against independent calculations.

Run from the repository root:  python tests/validate_analysis.py
Loads the analysis cell from mixed_anova_prepost.ipynb (no Colab needed) and checks:
  1. the three ANOVA F-tests on deliberately unbalanced simulated data;
  2. that the outlier rule can flag an extreme change in a group of 10;
  3. Morris d_ppc2 against its formula;
  4. a full report run on the synthetic SPSS file, including user-missing handling.
"""
import json, math, sys, tempfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import pyreadstat
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
nb = json.loads((ROOT / 'mixed_anova_prepost.ipynb').read_text(encoding='utf-8'))
analysis_cell = next(''.join(c['source']) for c in nb['cells']
                     if c['cell_type'] == 'code' and 'def mixed_anova_two_times' in ''.join(c['source']))
ns = {}
exec(analysis_cell, ns)
failures = []

def check(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + (f'  ({detail})' if detail else ''))
    if not ok:
        failures.append(name)

def frame(groups):
    d = pd.DataFrame(groups)
    d['Subject'] = [str(i) for i in range(len(d))]
    d['MeanScore'] = (d.Pre + d.Post) / 2
    d['Change'] = d.Post - d.Pre
    return d

# 1. ANOVA against independent calculations, unbalanced groups
rng = np.random.default_rng(1)
rows = []
for g, (n, shift) in enumerate(zip([9, 17, 21], [0, .5, 1.2])):
    pre = rng.normal(20, 5, n)
    post = 0.7 * pre + rng.normal(6 + shift, 3, n)
    rows += [dict(Group=f'G{g}', Pre=a, Post=b) for a, b in zip(pre, post)]
d = frame(rows)
res = ns['mixed_anova_two_times'](d).set_index('Source')
by = d.groupby('Group')
f_group = stats.f_oneway(*[x.MeanScore for _, x in by]).statistic
f_inter = stats.f_oneway(*[x.Change for _, x in by]).statistic
k, N = by.ngroups, len(d)
mse = sum(((x.Change - x.Change.mean()) ** 2).sum() for _, x in by) / (N - k)
f_time = by.Change.mean().mean() ** 2 / (mse * (1 / by.size()).sum() / k ** 2)
check('Group F equals one-way ANOVA on subject means', np.isclose(res.loc['Group', 'F'], f_group, rtol=1e-10))
check('Group × Time F equals one-way ANOVA on change scores', np.isclose(res.loc['Group × Time', 'F'], f_inter, rtol=1e-10))
check('Time F equals the unweighted-marginal-mean test', np.isclose(res.loc['Time', 'F'], f_time, rtol=1e-10))

# 2. Outlier rule must work in a group of 10
small = frame([dict(Group='A', Pre=10.0, Post=10.0 + c) for c in [0, 1, -1, 0.5, -0.5, 0.2, -0.2, 0.8, -0.8, 30]] +
              [dict(Group='B', Pre=10.0, Post=10.0 + c) for c in rng.normal(0, 1, 12)])
_, flagged = ns['assumption_tests'](small)
z_max = (10 - 1) / math.sqrt(10)
check('Extreme change in a group of 10 is flagged', (flagged.Group == 'A').sum() == 1,
      f'old |z| >= 3 rule could not fire here: max possible |z| = {z_max:.2f}')

# 3. Morris d_ppc2 against its formula
a, b = d[d.Group == 'G2'], d[d.Group == 'G0']
na, nb_ = len(a), len(b)
sd_pre = math.sqrt(((na - 1) * a.Pre.var() + (nb_ - 1) * b.Pre.var()) / (na + nb_ - 2))
expected = (1 - 3 / (4 * (na + nb_ - 2) - 1)) * ((a.Post.mean() - a.Pre.mean()) - (b.Post.mean() - b.Pre.mean())) / sd_pre
check('Morris d_ppc2 matches its formula', np.isclose(ns['morris_dppc2'](a, b), expected, rtol=1e-12))
pairs = ns['pairwise_tests'](d, 0.05)
change_rows = pairs[pairs.Family == 'Between-group change contrasts']
check('Change contrasts report both effect sizes', change_rows.Effect_size_2.notna().all() and
      change_rows.Effect_size_type.str.contains('change scores').all())

# 4. Full run on the synthetic SPSS file
raw, meta = pyreadstat.read_sav(str(ROOT / 'data' / 'demo_prepost.sav'), user_missing=False, apply_value_formats=False)
check('SPSS user-missing code (-99) is read as missing', raw['mood_post'].isna().sum() == 1 and (raw['mood_post'] == -99).sum() == 0)
with tempfile.TemporaryDirectory() as tmp:
    out = {}
    for name, pre, post in [('Anxiety', 'anxiety_pre', 'anxiety_post'), ('Low mood', 'mood_pre', 'mood_post')]:
        out[name] = ns['analyze_one'](raw, meta, 'demo_prepost.sav', 'group', pre, post, 'participant_id',
                                      name, 0.05, Path(tmp) / name.replace(' ', '_'))
    files = sorted(p.name for p in (Path(tmp) / 'Anxiety').iterdir())
    check('Report files are written', {'Statistical_Tables.xlsx', 'Mixed_ANOVA_Report.docx', 'Analysis_Notes.txt'} <= set(files), ', '.join(files))
    flags = pd.read_excel(Path(tmp) / 'Anxiety' / 'Statistical_Tables.xlsx', sheet_name='Outlier_Flags', skiprows=2)
    check('Planted extreme change (P004, 10-person group) is flagged', 'P004' in set(flags.Subject.astype(str)))
check('Complete-case N excludes the missing value', out['Anxiety']['N'] == 42 and out['Low mood']['N'] == 41,
      f"N = {out['Anxiety']['N']} and {out['Low mood']['N']}")

print('\nAll checks passed.' if not failures else f'\n{len(failures)} check(s) failed.')
sys.exit(1 if failures else 0)
