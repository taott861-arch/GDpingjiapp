import streamlit as st
import rating
# =========================================================
# 页面设置
# =========================================================

st.set_page_config(
    page_title="工业金属管道定期检验辅助评级系统",
    page_icon="🛠️",
    layout="centered"
)



def generate_judgement(
    actual_depth,
    level_23_limit,
    level_4_limit,
    result
):

    if result == "2级或者3级":

        judgement = (
            f"{actual_depth:.3f} ≤ "
            f"{level_23_limit:.3f}"
        )

    elif result == "4级":

        judgement = (
            f"{level_23_limit:.3f} < "
            f"{actual_depth:.3f} ≤ "
            f"{level_4_limit:.3f}"
        )

    else:

        judgement = (
            f"{actual_depth:.3f} > "
            f"{level_4_limit:.3f}"
        )

    return judgement
# =========================================================
# 网页标题
# =========================================================

st.title("🛠️ 工业金属管道定期检验辅助评级系统")

st.caption("依据 TSG 31—2025")

st.info(
    "当前版本：管子局部减薄辅助评级模块。"
    "计算结果用于辅助检验人员进行规则核对。"
)


# =========================================================
# 基本参数
# =========================================================
# =========================================================
# 输入表单
# =========================================================

with st.form("inspection_form"):

    # -----------------------------------------------------
    # 一、管道基本信息
    # -----------------------------------------------------

    st.header("一、管道基本信息")

    col1, col2 = st.columns(2)

    with col1:

        pipe_class = st.selectbox(
            "管道级别",
            ["GC1", "GC2"]
        )

        ReL = st.number_input(
            "材料屈服强度下限值 ReL（MPa）",
            min_value=0.0,
            value=235.0
        )

    with col2:

        P = st.number_input(
            "管道最大工作压力 P（MPa）",
            min_value=0.0,
            value=10.0
        )


    # -----------------------------------------------------
    # 二、现场检测数据
    # -----------------------------------------------------

    st.header("二、现场检测数据")

    col1, col2 = st.columns(2)

    with col1:

        D = st.number_input(
            "缺陷附近管道外径实测最大值 D（mm）",
            min_value=0.0,
            value=108.0
        )

        minimum_wall_thickness = st.number_input(
            "缺陷附近壁厚实测最小值（mm）",
            min_value=0.0,
            value=6.5
        )

        B = st.number_input(
            "缺陷环向长度实测最大值 B（mm）",
            min_value=0.0,
            value=50.0
        )

    with col2:

        corrosion_to_next_inspection = st.number_input(
            "至下一检验周期的腐蚀量（mm）",
            min_value=0.0,
            value=0.5
        )

        C = st.number_input(
            "局部减薄深度扩展量 C（mm）",
            min_value=0.0,
            value=0.5
        )

        actual_depth = st.number_input(
            "实际局部减薄深度（mm）",
            min_value=0.0,
            value=0.8
        )


    # -----------------------------------------------------
    # 自动计算 te
    # -----------------------------------------------------

    te = rating.calculate_te(
        minimum_wall_thickness,
        corrosion_to_next_inspection
    )

    st.write("### 自动计算参数")

    st.metric(
        "有效厚度 te",
        f"{te:.3f} mm"
    )


    # -----------------------------------------------------
    # 三、前置条件
    # -----------------------------------------------------

    st.header("三、7.4.2.4.1 前置条件检查")

    condition1 = st.checkbox(
        "1. 管道结构或者应力分析满足要求"
    )

    condition2 = st.checkbox(
        "2. 材料韧性良好，并且无性能劣化趋势"
    )

    condition3 = st.checkbox(
        "3. 局部减薄及附近无其他表面或者埋藏缺陷"
    )

    condition4 = st.checkbox(
        "4. 局部减薄处剩余壁厚大于 2 mm"
    )

    condition5 = st.checkbox(
        "5. 管道不承受疲劳载荷"
    )


    # -----------------------------------------------------
    # 提交按钮
    # -----------------------------------------------------

    submitted = st.form_submit_button(
        "开始评级",
        type="primary",
        use_container_width=True
    )

