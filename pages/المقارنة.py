elif st.session_state.page == "المقارنة":
    st.subheader("المقارنة بين الجامعات")

    # تحميل نفس بيانات الجامعات هنا
    unis = normalize_unis(load_unis_csv(UNIS_PATH))

    if unis.empty:
        st.error("ملف الجامعات فاضي أو ما انقرأ بشكل صحيح.")
        st.stop()

    st.write("اختاري 2 إلى 4 جامعات للمقارنة:")

    # قائمة اختيار مرتبة
    unis_sorted = unis.copy()
    unis_sorted["label"] = unis_sorted.apply(make_uni_label, axis=1)
    unis_sorted = unis_sorted.sort_values(["country", "city", "name_en"], na_position="last")

    options = unis_sorted[["uni_id", "label"]].to_dict("records")

    selected_ids = st.multiselect(
        "اختيار الجامعات",
        options=[o["uni_id"] for o in options],
        format_func=lambda x: unis_sorted.loc[unis_sorted["uni_id"] == x, "label"].values[0]
        if (unis_sorted["uni_id"] == x).any() else x,
        default=[],
        max_selections=4
    )

    if len(selected_ids) < 2:
        st.info("لازم تختارين جامعتين على الأقل عشان تظهر المقارنة.")
        st.stop()

    comp = unis_sorted[unis_sorted["uni_id"].isin(selected_ids)].copy()

    # ترتيب أعمدة المقارنة
    cols_compare = [
        "name_ar", "name_en", "country", "city", "type",
        "scholarship",
        "ranking_source", "ranking_value",
        "accreditation_notes",
        "website", "admissions_url", "programs_url"
    ]
    for c in cols_compare:
        if c not in comp.columns:
            comp[c] = ""

    # عرض مقارنة بشكل جدول نظيف
    st.write("")
    st.markdown("### جدول المقارنة")

    st.dataframe(
        comp[["uni_id"] + cols_compare],
        use_container_width=True,
        hide_index=True,
        column_config={
            "website": st.column_config.LinkColumn("Website", display_text="Click here"),
            "admissions_url": st.column_config.LinkColumn("Admissions", display_text="Click here"),
            "programs_url": st.column_config.LinkColumn("Programs", display_text="Click here"),
        }
    )

    st.write("")
    st.markdown("---")
    st.markdown("### مقارنة سريعة (بطاقات)")

    # بطاقات مقارنة (كل جامعة كارد)
    cols = st.columns(len(selected_ids))
    for i, uni_id in enumerate(selected_ids):
        row = comp[comp["uni_id"] == uni_id].iloc[0]
        with cols[i]:
            with st.expander(f"{row['name_ar']} — {row['name_en']}", expanded=True):
                st.write(f"**الموقع:** {row['city']} — {row['country']}")
                st.write(f"**النوع:** {row['type']}")
                st.write(f"**المنح:** {row['scholarship']}")
                st.write(f"**الترتيب:** {row['ranking_source']} {row['ranking_value']}".strip())
                if str(row.get("accreditation_notes", "")).strip():
                    st.write(f"**ملاحظات:** {row['accreditation_notes']}")

                st.write("")
                c1, c2, c3 = st.columns(3)
                if str(row.get("website", "")).strip():
                    c1.link_button("Website", str(row["website"]))
                if str(row.get("admissions_url", "")).strip():
                    c2.link_button("Admissions", str(row["admissions_url"]))
                if str(row.get("programs_url", "")).strip():
                    c3.link_button("Programs", str(row["programs_url"]))
