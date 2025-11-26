```
1. build_draft_contBeam(axNod, axSpan, all_path_details)

2. add_equivalent_contBeam_info(draft_contBeam)

3. add_close_contBeam_info(draft_contBeam, spanDistMin, spanDistMinLim)

4. add_end_allowed_col_info(draft_contBeam, mask_col_never)

5. add_outer_contBeam_info(draft_contBeam, mask_basePol_spans)

6. add_never_contBeam_info(draft_contBeam, mask_beam_never, mask_colSpan_never)

7. add_fitness_info(draft_contBeam, fitness_span_in_area)

8. update_never_contBeam_info(draft_contBeam)

9. update_equivalent_and_close_info(draft_contBeam)

10. add_include_exclude_info(draft_contBeam)

11. build_contBeam(geoData, all_path_details, xls, repair_mask)
    1. build_draft_contBeam(axNod, axSpan, all_path_details)
    2. add_equivalent_contBeam_info(draft_contBeam)
    3. add_close_contBeam_info(draft_contBeam, spanDistMin, spanDistMinLim)
    4. add_end_allowed_col_info(draft_contBeam, mask_col_never)
    5. add_outer_contBeam_info(draft_contBeam, mask_basePol_spans)
    6. add_never_contBeam_info(draft_contBeam, mask_beam_never, mask_colSpan_never)
    7. add_fitness_info(draft_contBeam, fitness_span_in_area)
    8. update_never_contBeam_info(draft_contBeam)
    9. update_equivalent_and_close_info(draft_contBeam)
    10. add_include_exclude_info(draft_contBeam)

12. build_mask_contBeam_never(contBeam)
```