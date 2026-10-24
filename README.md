# Mixed ANOVA for pre/post designs

A Google Colab notebook for one of the most common designs in intervention research: two or more groups, each measured before and after. It reads an SPSS file, runs a two-time-point mixed ANOVA, and writes an Excel workbook, a Word report and figures for each outcome.

## What it does

- **Reads SPSS files directly**, keeping variable and value labels. SPSS-declared missing codes are treated as missing.
- **Lets you choose the variables in a form:** group, participant ID, and one or more pre/post outcome pairs.
- **Runs the mixed ANOVA.** The group effect is tested on each person's mean score; time and group × time are tested on change scores, each with its own error term. Type III tests with sum-to-zero contrasts are used, so with unequal group sizes the time effect weights each group equally. The code checks its own interaction result against an independent calculation.
- **Checks assumptions:** Shapiro–Wilk tests on change scores in each group, Brown–Forsythe tests on the two error terms, Q–Q plots, and outlier flags. Flagged participants are never excluded automatically.
- **Runs follow-up tests:** paired pre/post tests within each group, and Welch tests between groups at each time point and on change scores. Holm correction is applied within each family of comparisons.
- **Reports effect sizes:** partial η², Cohen's dz, Hedges' g, and Morris's d_ppc2 for differences in change.
- **Documents the analysis:** complete-case accounting, software versions, and interpretation cautions in every report.

## Revisions (October 2026)

The notebook was first committed as originally written, with outputs removed. The next commit made four changes, so the history shows exactly what changed:

1. **Outlier flags now use Tukey fences** (1.5 × IQR) on change scores within each group, the same rule as the boxplots. The earlier |z| ≥ 3 rule cannot flag anyone in a group of 10 or fewer, because the largest possible |z| with the sample SD is (n − 1)/√n, which is 2.85 for n = 10. On the demo data the earlier rule flagged nothing, including a planted extreme change.
2. **Change contrasts report two effect sizes.** Hedges' g standardized by the SD of change scores is now labelled as such. Morris's d_ppc2, standardized by the pre-test SD, is added. The change-score version is larger than an ordinary d whenever the pre–post correlation exceeds .5; at a correlation of .7 it is 1.29 times larger. Only d_ppc2 is comparable with published between-group effect sizes.
3. **Variance checks now test the model's two error terms**: subject means and change scores, instead of pre and post separately.
4. **Reports now state which question the analysis answers.** With randomized groups, adjusting post-test scores for pre-test (ANCOVA) answers the same question with more power. With pre-existing groups, the two analyses answer different questions and can disagree (Lord's paradox).

## Checks

```bash
pip install -r requirements.txt
python make_demo_sav.py              # writes data/demo_prepost.sav (already included)
python tests/validate_analysis.py
```

The validation script loads the notebook's analysis code and checks it against independent calculations. All 10 checks pass:

- the three F-tests on deliberately unbalanced groups (n = 9, 17, 21);
- outlier detection in a group of 10;
- d_ppc2 against its formula;
- SPSS missing-value handling;
- a full report run on the demo file.

## Using it

Open `mixed_anova_prepost.ipynb` in Google Colab and run the cells in order. Upload your `.sav` file (or `data/demo_prepost.sav` to try it), connect Google Drive, choose the variables, and click **Run analysis**. Reports are saved to `My Drive/Mixed_ANOVA_Reports`.

The demo file is synthetic: 42 participants in three groups of 10, 14 and 18, two outcomes, and one SPSS missing code.

## Limits

The notebook handles exactly two time points and one between-subject factor, using complete cases. It does not fit ANCOVA, mixed-effects or multilevel models, and it does not adjust for clustering (for example, participants within sites). Corrections for multiple comparisons apply within each outcome, not across outcomes.

## References

- Morris, S. B. (2008). Estimating effect sizes from pretest-posttest-control group designs. *Organizational Research Methods*, 11(2), 364–386.
- Van Breukelen, G. J. P. (2006). ANCOVA versus change from baseline had more power in randomized studies and more bias in nonrandomized studies. *Journal of Clinical Epidemiology*, 59(9), 920–925.
- Vickers, A. J., & Altman, D. G. (2001). Analysing controlled trials with baseline and follow up measurements. *BMJ*, 323, 1123. https://doi.org/10.1136/bmj.323.7321.1123

## License

MIT (see `LICENSE`).
