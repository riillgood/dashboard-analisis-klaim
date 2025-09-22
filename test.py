# file: test.py

import streamlit as st
import time

st.set_page_config(layout="wide")

st.title("Halaman Uji Coba Diagnostik")

st.info("Tes ini bertujuan untuk memeriksa apakah proses `import rumus` menyebabkan masalah.")
st.write(f"Waktu mulai: {time.time()}")

try:
    # Kita akan coba import file yang kita curigai
    import rumus as r
    
    # Jika baris ini muncul, berarti import berhasil dan tidak macet
    st.success("🎉 `rumus.py` BERHASIL DI-IMPORT!")
    st.balloons()
    st.write("Ini berarti masalahnya bukan pada proses import, melainkan pada beban total aplikasi multi-halaman Anda.")
    st.write(f"Waktu selesai: {time.time()}")

except Exception as e:
    st.error(f"Gagal total saat mencoba mengimpor 'rumus.py'. Error: {e}")