elif st.session_state.page == "المقارنة":
    st.subheader("المقارنة بين الجامعات")

    # تحميل بيانات الجامعات
    unis = normalize_unis(load_csv(UNIS_PATH))
    if unis.empty:
        st.error(f"universities.csv not found or empty: {UNIS_PATH}")
        st.stop()

    # نص مرتب للاختيار
    unis = unis.copy()
    unis["label"] = unis.apply(
        lambda r: f"{str(r['name_ar']).strip()} — {str(r['name_en']).strip()} ({str(r['city']).strip()}, {str(r['country']).strip()})",
        axis=1
    )
    unis = unis.sort_values(["country", "city", "name_en"], na_position="last")

    selected_ids = st.multiselect(
        "اختاري 2 إلى 4 جامعات للمقارنة",
        options=unis["uni_id"].tolist(),
        format_func=lambda x: unis.loc[unis["uni_id"] == x, "label"].values[0],
        max_selections=4
    )

    if len(selected_ids) < 2:
        st.info("لازم تختارين جامعتين على الأقل عشان تظهر المقارنة.")
        st.stop()

    comp = unis[unis["uni_id"].isin(selected_ids)].copy()

    # أعمدة المقارنة
    cols_compare = [
        "uni_id","name_ar","name_en","country","city","type",
        "scholarship","ranking_source","ranking_value","accreditation_notes",
        "website","admissions_url","programs_url"
    ]
    for c in cols_compare:
        if c not in comp.columns:
            comp[c] = ""

    st.markdown("### جدول المقارنة")
    st.dataframe(
        comp[cols_compare],
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

    cols = st.columns(len(selected_ids))
    for i, uni_id in enumerate(selected_ids):
        row = comp[comp["uni_id"] == uni_id].iloc[0]
        with cols[i]:
            with st.expander(f"{row['name_ar']} — {row['name_en']}", expanded=True):
                st.write(f"**الموقع:** {row['city']} — {row['country']}")
                st.write(f"**النوع:** {row['type']}")
                st.write(f"**المنح:** {row['scholarship']}")
                st.write(f"**الترتيب:** {str(row['ranking_source']).strip()} {str(row['ranking_value']).strip()}".strip())

                notes = str(row.get("accreditation_notes", "")).strip()
                if notes:
                    st.write(f"**ملاحظات:** {notes}")

                st.write("")
                c1, c2, c3 = st.columns(3)
                if str(row.get("website", "")).strip():
                    c1.link_button("Website", str(row["website"]))
                if str(row.get("admissions_url", "")).strip():
                    c2.link_button("Admissions", str(row["admissions_url"]))
                if str(row.get("programs_url", "")).strip():
                    c3.link_button("Programs", str(row["programs_url"]))
