"""Create a synthetic SPSS file for trying the notebook. No real participant data.

Three groups of unequal size (10, 14, 18), two outcomes measured pre and post,
SPSS value labels for the group variable, and a user-missing code (-99).
One participant in the smallest group has an extreme change score, so the
outlier check has something to find.
"""
import numpy as np
import pandas as pd
import pyreadstat

rng = np.random.default_rng(2026)
sizes = {1: 10, 2: 14, 3: 18}
extra_change = {1: 0.0, 2: -2.0, 3: -4.0}   # larger improvement (lower scores) in groups 2 and 3
rows = []
for g, n in sizes.items():
    for _ in range(n):
        anx_pre = rng.normal(22, 5)
        mood_pre = rng.normal(15, 4)
        rows.append(dict(
            group=g, age=float(rng.integers(18, 60)),
            anxiety_pre=anx_pre, anxiety_post=0.7 * anx_pre + 6 + extra_change[g] + rng.normal(0, 3),
            mood_pre=mood_pre, mood_post=0.6 * mood_pre + 6 + 0.5 * extra_change[g] + rng.normal(0, 3)))
df = pd.DataFrame(rows).round(1)
df.insert(0, 'participant_id', [f'P{i:03d}' for i in range(1, len(df) + 1)])
df.loc[3, 'anxiety_post'] = df.loc[3, 'anxiety_pre'] + 25   # extreme change in the 10-person group
df.loc[20, 'mood_post'] = -99                                # SPSS user-missing code
pyreadstat.write_sav(
    df, 'data/demo_prepost.sav',
    column_labels={'participant_id': 'Participant ID', 'group': 'Study group', 'age': 'Age (years)',
                   'anxiety_pre': 'Anxiety, pre', 'anxiety_post': 'Anxiety, post',
                   'mood_pre': 'Low mood, pre', 'mood_post': 'Low mood, post'},
    variable_value_labels={'group': {1: 'Control', 2: 'Brief intervention', 3: 'Full intervention'}},
    missing_ranges={'mood_post': [-99]},
    variable_measure={'group': 'nominal', 'participant_id': 'nominal'})
print('wrote data/demo_prepost.sav:', df.shape)