# =========================================================
# 开始计算按钮
# =========================================================

st.header("四、安全状况等级评定")


if submitted:
    # -----------------------------------------------------
    # 输入检查
    # -----------------------------------------------------

    if D <= 0:

        st.error("D 必须大于 0。")


    elif corrosion_to_next_inspection >= minimum_wall_thickness:

        st.error(
            "输入数据不合理："
            "至下一检验周期的腐蚀量必须小于"
            "缺陷附近壁厚实测最小值。"
        )


    elif te >= D / 2:

        st.error(
            "数据错误：必须满足 te < D / 2。"
        )


    elif ReL <= 0:

        st.error(
            "ReL 必须大于 0。"
        )


    else:

        # -------------------------------------------------
        # 计算 PL0
        # -------------------------------------------------

        PL0 = rating.calculate_pl0(
            D,
            te,
            ReL
        )


        # -------------------------------------------------
        # 计算两个比值
        # -------------------------------------------------

        pressure_ratio = rating.calculate_pressure_ratio(
            P,
            PL0
        )


        length_ratio = rating.calculate_length_ratio(
            B,
            D
        )


        # -------------------------------------------------
        # 显示中间计算结果
        # -------------------------------------------------

        st.subheader("计算参数")

        col1, col2, col3 = st.columns(3)


        col1.metric(
            "PL0",
            f"{PL0:.3f} MPa"
        )


        col2.metric(
            "P / PL0",
            f"{pressure_ratio:.3f}"
        )


        col3.metric(
            "B / (πD)",
            f"{length_ratio:.3f}"
        )


        # -------------------------------------------------
        # GC1 / GC2 查表
        # -------------------------------------------------

        if pipe_class == "GC1":

            limits = rating.lookup_gc1(
                pressure_ratio,
                length_ratio,
                te,
                C
            )


        else:

            limits = rating.lookup_gc2(
                pressure_ratio,
                length_ratio,
                te,
                C
            )


        # -------------------------------------------------
        # 表格适用范围判断
        # -------------------------------------------------

        if limits is None:

            st.warning(
                "当前数据超出表 7-3 / 表 7-4 "
                "可以直接判断的范围，请人工核对规范。"
            )


        else:

            level_23_limit, level_4_limit = limits


            st.subheader("TSG 查表结果")


            col1, col2 = st.columns(2)


            col1.metric(
                "2级或者3级允许最大减薄深度",
                f"{level_23_limit:.3f} mm"
            )


            col2.metric(
                "4级允许最大减薄深度",
                f"{level_4_limit:.3f} mm"
            )


            # ---------------------------------------------
            # 五个前置条件
            # ---------------------------------------------

            preconditions_ok = rating.check_preconditions(
                condition1,
                condition2,
                condition3,
                condition4,
                condition5
            )


            # =========================================================
            # 最终评级
            # =========================================================

            st.divider()


            if not preconditions_ok:

                st.error("安全状况等级：5级")

                st.warning(
                    "TSG 31—2025 第7.4.2.4.1规定的"
                    "前置条件未全部满足。"
                )


            else:

                result = rating.evaluate_thinning(
                    actual_depth,
                    level_23_limit,
                    level_4_limit
                )


                judgement = generate_judgement(
                    actual_depth,
                    level_23_limit,
                    level_4_limit,
                    result
                )


                # =====================================================
                # 评级结果
                # =====================================================

                if result == "5级":

                    st.error(
                        f"### 安全状况等级：{result}"
                    )

                elif result == "4级":

                    st.warning(
                        f"### 安全状况等级：{result}"
                    )

                else:

                    st.success(
                        f"### 安全状况等级：{result}"
                    )


                # =====================================================
                # 评级依据
                # =====================================================

                if pipe_class == "GC1":

                    table_name = "表 7-4"

                else:

                    table_name = "表 7-3"


                st.subheader("评级依据")

                st.write(
                    "依据：TSG 31—2025 "
                    "第 7.4.2.4.1 条，"
                    f"{table_name}（{pipe_class} 管道）"
                )


                # =====================================================
                # 关键计算参数
                # =====================================================

                st.subheader("关键计算参数")

                col1, col2 = st.columns(2)


                with col1:

                    st.metric(
                        "有效厚度 te",
                        f"{te:.3f} mm"
                    )

                    st.metric(
                        "P / PL0",
                        f"{pressure_ratio:.3f}"
                    )


                with col2:

                    st.metric(
                        "管道极限内压 PL0",
                        f"{PL0:.3f} MPa"
                    )

                    st.metric(
                        "B / (πD)",
                        f"{length_ratio:.3f}"
                    )


                # =====================================================
                # 允许值与实际值
                # =====================================================

                st.subheader("局部减薄深度比较")

                col1, col2, col3 = st.columns(3)


                col1.metric(
                    "实际局部减薄深度",
                    f"{actual_depth:.3f} mm"
                )


                col2.metric(
                    "2级或者3级允许最大值",
                    f"{level_23_limit:.3f} mm"
                )


                col3.metric(
                    "4级允许最大值",
                    f"{level_4_limit:.3f} mm"
                )


                # =====================================================
                # 自动判断过程
                # =====================================================

                st.subheader("判断过程")

                st.code(
                    judgement
                )


                st.write(
                    f"因此，本项安全状况等级评定结果为："
                    f"**{result}**。"
                )


                # =====================================================
                # 详细计算过程
                # =====================================================

                with st.expander("查看完整计算过程"):

                    st.write(
                        "### 1. 原始输入数据"
                    )

                    st.write(
                        "管道级别：",
                        pipe_class
                    )

                    st.write(
                        "缺陷附近管道外径 D：",
                        D,
                        "mm"
                    )

                    st.write(
                        "缺陷附近壁厚实测最小值：",
                        minimum_wall_thickness,
                        "mm"
                    )

                    st.write(
                        "至下一检验周期腐蚀量：",
                        corrosion_to_next_inspection,
                        "mm"
                    )

                    st.write(
                        "材料屈服强度下限值 ReL：",
                        ReL,
                        "MPa"
                    )

                    st.write(
                        "管道最大工作压力 P：",
                        P,
                        "MPa"
                    )

                    st.write(
                        "缺陷环向长度 B：",
                        B,
                        "mm"
                    )

                    st.write(
                        "局部减薄深度扩展量 C：",
                        C,
                        "mm"
                    )

                    st.write(
                        "实际局部减薄深度：",
                        actual_depth,
                        "mm"
                    )


                    st.write("---")


                    st.write(
                        "### 2. 有效厚度计算"
                    )

                    st.write(
                        f"te = {minimum_wall_thickness:.3f}"
                        f" - {corrosion_to_next_inspection:.3f}"
                        f" = {te:.3f} mm"
                    )


                    st.write(
                        "### 3. 管道极限内压"
                    )

                    st.write(
                        f"PL0 = {PL0:.3f} MPa"
                    )


                    st.write(
                        "### 4. 查表参数"
                    )

                    st.write(
                        f"P / PL0 = {pressure_ratio:.3f}"
                    )

                    st.write(
                        f"B / (πD) = {length_ratio:.3f}"
                    )


                    st.write(
                        "### 5. 查表结果"
                    )

                    st.write(
                        f"使用 {table_name}"
                    )

                    st.write(
                        "2级或者3级允许最大局部减薄深度：",
                        f"{level_23_limit:.3f} mm"
                    )

                    st.write(
                        "4级允许最大局部减薄深度：",
                        f"{level_4_limit:.3f} mm"
                    )


                    st.write(
                        "### 6. 比较"
                    )

                    st.write(
                        judgement
                    )


                    st.write(
                        "### 7. 评级结果"
                    )

                    st.write(
                        result
                    )
