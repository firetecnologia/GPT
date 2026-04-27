import streamlit as st

from modules.equipments import create_equipment, list_equipments


def render_equipamentos() -> None:
    st.title("Equipamentos")
    with st.form("novo_equip"):
        name = st.text_input("Nome do equipamento *")
        brand = st.text_input("Marca")
        model = st.text_input("Modelo")
        serial_number = st.text_input("Número de série")
        calibration_certificate = st.text_input("Certificado de calibração")
        calibration_date = st.text_input("Data da calibração (YYYY-MM-DD)")
        calibration_valid_until = st.text_input("Validade da calibração (YYYY-MM-DD)")
        notes = st.text_area("Observações")
        submitted = st.form_submit_button("Salvar equipamento")
        if submitted:
            if not name:
                st.error("Nome do equipamento é obrigatório.")
            else:
                create_equipment(
                    {
                        "name": name,
                        "brand": brand,
                        "model": model,
                        "serial_number": serial_number,
                        "calibration_certificate": calibration_certificate,
                        "calibration_date": calibration_date or None,
                        "calibration_valid_until": calibration_valid_until or None,
                        "notes": notes,
                    }
                )
                st.success("Equipamento cadastrado.")
                st.rerun()

    st.dataframe(list_equipments(), use_container_width=True)
