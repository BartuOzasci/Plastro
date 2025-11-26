```
1. build_mask_col_outside_basePol(nodes, axNod, basePol)

2. build_mask_col_inside_banned_area(nodInArea, no_columns)

3. build_mask_col_basePol_corner(nodes, basePol)

4. build_mask_beam_inside_banned_area(spanInArea, no_beams)

5. build_mask_beam_under_wall(wall_widths, full_wall_min_width)

6. build_mask_colSpan_outside_basePol(nodes, axNod, spans, basePol)

7. build_mask_colSpan_inside_banned_area(spanInArea, no_columns)

8. build_mask_colSpan_short_or_long(spanLen, colSpanLenMin, colSpanLenMax)

9. build_mask_outer(nodes, axNod, spans, nodMat, basePol, floorPol)

10. build_mask_user(nodes, spans, dxf)

11. combine_masks(masks)

12. build_data_repair(geoData, slabProp, span_walls, xls, dxf)
    1. build_mask_col_outside_basePol(nodes, axNod, basePol)
    2. build_mask_col_inside_banned_area(nodInArea, no_columns)
    3. build_mask_col_basePol_corner(nodes, basePol)
    4. build_mask_beam_inside_banned_area(spanInArea, no_beams)
    5. build_mask_beam_under_wall(wall_widths, full_wall_min_width)
    6. build_mask_colSpan_outside_basePol(nodes, axNod, spans, basePol)
    7. build_mask_colSpan_inside_banned_area(spanInArea, no_columns)
    8. build_mask_colSpan_short_or_long(spanLen, colSpanLenMin, colSpanLenMax)
    9. build_mask_outer(nodes, axNod, spans, nodMat, basePol, floorPol)
    10. build_mask_user(nodes, spans, dxf)
    11. combine_masks(masks)

13. apply_repair(cand, repair_mask)
```