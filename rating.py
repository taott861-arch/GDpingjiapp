import math
# =========================================================
# 定义一个函数来计算有效厚度 te
# =========================================================
def calculate_te(
    minimum_wall_thickness,
    corrosion_to_next_inspection
):

    te = (
        minimum_wall_thickness
        - corrosion_to_next_inspection
    )

    return te
# =========================================================
# 1. 计算 PL0
# =========================================================

def calculate_pl0(D, te, ReL):

    PL0 = (2 / math.sqrt(3)) * ReL * math.log(
        (D / 2) / (D / 2 - te)
    )

    return PL0


# =========================================================
# 2. 计算压力比
# =========================================================

def calculate_pressure_ratio(P, PL0):

    return P / PL0


# =========================================================
# 3. 计算缺陷长度比
# =========================================================

def calculate_length_ratio(B, D):

    return B / (math.pi * D)


# =========================================================
# 4. GC2 查表
#    TSG 31-2025 表 7-3
# =========================================================

def lookup_gc2(pressure_ratio, length_ratio, te, C):

    if pressure_ratio < 0.3:

        if length_ratio <= 0.25:

            level_23_limit = 0.33 * te - C
            level_4_limit = 0.40 * te - C

        elif length_ratio <= 0.75:

            level_23_limit = 0.25 * te - C
            level_4_limit = 0.33 * te - C

        elif length_ratio <= 1.00:

            level_23_limit = 0.20 * te - C
            level_4_limit = 0.25 * te - C

        else:

            return None


    elif 0.3 < pressure_ratio <= 0.5:

        if length_ratio <= 0.25:

            level_23_limit = 0.20 * te - C
            level_4_limit = 0.25 * te - C

        elif length_ratio <= 1.00:

            level_23_limit = 0.15 * te - C
            level_4_limit = 0.20 * te - C

        else:

            return None


    else:

        return None


    return level_23_limit, level_4_limit


# =========================================================
# 5. GC1 查表
#    TSG 31-2025 表 7-4
# =========================================================

def lookup_gc1(pressure_ratio, length_ratio, te, C):

    if pressure_ratio < 0.3:

        if length_ratio <= 0.25:

            level_23_limit = 0.30 * te - C
            level_4_limit = 0.35 * te - C

        elif length_ratio <= 0.75:

            level_23_limit = 0.20 * te - C
            level_4_limit = 0.30 * te - C

        elif length_ratio <= 1.00:

            level_23_limit = 0.15 * te - C
            level_4_limit = 0.20 * te - C

        else:

            return None


    elif 0.3 < pressure_ratio <= 0.5:

        if length_ratio <= 0.25:

            level_23_limit = 0.15 * te - C
            level_4_limit = 0.20 * te - C

        elif length_ratio <= 1.00:

            level_23_limit = 0.10 * te - C
            level_4_limit = 0.15 * te - C

        else:

            return None


    else:

        return None


    return level_23_limit, level_4_limit


# =========================================================
# 6. 前置条件检查
# =========================================================

def check_preconditions(
    condition1,
    condition2,
    condition3,
    condition4,
    condition5
):

    return (
        condition1
        and condition2
        and condition3
        and condition4
        and condition5
    )


# =========================================================
# 7. 最终评级
# =========================================================

def evaluate_thinning(
    actual_depth,
    level_23_limit,
    level_4_limit
):

    if actual_depth <= level_23_limit:

        return "2级或者3级"

    elif actual_depth <= level_4_limit:

        return "4级"

    else:

        return "5级"


print("rating加载成功")
print(calculate_te)